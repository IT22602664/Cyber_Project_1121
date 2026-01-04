"""
REST API for Face Verification (ResNet50 Triplet Embedding)
- Enroll: create a template embedding for a user from multiple images
- Verify: compare a new image embedding against the enrolled template
- Monitoring: health + enrolled users

Model checkpoint:
- best_resnet50_triplet.pth (PyTorch state_dict-style checkpoint)

Assumptions (based on your training pipeline):
- ResNet50 backbone
- fc replaced to output EMBED_DIM=512
- L2-normalized embeddings
- Verification by cosine similarity with a threshold (default 0.9535)
"""

from fastapi import FastAPI, HTTPException, status, UploadFile, File
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, Field
from typing import List, Dict, Optional
from loguru import logger
from datetime import datetime
import io
import base64
import time

import numpy as np
import torch
import torch.nn as nn
import torch.nn.functional as F
from PIL import Image

from torchvision import transforms, models


# =========================
# Configuration (edit as needed)
# =========================
class AppConfig(BaseModel):
    checkpoint_path: str = r"models\best_resnet50_triplet.pth"     # path to your checkpoint
    embed_dim: int = 512
    threshold: float = 0.30                                # cosine similarity threshold (optimized from evaluation)
    device: str = "cpu"                                    # "cuda" if GPU available
    face_size: int = 160                                   # use whatever you trained with (e.g., 160 or 112)
    allow_origins: List[str] = ["*"]                       # restrict in production


config = AppConfig()


# =========================
# Model definition (ResNet50 -> 512-d + L2 norm)
# =========================
class ResNet50TripletEmbedder(nn.Module):
    """
    ResNet50 backbone with final fully-connected replaced to output embeddings.
    L2 normalization applied to output embeddings.
    """
    def __init__(self, embed_dim: int = 512):
        super().__init__()

        # Create ResNet50 without pretrained weights (we load your trained weights)
        # Wrapped in a backbone attribute to match the saved model structure
        self.backbone = models.resnet50(weights=None)

        # Replace classification head (fc) with embedding head
        in_features = self.backbone.fc.in_features
        self.backbone.fc = nn.Linear(in_features, embed_dim)

    def forward(self, x: torch.Tensor) -> torch.Tensor:
        emb = self.backbone(x)               # [B, embed_dim]
        emb = F.normalize(emb, p=2, dim=1)   # L2 normalize
        return emb


# =========================
# Image preprocessing
# =========================
def build_transforms(face_size: int) -> transforms.Compose:
    """
    Must match training preprocessing as closely as possible.
    If you used Normalize(mean=0.5,std=0.5), keep it.
    """
    return transforms.Compose([
        transforms.Resize((face_size, face_size)),
        transforms.ToTensor(),
        transforms.Normalize(mean=[0.5, 0.5, 0.5], std=[0.5, 0.5, 0.5]),
    ])


img_tfms = build_transforms(config.face_size)


def decode_base64_image(b64: str) -> Image.Image:
    """
    Decode a base64 string into a PIL Image (RGB).
    Accepts both raw base64 and data URLs like: data:image/jpeg;base64,...
    """
    try:
        if "," in b64:
            b64 = b64.split(",", 1)[1]
        binary = base64.b64decode(b64)
        img = Image.open(io.BytesIO(binary)).convert("RGB")
        return img
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Invalid base64 image: {str(e)}"
        )


def pil_to_tensor(img: Image.Image, device: torch.device) -> torch.Tensor:
    """
    Convert PIL image -> model input tensor [1,3,H,W] on device.
    """
    x = img_tfms(img).unsqueeze(0)  # [1,3,H,W]
    return x.to(device)


# =========================
# Verification helpers
# =========================
@torch.no_grad()
def compute_embedding(model: nn.Module, x: torch.Tensor) -> torch.Tensor:
    """
    Compute embedding for a batch tensor.
    Returns normalized embedding(s).
    """
    model.eval()
    emb = model(x)  # already normalized in forward()
    return emb


def cosine_similarity(a: torch.Tensor, b: torch.Tensor) -> float:
    """
    Cosine similarity for two normalized vectors.
    a,b: shape [embed_dim] or [1, embed_dim]
    """
    if a.ndim == 2:
        a = a.squeeze(0)
    if b.ndim == 2:
        b = b.squeeze(0)
    sim = torch.dot(a, b).item()
    return float(sim)


def mean_template(embeddings: List[torch.Tensor]) -> torch.Tensor:
    """
    Mean multiple embeddings and re-normalize.
    """
    stack = torch.stack([e.squeeze(0) for e in embeddings], dim=0)  # [N, D]
    mu = stack.mean(dim=0, keepdim=True)                            # [1, D]
    mu = F.normalize(mu, p=2, dim=1)
    return mu


# =========================
# Pydantic request/response models
# =========================
class EnrollmentRequest(BaseModel):
    user_id: str = Field(..., description="Unique user identifier")
    images_base64: List[str] = Field(..., description="List of base64-encoded face images")
    session_id: Optional[str] = Field(default=None, description="Session identifier")


class VerificationRequest(BaseModel):
    user_id: str = Field(..., description="User identifier to verify")
    image_base64: str = Field(..., description="Base64-encoded face image")
    session_id: Optional[str] = Field(default=None, description="Session identifier")


class ImageComparisonRequest(BaseModel):
    image1: str = Field(..., description="Base64-encoded first face image")
    image2: str = Field(..., description="Base64-encoded second face image")


class ImageComparisonResponse(BaseModel):
    verified: bool
    similarity: float
    threshold: float
    latency_ms: float
    timestamp: str


class EnrollmentResponse(BaseModel):
    success: bool
    user_id: str
    n_samples: int
    embedding_dim: int
    message: Optional[str] = None


class VerificationResponse(BaseModel):
    verified: bool
    similarity: float
    threshold: float
    alert: bool
    critical: bool
    latency_ms: float
    user_id: str
    timestamp: str


class HealthResponse(BaseModel):
    status: str
    model_loaded: bool
    enrolled_users: int
    timestamp: str


# =========================
# FastAPI app
# =========================
app = FastAPI(
    title="Face Verification API",
    description="Face verification using ResNet50 Triplet Embeddings (best_resnet50_triplet.pth)",
    version="1.0.0"
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=config.allow_origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Globals initialized at startup
device = torch.device(config.device)
model: Optional[nn.Module] = None

# In-memory template store (user_id -> embedding tensor [1,512])
# NOTE: This is volatile; restart loses data. For production, persist to DB/files.
enrolled_templates: Dict[str, torch.Tensor] = {}


@app.on_event("startup")
async def startup_event():
    global model, device

    logger.info("Starting Face Verification API...")

    # Choose device
    if config.device == "cuda" and torch.cuda.is_available():
        device = torch.device("cuda")
    else:
        device = torch.device("cpu")

    # Build model
    model = ResNet50TripletEmbedder(embed_dim=config.embed_dim)

    # Load checkpoint
    try:
        ckpt = torch.load(config.checkpoint_path, map_location="cpu")

        # Support two common formats:
        # 1) state_dict directly
        # 2) dict containing 'model_state_dict'
        if isinstance(ckpt, dict) and "model_state_dict" in ckpt:
            state_dict = ckpt["model_state_dict"]
        else:
            state_dict = ckpt

        model.load_state_dict(state_dict, strict=True)
        model.to(device)
        model.eval()
        logger.info(f"Model loaded: {config.checkpoint_path} | device={device}")

    except Exception as e:
        logger.error(f"Failed to load model checkpoint: {e}")
        model = None
        raise

    logger.info("Face Verification API started successfully.")


@app.get("/", response_model=Dict)
async def root():
    return {
        "service": "Face Verification API",
        "version": "1.0.0",
        "status": "running",
        "model": "ResNet50 Triplet Embedder",
        "embedding_dim": config.embed_dim,
        "threshold": config.threshold,
    }


@app.get("/health", response_model=HealthResponse)
async def health_check():
    return HealthResponse(
        status="healthy" if model is not None else "unhealthy",
        model_loaded=model is not None,
        enrolled_users=len(enrolled_templates),
        timestamp=datetime.now().isoformat()
    )


@app.post("/enroll", response_model=EnrollmentResponse)
async def enroll_user(request: EnrollmentRequest):
    """
    Enroll a user by building a template embedding from multiple face images.
    """
    if model is None:
        raise HTTPException(status_code=503, detail="Model not loaded")

    try:
        logger.info(f"Enrollment request: user_id={request.user_id} samples={len(request.images_base64)}")

        if len(request.images_base64) < 2:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Enrollment requires at least 2 images (recommended: 5-10)."
            )

        embeddings: List[torch.Tensor] = []

        for b64 in request.images_base64:
            img = decode_base64_image(b64)
            x = pil_to_tensor(img, device)
            emb = compute_embedding(model, x)      # [1,512]
            embeddings.append(emb.cpu())           # store on CPU to reduce GPU memory use

        template = mean_template(embeddings)       # [1,512], normalized
        enrolled_templates[request.user_id] = template

        return EnrollmentResponse(
            success=True,
            user_id=request.user_id,
            n_samples=len(request.images_base64),
            embedding_dim=config.embed_dim,
            message="User enrolled successfully"
        )

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Enrollment error: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/verify", response_model=VerificationResponse)
async def verify_user(request: VerificationRequest):
    """
    Verify a user by comparing a new image embedding against the enrolled template.
    """
    if model is None:
        raise HTTPException(status_code=503, detail="Model not loaded")

    if request.user_id not in enrolled_templates:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"User '{request.user_id}' not enrolled"
        )

    t0 = time.time()

    try:
        logger.info(f"Verification request: user_id={request.user_id}")

        img = decode_base64_image(request.image_base64)
        x = pil_to_tensor(img, device)
        emb = compute_embedding(model, x).cpu()  # [1,512]

        template = enrolled_templates[request.user_id]  # [1,512] on CPU
        sim = cosine_similarity(emb, template)
        verified = sim >= config.threshold

        # Simple alert policy (tune as needed)
        alert = (sim < config.threshold)                       # failed
        critical = (sim < (config.threshold - 0.05))           # very low margin

        latency_ms = (time.time() - t0) * 1000.0

        if alert:
            logger.warning(f"ALERT user={request.user_id} sim={sim:.4f} thr={config.threshold:.4f}")
        if critical:
            logger.error(f"CRITICAL user={request.user_id} sim={sim:.4f} thr={config.threshold:.4f}")

        return VerificationResponse(
            verified=verified,
            similarity=sim,
            threshold=config.threshold,
            alert=alert,
            critical=critical,
            latency_ms=latency_ms,
            user_id=request.user_id,
            timestamp=datetime.now().isoformat()
        )

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Verification error: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/verify-images", response_model=ImageComparisonResponse)
async def verify_two_images(request: ImageComparisonRequest):
    """
    Compare two arbitrary images directly (no enrollment needed).
    Returns similarity and whether they match based on threshold.
    """
    if model is None:
        raise HTTPException(status_code=503, detail="Model not loaded")

    t0 = time.time()

    try:
        logger.info("Image comparison request received")

        # Decode both images
        img1 = decode_base64_image(request.image1)
        img2 = decode_base64_image(request.image2)

        # Generate embeddings
        x1 = pil_to_tensor(img1, device)
        x2 = pil_to_tensor(img2, device)
        
        emb1 = compute_embedding(model, x1).cpu()
        emb2 = compute_embedding(model, x2).cpu()

        # Compute similarity
        sim = cosine_similarity(emb1, emb2)
        verified = sim >= config.threshold

        latency_ms = (time.time() - t0) * 1000.0

        logger.info(f"Image comparison: similarity={sim:.4f}, verified={verified}")

        return ImageComparisonResponse(
            verified=verified,
            similarity=sim,
            threshold=config.threshold,
            latency_ms=latency_ms,
            timestamp=datetime.now().isoformat()
        )

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Image comparison error: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/enrolled-users")
async def get_enrolled_users():
    return {
        "enrolled_users": list(enrolled_templates.keys()),
        "count": len(enrolled_templates),
    }


# Optional: multipart upload verify (useful for Postman/testing)
@app.post("/verify-upload", response_model=VerificationResponse)
async def verify_user_upload(user_id: str, file: UploadFile = File(...)):
    """
    Verify using a multipart file upload (image).
    """
    if model is None:
        raise HTTPException(status_code=503, detail="Model not loaded")

    if user_id not in enrolled_templates:
        raise HTTPException(status_code=404, detail=f"User '{user_id}' not enrolled")

    t0 = time.time()

    try:
        raw = await file.read()
        img = Image.open(io.BytesIO(raw)).convert("RGB")
        x = pil_to_tensor(img, device)
        emb = compute_embedding(model, x).cpu()

        template = enrolled_templates[user_id]
        sim = cosine_similarity(emb, template)
        verified = sim >= config.threshold

        alert = (sim < config.threshold)
        critical = (sim < (config.threshold - 0.05))

        latency_ms = (time.time() - t0) * 1000.0

        return VerificationResponse(
            verified=verified,
            similarity=sim,
            threshold=config.threshold,
            alert=alert,
            critical=critical,
            latency_ms=latency_ms,
            user_id=user_id,
            timestamp=datetime.now().isoformat()
        )

    except Exception as e:
        logger.error(f"verify-upload error: {e}")
        raise HTTPException(status_code=500, detail=str(e))


if __name__ == "__main__":
    import uvicorn

    # Run: python api.py
    uvicorn.run(
        "api:app",
        host="0.0.0.0",
        port=8000,
        reload=True,
        log_level="info"
    )
