#!/usr/bin/env python
# -*- coding: utf-8 -*-
import pprint
import re
from lxml import etree
from io import StringIO,BytesIO
"""
The task is to explore the data a bit more.
Before I process the data and add it into MongoDB, I check the "addr:postcode" value for each 
"<tag>" under parent node "node' and "way" and see if they are valid postcodes.

The regular expression to check for correct pattern for postcode is used.
Dictionary for count of correct and incorrect postcodes is retrieved.
Dictionary for wrong postcodes with 'id' info as key is collected for further cleaning
"""

zipcode = re.compile(r'^[0-9]{5}(?:-[0-9]{4})?$')


def process(file_in, zipstat,wrongzip):
    for event, element in etree.iterparse(file_in, events=("start",)):
        if element.tag == "node" or element.tag == "way":
            for tag in element.iter("tag"):
                if tag.attrib['k']=="addr:postcode":
                    if zipcode.search(tag.attrib['v']):
                        zipstat["zipcode"]+=1
                    else:
                        zipstat["other"]+=1
                        wrongzip[tag.getparent().attrib['id']]=tag.attrib['v']
        
        
    return zipstat,wrongzip

if __name__ == "__main__":
    zipstat = {"zipcode": 0, "other": 0}
    wrongzip={}
    zipstat,wrongzip = process('atlanta.osm',zipstat,wrongzip)
    pprint.pprint(zipstat)
    pprint.pprint(wrongzip)