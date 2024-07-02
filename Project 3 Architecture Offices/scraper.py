import scrapy
from scrapy.http import FormRequest
import re

class MySpider(scrapy.Spider):
    name = "myspider"

    def start_requests(self):
        url = "https://www.landschaftsarchitektur-heute.de/de/index.php?option=com_laheute&view=bueros&Itemid=101"
        
        headers = {
            'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.7',
            'Accept-Language': 'en-US,en;q=0.9',
            'Connection': 'keep-alive',
            'Content-Type': 'application/x-www-form-urlencoded',
            'Origin': 'https://www.landschaftsarchitektur-heute.de',
            'Referer': 'https://www.landschaftsarchitektur-heute.de/de/bueros',
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/125.0.0.0 Safari/537.36',
        }

        for page in range(1, 41):
            formdata = {
                'page': str(page),
                'distance': '10'
            }
            yield FormRequest(
                url=url,
                formdata=formdata,
                headers=headers,
                callback=self.parse
            )
            break

    def parse(self, response):

        hrefs = response.css("div.col-lg-3 a::attr(href)").getall() 

        for href in hrefs:
            code = href.split('=')[1]
            full_url = f'https://www.landschaftsarchitektur-heute.de/de/buero/buero?contentID={code}'

            #yield{'url':full_url}
            
            yield scrapy.Request(full_url, callback=self.parse_detail)
            break

    def parse_detail(self, response):

        target_elem = response.css('div.col-lg-4.col-md-12.bueroData')

        name = target_elem.css('h3::text').get().strip()

        
        contact_persons_text = target_elem.css('p.small.ugp8::text').get()
        contact_persons = [person.strip() for person in contact_persons_text.split('; ')] if contact_persons_text else []


        address_parts = target_elem.css('p.small.ugp16::text').extract()
        
        street_and_number = address_parts[0].strip().replace(' ',' ')
        post_code_and_city = address_parts[1].strip()

        parts = post_code_and_city.split('\xa0')
        post_code = parts[0].strip()
        city = parts[1].strip()


        telephone = re.sub(r'<[^>]*>', '', target_elem.css('p')[-2].get()).replace('\t','').replace('\n','').replace('\xa0','').replace('Tel.','').split('Fax')[0].strip()

        email = target_elem.css('p.small.ugp16 a[href^="mailto:"]::text').get()
        website = target_elem.css('p.small.ugp16 a[href^="http"]::text').get()

        data = {
            'url': response.url,
            'name': name,
            'street_and_number': street_and_number,
            'post_code': post_code,
            'city': city,
            'telephone': telephone,
            'email': email,
            'website': website
        }

        for i, person in enumerate(contact_persons, start=1):

            data[f'contact_person_{i}'] = person

        yield data

#https://www.landschaftsarchitektur-heute.de/de/buero/buero?contentID=501287
#https://www.landschaftsarchitektur-heute.de/de/buero/buero?contentID=500564
#https://www.landschaftsarchitektur-heute.de/de/buero/buero?contentID=501316