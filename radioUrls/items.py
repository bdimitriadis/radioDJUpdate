# -*- coding: utf-8 -*-

# Define here the models for your scraped items
#
# See documentation in:
# http://doc.scrapy.org/en/latest/topics/items.html

import scrapy


class StationItem(scrapy.Item):
    # define the fields for your item here like:
    # name = scrapy.Field()
    name = scrapy.Field()
    stationUrl = scrapy.Field()
    area = scrapy.Field()
    genre = scrapy.Field()
    image_urls = scrapy.Field()
    images = scrapy.Field()



# class GenreItem(scrapy.Item):
#     # define the fields for your item here like:
#     # name = scrapy.Field()
#     name = scrapy.Field()
#     station_url = scrapy.Field()
#     genre = scrapy.Field()
#     image_urls = scrapy.Field()
#     images = scrapy.Field()
