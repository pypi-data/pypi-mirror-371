# Define your item pipelines here
#
# Don't forget to add your pipeline to the ITEM_PIPELINES setting
# See: https://docs.scrapy.org/en/latest/topics/item-pipeline.html
import json

# useful for handling different item types with a single interface
from itemadapter import ItemAdapter


class ScrahotPipeline:
    def open_spider(self, spider):
        self.file = open(f"items-{spider.params['uuid']}.json", "w")

    def close_spider(self, spider):
        self.file.close()

    def process_item(self, item, spider):
        print(f"process_item")
        print(f"{spider.name}: {item['json']}")
        line = json.dumps(ItemAdapter(item['json']).asdict()) + "\n"
        self.file.write(line)
        return item
