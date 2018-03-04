# -*- coding: utf-8 -*-
import scrapy
import re
import os


class LocationsspiderSpider(scrapy.Spider):
    name = 'locationsSpider'
    allowed_domains = ['live24.gr']
    start_urls = ['http://live24.gr/', 'http://live24.gr/list.jsp']


    def parse(self, response):
        locationsUls = response.xpath('//ul[@class="locations"]')

        for loc in locationsUls:
            locEnt = loc.xpath('.//li[@class="title"]')
            location = locEnt.xpath('./a/text()')[1].extract()

            areasEnts = loc.xpath('.//li[@class="area"]')

            scrapped_info ={
                'location' : location,
                'locUrl' : locEnt.css('a::attr(href)').extract_first(),
                'areas' : list(filter(bool, map(lambda s:re.sub("[\n\t\r]", "", s) , areasEnts.xpath('.//a/text()').extract()))),
                'areasUrls' : areasEnts.css('a::attr(href)').extract()
            }

            yield scrapped_info
