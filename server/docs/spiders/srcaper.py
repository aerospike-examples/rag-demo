from scrapy.spiders import SitemapSpider
from config import Config
from data_encoder import encoder
from proximus_client import proximus_client

class MySpider(SitemapSpider):
    name = "docs"
    sitemap_urls = [
        "https://aerospike.com/docs/sitemap.xml",
        "https://aerospike.com/developer/sitemap.xml"
    ]

    def parse(self, response):
        doc_node = response.css("div.theme-doc-markdown")
        blog_node = response.css("#__blog-post-container")
        
        doc = doc_node or blog_node

        if doc:
            title = response.css("h1::text").get()
            desc = response.css("meta[name=description]::attr(content)").get() or title

            text = " ".join(doc.xpath(".//*//text()").getall())
            documents = []

            if len(text.split()) < 300:
                documents.append(f"Document title: {title}. Document description: {desc}. Document text: {text}")
            else:
                words = []
                for node in doc.xpath("./*"):
                    words.append(" ".join(node.xpath(".//*//text()").getall()))
                    text = " ".join(words)
                    if len(text) > 300:
                        documents.append(f"Document title: {title}. Document description: {desc}. Document text: {text}")
                        words.clear()
                        
            for idx, document in enumerate(documents):
                doc_entry = {"title": title, "url": response.url}
                embedding = encoder(document)
                doc_entry["doc_embedding"] = embedding.tolist()
                doc_entry["content"] = document

                try:
                    proximus_client.put(
                        Config.PROXIMUS_NAMESPACE, Config.PROXIMUS_SET, title + str(idx), doc_entry
                    )
                except Exception as e:
                    yield {"embedding": "failed to write{e}".format(e)}
                    
        else:
            return