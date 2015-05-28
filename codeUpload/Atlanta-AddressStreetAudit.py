"""
The tasks in this program have two steps:

- audit the OSMFILE and process the whole file to generate json file that contains all the street 
  names (defaultdict(set)) that are not expected from the expected dictionary. Feel free to edit the expected dictionary 
  to include the additional ones based on on the particular area you are auditing.
- process function is used to actually align the non-standard/unexpected street names with the standard ones from mapping
  dictionary. Feel free to change the variable 'mapping' to reflect the changes needed to fix the non-standard/unexpected 
  street types to the appropriate ones in the expected list.
    
"""
import xml.etree.cElementTree as ET
from collections import defaultdict
from lxml import etree
import re
import pprint
import codecs
import json


OSMFILE = "atlanta.osm"
street_type_re = re.compile(r'\b\S+\.?$', re.IGNORECASE)

#UPDATE THIS DICTIONARY TO SPEED UP THE AUDITING PROCESS
expected = ["Street", "Avenue", "Boulevard", "Drive", "Court", "Place", "Square", "Lane", "Road", 
            "Trail", "Parkway", "Commons"]

# UPDATE THIS VARIABLE FOR  ALL REPLACEMENTS YOU WNAT TO MAKE
mapping = { 
            "St.": "Street",
            "Ave": "Avenue",
            "Rd.":"Road"
            }


def audit_street_type(street_types, street_name):
    m = street_type_re.search(street_name)
    if m:
        street_type = m.group()
        if street_type not in expected:
            street_types[street_type].add(street_name)

def is_street_name(elem):
    return (elem.attrib['k'] == "addr:street")

def audit(osmfile):
    osm_file = open(osmfile, "r")
    street_types = defaultdict(set)
    for event, elem in ET.iterparse(osm_file, events=("start",)):

        if elem.tag == "node" or elem.tag == "way":
            for tag in elem.iter("tag"):
                if is_street_name(tag):
                    audit_street_type(street_types, tag.attrib['v'])

    return street_types

#string replacement function
def update_name(name, mapping):
    c=name
    for k in mapping.keys():
        if name.find(k)>=0:
            c=str.replace(name,k,mapping[k])
    return c


#step 1: process the whole file to generate json file that contains all the street names(defaultdict(set))
#that are not expected
def process_map(file_in, pretty = False):
    file_out = "{0}.json".format(file_in)
    data = []
    street_types = defaultdict(set)
    with codecs.open(file_out, "w") as fo:
        for event, element in ET.iterparse(file_in, events=("start",)):
            if element.tag == "node" or element.tag == "way":
              for tag in element.iter("tag"):
                    if is_street_name(tag):
                        audit_street_type(street_types, tag.attrib['v'])
        for key in street_types.keys():
            temp={}
            temp[key]=list(street_types[key])                     
            fo.write(json.dumps(temp) + "\n")
    return data
    

#step 2: update the whole file with the mapping dictionary for the values of addr:street
def process(file_in, mapping):
    file_out = "{0}-streetname.xml".format(file_in)
    tree=etree.parse(file_in)
    elements=tree.iterfind('//tag[@k="addr:street"]')
    for el in elements:
        el.set('v',update_name(el.get('v'),mapping))
    tree.write(file_out)
    return None

def test():
    st_types = audit(OSMFILE)
    data = process_map(OSMFILE, False)
    pprint.pprint(dict(st_types))
    process(OSMFILE,mapping)

if __name__ == '__main__':
    test()