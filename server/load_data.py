import gc
import os
from embed import create_embedding, MODEL_DIM
from aerospike_vector_search import types, AdminClient, Client
from markdownify import MarkdownConverter
from scraper.run_scraper import Scraper

namespace = "rag-vector"
index_name = os.getenv("AVS_INDEX_NAME")
set_name = os.getenv("AVS_SET_NAME")

class MarkdownConvert(MarkdownConverter):
    def convert_hn(self, n, el, text, convert_as_inline):
        style = self.options['heading_style'].lower()
        if style == "none":
            text = text.strip()
            return text + "\n\n "
        return super().convert_hn(n, el, text, convert_as_inline)

        
def md(html, **options):
    return MarkdownConvert(**options).convert(html)

def code_callback(el):
    if el.has_attr('class'):
        return el['class'][1].split("-")[1] if not el['class'][0] == "ckeditor_codeblock"  else None
    else:
        return None
    
# Creates the vector index on the "img_embedding" bin
# Returns if it already exists
def create_vector_index(vector_admin: AdminClient):   
    print("Checking for vector index")
    
    for idx in vector_admin.index_list():
        if (
            idx["id"]["namespace"] == namespace
            and idx["id"]["name"] == index_name
        ):
            print("Index already exists")
            return
        
    print("Creating vector index")
    vector_admin.index_create(
        namespace=namespace,
        name=index_name,
        sets=set_name,
        vector_field="doc_embedding",
        dimensions=MODEL_DIM,
        vector_distance_metric=types.VectorDistanceMetric.COSINE,
    )    
    print("Index created")

options = {
    "escape_asterisks": False, 
    "escape_underscores": False,
    "code_language_callback": code_callback,
    "heading_style": "none",
    "strip": ["hr"]
}

def create_document_chunks(vector_client: Client, document: dict):
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
        doc["doc_embedding"] = create_embedding(f"TITLE: {doc['title']}, DESCRIPTION: {doc['desc']}, CONTENT: {doc['content']}")
        vector_client.upsert(
            namespace=namespace, 
            set_name=set_name,
            key=f"{doc['url'] + str(chunk_idx)}", 
            record_data=doc
        )
        chunk = ""
        chunk_idx += 1
        del doc
    del document, chunk
    gc.collect()

if __name__=="__main__": 
    docs_scraper = Scraper()
    docs_scraper.run_spiders()