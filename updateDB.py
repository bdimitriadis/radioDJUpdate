#!/usr/bin/env python3
# -*- coding: utf-8 -*-

from collections import OrderedDict
from subprocess import call
from itertools import chain
import os
import json

if __name__ == '__main__':
    jsonPath = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'radioUrls', 'jsons')
    spidies = ['locationsSpider', 'genrespider', 'areaspider']
    jsonFiles = ['locationUrls.json','genres.json' , 'areas.json']
    jsonOuts = ['locationUrls.json','stations.json']
    managePath = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), 'manage.py')
    
    
    for i in range(len(spidies)):
        try:
            os.remove(os.path.join(jsonPath, jsonFiles[i]))
        except OSError:
            pass
        #free
        call("scrapy crawl {0} -o {1} -t json".format(spidies[i], os.path.join(jsonPath, jsonFiles[i])).split())

    models = ["Location", "Station"]
    pkIndxOffset = 0

    areaObjs = []

    genresDict = {}
    genreObjs = []
    areasPkDict = {}
    lstOfEnts = []
    
    for jindx, jsonFile in enumerate(jsonFiles):
        with open(os.path.join(jsonPath, jsonFile), 'r') as fp:
            lstOfEnts += json.load(fp)
            
        if jsonFile=='genres.json':
            continue

        tmpList = []

        for item in lstOfEnts:
            if item not in tmpList:
                tmpList.append(item)
        lstOfEnts = tmpList
          
        [el.pop("image_urls", None) for el in lstOfEnts]
        # Create area table entity
        if jsonFile == 'locationUrls.json':
            areasDict = OrderedDict(list(chain.from_iterable(map(lambda ent: zip(ent['areas'], zip(ent['areasUrls'], [lstOfEnts.index(list(filter(lambda elem: elem['location']==ent['location'], lstOfEnts))[0])+1]*len(ent['areasUrls']))), lstOfEnts))))
            areaObjs = [{"model": "radioApp.Area", "pk": pkIndxOffset+indx+1, "fields": {'area': k,'areaUrl': areasDict[k][0], 'loc':areasDict[k][1]}} for indx, k in enumerate(areasDict)]
            areasPkDict = dict(zip(areasDict.keys(), range(1, len(areasDict)+1)))
        
            [el.pop("locUrl", None) for el in lstOfEnts]
            [el.pop("images", None) for el in lstOfEnts]
            [el.pop("areas", None) for el in lstOfEnts]
            [el.pop("areasUrls", None) for el in lstOfEnts]
                
        else:
            for elm in lstOfEnts:
                if elm['genre'] not in genresDict:
                    genresDict[elm['genre']] = len(genresDict)+1
                
                elm['genre']=genresDict[elm['genre']]
                elm['area']=areasPkDict[elm['area']]

        
        
        lstOfEnts = [{"model": "radioApp.%s"%(models[(jindx+1)//len(models)]), "pk": pkIndxOffset+indx+1, "fields": elm} for indx,elm in enumerate(lstOfEnts)]  ### change area with id
        pkIndxOffset = jindx*len(lstOfEnts)
        with open(os.path.join(jsonPath, jsonOuts[jindx//2]), 'w') as fp:
                json.dump(lstOfEnts, fp)
        lstOfEnts = []

    genreObjs = [{"model": "radioApp.Genre", "pk": indx, "fields": {'genre': k}} for k,indx in genresDict.items()]

    
    files2objs = {'areaTable.json': areaObjs, 'genreTable.json': genreObjs}
    
    for f in files2objs:
        try:
            os.remove(os.path.join(jsonPath, f))
        except OSError:
            pass
         
        with open(os.path.join(jsonPath, f), 'w') as fp:
                json.dump(files2objs[f], fp)
                
      
    for f in [jsonOuts[0]]+list(files2objs)+[jsonOuts[1]]:
        call("python3 {0} loaddata {1}".format(managePath, os.path.join(jsonPath, f)).split())
         
