import torch
import torch.nn.functional as F
from transformers import AutoModel, AutoTokenizer

def mean_pooling(model_output, attention_mask):
    token_embeddings = model_output[0]
    input_mask_expanded = attention_mask.unsqueeze(-1).expand(token_embeddings.size()).float()
    return torch.sum(token_embeddings * input_mask_expanded, 1) / torch.clamp(input_mask_expanded.sum(1), min=1e-9)

tokenizer = AutoTokenizer.from_pretrained('bert-base-uncased')
model = AutoModel.from_pretrained("../../Models/nomic-embed-text-v1.5/", trust_remote_code=True, safe_serialization=True)
model.eval()

MODEL_DIM = 768

def encoder(data, type: str = "document"):
    doc = f"search_{type}: {data}"
    encoded_input = tokenizer(doc, padding=True, truncation=True, return_tensors='pt')

    with torch.no_grad():
        model_output = model(**encoded_input)
    
    embeddings = mean_pooling(model_output, encoded_input['attention_mask'])
    embeddings = F.normalize(embeddings, p=2, dim=1)
    return embeddings[0].tolist()