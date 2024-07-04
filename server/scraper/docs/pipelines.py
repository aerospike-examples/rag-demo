# Define your item pipelines here
#
# Don't forget to add your pipeline to the ITEM_PIPELINES setting
# See: https://docs.scrapy.org/en/latest/topics/item-pipeline.html


# useful for handling different item types with a single interface
from clients import vector_client, vector_admin
from load_data import create_vector_index, create_document_chunks
from tqdm import tqdm

class DocsPipeline:
    def open_spider(self, spider):
        self.progress = None
        self.client = vector_client
        create_vector_index(vector_admin)
        vector_admin.close()

    def close_spider(self, spider):
        self.progress.close()
        self.client.close()
        print("Crawling complete, content and embeddings loaded.")

    def process_item(self, item, spider):
        if self.progress is None:
            self.progress = tqdm(desc="Crawling site and generating embeddings...", total=spider.page_total)
        self.progress.update(1)
        if item.get("generated_idx") is None:
            create_document_chunks(vector_client, item)
        return
