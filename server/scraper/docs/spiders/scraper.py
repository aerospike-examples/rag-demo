from scrapy.spiders import SitemapSpider, Request
from scrapy.utils.sitemap import Sitemap
   
class DocSpider(SitemapSpider):
    name = "docs"
    page_total = 0
    
    def _parse_sitemap(self, response):
        body = self._get_sitemap_body(response)
        sitemap = Sitemap(body)

        # Specific to crawling https://aerospike.com/docs/
        ignore_paths_includes = [
            "/tags",
            "/release_notes",
            "/release-notes",
            "/docs/graph/1.",
            "/docs/graph/2.",
            "/docs/cloud/kubernetes/operator/1.",
            "/docs/cloud/kubernetes/operator/2.",
            "/docs/cloud/kubernetes/operator/3.",
            "/docs/reference/metrics",
            "/docs/server/reference",
            "/docs/tools/tools_issues"
        ]

        for entry in sitemap:
            url = entry["loc"]
            if any(path in url for path in ignore_paths_includes):
                yield None
            else:
                self.page_total += 1
                yield Request(url, self.parse, meta={"playwright": True})
        
    def parse(self, response):
        url = response.url
        doc = response.xpath("//div[contains(@class, 'markdown')]/node()").extract()    
        index_page = response.xpath("//div[contains(@class, 'generatedIndexPage')]").get()    
          
        if doc and not index_page:
            title = response.css("title::text").get().split(" |")[0];
            desc = response.css("meta[name=description]::attr(content)").get() or title
         
            return {
                "meta": {
                    "title": title,
                    "desc": desc,
                    "url": url
                },
                "doc": doc
            }
                   
        else:
            return {"generated_idx": True}
