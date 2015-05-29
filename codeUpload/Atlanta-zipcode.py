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
zipcode_ext = re.compile(r'^[0-9]{5}-[0-9]{4}$')


def process(file_in, zipstat,wrongzip):
    for event, element in etree.iterparse(file_in, events=("start",)):
        if element.tag == "node" or element.tag == "way":
            for tag in element.iter("tag"):
                if tag.attrib['k']=="addr:postcode":
                    if zipcode.search(tag.attrib['v']):
                        zipstat["zipcode"]+=1
                    else:
                        zipstat["other"]+=1
                        wrongzip[tag.getparent().attrib['id']]=\
                        tag.attrib['v']
        
        
    return zipstat,wrongzip
    
#Enforce consistency by choosing a single format for postal codes. 
#Something like 10027-4050 could be stored as 10027 and 4050 in a new 
#field 'postal_code_extension'.
def process_extension(file_in):
    file_out = "{0}-zipcode.xml".format(file_in)
    tree=etree.parse(file_in)
    elements=tree.iterfind('//tag[@k="addr:postcode"]')
    for el in elements:
        if zipcode_ext.search(el.attrib['v']):
            el.set('postal_code_extension',el.attrib['v'][6:])
            el.set('v',el.attrib['v'][:5])
            
    tree.write(file_out)
    return None

if __name__ == "__main__":
    zipstat = {"zipcode": 0, "other": 0}
    wrongzip={}
    zipstat,wrongzip = process('atlanta.osm',zipstat,wrongzip)
    pprint.pprint(zipstat)
    pprint.pprint(wrongzip)
    process_extension("atlanta.osm")