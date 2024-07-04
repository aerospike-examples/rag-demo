import os
from scraper.docs.spiders.scraper import DocSpider
from scrapy.crawler import CrawlerProcess
from scrapy.utils.project import get_project_settings

class Scraper:
    def __init__(self):
        settings_file_path = 'scraper.docs.settings'
        os.environ.setdefault('SCRAPY_SETTINGS_MODULE', settings_file_path)
        self.process = CrawlerProcess(get_project_settings())
        self.spider = DocSpider

    def run_spiders(self):
        self.process.crawl(self.spider, sitemap_urls=[os.getenv("SCRAPER_SITE_MAP")])
        self.process.start()