# -*- coding: utf-8 -*-
"""
Created on Wed Apr 12 21:24:05 2017

@author: mike
"""

import datetime
import csv, re
import openpyxl
from PIL import Image,ImageColor, ImageDraw, ImageFont
import io, os
import httplib2
from apiclient import discovery
import oauth2client
from oauth2client import client
from oauth2client import tools
from apiclient import errors
from apiclient.http import MediaFileUpload,MediaIoBaseDownload
import argparse
flags = argparse.ArgumentParser(parents=[tools.argparser]).parse_args()

now=datetime.datetime.now()
polls_close=datetime.datetime(year=2017,month=6,day=20,hour=16)
if(now<polls_close):
    sample_only=True
else:
    sample_only=False

SCOPES = ['https://www.googleapis.com/auth/drive',
          'https://www.googleapis.com/auth/spreadsheets']
if(os.name=='posix'):
    CLIENT_SECRET_FILE = '/home/mike/Downloads/client_id.json'
elif(os.name=='nt'):
    CLIENT_SECRET_FILE = r'C:\Users\MGUIDRY\workspace\dd\client_id.json'
APPLICATION_NAME = 'Map Drawing Script'
SCRIPT_ID = 'MUVhXLGI6BP6BWWA2rZWczzimZkoIcWwo'

def get_credentials():
    """Gets valid user credentials from storage.

    If nothing has been stored, or if the stored credentials are invalid,
    the OAuth2 flow is completed to obtain the new credentials.

    Returns:
        Credentials, the obtained credential.
    """
    home_dir = os.path.expanduser('~')
    credential_dir = os.path.join(home_dir, '.credentials')
    if not os.path.exists(credential_dir):
        os.makedirs(credential_dir)
    credential_path = os.path.join(credential_dir,
                                   'script-draw-map.json')

    store = oauth2client.file.Storage(credential_path)
    credentials = store.get()
    if not credentials or credentials.invalid:
        flow = client.flow_from_clientsecrets(CLIENT_SECRET_FILE, SCOPES)
        flow.user_agent = APPLICATION_NAME
        if flags:
            credentials = tools.run_flow(flow, store, flags)
        else: # Needed only for compatibility with Python 2.6
            credentials = tools.run(flow, store)
        print('Storing credentials to ' + credential_path)
    return credentials

credentials = get_credentials()
http = credentials.authorize(httplib2.Http())
service = discovery.build('drive', 'v3', http=http)
folder_id='0B_2y4tkk4P5wc3FZbmJQVXM1TkU'
folder_name='For Buzzfeed'

# Check for PNG files
file_names=['GA06_runoff_combine.png',
            'GA06_runoff_results.png',
            'GA06_runoff_comp_primary.png',
            'GA06_runoff_comp_pres.png']
file_dict=dict()
page_token=None
while True:
    response = service.files().list(q="'"+folder_id+"' in parents",
                                         spaces='drive',
                                         fields='nextPageToken, files(id, name)',
                                         pageToken=page_token).execute()
    for f in response.get('files', []):
        if(f.get('name') in file_names):
            file_dict[f.get('name')]=f.get('id')
    page_token = response.get('nextPageToken', None)
    if page_token is None:
        break;
    
# convert Google Sheet to input CSV
input_csv="GA06_Runoff.csv"
input_csv_id='13EpEyndrxgubpatKUKEYH6DZE6Gp_CGLGl1OOIbxfyI'
request = service.files().export_media(fileId=input_csv_id,
                                             mimeType='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet')
fh = io.BytesIO()
downloader = MediaIoBaseDownload(fh, request)
done = False
while done is False:
    status, done = downloader.next_chunk()
wb = openpyxl.load_workbook(fh,data_only=True)
sheet=wb['CSV OUTPUT']
with open(os.path.expanduser("~/Desktop/")+input_csv, 'wb') as f:
    c = csv.writer(f)
    for r in sheet.rows:
        c.writerow([cell.value for cell in r])



#Candidate profiles
candidates={}
candidates['OSSOFF']    ={'color':['#ccccff',
                                  '#9999ff',
                                  '#6666ff',
                                  '#0000ff', 
                                  '#0000cc', 
                                  '#000099',
                                  '#000077',
                                  '#000055'],
                          'party':'D'}
candidates['HANDEL']    ={'color':['#ffcccc',
                                   '#ff9999',
                                   '#ff6666',
                                   '#ff0000',
                                   '#cc0000',
                                   '#990000',
                                   '#770000',
                                   '#550000'],
                          'party':'R'}

for candidate in candidates:
    if(candidates[candidate]['color']==''):
        if(candidates[candidate]['party']=='D'):
            candidates[candidate]['color']=['#99f4ff','#00e6ff','#00c7dd','#008a99']
        elif(candidates[candidate]['party']=='R'):
            candidates[candidate]['color']=['#ff99f4','#ff00e6','#dd00c7','#99008a']
        else:
            candidates[candidate]['color']=['#ffd799','#ff9900','#dd8500','#995b00']

titles=['Results',
        'Ossoff 6/2017 vs Ossoff 4/2017',
        'Ossoff 2017 vs Clinton 2016']

# Grab coordinates for each precinct
precinct_xy=dict()
with open('./data_files/GA06_runoff.csv','rb') as csvfile:
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

# Get the 2016 gov results for comparison
margins_primary=dict()
with open('./data_files/2017_GA06_primary_margins.csv','rb') as csvfile:
    reader=csv.reader(csvfile)
    for row in reader:
        margins_primary[row[0]]=float(row[1])

# Get the 2016 pres results for comparison
margins_pres_2016=dict()
with open('./data_files/2016_GA06_pres_margins.csv','rb') as csvfile:
    reader=csv.reader(csvfile)
    for row in reader:
        margins_pres_2016[row[0]]=float(row[1])

# Grab votes from CSV input file
votes_dict=dict()
votes_file=open(os.path.expanduser("~/Desktop/")+input_csv,'rb')
reader=csv.reader(votes_file)
#headers = reader.next()
#cand_col=[i for i,x in enumerate(headers) if 'CandidateName' in x][0]
#prec_col=[i for i,x in enumerate(headers) if 'PrecinctName' in x][0]
#votes_col=[i for i,x in enumerate(headers) if 'Votes' in x][0]
cand_col=5
prec_col=4
votes_col=7
for row in reader:
    cname=row[cand_col]
    candidate=[c for c in candidates if c in cname.upper()][0]
    precinct=row[prec_col]
    precinct=re.sub('\s+$','',precinct)
    votes=int(row[votes_col])
    if(precinct!='Marietta 5B'):
        if(precinct not in votes_dict):
            votes_dict[precinct]=dict()
        if(candidate not in votes_dict[precinct]):
            votes_dict[precinct][candidate]=votes
        else:
            votes_dict[precinct][candidate]=votes_dict[precinct][candidate]+votes

precincts_reporting=len([precinct for precinct in votes_dict if sum(votes_dict[precinct].values())>0])
precincts=len(votes_dict)


im = Image.open("./data_files/GA06_BW_runoff.png")
xsize=im.size[0]
ysize=im.size[1]
img_all=im.copy() # Top individual vote getters
img_comp_primary=im.copy() # Compared to April primary
img_comp_pres=im.copy() # Compared to 2016 presidential results


mode="RGB"
#img=img.convert(mode)
red=ImageColor.getcolor('red',mode)
black=ImageColor.getcolor('black',mode)
gray=ImageColor.getcolor('gray',mode)

for precinct in votes_dict:
    if(precinct in precinct_xy):
        all_votes=sum([votes_dict[precinct][candidate] for candidate in votes_dict[precinct]])
        order=sorted(votes_dict[precinct],key=votes_dict[precinct].get,reverse=True)

        best=order[0]
        next_best=order[1]
        # Color results map
        # Color all candidates map, check if only one top votegetter, otherwise a tie
        best_votes=votes_dict[precinct][best]
        next_best_votes=votes_dict[precinct][next_best]
        if(all_votes>0):
            best_margin=float(best_votes-next_best_votes)/all_votes
        else:
            best_margin=0
        if(best_margin>0.5):
            color=ImageColor.getcolor(candidates[best]['color'][7],mode)
        elif(best_margin>0.4):
            color=ImageColor.getcolor(candidates[best]['color'][6],mode)
        elif(best_margin>0.3):
            color=ImageColor.getcolor(candidates[best]['color'][5],mode)
        elif(best_margin>0.2):
            color=ImageColor.getcolor(candidates[best]['color'][4],mode)
        elif(best_margin>0.15):
            color=ImageColor.getcolor(candidates[best]['color'][3],mode)
        elif(best_margin>0.1):
            color=ImageColor.getcolor(candidates[best]['color'][2],mode)
        elif(best_margin>0.05):
            color=ImageColor.getcolor(candidates[best]['color'][1],mode)
        elif(best_margin>0.):
            color=ImageColor.getcolor(candidates[best]['color'][0],mode)
        elif(best_votes>0):
            color=gray
        if(best_votes>0):
            ImageDraw.floodfill(img_all,(precinct_xy[precinct][0],precinct_xy[precinct][1]),color)

        if(all_votes>0):
            ossoff_margin=float(votes_dict[precinct]['OSSOFF']-votes_dict[precinct]['HANDEL'])/all_votes
        else:
            ossoff_margin=0.
        # Comparison map, how Ossoff is doing vs the April primary
        delta_primary=ossoff_margin-margins_primary[precinct]
        if(delta_primary>0):
            cand_color='OSSOFF'
        else:
            cand_color='HANDEL'
        if(abs(delta_primary)>0.5):
            color=ImageColor.getcolor(candidates[cand_color]['color'][7],mode)
        elif(abs(delta_primary)>0.4):
            color=ImageColor.getcolor(candidates[cand_color]['color'][6],mode)
        elif(abs(delta_primary)>0.3):
            color=ImageColor.getcolor(candidates[cand_color]['color'][5],mode)
        elif(abs(delta_primary)>0.2):
            color=ImageColor.getcolor(candidates[cand_color]['color'][4],mode)
        elif(abs(delta_primary)>0.15):
            color=ImageColor.getcolor(candidates[cand_color]['color'][3],mode)
        elif(abs(delta_primary)>0.1):
            color=ImageColor.getcolor(candidates[cand_color]['color'][2],mode)
        elif(abs(delta_primary)>0.05):
            color=ImageColor.getcolor(candidates[cand_color]['color'][1],mode)
        elif(abs(delta_primary)>0.):
            color=ImageColor.getcolor(candidates[cand_color]['color'][0],mode)
        elif(best_votes>0):
            color=gray
        if(all_votes>0):
            ImageDraw.floodfill(img_comp_primary,(precinct_xy[precinct][0],precinct_xy[precinct][1]),color)
        
        # Comparison map, how Ossoff is doing vs 2016 presidential 
        delta_pres=ossoff_margin-margins_pres_2016[precinct]
        if(delta_pres>0):
            cand_color='OSSOFF'
        else:
            cand_color='HANDEL'
        if(abs(delta_pres)>0.5):
            color=ImageColor.getcolor(candidates[cand_color]['color'][7],mode)
        elif(abs(delta_pres)>0.4):
            color=ImageColor.getcolor(candidates[cand_color]['color'][6],mode)
        elif(abs(delta_pres)>0.3):
            color=ImageColor.getcolor(candidates[cand_color]['color'][5],mode)
        elif(abs(delta_pres)>0.2):
            color=ImageColor.getcolor(candidates[cand_color]['color'][4],mode)
        elif(abs(delta_pres)>0.15):
            color=ImageColor.getcolor(candidates[cand_color]['color'][3],mode)
        elif(abs(delta_pres)>0.1):
            color=ImageColor.getcolor(candidates[cand_color]['color'][2],mode)
        elif(abs(delta_pres)>0.05):
            color=ImageColor.getcolor(candidates[cand_color]['color'][1],mode)
        elif(abs(delta_pres)>0.):
            color=ImageColor.getcolor(candidates[cand_color]['color'][0],mode)
        elif(best_votes>0):
            color=gray
        if(all_votes>0):
            ImageDraw.floodfill(img_comp_pres,(precinct_xy[precinct][0],precinct_xy[precinct][1]),color)

all_votes_dict=dict()
for cand in candidates:
    all_votes_dict[cand]=sum([votes_dict[precinct][cand] for precinct in votes_dict])
all_votes=sum(all_votes_dict[cand] for cand in candidates)
order=sorted(all_votes_dict,key=all_votes_dict.get,reverse=True)

img_combine=Image.new(mode,(4*58+2*xsize,4*58+2*ysize),"white")
#img_combine=Image.new(mode,(1530,1530),"white")
yt=58+ysize/2
yb=58+ysize+58*2+ysize/2
xl=58+xsize/2
xr=58+xsize+58*2+xsize/2
xc=58+xsize+58
yc=58+ysize+58
#yc=xc
#yt=xl
#yb=xr

img_ddhq=Image.open('./data_files/cropped-ddhq-icon.png')
img_combine.paste(img_all,(xc-xsize/2,yt-ysize/2,xsize+(xc-xsize/2),ysize+(yt-ysize/2)))
img_combine.paste(img_comp_primary,(xl-xsize/2,yb-ysize/2,xsize+(xl-xsize/2),ysize+(yb-ysize/2)))
img_combine.paste(img_comp_pres,(xr-xsize/2,yb-ysize/2,xsize+(xr-xsize/2),ysize+(yb-ysize/2)))
ddhq_size=img_ddhq.size
img_ddhq_sm=img_ddhq.resize((48,48))
img_combine.paste(img_ddhq_sm,(0+10,0+10,48+10,48+10))

draw = ImageDraw.Draw(img_combine)
#font = ImageFont.truetype("FRAHVIT.TTF", 48)
if(os.name=='nt'):
    font = ImageFont.truetype("micross.ttf", 48)
    font_sm = ImageFont.truetype("micross.ttf", 24)
    font_half = ImageFont.truetype("micross.ttf", 16)
elif(os.name=='posix'):
    font_dir='/usr/share/fonts/opentype/freefont/'
    font = ImageFont.truetype(font_dir+"FreeSans.otf", 48)
    font_sm = ImageFont.truetype(font_dir+"FreeSans.otf", 24)
    font_half = ImageFont.truetype(font_dir+"FreeSans.otf", 16)
    

# Title
title="2017 GA-06 Special Election Runoff"
draw.text((xc-64*len(title)/4+174, 10),title,black,font=font)    

draw.text((xc-xsize/2+10+0*xsize/16, yt+ysize/2-2.5*48),"1",black,font=font)
draw.text(( 0+10+0*xsize/16, yb+ysize/2-2.5*48),"2",black,font=font)
draw.text((xc+10+0*xsize/16, yb+ysize/2-2.5*48),"3",black,font=font)

draw.text((xc-xsize/2+10, yt+ysize/2-ysize/8),"Results",black,font=font_sm)
draw.text((0+10, yb+ysize/2-ysize/8),"vs 2017 April Primary",black,font=font_sm)
draw.text((xc+10, yb+ysize/2-ysize/8),"vs 2016 Presidential",black,font=font_sm)

margins=['> 0%','> 5%','>10%','>15%','>20%','>30%','>40%','>50%']
for k in range(8):
    draw.rectangle((xr-4*50+50*k,yc-25,xr-4*50+50*(k+1),yc),fill=candidates['OSSOFF']['color'][k],outline=black)
    draw.rectangle((xr-4*50+50*k,yc,xr-4*50+50*(k+1),yc+25),fill=candidates['HANDEL']['color'][k],outline=black)
    draw.text((xr-4*50+50*k,yc-50),margins[k],black,font=font_half)

for k,cand in enumerate(order):
    draw.text((xl-125,yc-25+25*k),cand+' ('+candidates[cand]['party']+')',candidates[cand]['color'][3],font=font_half)
    if(all_votes>0):
        draw.text((xl,yc-25+25*k),'%5s' % str(100*round(float(all_votes_dict[cand])/all_votes,3))+'%',black,font=font_half)
    else:
        draw.text((xl,yc-25+25*k),'%5s' % str(0.0)+'%',black,font=font_half)
        
draw.text((xc-90,4*58+2*ysize-38),str(precincts_reporting)+'/'+str(precincts)+' precincts reporting',black,font=font_half)    


img_combine.save(os.path.expanduser("~/Desktop/")+file_names[0])


#Individuals
img_ddhq=img_ddhq.resize((80,80))
ratio=max([float(xsize)/(1920-2*100),float(ysize)/(1080-2*100)])
if(sample_only):
    sample_text="SAMPLE"
    img_sample=Image.new(mode,(120,120),"white")
    draw_sample = ImageDraw.Draw(img_sample)
    font_sample_size=48
    font_too_big=True
    while(font_too_big):
        if(os.name=='nt'):
            font_sample = ImageFont.truetype("micross.ttf", font_sample_size)
        elif(os.name=='posix'):
            font_dir='/usr/share/fonts/opentype/freefont/'
            font_sample = ImageFont.truetype(font_dir+"FreeSans.otf", font_sample_size)
        textwidth, textheight = draw_sample.textsize(sample_text, font_sample)
        if(textwidth>120):
            font_too_big=True
            font_sample_size=font_sample_size/2
        else:
            font_too_big=False
            draw_sample.text((60-textwidth/2, 60-textheight), sample_text, gray,font=font_sample)

img_all_i=Image.new(mode,(1920,1080),"white")
if(sample_only):
    for x in range(0,1920,120):
        y=1080/2
        img_all_i.paste(img_sample,(x,y))
img_all_sm=img_all.resize((int(round(xsize/ratio)),int(round(ysize/ratio))))
xc=1920/2
yc=1080/2
xr=xc+xc/2
xgeo,ygeo=img_all_sm.size
img_all_i.paste(img_all_sm,(xc-xgeo/2,yc-ygeo/2,xc-xgeo/2+xgeo,yc-ygeo/2+ygeo))
draw_1 = ImageDraw.Draw(img_all_i)
textwidth, textheight = draw_1.textsize(title,font=font)
draw_1.text((xc-textwidth/2, 10),title,black,font=font)
title_1=titles[0]+', as of '+datetime.datetime.now().strftime("%I:%M%p, %B %d")
textwidth, textheight = draw_1.textsize(title_1,font=font_sm)
draw_1.text((xc-textwidth/2, 10+58),title_1,black,font=font_sm)
for k,cand in enumerate(order):
    draw_1.text((58,1080-10-25*4+25*k),cand,candidates[cand]['color'][3],font=font_sm)
    if(all_votes>0):
        draw_1.text((58+118,1080-10-25*4+25*k),'%5s' % str(100*round(float(all_votes_dict[cand])/all_votes,3))+'%',black,font=font_sm)
    else:
        draw_1.text((58+118,1080-10-25*4+25*k),'%5s' % str(0.0)+'%',black,font=font_sm)    
    results_str='%12s' % "{:,}".format(all_votes_dict[cand])
    if(k!=0):
        results_str=results_str+'  (-%s)' % "{:,}".format(all_votes_dict[order[0]]-all_votes_dict[cand])
    draw_1.text((58+178,1080-10-25*4+25*k),results_str,black,font=font_sm)
draw_1.text((58,1080-10-25),'Total votes',black,font=font_sm)
draw_1.text((58+178,1080-10-25),'%12s' % "{:,}".format(all_votes),black,font=font_sm)
for l,cand in enumerate(['OSSOFF','HANDEL']):
    for k in range(8):
        draw_1.rectangle((1920-10-70*8+70*k,1080-10-25*2+25*l,1920-10-70*8+70*(k+1),1080-10-25*2+25*(l+1)),fill=candidates[cand]['color'][k],outline=black)
        if(l==0):
            draw_1.text((1920-10-70*8+70*k,1080-10-25*3),margins[k],black,font=font_sm)
    textwidth, textheight = draw_1.textsize(cand, font_sm)
    draw_1.text((1920-10-70*8-10-textwidth,1080-10-25*2+25*l),cand,black,font=font_sm)    
img_all_i.paste(img_ddhq,(0+10,0+10,80+10,80+10))
precinct_text=str(precincts_reporting)+'/'+str(precincts)+" precincts reporting"
textwidth, textheight = draw_1.textsize(precinct_text, font_sm)
draw_1.text((xc-textwidth/2,1080-10-textheight),precinct_text,black,font=font_sm)
draw_1.text((579,291),'Cobb',black,font=font_sm)
draw_1.text((1299,741),'DeKalb',black,font=font_sm)
draw_1.text((1259,257),'Fulton',black,font=font_sm)
img_all_i.save(os.path.expanduser("~/Desktop/")+file_names[1])

img_comp_primary_i=Image.new(mode,(1920,1080),"white")
if(sample_only):
    for x in range(0,1920,120):
        y=1080/2
        img_comp_primary_i.paste(img_sample,(x,y))
img_comp_primary_sm=img_comp_primary.resize((int(round(xsize/ratio)),int(round(ysize/ratio))))
xgeo,ygeo=img_comp_primary_sm.size
img_comp_primary_i.paste(img_comp_primary_sm,(xc-xgeo/2,yc-ygeo/2,xc-xgeo/2+xgeo,yc-ygeo/2+ygeo))
draw_2 = ImageDraw.Draw(img_comp_primary_i)
textwidth, textheight = draw_2.textsize(title,font=font)
draw_2.text((xc-textwidth/2, 10),title,black,font=font)
title_2=titles[1]+', as of '+datetime.datetime.now().strftime("%I:%M%p, %B %d")
textwidth, textheight = draw_2.textsize(title_2,font=font_sm)
draw_2.text((xc-textwidth/2, 10+58),title_2,black,font=font_sm)
for k,cand in enumerate(order):
    draw_2.text((58,1080-10-25*4+25*k),cand,candidates[cand]['color'][3],font=font_sm)
    if(all_votes>0):
        draw_2.text((58+118,1080-10-25*4+25*k),'%5s' % str(100*round(float(all_votes_dict[cand])/all_votes,3))+'%',black,font=font_sm)
    else:
        draw_2.text((58+118,1080-10-25*4+25*k),'%5s' % str(0.0)+'%',black,font=font_sm)    
    results_str='%12s' % "{:,}".format(all_votes_dict[cand])
    if(k!=0):
        results_str=results_str+'  (-%s)' % "{:,}".format(all_votes_dict[order[0]]-all_votes_dict[cand])
    draw_2.text((58+178,1080-10-25*4+25*k),results_str,black,font=font_sm)
draw_2.text((58,1080-10-25),'Total votes',black,font=font_sm)
draw_2.text((58+178,1080-10-25),'%12s' % "{:,}".format(all_votes),black,font=font_sm)
for l,cand in enumerate(['OSSOFF','HANDEL']):
    for k in range(8):
        draw_2.rectangle((1920-10-70*8+70*k,1080-10-25*2+25*l,1920-10-70*8+70*(k+1),1080-10-25*2+25*(l+1)),fill=candidates[cand]['color'][k],outline=black)
        if(l==0):
            draw_2.text((1920-10-70*8+70*k,1080-10-25*3),margins[k],black,font=font_sm)
textwidth, textheight = draw_2.textsize('Ossoff under', font_sm)
draw_2.text((1920-10-70*8-10-textwidth,1080-10-25*2+25*0),'Ossoff over',black,font=font_sm)
draw_2.text((1920-10-70*8-10-textwidth,1080-10-25*2+25*1),'Ossoff under',black,font=font_sm)   
img_comp_primary_i.paste(img_ddhq,(0+10,0+10,80+10,80+10))
precinct_text=str(precincts_reporting)+'/'+str(precincts)+" precincts reporting"
textwidth, textheight = draw_2.textsize(precinct_text, font_sm)
draw_2.text((xc-textwidth/2,1080-10-textheight),precinct_text,black,font=font_sm)
draw_2.text((579,291),'Cobb',black,font=font_sm)
draw_2.text((1299,741),'DeKalb',black,font=font_sm)
draw_2.text((1259,257),'Fulton',black,font=font_sm)
img_comp_primary_i.save(os.path.expanduser("~/Desktop/")+file_names[2])

img_comp_pres_i=Image.new(mode,(1920,1080),"white")
if(sample_only):
    for x in range(0,1920,120):
        y=1080/2
        img_comp_pres_i.paste(img_sample,(x,y))
img_comp_pres_sm=img_comp_pres.resize((int(round(xsize/ratio)),int(round(ysize/ratio))))
xgeo,ygeo=img_comp_pres_sm.size
img_comp_pres_i.paste(img_comp_pres_sm,(xc-xgeo/2,yc-ygeo/2,xc-xgeo/2+xgeo,yc-ygeo/2+ygeo))
draw_3 = ImageDraw.Draw(img_comp_pres_i)
textwidth, textheight = draw_3.textsize(title,font=font)
draw_3.text((xc-textwidth/2, 10),title,black,font=font)
title_3=titles[2]+', as of '+datetime.datetime.now().strftime("%I:%M%p, %B %d")
textwidth, textheight = draw_3.textsize(title_3,font=font_sm)
draw_3.text((xc-textwidth/2, 10+58),title_3,black,font=font_sm)
for k,cand in enumerate(order):
    draw_3.text((58,1080-10-25*4+25*k),cand,candidates[cand]['color'][3],font=font_sm)
    if(all_votes>0):
        draw_3.text((58+118,1080-10-25*4+25*k),'%5s' % str(100*round(float(all_votes_dict[cand])/all_votes,3))+'%',black,font=font_sm)
    else:
        draw_3.text((58+118,1080-10-25*4+25*k),'%5s' % str(0.0)+'%',black,font=font_sm)    
    results_str='%12s' % "{:,}".format(all_votes_dict[cand])
    if(k!=0):
        results_str=results_str+'  (-%s)' % "{:,}".format(all_votes_dict[order[0]]-all_votes_dict[cand])
    draw_3.text((58+178,1080-10-25*4+25*k),results_str,black,font=font_sm)
draw_3.text((58,1080-10-25),'Total votes',black,font=font_sm)
draw_3.text((58+178,1080-10-25),'%12s' % "{:,}".format(all_votes),black,font=font_sm)
for l,cand in enumerate(['OSSOFF','HANDEL']):
    for k in range(8):
        draw_3.rectangle((1920-10-70*8+70*k,1080-10-25*2+25*l,1920-10-70*8+70*(k+1),1080-10-25*2+25*(l+1)),fill=candidates[cand]['color'][k],outline=black)
        if(l==0):
            draw_3.text((1920-10-70*8+70*k,1080-10-25*3),margins[k],black,font=font_sm)
textwidth, textheight = draw_3.textsize('Ossoff under', font_sm)
draw_3.text((1920-10-70*8-10-textwidth,1080-10-25*2+25*0),'Ossoff over',black,font=font_sm)
draw_3.text((1920-10-70*8-10-textwidth,1080-10-25*2+25*1),'Ossoff under',black,font=font_sm)   
img_comp_pres_i.paste(img_ddhq,(0+10,0+10,80+10,80+10))
precinct_text=str(precincts_reporting)+'/'+str(precincts)+" precincts reporting"
textwidth, textheight = draw_1.textsize(precinct_text, font_sm)
draw_3.text((xc-textwidth/2,1080-10-textheight),precinct_text,black,font=font_sm)
draw_3.text((579,291),'Cobb',black,font=font_sm)
draw_3.text((1299,741),'DeKalb',black,font=font_sm)
draw_3.text((1259,257),'Fulton',black,font=font_sm)
img_comp_pres_i.save(os.path.expanduser("~/Desktop/")+file_names[3])

for name in file_names:
    media = MediaFileUpload(os.path.expanduser("~/Desktop/")+name,
                        mimetype='image/png',
                        resumable=True)
    if(name in file_dict):
        file_metadata={'name' : name}
        f = service.files().update(  fileId=file_dict[name],
                                        body=file_metadata,
                                        media_body=media,
                                        fields='id').execute()
    else:
        file_metadata = {'name' : name,
                         'parents': [ folder_id ]
                         }
        f = service.files().create(body=file_metadata,
                                   media_body=media,
                                   fields='id').execute()
    

#img_all.close()
#img_comp_primary.close()
#img_comp_pres.close()
#img_combine.close()
    