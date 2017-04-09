# -*- coding: utf-8 -*-
"""
Created on Sat Apr  8 13:33:51 2017

@author: mike
"""

import xml.etree.ElementTree as ET
import csv, re
from PIL import Image,ImageColor, ImageDraw


xml_files=['./XML/2016_Cobb_detail.xml',
           './XML/2016_DeKalb_detail.xml',
           './XML/2016_Fulton_detail.xml',
           ]

precinct_dict=dict()

for f in xml_files:
    tree=ET.parse(f)
    county=tree.find('Region').text
    contest=[contest for contest in tree.findall('Contest') if contest.attrib['text']=='U.S. Representative, District 6'][0]
    choices=contest.findall('Choice')
    for choice in choices:
        choice_name=choice.attrib['text']
        vts=choice.findall('VoteType')
        for vt in vts:
            precincts=vt.getchildren()
            for precinct in precincts:
                votes=int(precinct.attrib['votes'])
                name=precinct.attrib['name']
                name = re.sub(r'\s+$', '', name)
                if(name not in precinct_dict):
                    precinct_dict[name]=dict()
                if(choice_name not in precinct_dict[name]):
                    precinct_dict[name][choice_name]=0
                precinct_dict[name][choice_name]=precinct_dict[name][choice_name]+votes

precincts=dict()
maxx=0
maxy=0
with open('GA06.csv','rb') as csvfile:
    reader=csv.reader(csvfile)
    for row in reader:
        s=row[1]
        s=re.sub('M ','',s)
        s=re.sub('L ','',s)
        s=re.sub(' z','',s)
        nums=[float(x) for x in s.split(' ')]
        xs=nums[0::2]
        ys=nums[1::2]
        maxx=max(maxx,max(xs))
        maxy=max(maxy,max(ys))
        precincts[row[0]]=int(nums[0]+0.5),int(nums[1]+0.5)

im = Image.open("GA06_BW.png")
im2=im.copy()
mode="RGB"
img=im2.convert(mode)
red=ImageColor.getcolor('red',mode)
blue=ImageColor.getcolor('blue',mode)
for precinct in precincts:
    gop_key=[key for key in precinct_dict[precinct] if 'PRICE' in key][0]
    dem_key=[key for key in precinct_dict[precinct] if 'STOOKSBURY' in key][0]
    if(precinct_dict[precinct][gop_key]>precinct_dict[precinct][dem_key]):
        ImageDraw.floodfill(img,(precincts[precinct][0],precincts[precinct][1]),red)
    else:
        ImageDraw.floodfill(img,(precincts[precinct][0],precincts[precinct][1]),blue)

img.show()
img.save("GA06_2016_house.png")
