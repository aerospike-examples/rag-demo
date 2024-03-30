import json
from data_encoder import encoder, MODEL_DIM
from proximus_client import proximus_client, proximus_admin_client
from aerospike_vector import types_pb2
from config import Config
from markdownify import MarkdownConverter

class MarkdownConvert(MarkdownConverter):
    def convert_a(self, el, text, convert_as_inline):
        class_name = el.get("class")
        if class_name and  "hash-link" in class_name:
            return ""
        href = el.get("href")
        if href and href.startswith("/"):
            el["href"] = f"https://aerospike.com{href}" 
        return super().convert_a(el, text, convert_as_inline)

    def convert_hn(self, n, el, text, convert_as_inline):
        style = self.options['heading_style'].lower()
        if style == "none":
            text = text.strip()
            return text + "\n\n "
        return super().convert_hn(n, el, text, convert_as_inline)

        
def md(html, **options):
    return MarkdownConvert(**options).convert(html)

def code_callback(el):
    return el['class'][1].split("-")[1] if el.has_attr('class') else None

def create_index():
    print("Checking for vector index")
    for index in proximus_admin_client.indexList():
        if (
            index.id.namespace == Config.PROXIMUS_NAMESPACE
            and index.id.name == Config.PROXIMUS_INDEX_NAME
        ):
            print("Index already exists")
            return
    print("Creating vector index")
    proximus_admin_client.indexCreate(
        namespace=Config.PROXIMUS_NAMESPACE,
        name=Config.PROXIMUS_INDEX_NAME,
        setFilter=Config.PROXIMUS_SET,
        vector_bin_name="doc_embedding",
        dimensions=MODEL_DIM,
        vector_distance_metric=types_pb2.VectorDistanceMetric.COSINE,
    )    
    print("Index created")

create_index()

print("Generating embeddings")

options = {
    "escape_asterisks": False, 
    "escape_underscores": False,
    "code_language_callback": code_callback,
    "heading_style": "none",
    "strip": ["hr"]
}

with open('documents.jsonl') as f:
    for line in f:
        document = json.loads(line)
        chunk = ""
        chunk_idx = 0 
        
        for section in document["doc"]:
            try:
                chunk += (" " + md(section, **options))
            except:
                print(section)

            if (len(chunk) - chunk.count(" ")) < 2000:
                continue
            doc = {
                "title": document["meta"]["title"],
                "url": document["meta"]["url"],
                "desc": document["meta"]["desc"],
                "content": chunk.strip(), 
                "idx": chunk_idx
            }
            doc_embedding = encoder(doc["content"])
            doc["doc_embedding"] = doc_embedding.tolist()
            proximus_client.put(Config.PROXIMUS_NAMESPACE, Config.PROXIMUS_SET, f"{doc['url'] + str(chunk_idx)}", doc)
            chunk = ""
            chunk_idx += 1

proximus_client.close()
proximus_admin_client.close()

print("Embedding generation complete")