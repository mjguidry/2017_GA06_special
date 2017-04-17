# -*- coding: utf-8 -*-
"""
Created on Wed Apr 12 21:24:05 2017

@author: mike
"""
import csv, re
from PIL import Image,ImageColor, ImageDraw
import sys, os
from PyQt4.QtCore import pyqtSlot
from PyQt4.QtGui import *
import ctypes

myappid = u'DDHQ.2017.GA06' # arbitrary string
ctypes.windll.shell32.SetCurrentProcessExplicitAppUserModelID(myappid)

input_csv_def=os.path.expanduser("~/Desktop/Sample GA06.csv")
r_vs_d_png_def=os.path.expanduser("~/Desktop/GA06_R_vs_D.png")
all_cands_png_def=os.path.expanduser("~/Desktop/GA06_all_cands.png")
all_R_cands_png_def=os.path.expanduser("~/Desktop/GA06_R_cands.png")
ossoff_50_png_def=os.path.expanduser("~/Desktop/GA06_ossoff_50.png")

qt_app = QApplication(sys.argv)

def color_maps(input_csv,r_vs_d_png,all_cands_png,all_R_cands_png,ossoff_50_png):
    
    #Candidate profiles
    candidates={}
    candidates['OSSOFF']    ={'color':'#0000ff','party':'D'}
    candidates['EDWARDS']   ={'color':'','party':'D'}
    candidates['QUIGG']     ={'color':'','party':'D'}
    candidates['KEATLEY']   ={'color':'','party':'D'}
    candidates['SLOTIN']    ={'color':'','party':'D'}
    
    candidates['KREMER']    ={'color':'','party':'R'}
    candidates['GRAY']      ={'color':'#ffff00','party':'R'}
    candidates['LEVELL']    ={'color':'','party':'R'}
    candidates['MOODY']     ={'color':'#cc00ff','party':'R'}
    candidates['ABROMS']    ={'color':'','party':'R'}
    candidates['HILL']      ={'color':'#00ff00','party':'R'}
    candidates['HANDEL']    ={'color':'#ff0000','party':'R'}
    candidates['GRAWERT']   ={'color':'','party':'R'}
    candidates['WILSON']    ={'color':'','party':'R'}
    candidates['BHUIYAN']   ={'color':'','party':'R'}
    candidates['LLOP']      ={'color':'','party':'R'}
    
    candidates['HERNANDEZ'] ={'color':'','party':'I'}
    candidates['POLLARD']   ={'color':'','party':'I'}
    candidates['WRITE IN']   ={'color':'','party':'I'}
    
    for candidate in candidates:
        if(candidates[candidate]['color']==''):
            if(candidates[candidate]['party']=='D'):
                candidates[candidate]['color']='#00e6ff'
            elif(candidates[candidate]['party']=='R'):
                candidates[candidate]['color']='#ff00e6'
            else:
                candidates[candidate]['color']='#ff9900'
    
    # Grab coordinates for each precinct
    precinct_xy=dict()
    with open('./data_files/GA06_coords.csv','rb') as csvfile:
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
    
    # Grab votes from CSV input file
    votes_dict=dict()
    votes_file=open(input_csv,'rb')
    reader=csv.reader(votes_file)
    headers = reader.next()
    cand_col=[i for i,x in enumerate(headers) if 'CandidateName' in x][0]
    prec_col=[i for i,x in enumerate(headers) if 'PrecinctName' in x][0]
    votes_col=[i for i,x in enumerate(headers) if 'Votes' in x][0]
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
    
    im = Image.open("./data_files/GA06_BW.png")
    
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
    for precinct in votes_dict:
        all_votes=sum([votes_dict[precinct][candidate] for candidate in votes_dict[precinct]])
        Ds=sum([votes_dict[precinct][candidate] for candidate in votes_dict[precinct] if candidates[candidate]['party']=='D'])
        Rs=sum([votes_dict[precinct][candidate] for candidate in votes_dict[precinct] if candidates[candidate]['party']=='R'])
        best=[candidate for candidate in votes_dict[precinct] if votes_dict[precinct][candidate]==max(votes_dict[precinct].values())]
        most_R_votes=max([votes_dict[precinct][candidate] for candidate in votes_dict[precinct] if candidates[candidate]['party']=='R'])
        best_R=[candidate for candidate in votes_dict[precinct] if candidates[candidate]['party']=='R' and votes_dict[precinct][candidate]==most_R_votes]
        if('OSSOFF' in votes_dict[precinct]):
            ossoff_votes=votes_dict[precinct]['OSSOFF']
        else:
            ossoff_votes=0
            
        # Color R vs D map, check for ties
        if(Rs>Ds):
            ImageDraw.floodfill(img_rvd,(precinct_xy[precinct][0],precinct_xy[precinct][1]),red)
        elif(Ds>Rs):
            ImageDraw.floodfill(img_rvd,(precinct_xy[precinct][0],precinct_xy[precinct][1]),blue)
        elif(Ds>0 and Rs>0):
            ImageDraw.floodfill(img_rvd,(precinct_xy[precinct][0],precinct_xy[precinct][1]),gray)
    
        # Color all candidates map, check if only one top votegetter, otherwise a tie
        if(len(best)==1):
            candidate=best[0]
            color=ImageColor.getcolor(candidates[candidate]['color'],mode)
            ImageDraw.floodfill(img_all,(precinct_xy[precinct][0],precinct_xy[precinct][1]),color)
        elif(len(best)>1 and votes_dict[precinct][best[0]]>0):
            ImageDraw.floodfill(img_all,(precinct_xy[precinct][0],precinct_xy[precinct][1]),gray)
    
        # Color all R candidates map, check if only one top R votegetter, otherwise a tie
        if(len(best_R)==1):
            candidate=best_R[0]
            color=ImageColor.getcolor(candidates[candidate]['color'],mode)
            ImageDraw.floodfill(img_gop,(precinct_xy[precinct][0],precinct_xy[precinct][1]),color)
        elif(len(best_R)>1 and votes_dict[precinct][best_R[0]]>0):
            ImageDraw.floodfill(img_gop,(precinct_xy[precinct][0],precinct_xy[precinct][1]),gray)

        # Color map indicating if Ossoff has reached 50%
        if(all_votes>0):
            if((float(ossoff_votes)/all_votes)>0.5):
                color=ImageColor.getcolor(candidates['OSSOFF']['color'],mode)
                ImageDraw.floodfill(img_ossoff,(precinct_xy[precinct][0],precinct_xy[precinct][1]),color)
            else:
                ImageDraw.floodfill(img_ossoff,(precinct_xy[precinct][0],precinct_xy[precinct][1]),not_ossoff)
    
    img_rvd.save(r_vs_d_png)
    img_all.save(all_cands_png)
    img_gop.save(all_R_cands_png)
    img_ossoff.save(ossoff_50_png)
    
    img_rvd.close()
    img_all.close()
    img_gop.close()
    img_ossoff.close()
    
class LayoutExample(QWidget):
    ''' An example of PySide/PyQt absolute positioning; the main window
        inherits from QWidget, a convenient widget for an empty window. '''
 
    def __init__(self):
        # Initialize the object as a QWidget and
        # set its title and minimum width
        QWidget.__init__(self)
        self.setWindowTitle('2017 GA06 Special Election')
        self.setWindowIcon(QIcon('./data_files/cropped-ddhq-icon.png'))
        self.setMinimumWidth(600)
 
        self.color_maps=color_maps 
 
        # Create the QVBoxLayout that lays out the whole form
        self.layout = QVBoxLayout()
 
        # Create the form layout that manages the labeled controls
        self.form_layout = QFormLayout()
 
        # Create the entry control to specify a csv_input
        # and set its placeholder text
        self.csv_input = QLineEdit(self)
        self.csv_input.setPlaceholderText('CSV file')
        self.csv_input.setText(input_csv_def)
 
        # Add it to the form layout with a label
        self.form_layout.addRow('Input CSV file:', self.csv_input)

        # Add empty row

        # Create the entry control to specify an R vs D PNG
        # and set its placeholder text
        self.r_vs_d = QLineEdit(self)
        self.r_vs_d.setPlaceholderText('PNG file')
        self.r_vs_d.setText(r_vs_d_png_def)
 
        # Add it to the form layout with a label
        self.form_layout.addRow('Output R vs D PNG:', self.r_vs_d)

        # Create the entry control to specify an all candidates PNG
        # and set its placeholder text
        self.all_cands = QLineEdit(self)
        self.all_cands.setPlaceholderText('PNG file')
        self.all_cands.setText(all_cands_png_def)
 
        # Add it to the form layout with a label
        self.form_layout.addRow('Output all candidates PNG:', self.all_cands)

        # Create the entry control to specify an only R candidates PNG
        # and set its placeholder text
        self.all_R_cands = QLineEdit(self)
        self.all_R_cands.setPlaceholderText('PNG file')
        self.all_R_cands.setText(all_R_cands_png_def)
 
        # Add it to the form layout with a label
        self.form_layout.addRow('Output R-only candidates PNG:', self.all_R_cands)

        # Create the entry control to specify an only R candidates PNG
        # and set its placeholder text
        self.ossoff_50 = QLineEdit(self)
        self.ossoff_50.setPlaceholderText('PNG file')
        self.ossoff_50.setText(ossoff_50_png_def)
 
        # Add it to the form layout with a label
        self.form_layout.addRow('Output Ossoff at 50% PNG:', self.ossoff_50)
  
        # Add the form layout to the main VBox layout
        self.layout.addLayout(self.form_layout)
 
        # Add stretch to separate the form layout from the button
        self.layout.addStretch(1)
 
        # Create a horizontal box layout to hold the button
        self.button_box = QHBoxLayout()
 
        # Add stretch to push the button to the far right
        self.button_box.addStretch(1)
 
        # Create the build button with its caption
        self.build_button = QPushButton('Generate PNGs', self)

        # Add it to the button box
        self.button_box.addWidget(self.build_button)
        
        # Connect signal to button
        self.build_button.clicked.connect(self.on_click)
 
        # Add the button box to the bottom of the main VBox layout
        self.layout.addLayout(self.button_box)
 
        # Set the VBox layout as the window's main layout
        self.setLayout(self.layout)
        
    @pyqtSlot()
    def on_click(self):
        input_csv=str(self.csv_input.text())
        r_vs_d_png=str(self.r_vs_d.text())
        all_cands_png=str(self.all_cands.text())
        all_R_cands_png=str(self.all_R_cands.text())
        ossoff_50_png=str(self.ossoff_50.text())
        if(not os.path.isfile(input_csv)):
            self.error_message=QErrorMessage()
            self.error_message.setWindowTitle('File not found!')
            self.error_message.setWindowIcon(QIcon('./data_files/cropped-ddhq-icon.png'))
            self.error_message.showMessage('File '+input_csv+' not found!')
        else:
#            try:
            self.color_maps(input_csv,r_vs_d_png,all_cands_png,all_R_cands_png,ossoff_50_png)
#            except:
#                self.error_message=QErrorMessage()
#                self.error_message.setWindowTitle('Error!')
#                self.error_message.setWindowIcon(QIcon('cropped-ddhq-icon.png'))
#                self.error_message.showMessage(str(sys.exc_info()[0]))

                    
            
    def run(self):
        # Show the form
        self.show()
        # Run the qt application
        qt_app.exec_()
 
# Create an instance of the application window and run it
app = LayoutExample()
app.run()