from scrapy.spiders import SitemapSpider, Request
from scrapy.utils.sitemap import Sitemap
   
class MySpider(SitemapSpider):
    name = "docs"
    sitemap_urls = [
        "https://aerospike.com/docs/sitemap.xml",
        "https://aerospike.com/developer/sitemap.xml"
    ]

    def _parse_sitemap(self, response):
        body = self._get_sitemap_body(response)
        sitemap = Sitemap(body)

        ignore_paths = [
            "/developer/tags",
            "/developer/blog/page/",
            "/developer/blog/tags",
            "/developer/blog/vol-",
            "/release_notes/",
            "/docs/graph/tags",
            "/docs/graph/1.",
            "/docs/cloud/kubernetes/operator/tags",
            "/docs/cloud/kubernetes/operator/1.",
            "/docs/cloud/kubernetes/operator/2.",
            "/docs/cloud/kubernetes/operator/3.",
            "/docs/tags",
            "/docs/reference/metrics",
            "/docs/server/reference/",
            "/docs/tools/tools_issues"
        ]

        client_paths = [
            "/use-cases/",
            "/client/install",
            "/client/logging",
            "/client/connect",
            "/client/data_type",
            "/client/usage",
            "/client/async",
            "/client/error",
            "/client/metrics",
            "/client/best_practices",
            "/client/benchmarks",
            "/client/incompatible"
        ]
        
        clients = ["c", "csharp", "go", "java", "nodejs", "php", "python", "ruby", "rust"]
        
        for entry in sitemap:
            url = entry["loc"]
            if any(path in url for path in ignore_paths):
                yield None
            elif any(path in url for path in client_paths):
                for client in clients:
                    yield Request(f"{url}?client={client}", self.parse, meta={"playwright": True})
            else:
                yield Request(url, self.parse, meta={"playwright": True})
        
    def parse(self, response):
        doc = response.xpath("//div[contains(@class, 'markdown')]/node()").extract()
        index_page = response.xpath("//div[contains(@class, 'generatedIndexPage')]").get()

        if doc and not index_page:
            if response.xpath("//div[contains(@class, 'placeholder')]"):
                return
            
            title = response.css("h1::text").get()
            desc = response.css("meta[name=description]::attr(content)").get() or title
         
            return {
                "meta": {
                    "title": title,
                    "desc": desc,
                    "url": response.url
                },
                "doc": doc
            }
                   
        else:
            return
