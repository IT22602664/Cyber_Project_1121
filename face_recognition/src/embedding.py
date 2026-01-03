import torch
import torch.nn as nn
import torchvision.transforms as transforms
from torchvision import models
from PIL import Image
import os

# Define the model architecture with backbone wrapper
class TripletModel(nn.Module):
    def __init__(self):
        super(TripletModel, self).__init__()
        self.backbone = models.resnet50(weights=None)
        self.backbone.fc = nn.Linear(self.backbone.fc.in_features, 512)
    
    def forward(self, x):
        return self.backbone(x)

# Load the pretrained model
# Get the absolute path to the models directory
SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
MODEL_PATH = os.path.join(SCRIPT_DIR, "..", "models", "best_resnet50_triplet.pth")

# Create model and load weights
model = TripletModel()
state_dict = torch.load(MODEL_PATH, map_location=torch.device('cpu'))
model.load_state_dict(state_dict)
model.eval()

# Preprocessing pipeline
def preprocess_image(image_path):
    """Preprocess the input image to match the model's requirements."""
    transform = transforms.Compose([
        transforms.Resize((160, 160)),
        transforms.ToTensor(),
        transforms.Normalize(mean=[0.5, 0.5, 0.5], std=[0.5, 0.5, 0.5])
    ])
    image = Image.open(image_path).convert('RGB')
    return transform(image).unsqueeze(0)

# Generate embedding
def generate_embedding(image_path):
    """Generate a 512-dimensional embedding for the input image."""
    image_tensor = preprocess_image(image_path)
    with torch.no_grad():
        embedding = model(image_tensor)
    return embedding.squeeze().numpy()