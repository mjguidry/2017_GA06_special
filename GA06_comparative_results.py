# -*- coding: utf-8 -*-
"""
Created on Mon May 29 09:14:01 2017

@author: mike
"""
import xml.etree.ElementTree as ET
import csv
import re

primary_XML_files=['./XML/2017_Cobb_detail.xml',
           './XML/2017_DeKalb_detail.xml',
           './XML/2017_Fulton_detail.xml']

Rs=['KREMER',
'GRAY',
'LEVELL',
'MOODY',
'ABROMS',
'HILL',
'HANDEL',
'GRAWERT',
'WILSON',
'BHUIYAN',
'LLOP']

precinct_dict=dict()

for f in primary_XML_files:
    tree=ET.parse(f)
    county=tree.find('Region').text
    date=tree.find('ElectionDate')
    year=int(date.text[-4:])
    contest=[contest for contest in tree.findall('Contest') if contest.attrib['text']=='U.S. Representative, District 6'][0]
    choices=contest.findall('Choice')
    for choice in choices:
        vts=choice.findall('VoteType')
        cand=choice.attrib['text']
        for vt in vts:
            precincts=vt.getchildren()
            for precinct in precincts:
                votes=int(precinct.attrib['votes'])
                name=precinct.attrib['name']
                name=re.sub('\s+$','',name)
                if(name not in precinct_dict):
                    precinct_dict[name]=dict()
                if(cand not in precinct_dict[name]):
                    precinct_dict[name][cand]=0
                precinct_dict[name][cand]+=votes

with open('./data_files/2017_GA06_primary_margins.csv','wb') as csvfile:
    writer=csv.writer(csvfile)    
    for precinct in precinct_dict:
        sum_votes=sum([precinct_dict[precinct][cand] for cand in precinct_dict[precinct]])
        ossoff_votes=sum([precinct_dict[precinct][cand] for cand in precinct_dict[precinct] if 'OSSOFF' in cand])
        R_votes=sum([precinct_dict[precinct][cand] for cand in precinct_dict[precinct] if any([R in cand for R in Rs])])
        ossoff_margin=float(ossoff_votes-R_votes)/sum_votes
        writer.writerow([precinct,ossoff_margin])

old_precinct_dict=precinct_dict.copy()
        
pres_XML_files=['./XML/2016_Cobb_detail.xml',
           './XML/2016_DeKalb_detail.xml',
           './XML/2016_Fulton_detail.xml']

precinct_dict=dict()

for f in pres_XML_files:
    tree=ET.parse(f)
    county=tree.find('Region').text
    date=tree.find('ElectionDate')
    year=int(date.text[-4:])
    contest=[contest for contest in tree.findall('Contest') if contest.attrib['text']=='President of the United States'][0]
    choices=contest.findall('Choice')
    for choice in choices:
        vts=choice.findall('VoteType')
        cand=choice.attrib['text']
        for vt in vts:
            precincts=vt.getchildren()
            for precinct in precincts:
                votes=int(precinct.attrib['votes'])
                name=precinct.attrib['name']
                name=re.sub('\s+$','',name)
                name=re.sub('Rocky Mountain','Rocky Mount',name)
                name=re.sub('Lasssiter','Lassiter',name)
                name=re.sub('Shallowford Fall ','Shallowford Falls ',name)
                name=re.sub('Wileo','Willeo',name)
                name=re.sub('PLEASANTDALE ELEM','PLEASANTDALE ROAD',name)
                if(name not in precinct_dict):
                    precinct_dict[name]=dict()
                if(cand not in precinct_dict[name]):
                    precinct_dict[name][cand]=0
                precinct_dict[name][cand]+=votes

with open('./data_files/2016_GA06_pres_margins.csv','wb') as csvfile:
    writer=csv.writer(csvfile)    
    for precinct in precinct_dict:
        sum_votes=sum([precinct_dict[precinct][cand] for cand in precinct_dict[precinct]])
        clinton_votes=sum([precinct_dict[precinct][cand] for cand in precinct_dict[precinct] if 'CLINTON' in cand])
        trump_votes=sum([precinct_dict[precinct][cand] for cand in precinct_dict[precinct] if 'TRUMP' in cand])
        clinton_margin=float(clinton_votes-trump_votes)/sum_votes
        writer.writerow([precinct,clinton_margin])