import scrapy
import json


class PricespiderSpider(scrapy.Spider):
    name = "pricespider"
    allowed_domains = ["www.rightmove.co.uk"]

    start_urls = ["https://www.rightmove.co.uk/house-prices/southwark-85215.html?soldIn=1&page=1"]

    def parse(self, response):
        
        script_content = response.xpath("//script[contains(text(),'window.__PRELOADED_STATE__')]//text()").get()[29:]

        data = json.loads(script_content)

        properties = data['results']['properties']

        if len(properties) == 0:
            return None

        for property_item in properties:

            yield{
                'address': property_item['address'],
                'type': property_item['propertyType'],
                'transactions': property_item['transactions'],
                'location': property_item['location'],
                'url': property_item['detailUrl']
            }

        current_page = int(response.url.split('=')[-1])

        next_page = current_page + 1

        next_page_url = f"https://www.rightmove.co.uk/house-prices/southwark-85215.html?soldIn=1&page={next_page}"

        yield response.follow(next_page_url,callback= self.parse)



   