import scrapy

from scrapy import FormRequest
import json

class AGENT(scrapy.Spider):
    name= 'agent'
    loadedAgents = None
    stop = 0

    def start_requests(self):

        url = 'https://www.fir.com/agents'

        yield scrapy.Request(url,callback= self.run)

    def run(self,response):
        
        agents = response.css("div.card-cont")

        for agent in agents:

            yield{
                "Name": agent.css("div.name a::text").get(),
                "Phone": agent.css("div.info a::text").getall()[0],
                "Email": agent.css("div.info a::text").getall()[1],
            }
        

        string_format = response.xpath("//input[@id='loadedAgents']").attrib['value']

        self.loadedAgents = json.loads(string_format)


        ajax_url = 'https://www.fir.com/wp-admin/admin-ajax.php'

        while self.stop == 0:

            data = {
                'action': 'get_agents',
                'loadedAgents': self.loadedAgents,
                'office': 'office',
            }

            yield FormRequest(ajax_url,formdata=data,callback=self.ajax_parser)


    def ajax_parser(self,response):

        data = json.loads(response.text)
        if len(data) == 0:
            self.stop = 1
            return None
            
        for d in data:
            yield{

                "Name": d['title'],
                "Phone": d['mobile'],
                "Email": d['email'],
            }

            self.loadedAgents.append(d['post_id'])

