# -*- coding: utf-8 -*-
"""
Created on Wed Apr 12 21:24:05 2017

@author: mike
"""
import csv, re
import pandas as pd
from PIL import Image,ImageColor, ImageDraw

f='Sample GA06.csv'

#Candidate profiles
candidates={}
candidates['OSSOFF']={'color':'0072b2','party':'D'}
candidates['EDWARDS']={'color':'','party':'D'}
candidates['QUIGG']={'color':'','party':'D'}
candidates['KEATLEY']={'color':'','party':'D'}
candidates['SLOTIN']={'color':'','party':'D'}

candidates['KREMER']={'color':'','party':'R'}
candidates['GRAY']={'color':'e69f00','party':'R'}
candidates['LEVELL']={'color':'','party':'R'}
candidates['MOODY']={'color':'f0e442','party':'R'}
candidates['ABROMS']={'color':'','party':'R'}
candidates['HILL']={'color':'009e73','party':'R'}
candidates['HANDEL']={'color':'cc79a7','party':'R'}
candidates['GRAWERT']={'color':'','party':'R'}
candidates['WILSON']={'color':'','party':'R'}
candidates['BHUIYAN']={'color':'','party':'R'}
candidates['LLOP']={'color':'','party':'R'}

candidates['HERNANDEZ']={'color':'','party':'I'}
candidates['POLLARD']={'color':'','party':'I'}

for candidate in candidates:
    if(candidates[candidate]['color']==''):
        candidates[candidate]['color']='gray'

# Grab coordinates for each precinct
precinct_xy=dict()
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
        precinct_xy[row[0]]=int(nums[0]+0.5),int(nums[1]+0.5)

votes_dict=dict()
votes_df=pd.read_csv(f)
for index,row in votes_df.iterrows():
    cname=row['CandidateName']
    candidate=[c for c in candidates if c in cname.upper()][0]
    precinct=row['PrecinctName']
    votes=row['Votes']
    if(precinct not in votes_dict):
        votes_dict[precinct]=dict()
    votes_dict[precinct][candidate]=votes

im = Image.open("GA06_BW.png")

img_all=im.copy() # Top individual vote getters
img_rvb=im.copy() # Total R vs Total D
img_gop=im.copy() # Top R vote getter

mode="RGB"
#img=img.convert(mode)
red=ImageColor.getcolor('red',mode)
blue=ImageColor.getcolor('blue',mode)
gray=ImageColor.getcolor('gray',mode)
for precinct in votes_dict:
    Ds=sum([votes_dict[precinct][candidate] for candidate in votes_dict[precinct] if candidates[candidate]['party']=='D'])
    Rs=sum([votes_dict[precinct][candidate] for candidate in votes_dict[precinct] if candidates[candidate]['party']=='R'])
    best=[candidate for candidate in votes_dict[precinct] if votes_dict[precinct][candidate]==max(votes_dict[precinct].values())]
    if(Rs>Ds):
        ImageDraw.floodfill(img_rvb,(precinct_xy[precinct][0],precinct_xy[precinct][1]),red)
    elif(Ds>Rs):
        ImageDraw.floodfill(img_rvb,(precinct_xy[precinct][0],precinct_xy[precinct][1]),blue)
    else:
        ImageDraw.floodfill(img_rvb,(precinct_xy[precinct][0],precinct_xy[precinct][1]),gray)
    if(len(best)==1):
        candidate=best[0]
        color=ImageColor.getcolor(candidates[candidate]['color'],mode)
        ImageDraw.floodfill(img_all,(precinct_xy[precinct][0],precinct_xy[precinct][1]),color)
    else:
        ImageDraw.floodfill(img_all,(precinct_xy[precinct][0],precinct_xy[precinct][1]),gray)

