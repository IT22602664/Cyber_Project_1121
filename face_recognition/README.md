# Face Verification with ResNet50 Triplet Model

This project implements a face verification system using a ResNet50 model trained with Triplet Loss. The system generates embeddings for face images and compares them using cosine similarity.

## Features
- **Model**: ResNet50 trained with Triplet Loss.
- **Task**: Face verification (1:1 identity matching).
- **Input**: RGB face images (160x160).
- **Output**: 512-dimensional embeddings.

## Setup Instructions

### 1. Install Dependencies
Ensure you have Python 3.8+ installed. Install the required packages:
```bash
pip install -r requirements.txt
```

### 2. Preprocess Input Images
Ensure input images are:
- Resized to 160x160.
- Normalized with mean=[0.5, 0.5, 0.5] and std=[0.5, 0.5, 0.5].

### 3. Run the API
Start the API to generate embeddings and compare faces:
```bash
python src/api.py
```

### 4. Test the System
Run the test script to validate the system:
```bash
python test.py
```

## Directory Structure
- `src/`: Source code for preprocessing, embedding generation, and API.
- `models/`: Pretrained model checkpoint (`best_resnet50_triplet.pth`).
- `test.py`: Script for testing the system.

## Usage
1. Place the pretrained model in the `models/` directory.
2. Use the API or test script to verify faces.

## Example
Generate embeddings for two images and compute similarity:
```python
from src.embedding import generate_embedding
from src.similarity import compute_similarity

embedding1 = generate_embedding('face1.jpg')
embedding2 = generate_embedding('face2.jpg')
similarity = compute_similarity(embedding1, embedding2)

if similarity >= 0.9535:
    print("MATCH")
else:
    print("NO MATCH")
```

## Notes
- Ensure preprocessing matches the training pipeline.
- Use the validated threshold (0.9535) for similarity comparison.