from scrapy.spiders import SitemapSpider, Request
from scrapy.utils.sitemap import Sitemap
from scrapy_playwright.page import PageMethod
   
class MySpider(SitemapSpider):
    name = "docs"
    sitemap_urls = [
        "https://aerospike-vector-search.netlify.app/sitemap.xml",
        "https://aerospike.com/docs/sitemap.xml",
        "https://aerospike.com/developer/sitemap.xml",
        "https://support.aerospike.com/s/sitemap-topicarticle-1.xml",
        "https://aerospike.com/sitemap-1.xml"
    ]

    def _parse_sitemap(self, response):
        body = self._get_sitemap_body(response)
        sitemap = Sitemap(body)
        
        ignore_paths_full = [
            "https://aerospike.com/",
            "https://aerospike.com/blog/",
            "https://aerospike.com/docs/",
            "https://aerospike.com/developer/",
            "https://aerospike.com/developer/tutorials",
            "https://aerospike.com/developer/tutorials/sandbox",
            "https://aerospike.com/developer/new"
        ]

        ignore_paths_includes = [
            "/author/",
            "/blog/category/",
            "aerospike-standup",
            "/search/",
            "/download/",
            "/about-us",
            "/compare/",
            "/tags",
            "/developer/video",
            "/developer/blog",
            "/release_notes",
            "/release-notes",
            "/docs/graph/1.",
            "/docs/cloud/kubernetes/operator/1.",
            "/docs/cloud/kubernetes/operator/2.",
            "/docs/cloud/kubernetes/operator/3.",
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
            if "aerospike.com/vector" in url:
                url = url.replace("aerospike.com", "aerospike-vector-search.netlify.app")
            
            if url in ignore_paths_full:
                yield None
            elif any(path in url for path in ignore_paths_includes):
                yield None
            elif "support.aerospike.com" in url:
                yield Request(url, self.parse, meta={
                    "playwright": True, 
                    "playwright_page_methods": [
                        PageMethod("wait_for_selector", "article.content > div.full")
                    ]
                })
            elif any(path in url for path in client_paths) and url != "https://aerospike.com/developer/client/connection_tuning_guide":
                for client in clients:
                    yield Request(f"{url}?client={client}", self.parse, meta={"playwright": True})
            else:
                yield Request(url, self.parse, meta={"playwright": True})
        
    def parse(self, response):
        url = response.url
        if "aerospike.com/blog" in url:
            doc = response.xpath("//div[contains(@class, '_main')]/astro-island/node()").extract()
        elif "support.aerospike.com" in url:
            doc = response.xpath("/descendant::div[contains(@class, 'section__content')][2]/div/node()").extract()
        else:
            doc = response.xpath("//div[contains(@class, 'markdown')]/node()").extract()
            
        index_page = response.xpath("//div[contains(@class, 'generatedIndexPage')]").get()
        placeholder = response.xpath("//div[contains(@class, 'placeholder')]").get()    
          
        if doc and not index_page and not placeholder:
            title = response.css("title::text").get().split(" |")[0];
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
