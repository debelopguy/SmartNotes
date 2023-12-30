# NOTES BY DEBEBOPMENT
from PyQt5.QtCore import *
from PyQt5.QtWidgets import *
from PyQt5.QtGui import *
from random import*
import json,os
#UI
app = QApplication([])
win = QWidget()
settingswin = QWidget()

#checking main directory TODO for later... this stupid thing doesnt work
"""AppDataFolder = os.path.abspath(os.environ["LOCALAPPDATA"])
os.mkdir(AppDataFolder+r"\DBSN")"""

#loading files
notes = open("notes.json","r")
settings = json.load(open("settings.json","r"))
defaultsettings = {
    "theme":"Default",
    "lettercount":False,
    "starttext":"",
}

wicon = QIcon("notebook.png")
wtitle = "Smart Notes 📝"

win.setWindowIcon(wicon)
win.setWindowTitle(wtitle)
screensize = app.primaryScreen().size()
ssx,ssy = screensize.width(),screensize.height()
sx,sy=int(ssx/2),int(ssy/1.6)
#for ui scaling on different resolutions
def getscaledsize(side,num):
    return int(sx*(num/900) if side=="y" else sy*(num/650))
#for applying styles, on launch and settings change
def changeSetting(setting,newval):
    global settings
    settings = json.load(open("settings.json","r"))
    settings[setting]=newval
    with open("settings.json","w") as f:
        json.dump(settings,f)
#setup settings
for setting in defaultsettings:
    if not setting in settings:
        changeSetting(setting,defaultsettings[setting])

def ApplyStyle(style):
    stylepath = "./Themes/"+style+".txt"
    if os.path.exists(stylepath)==True:
        StyleSheet = open(stylepath,"r").read()
        app.setStyleSheet(StyleSheet)
        changeSetting("theme",style)
    else:
        msgbox = QMessageBox()
        msgbox.setText("⚠ Warning!")
        msgbox.setWindowTitle(wtitle)
        msgbox.setWindowIcon(wicon)
        msgbox.setInformativeText("Style \""+style+"\" doesnt exist in Themes folder! No style has been applied. It's recommended that you change the style in settings!")
        msgbox.setStandardButtons(QMessageBox.Ok)
        msgbox.exec()
ApplyStyle(settings["theme"])

win.move(int((ssx/2)-(sx/2)-(getscaledsize("x",100)/2)),int((ssy/2)-(sy/2)-(getscaledsize("y",50)/2)))
win.setFixedSize(sx+getscaledsize("x",100),sy+getscaledsize("y",100))
#LAYOUTING 🔥🔥🔥🔥🔥🔥🔥🔥
class Layouting:
    def __init__(self):
        self.layouts={}
        self.widgets={}
        self.listitems={}
        with open("notes.json","r") as f:
            self.listitems = json.load(f)
    #RENDER ALL EXISTING NOTES
    def showALLnotes(self,tag):
        self.widgets["listw"].clear()
        textl.setText("List of Notes"+(" (with tag \""+tag+"\")" if tag!="" else ""))
        for thing in self.listitems:
            tagFound = False
            if not "tags" in self.listitems[thing]:
                self.listitems[thing]["tags"]=[]
            for ctag in self.listitems[thing]["tags"]:
                tagFound = True if ctag.find(tag)!=-1 else False
            if tagFound or tag=="":
                self.addtoList(self.listitems[thing]["name"],self.listitems[thing]["savedtext"],self.listitems[thing]["tags"])
    #LAYOUT/WIDGET STUFF
    def addLayout(self,st):
        self.layouts[st["name"]]=st["layout"]
        return st["layout"]
    def addWidget(self,st):
        self.widgets[st["name"]]=st["widget"]
        if st["layout"]:
            self.layouts[st["layout"]].addWidget(st["widget"])
        return st["widget"]
    #LIST AND NOTE STUFF
    def savelist(self):
        with open("notes.json","w") as f:
            json.dump(self.listitems,f)

    def noteExists(self,txt):
        return True if txt in self.listitems else False
    
    def addtoList(self,txt,note,tags):
        listitem = self.widgets["listw"].addItem(txt)
        self.listitems[txt]={"obj":listitem,"name":txt,"savedtext":note,"tags":tags}
        self.savelist()

    def savetoList(self,txt,tosave):
        self.listitems[txt]["savedtext"]=tosave
        self.savelist()

    def returnNote(self,txt):
        return self.listitems[txt]["savedtext"] or ""

    def removefromList(self,item):
        noteName = item.text()
        self.listitems.pop(noteName)
        self.widgets["listw"].takeItem(self.widgets["listw"].row(item))
        textbox.setText("")
        self.savelist()

    def renameItem(self,item,newname):
        #remove old val
        oldval = self.listitems[item.text()]
        self.listitems.pop(item.text())
        #modify new val
        oldval["name"]=newname
        self.listitems[newname]=oldval

        item.setText(newname)
        BFuncs.changeChosenItem(None)
        textbox.setText("")
        self.showALLnotes(linee3.text())
        self.savelist()
    #tags
    def addTag(self,item,tag):
        if not tag in self.listitems[item.text()]["tags"]:
            self.listitems[item.text()]["tags"].append(tag)
            self.redrawTags(item)
    
    def removeTag(self,item,tag):
        if tag in self.listitems[item.text()]["tags"]:
            self.listitems[item.text()]["tags"].remove(tag)
            self.redrawTags(item)

    def redrawTags(self,item):
        taglist.clear()
        if item!=None:
            for tag in self.listitems[item.text()]["tags"]:
                tagitem = taglist.addItem(tag)

LT = Layouting()
# FUNCTIONS
class ButtonFunctions:
    def __init__(self):
        self.chosenItem = None

    def updateEditingText(self,newitem):
        lettercount = " ("+str(len(textbox.toPlainText()))+" letters)" if settings["lettercount"] else ""
        currenttext.setText("Currently Editing: "+(newitem.text()+lettercount if newitem!=None else "???"))

    def changeChosenItem(self,newitem):
        self.chosenItem = newitem
        textbox.setText("" if not newitem else LT.returnNote(self.chosenItem.text()))
        self.updateEditingText(newitem)
        listw.setCurrentItem(newitem)#visual selection:D
        LT.redrawTags(self.chosenItem)

    def listItemDoubleClicked(self,item):
        self.changeChosenItem(item)
        text,yuhhuh = QInputDialog.getText(win,"Smart Notes","Enter a new name for the note:",text=item.text())
        if text and yuhhuh:
            if LT.noteExists(text):
                msgbox = QMessageBox()
                msgbox.setText("⚠ Watch out!")
                msgbox.setWindowTitle(wtitle)
                msgbox.setWindowIcon(wicon)
                msgbox.setInformativeText("You were about to rename a note to a name that's already used!")
                msgbox.setStandardButtons(QMessageBox.Ok)
                msgbox.exec()
            else:
                LT.renameItem(item,text)
    def getItemFromText(self,text):
        items = listw.findItems(text,Qt.MatchExactly)
        itemtoreturn = None
        if len(items) > 0:
            for item in items:
                itemtoreturn = item

        return itemtoreturn

    def b11func(self):#CREATE NOTE
        text,yuhhuh = QInputDialog.getText(win,"Smart Notes","Enter a name for the note:")
        if text and yuhhuh:
            if LT.noteExists(text):
                msgbox = QMessageBox()
                msgbox.setText("⚠ Watch out!")
                msgbox.setWindowTitle(wtitle)
                msgbox.setWindowIcon(wicon)
                msgbox.setInformativeText("You were about to create a note with a name that's already used!")
                msgbox.setStandardButtons(QMessageBox.Ok)
                msgbox.exec()
            else:
                LT.addtoList(text,settings["starttext"],[])
                item = self.getItemFromText(text)
                self.changeChosenItem(item)

    def b12func(self):#DELETE NOTE
        if self.chosenItem!=None:
            msgbox = QMessageBox()
            msgbox.setText("⚠ Confirm deletion")
            msgbox.setWindowTitle(wtitle)
            msgbox.setWindowIcon(wicon)
            msgbox.setInformativeText("Are you sure you want to permanently delete this note?")
            msgbox.setStandardButtons(QMessageBox.Yes | QMessageBox.Cancel)
            result = msgbox.exec()
            if result==QMessageBox.Yes:
                oldrow = listw.row(self.chosenItem)#starts from 0 :/
                LT.removefromList(self.chosenItem)
                newitem = listw.item(oldrow-1) if oldrow-1>=0 else None#selects previous note if possible
                self.changeChosenItem(newitem)

    def b1func(self):#SAVE NOTE (USED BY TEXT CHANGE NOW)
        if self.chosenItem!=None:
            tbText = textbox.toPlainText()
            noteName = self.chosenItem.text() #breaks when item isnt in the widget
            if tbText!="":#turns out that prevents delete note crash
                self.updateEditingText(self.chosenItem)
                LT.savetoList(noteName,tbText)

    def b21func(self):#ADD TAG
        if self.chosenItem!=None and linee3.text()!="":
            LT.addTag(self.chosenItem,linee3.text())

    def b22func(self):#REMOVE TAG
        if self.chosenItem!=None and linee3.text()!="":
            LT.removeTag(self.chosenItem,linee3.text())

    def b2func(self):#SHOW NOTES BY TAG
        self.changeChosenItem(None)#prevents crashing
        LT.showALLnotes(linee3.text())

    def settings_style(self,item):
        textslc.setText("Chosen Style: "+item.text())
        ApplyStyle(item.text())
    def b3func(self):#TODO SETTINGS BUTTON
        #update style stuff
        stylelist.clear()
        themesavailable = os.listdir("./Themes")
        for theme in themesavailable:
            modifiedname = theme[0:len(theme)-4]
            stylelist.addItem(modifiedname)

        settingswin.show()
BFuncs = ButtonFunctions()

#MAIN UI 🔥🔥🔥
BigHoriz = LT.addLayout({"layout":QHBoxLayout(win),"name":"BigHoriz1"})
BigHoriz.addStretch() # ---
#1st bighoriz
BiggerVert = LT.addLayout({"layout":QVBoxLayout(win),"name":"BiggerVert"})
BigHoriz.addLayout(BiggerVert)
BiggerVert.addStretch() # ---

currenttext = LT.addWidget({"widget":QLabel(win),"name":"currenttext","layout":"BiggerVert"})
currenttext.setText("Currently Editing: ???")
currenttext.setWordWrap(True)

textbox = LT.addWidget({"widget":QTextEdit(win),"name":"textbox","layout":"BiggerVert"})
textbox.setFixedSize(int(sx/2),int(sy))
textbox.textChanged.connect(BFuncs.b1func)#autosave

BiggerVert.addStretch() # ---
#2nd part of bighoriz
#title, input, smalled input, h
BigVert = LT.addLayout({"layout":QVBoxLayout(win),"name":"BigVert"})
BigHoriz.addLayout(BigVert)
BigVert.addStretch() # ---

textl = LT.addWidget({"widget":QLabel(win),"name":"textl","layout":"BigVert"})
textl.setText("List of Notes")

listw = LT.addWidget({"widget":QListWidget(win),"name":"listw","layout":"BigVert"})
listw.setFixedSize(int((sx/2)+getscaledsize("x",25)),getscaledsize("y",200))
listw.itemClicked.connect(BFuncs.changeChosenItem) # get note
listw.itemDoubleClicked.connect(BFuncs.listItemDoubleClicked) # prompt rename

#2b
SmallHoriz = LT.addLayout({"layout":QHBoxLayout(win),"name":"SmallHoriz"})
BigVert.addLayout(SmallHoriz)
SmallHoriz.addStretch() # ---

b11 = LT.addWidget({"widget":QPushButton(win),"name":"b11","layout":"SmallHoriz"})
b11.setText("Create Note")
b11.setFixedSize(int(sx/4)+getscaledsize("x",10),getscaledsize("y",25))
b12 = LT.addWidget({"widget":QPushButton(win),"name":"b12","layout":"SmallHoriz"})
b12.setText("Delete Selected Note")
b12.setFixedSize(int(sx/4)+getscaledsize("x",10),getscaledsize("y",25))
#b
"""b1 = LT.addWidget({"widget":QPushButton(win),"name":"b1","layout":"BigVert"})
b1.setText(":3 doesnt work XD")
b1.setFixedSize(int(sx/2)+getscaledsize("x",25),getscaledsize("y",25))"""
SmallHoriz.addStretch() # ---

#title + input
textl2 = LT.addWidget({"widget":QLabel(win),"name":"textl2","layout":"BigVert"})
textl2.setText("List of Tags")

taglist = LT.addWidget({"widget":QListWidget(win),"name":"taglist","layout":"BigVert"})
taglist.setFixedSize(int(sx/2)+getscaledsize("x",25),getscaledsize("y",200))
#small input
linee3 = LT.addWidget({"widget":QLineEdit(win),"name":"linee3","layout":"BigVert"})
linee3.setFixedSize(int(sx/2)+getscaledsize("x",25),getscaledsize("y",30))
linee3.setPlaceholderText("Enter a Tag...")

#2b
SmallHoriz2 = LT.addLayout({"layout":QHBoxLayout(win),"name":"SmallHoriz2"})
BigVert.addLayout(SmallHoriz2)
SmallHoriz2.addStretch() # ---

b21 = LT.addWidget({"widget":QPushButton(win),"name":"b21","layout":"SmallHoriz2"})
b21.setText("Add to the Note")
b21.setFixedSize(int(sx/4)+getscaledsize("x",10),getscaledsize("y",25))
b22 = LT.addWidget({"widget":QPushButton(win),"name":"b22","layout":"SmallHoriz2"})
b22.setText("Remove from the Note")
b22.setFixedSize(int(sx/4)+getscaledsize("x",10),getscaledsize("y",25))
#b
b2 = LT.addWidget({"widget":QPushButton(win),"name":"b2","layout":"BigVert"})
b2.setText("Search Notes by Tag")
b2.setFixedSize(int(sx/2)+getscaledsize("x",25),getscaledsize("y",25))
SmallHoriz2.addStretch() # ---

#settings button
SmallHoriz3 = LT.addLayout({"layout":QHBoxLayout(win),"name":"SmallHoriz3"})
BigVert.addLayout(SmallHoriz3)
SmallHoriz3.addStretch() # ---

b3 = LT.addWidget({"widget":QPushButton(win),"name":"b21","layout":"SmallHoriz3"})
b3.setText("⚙Settings")
b3.setFixedSize(int(sx/4)+getscaledsize("x",10),getscaledsize("y",25))

SmallHoriz3.addStretch() # ---
BigHoriz.addStretch() # ---

#SETTINGS UI ⚙⚙⚙
settingswin.setWindowTitle(wtitle+" - Settings")
settingswin.setWindowIcon(wicon)

settingswin.move(int((ssx/2)-(sx/4)),int((ssy/2)-(sy/2)))
settingswin.setFixedSize(int(sx/2),int(sy/1.75))

BVert1 = LT.addLayout({"layout":QVBoxLayout(settingswin),"name":"BVert1"})
#BigVert.addLayout(SmallHoriz2)
BVert1.addStretch() # ---
#style list
textsl = LT.addWidget({"widget":QLabel(win),"name":"textsl","layout":"BVert1"})
textsl.setText("List of Styles")

stylelist = LT.addWidget({"widget":QListWidget(win),"name":"stylelist","layout":"BVert1"})
stylelist.setFixedSize(int(sx/2)-getscaledsize("x",25),getscaledsize("y",200))
stylelist.itemClicked.connect(BFuncs.settings_style)

textslc = LT.addWidget({"widget":QLabel(win),"name":"textslc","layout":"BVert1"})
textslc.setText("Chosen Style: "+settings["theme"])

sizetoggle = LT.addWidget({"widget":QCheckBox(win),"name":"sizetoggle","layout":"BVert1"})
sizetoggle.setText("Toggle letters counter while editing.")
sizetoggle.setChecked(settings["lettercount"])
sizetoggle.stateChanged.connect(lambda: changeSetting("lettercount",sizetoggle.isChecked()))

starttextlabel = LT.addWidget({"widget":QLabel(win),"name":"starttextlabel","layout":"BVert1"})
starttextlabel.setText("Starting Note Text (on creation):")

starttextedit = LT.addWidget({"widget":QLineEdit(win),"name":"starttextedit","layout":"BVert1"})
starttextedit.setFixedSize(int(sx/2)-getscaledsize("x",25),getscaledsize("y",30))
starttextedit.setPlaceholderText("...")
starttextedit.setText(settings["starttext"])
starttextedit.textChanged.connect(lambda: changeSetting("starttext",starttextedit.text()))

BVert1.addStretch() # ---
# CONNECT FUNCTIONS
b11.clicked.connect(BFuncs.b11func)
b12.clicked.connect(BFuncs.b12func)
#b1.clicked.connect(BFuncs.b1func)
b21.clicked.connect(BFuncs.b21func)
b22.clicked.connect(BFuncs.b22func)
b2.clicked.connect(BFuncs.b2func)
b3.clicked.connect(BFuncs.b3func)

LT.showALLnotes("")

BigVert.addStretch() # ---

#RUN
win.show()
app.exec_()