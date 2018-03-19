# -*- coding: utf-8 -*-
import scrapy
import json
import itertools
import os
import re
from radioUrls.items import StationItem


class AreaspiderSpider(scrapy.Spider):
    name = 'areaspider'
    allowed_domains = ['live24.gr']
    baseUrl = 'http://live24.gr'
    areasJoined=[]
    jsonPath = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))),'jsons')
    fname = os.path.join(jsonPath,'locationUrls.json')
    if os.path.isfile(fname):
        with open(fname) as fp:
            jsonLd = json.load(fp)
            areasJoined = itertools.chain.from_iterable(map(lambda el: el['areasUrls'], jsonLd))
    start_urls = list(map(lambda elm: "http://live24.gr%s"%elm, areasJoined))


    def parse(self, response):
        lis = response.xpath("//li[contains(@class, 'stationblock')]")
        namesUrls = lis.xpath(".//a[contains(@class, 'name')]")
        names = namesUrls.xpath(".//text()").extract()
        urls = namesUrls.xpath(".//@href").extract()
        liveUrls = lis.xpath(".//a[contains(@class, 'button') and contains(text(), 'Live')]/@href").extract()
        genres = lis.xpath(".//p[contains(@class, 'genre')]/text()").extract()
        infoUrls = lis.xpath(".//a[contains(@class, 'button') and contains(text(), 'Radio info')]/@href").extract()
        
        
        for i in range(len(infoUrls)):
            item = StationItem(
                name = names[i].strip(),
                stationUrl = liveUrls[i],
                genre = genres[i])
            yield scrapy.Request("%s%s"%(self.baseUrl, infoUrls[i]), callback=self.parse_station_info, meta={'item': item})
            


    def parse_station_info(self, response):
        item = response.meta['item']
        item['area'] = response.xpath(".//p[contains(text(),'Περιοχή:')]/a/text()").extract_first()
        item['image_urls'] = [response.xpath("//div[@id='stationInfo']/p[@class='logo']/img/@src").extract_first()]
        yield scrapy.Request("%s%s"%(self.baseUrl, item['stationUrl']), callback=self.parse_station_stream, meta={'item': item})

    def parse_station_stream(self, response):
        item = response.meta['item']
        tmpStr = response.xpath(".//script[contains(text(),'streamsrc:')]/text()").extract_first()
        item['stationUrl'] = re.findall("streamsrc: .*?,",tmpStr)
        item['stationUrl'] = item['stationUrl'][0].replace("',","").replace("streamsrc: '","") if item['stationUrl'] else ""
        yield item
