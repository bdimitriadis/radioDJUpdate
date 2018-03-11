# -*- coding: utf-8 -*-
import scrapy
import os
from radioUrls.items import StationItem


class GenrespiderSpider(scrapy.Spider):
    name = "genrespider"
    allowed_domains = ['live24.gr']
    start_urls = ['http://live24.gr/', 'http://live24.gr/list.jsp']


    def parse(self, response):
        locEnts = response.xpath('//ul[@class="locations"]').xpath('.//li[@class="title"]')

        webRadiosEnt = list(filter(lambda loc: loc.xpath('./a/text()')[1].extract()=="Web Radios", locEnts))
        webRadioLink = "http://live24.gr/radio.jsp?aid=84"
        for loc in locEnts:
            if loc.xpath('./a/text()')[1].extract()=="Web Radios":
                webRadioLink = self.start_urls[0]+loc.css('a::attr(href)').extract_first()
        yield scrapy.Request(webRadioLink, callback=self.parse_webradio_link)

    def parse_webradio_link(self, response):
        lis = response.xpath("//li[contains(@class, 'stationblock')]")
        namesUrls = lis.xpath(".//a[contains(@class, 'name')]")
        names = namesUrls.xpath(".//text()").extract()
        urls = namesUrls.xpath(".//@href").extract()
        liveUrls = lis.xpath(".//a[contains(@class, 'button') and contains(text(), 'Live')]/@href").extract()
        genres = lis.xpath(".//p[contains(@class, 'genre')]/text()").extract()
        infoUrls = lis.xpath(".//a[contains(@class, 'button') and contains(text(), 'Radio info')]/@href").extract()

        for i in range(len(infoUrls)):
#             if not genres[i].strip():
#                 genres[i]='N/A'
            item = StationItem(name = names[i].strip(),
                stationUrl = liveUrls[i],
                genre = genres[i])
            
            
            yield scrapy.Request("%s%s"%(self.start_urls[0][:-1], infoUrls[i]), callback=self.parse_station_info, meta={'item': item})




    def parse_station_info(self, response):
        item = response.meta['item']
        item['area'] = response.xpath(".//p[contains(text(),'Περιοχή:')]/a/text()").extract_first()
        item['image_urls'] = [response.xpath("//div[@id='stationInfo']/p[@class='logo']/img/@src").extract_first()]
        yield item
