#!/usr/bin/python

import os
import wx
import time
import ConfigParser

class  pyTime(wx.Frame):
    __HELP__ = """
    [pyTime]
    #format is passed to strftime() to format a date string.
    format: %Y-%m-%d %H:%M:%S [%z]
    
    # Any string that starts with the word 'offset' will be appended and 
    # displayed.  The string format is:
    # <Unix TZ: eg US/Eastern>:<Text for offset>:[optional format]
    # if the optional format is not give, the above defined will be used the 
    # offsets are sorted in ascii-betical order (alphebetical with order on 
    # caps and numbers)
    
    #offset0: UTC              : UTC                   : %Y%m%d%H%M     %S
    offset1: UTC              : UTC
    offset2: Pacific/Auckland : McMurdo
    offset3: Indian/Mahe      : Seychelles
    offset4: US/Eastern       : US Eastern
    offset5: US/Mountain      : US Mountain
    offset6: Europe/Paris     : Paris
    
    #Optional
    # colorSchema determins the usage of the following variables:
    #     backgroundToneA
    #     backgroundToneB
    # If colorSchema is not set; or set to something invalid; or set to 
    # 'alternating' the above variables will be used to paint every other offset
    # cell color (eg.  offset 1,3,5,... will be background Tone A 
    # and offset 2,4,6,... will use background Tone B
    # If colorSchea is set to 'diurnal', Tone A will be used for  daylight hours and
    # Tone B will be used for night hour.  Defaults to alternating
    colorSchema: diurnal
    
    
    # the Tone colors are given in 6 character hex format: RRBBGG. eg FFFFFF 
    # translates to white, FF0000 is red, 00FF00 is blue, 0000FF is green, 
    # while 000000 is black.
    
    backgroundToneA: 749bff
    backgroundToneB: bdc8e4
    """
    __PAINT_ALTERNATING__ = 'alternating'
    __PAINT_DIURNAL__ = 'diurnal'
    paintFormat = __PAINT_ALTERNATING__
    pixlesPerCharX = 9
    #below is a list of all possible location to find the pyTime.cfg file
    configSearch = [os.path.join(os.path.expanduser("~"), ".pyTime.cfg"), \
                   os.path.join(os.path.expanduser("~"), "pyTime.cfg"), \
                   os.path.join("/etc/", "pyTime.cfg"), \
                   os.path.join(os.getcwd(), ".pyTime.cfg"), \
                   os.path.join(os.getcwd(), "pyTime.cfg")]
    def __init__(self, *args, **kwds):
        wx.Frame.__init__(self, *args, **kwds)
        self.SetTitle("pyTime")
        sizer = wx.BoxSizer(wx.VERTICAL)
        #setup initial colors to use
        self.fgA = [  0,   0,   0] #defaults to black
        self.fgB = [ 13, 127, 255] #defaults to white
        self.bgA = [  0,   0,   0]
        self.bgB = [255, 255, 255]
        #Look in several directories for a .pyTime.cfg file that I should use
        #to fetch settings from
        self.config = None
        for i in self.configSearch:
            if os.path.isfile(i):
                self.config = self.getConfig(i) #confg has placeholders for textBoxes
                break
        if self.config == None:
            self.usageCFG()
        #now that we have read the config, make the GUI and show it
        self.displays=[]
        for i in self.config: #add the text boxes to the config
            i[3]  =wx.TextCtrl(self, -1, "")
            i[3].SetFont(wx.Font(10, wx.MODERN, wx.NORMAL, wx.NORMAL, 0, ""))
            sizer.Add(i[3], 0, wx.ADJUST_MINSIZE, 0)
        self.SetSizer(sizer)
        sizer.Fit(self)
        self.Layout()
        self.timer = wx.Timer(self, -1)
        self.Bind(wx.EVT_TIMER, self.updateTime, self.timer)
        self.timer.Start(milliseconds=1000, oneShot=False)
        self.updateTime()
        
    def getConfig(self,  configFile):
        """Open  the  config  file  and  make  a  record  for  the  times  and
        dates  to  display.  It also looks for color values and if they are
        found, will set them quietly"""
        cfg  =  ConfigParser.RawConfigParser()  #read  config
        try:
            print("Found %s" % configFile)
            cfg.read(configFile)  #read  from  file
        except:
            exit("ERROR:  Could  not  open  %s"  %  configFile)
        try:
            defaultFormat  =  cfg.get('pyTime','format')  #fetch  default  format
        except  Exception,  e:
            exit("ERROR:    did  not  find  a  default  format.    Set  one  in  the  config  \
                        file  and  try  again:  %s"  %  e)
        offsets=[] #find all the offsets then sort then
        for  i  in  cfg.options('pyTime'):
            if  i.find("offset")  ==  0:  #we  have  an  offset  value
                offsets.append(i)
        offsets.sort()
        offsets_triplets=[]#this  should  hold  arrays  of  size  3  int  offset,  str  name,  str  format
        for i in offsets:
            opt  =  cfg.get('pyTime',  i)
            if  len(opt.split(':'))  ==  3:
                [tz,  title,  format]  =  opt.split(':')
                offsets_triplets.append([tz.strip(),  title.strip(),  format.strip(), None])
            elif  len(opt.split(':'))  ==  2:  #use  the  default  date  format
                [tz,  title]  =  opt.split(":")
                offsets_triplets.append([tz.strip(),  title.strip(),  defaultFormat.strip(), None])
        #try to pull out colors:
        if cfg.has_option('pyTime', 'foregroundToneA'):
            self.fgA = self.parseColors(cfg.get('pyTime','foregroundToneA'), self.fgA)
        if cfg.has_option('pyTime', 'backgroundToneA'):
            self.bgA = self.parseColors(cfg.get('pyTime','backgroundToneA'), self.bgA)
        if cfg.has_option('pyTime', 'foregroundToneB'):
            self.fgB = self.parseColors(cfg.get('pyTime','foregroundToneB'), self.fgB)
        if cfg.has_option('pyTime', 'backgroundToneB'):
            self.bgB = self.parseColors(cfg.get('pyTime','backgroundToneB'), self.bgB)
        if cfg.has_option('pyTime', 'colorSchema') and cfg.get('pyTime', 'colorSchema') == self.__PAINT_DIURNAL__:
            self.paintFormat = self.__PAINT_DIURNAL__ #silently ignore other options
        return  offsets_triplets
    def parseColors(self, htmlColor, fallback):
        """If we cannot convert an html Hex Color properly, return the passed fallback color"""
        htmlColor = htmlColor.strip()
        if len(htmlColor) != 6:
            print("Using builtin colors")
            return fallback
        red = int(htmlColor[0:2], 16)
        grn = int(htmlColor[2:4], 16)
        blu = int(htmlColor[4:6], 16)
        return [red, grn, blu]
    def updateTime(self, event = None):
        """When this is called, update all the text boxes with the correct time"""
        boxWidth = 80 #used to force the window to be the correct width
        for [tz, title, format, wxtextbox] in self.config:
            os.environ['TZ'] = tz #set the TZ to that given in the config
            time.tzset() #set the time zone in the time module
            dateStr = time.strftime(format) + " " + title
            boxWidth = max(boxWidth, len(dateStr)*self.pixlesPerCharX)
            wxtextbox.SetValue(dateStr)
            if self.paintFormat == self.__PAINT_DIURNAL__ and \
                    int(time.strftime("%H")) >= 7 and int(time.strftime("%H")) <= 19:  #rudimentary check for daylight
                wxtextbox.SetBackgroundColour(wx.Colour(self.bgA[0], self.bgA[1], self.bgA[2]))
            if self.paintFormat == self.__PAINT_DIURNAL__ and \
                    int(time.strftime("%H")) < 7 or int(time.strftime("%H")) > 19:  #checking for daylight
                wxtextbox.SetBackgroundColour(wx.Colour(self.bgB[0], self.bgB[1], self.bgB[2]))
        for i in range(len(self.config)): #set smallest size and colorize
            self.config[i][3].SetMinSize([boxWidth, 27]) #set smallest size
            if (i % 2) == 0 and self.paintFormat == self.__PAINT_ALTERNATING__:
                self.config[i][3].SetBackgroundColour(wx.Colour(self.bgA[0], self.bgA[1], self.bgA[2]))
            if (i % 2) == 1 and self.paintFormat == self.__PAINT_ALTERNATING__:
                self.config[i][3].SetBackgroundColour(wx.Colour(self.bgB[0], self.bgB[1], self.bgB[2]))
        self.SetMinSize([boxWidth, -1])      
        self.SetMaxSize([boxWidth, 27*len(self.config)])
        try:
            event.Skip
        except:
            pass

    def usageCFG(self):
        """Prints a usage on the config file with an example"""
        print("It appears that you do not have a pyTime.cfg file\nin any of the following places (in order):")
        for i in self.configSearch:
            print("\t" + i)
        print("""\
To Fix this, simply copy the template past the scissors into a
blank text file and save.  Edit as needed
  
8<--------8<--------8<--------8<--------8<--------8<--------8<--------8<--------
[pyTime]
#format is passed to strftime() to format a date string.
format: %Y-%m-%d %H:%M:%S [%z]

# Any string that starts with the word 'offset' will be appended and displayed
# The string format is:
# <Unix TZ: eg US/Eastern>:<Text for offset>:[optional format]
# if the optional format is not give, the above defined will be used the 
# offsets are sorted in ascii-betical order (alphebetical with order on caps and numbers)

#offset0: UTC              : UTC                   : %Y%m%d%H%M     %S
offset3: UTC              : UTC
offset1: Pacific/Auckland : McMurdo
offset2: Indian/Mahe      : Seychelles
offset4: US/Eastern       : US Eastern
offset5: US/Mountain      : US Mountain
offset6: Europe/Paris     : Paris



# colorSchema determins the usage of the following variables:
#     backgroundToneA
#     backgroundToneB
# If colorSchema is not set; or set to something invalid; or set to 
# 'alternating' the above variables will be used to paint every other offset
# cell color (eg.  offset 1,3,5,... will be background Tone A 
# and offset 2,4,6,... will use background Tone B
# If colorSchea is set to 'diurnal', Tone A will be used for  daylight hours and
# Tone B will be used for night hours
colorSchema: alternating


#the Tone colors are given in HTML 6 character hex format: eg FFFFFF for white,
#FF0000 for red, 00FF00 for blue, 0000FF for green, and 000000 for black.

backgroundToneA: 749bff
backgroundToneB: bdc8e4
8<--------8<--------8<--------8<--------8<--------8<--------8<--------8<--------
""")
        exit()
  
if  __name__  ==  '__main__':
    pytime = wx.PySimpleApp(0)
    wx.InitAllImageHandlers()
    frame = pyTime(None, -1, "")
    pytime.SetTopWindow(frame)
    frame.Show()
    pytime.MainLoop()
