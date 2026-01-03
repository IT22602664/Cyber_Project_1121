from src.embedding import generate_embedding
from src.similarity import compute_similarity

# Test images
image1_path = "test_images/face1.jpg"
image2_path = "test_images/face2.jpg"

# Generate embeddings
embedding1 = generate_embedding(image1_path)
embedding2 = generate_embedding(image2_path)

# Compute similarity
similarity = compute_similarity(embedding1, embedding2)

# Decision logic
threshold = 0.9535
if similarity >= threshold:
    print("MATCH")
else:
    print("NO MATCH")