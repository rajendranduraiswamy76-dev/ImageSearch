"""CLIP embedding wrapper shared by text and image queries (same embedding space)."""
import numpy as np
from PIL import Image
from sentence_transformers import SentenceTransformer


class ClipEmbedder:
    def __init__(self, model_name="clip-ViT-B-32"):
        self.model = SentenceTransformer(model_name)

    def encode_image(self, image_path):
        image = Image.open(image_path).convert("RGB")
        vec = self.model.encode(image, convert_to_numpy=True, normalize_embeddings=True)
        return vec.astype(np.float32)

    def encode_text(self, text):
        vec = self.model.encode(text, convert_to_numpy=True, normalize_embeddings=True)
        return vec.astype(np.float32)
