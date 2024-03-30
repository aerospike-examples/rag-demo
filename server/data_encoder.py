import torch.nn.functional as F
from sentence_transformers import SentenceTransformer

# The image or text encoding model.
model = SentenceTransformer("../../nomic-embed-text-v1.5/", trust_remote_code=True)
MODEL_DIM = 768

def encoder(data, type: str = "document"):
    doc = f"search_{type}: {data}"
    return model.encode(doc)