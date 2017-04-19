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
    contest=[contest for contest in tree.findall('Contest') if contest.attrib['text']=='President of the United States'][0]
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
                name = re.sub('Wileo','Willeo',name)
                name = re.sub('Lasssiter','Lassiter',name)
                name = re.sub('Fall ','Falls ',name)
                name = re.sub('Rocky Mountain','Rocky Mount',name)
                name = re.sub('PLEASANTDALE ELEM','PLEASANTDALE ROAD',name)
                if(name not in precinct_dict):
                    precinct_dict[name]=dict()
                if(choice_name not in precinct_dict[name]):
                    precinct_dict[name][choice_name]=0
                precinct_dict[name][choice_name]=precinct_dict[name][choice_name]+votes

precinct_xy=dict()
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
        precinct_xy[row[0]]=int(nums[0]+0.5),int(nums[1]+0.5)

im = Image.open("GA06_BW.png")
im2=im.copy()
mode="RGB"
img=im2.convert(mode)
red=ImageColor.getcolor('red',mode)
blue=ImageColor.getcolor('blue',mode)
gray=ImageColor.getcolor('gray',mode)
for precinct in precinct_dict:
    if(precinct in precinct_xy):
        R=precinct_dict[precinct]['DONALD J. TRUMP']
        D=precinct_dict[precinct]['HILLARY CLINTON']
        total=sum([precinct_dict[precinct][cand] for cand in precinct_dict[precinct]])
        if(R>D):
            R_margin=float(R-D)/total
            if(R_margin>0.2):
                color=ImageColor.getcolor('#990000',mode)
            elif(R_margin>0.1):
                color=ImageColor.getcolor('#dd0000',mode)
            elif(R_margin>0.05):
                color=ImageColor.getcolor('#ff0000',mode)
            else:
                color=ImageColor.getcolor('#ff9999',mode)            
            ImageDraw.floodfill(img,(precinct_xy[precinct][0],precinct_xy[precinct][1]),color)
        elif(D>R):
            D_margin=float(D-R)/total
            if(D_margin>0.2):
                color=ImageColor.getcolor('#000099',mode)
            elif(D_margin>0.1):
                color=ImageColor.getcolor('#0000dd',mode)
            elif(D_margin>0.05):
                color=ImageColor.getcolor('#0000ff',mode)
            else:
                color=ImageColor.getcolor('#9999ff',mode)            
            ImageDraw.floodfill(img,(precinct_xy[precinct][0],precinct_xy[precinct][1]),color)
        elif(D>0 and R>0):
            ImageDraw.floodfill(img,(precinct_xy[precinct][0],precinct_xy[precinct][1]),gray)

img.show()
img.save("GA06_2016_pres.png")
