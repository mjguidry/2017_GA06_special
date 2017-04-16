# -*- coding: utf-8 -*-
"""
Created on Wed Apr 12 21:24:05 2017

@author: mike
"""
import csv, re
from PIL import Image,ImageColor, ImageDraw
from numpy.random import randint
r_vs_d_png_test="test_R_vs_D.png"
all_cands_png_test="test_all_cands.png"
all_R_cands_png_test="test_R_cands.png"
ossoff_50_png_test="test_ossoff_50.png"


#Candidate profiles
candidates={}
candidates['OSSOFF']    ={'color':'#0072b2','party':'D'}
candidates['EDWARDS']   ={'color':'','party':'D'}
candidates['QUIGG']     ={'color':'','party':'D'}
candidates['KEATLEY']   ={'color':'','party':'D'}
candidates['SLOTIN']    ={'color':'','party':'D'}

candidates['KREMER']    ={'color':'','party':'R'}
candidates['GRAY']      ={'color':'#e69f00','party':'R'}
candidates['LEVELL']    ={'color':'','party':'R'}
candidates['MOODY']     ={'color':'#f0e442','party':'R'}
candidates['ABROMS']    ={'color':'','party':'R'}
candidates['HILL']      ={'color':'#009e73','party':'R'}
candidates['HANDEL']    ={'color':'#cc79a7','party':'R'}
candidates['GRAWERT']   ={'color':'','party':'R'}
candidates['WILSON']    ={'color':'','party':'R'}
candidates['BHUIYAN']   ={'color':'','party':'R'}
candidates['LLOP']      ={'color':'','party':'R'}

candidates['HERNANDEZ'] ={'color':'','party':'I'}
candidates['POLLARD']   ={'color':'','party':'I'}

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

im = Image.open("GA06_BW.png")

img_all=im.copy() # Top individual vote getters
img_rvd=im.copy() # Total R vs Total D
img_gop=im.copy() # Top R vote getter
img_ossoff=im.copy() # Ossoff at 50%

mode="RGB"
#img=img.convert(mode)
red=ImageColor.getcolor('red',mode)
blue=ImageColor.getcolor('blue',mode)
gray=ImageColor.getcolor('gray',mode)
not_ossoff=ImageColor.getcolor('#ff8d4d',mode)
for precinct in precinct_xy:
        
    # Color R vs D map, check for ties
    x=randint(0,2)
    if(x==1):
        ImageDraw.floodfill(img_rvd,(precinct_xy[precinct][0],precinct_xy[precinct][1]),red)
    else:
        ImageDraw.floodfill(img_rvd,(precinct_xy[precinct][0],precinct_xy[precinct][1]),blue)

    # Color all candidates map, check if only one top votegetter, otherwise a tie
    x=randint(0,5)
    cands=['OSSOFF','GRAY','MOODY','HILL','HANDEL']
    candidate=cands[x]
    color=ImageColor.getcolor(candidates[candidate]['color'],mode)
    ImageDraw.floodfill(img_all,(precinct_xy[precinct][0],precinct_xy[precinct][1]),color)


    # Color all R candidates map, check if only one top R votegetter, otherwise a tie
    x=randint(0,4)
    cands=['GRAY','MOODY','HILL','HANDEL']
    candidate=cands[x]
    color=ImageColor.getcolor(candidates[candidate]['color'],mode)
    ImageDraw.floodfill(img_gop,(precinct_xy[precinct][0],precinct_xy[precinct][1]),color)


    # Color map indicating if Ossoff has reached 50%
    x=randint(0,2)
    if(x==1):
        color=ImageColor.getcolor(candidates['OSSOFF']['color'],mode)
        ImageDraw.floodfill(img_ossoff,(precinct_xy[precinct][0],precinct_xy[precinct][1]),color)
    else:
        ImageDraw.floodfill(img_ossoff,(precinct_xy[precinct][0],precinct_xy[precinct][1]),not_ossoff)

img_rvd.save(r_vs_d_png_test)
img_all.save(all_cands_png_test)
img_gop.save(all_R_cands_png_test)
img_ossoff.save(ossoff_50_png_test)

    
