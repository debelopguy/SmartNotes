# NOTES BY DEBEBOPMENT
from PyQt5.QtCore import *
from PyQt5.QtWidgets import *
from PyQt5.QtGui import *
from random import*
import json,os
from pypresence import Presence

client_id = "1375778718940790874"
RPC = Presence(client_id,pipe=0)  # Initialize the client class
RPCConnected = False
try:
    RPC.connect() # Start the handshake loop
    RPCConnected = True
except:
    print("RPC FAILED TO CONNECT")

#UI
app = QApplication([])
win = QWidget()
settingswin = QWidget()

#loading files
notes = open("notes.json","r")
settings = json.load(open("settings.json","r"))
defaultsettings = {
    "theme":"Default",
    "lettercount":False,
    "starttext":"",
    "rpc":False,
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
#RPC
def UpdateRPC(Idling: bool):
    if settings["rpc"] and RPCConnected:
        if Idling:
            RPC.update(state="Idle")  # Set the presence
        else:
            RPC.update(state="Editing",details="a note with "+str(len(NoteTextBox.toPlainText()))+" letters")
UpdateRPC(True)
#UI & BUTTON FUNCTIONS
class SNFuncs:
    def __init__(self):
        self.layouts={}
        self.widgets={}
        self.listitems={}

        self.chosenItem = None
        self.chosenTagText = None

        with open("notes.json","r") as f:
            self.listitems = json.load(f)
    #RENDER ALL EXISTING NOTES
    def showALLnotes(self,tag):
        #no tag entered get it from selected
        if tag == "" and self.chosenTagText:
            tag = self.chosenTagText
            self.chosenTagText = None

        self.widgets["ListOfNotes"].clear()
        ListOfNotesLabel.setText("List of Notes"+(" (with tag \""+tag+"\")" if tag!="" else ""))
        for thing in self.listitems:
            #tag specific render
            tagFound = False
            if not "tags" in self.listitems[thing]:
                self.listitems[thing]["tags"]=[]
            for currentTag in self.listitems[thing]["tags"]:
                lowerCurrentTag,lowerTag = currentTag.lower(),tag.lower()

                tagFound = (lowerCurrentTag == lowerTag or lowerCurrentTag.find(lowerTag)!=-1)
                if tagFound:
                    break
            #show note here
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
        listitem = self.widgets["ListOfNotes"].addItem(txt)
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
        self.widgets["ListOfNotes"].takeItem(self.widgets["ListOfNotes"].row(item))
        NoteTextBox.setText("")
        self.savelist()

    def renameItem(self,item,newname):
        #remove old val
        oldval = self.listitems[item.text()]
        self.listitems.pop(item.text())
        #modify new val
        oldval["name"]=newname
        self.listitems[newname]=oldval

        item.setText(newname)
        SN.changeChosenItem(None)
        NoteTextBox.setText("")
        self.showALLnotes(TagTextBox.text())
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

    def changeChosenTag(self,newitem):
        self.chosenTagText = newitem.text()
    
    #other stuff
    def updateEditingText(self,newitem):
        lettercount = " ("+str(len(NoteTextBox.toPlainText()))+" letters)" if settings["lettercount"] else ""
        CurrentEditingLabel.setText("Currently Editing: "+(newitem.text()+lettercount if newitem!=None else "???"))

    def changeChosenItem(self,newitem):
        self.chosenItem = newitem
        NoteTextBox.setText("" if not newitem else SN.returnNote(self.chosenItem.text()))
        self.updateEditingText(newitem)
        ListOfNotes.setCurrentItem(newitem)#visual selection:D
        SN.redrawTags(self.chosenItem)
        UpdateRPC(False)

    def listItemDoubleClicked(self,item):
        self.changeChosenItem(item)
        text,yuhhuh = QInputDialog.getText(win,"Smart Notes","Enter a new name for the note:",text=item.text())
        if text and yuhhuh:
            if SN.noteExists(text):
                msgbox = QMessageBox()
                msgbox.setText("⚠ Watch out!")
                msgbox.setWindowTitle(wtitle)
                msgbox.setWindowIcon(wicon)
                msgbox.setInformativeText("You were about to rename a note to a name that's already used!")
                msgbox.setStandardButtons(QMessageBox.Ok)
                msgbox.exec()
            else:
                SN.renameItem(item,text)
    def getItemFromText(self,text):
        items = ListOfNotes.findItems(text,Qt.MatchExactly)
        itemtoreturn = None
        if len(items) > 0:
            for item in items:
                itemtoreturn = item

        return itemtoreturn

    def CreateNewNoteWithPrompt(self):#CREATE NOTE
        text,yuhhuh = QInputDialog.getText(win,"Smart Notes","Enter a name for the note:")
        if text and yuhhuh:
            if SN.noteExists(text):
                msgbox = QMessageBox()
                msgbox.setText("⚠ Watch out!")
                msgbox.setWindowTitle(wtitle)
                msgbox.setWindowIcon(wicon)
                msgbox.setInformativeText("You were about to create a note with a name that's already used!")
                msgbox.setStandardButtons(QMessageBox.Ok)
                msgbox.exec()
            else:
                SN.addtoList(text,settings["starttext"],[])
                item = self.getItemFromText(text)
                self.changeChosenItem(item)

    def DeleteNoteWithPrompt(self):#DELETE NOTE
        if self.chosenItem!=None:
            msgbox = QMessageBox()
            msgbox.setText("⚠ Confirm deletion")
            msgbox.setWindowTitle(wtitle)
            msgbox.setWindowIcon(wicon)
            msgbox.setInformativeText("Are you sure you want to permanently delete this note?")
            msgbox.setStandardButtons(QMessageBox.Yes | QMessageBox.Cancel)
            result = msgbox.exec()
            if result==QMessageBox.Yes:
                oldrow = ListOfNotes.row(self.chosenItem)#starts from 0 :/
                SN.removefromList(self.chosenItem)
                newitem = ListOfNotes.item(oldrow-1) if oldrow-1>=0 else None#selects previous note if possible
                self.changeChosenItem(newitem)

    def SaveNoteContents(self):#SAVE NOTE (USED BY TEXT CHANGE NOW)
        if self.chosenItem!=None:
            tbText = NoteTextBox.toPlainText()
            noteName = self.chosenItem.text() #breaks when item isnt in the widget
            if tbText!="":#turns out that prevents delete note crash
                self.updateEditingText(self.chosenItem)
                SN.savetoList(noteName,tbText)

    def AddTagToNote(self):#ADD TAG
        if self.chosenItem!=None and TagTextBox.text()!="":
            SN.addTag(self.chosenItem,TagTextBox.text())

    def RemoveTagFromNote(self):#REMOVE TAG
        if self.chosenItem!=None and TagTextBox.text()!="":
            SN.removeTag(self.chosenItem,TagTextBox.text())

    def ShowNotesWithTag(self):#SHOW NOTES BY TAG
        self.changeChosenItem(None)#prevents crashing
        SN.showALLnotes(TagTextBox.text())
    
    #SETTINGS STUFF
    def settings_style(self,item):
        SelectedStyleLabel.setText("Chosen Style: "+item.text())
        ApplyStyle(item.text())

    def ShowSettingsWindow(self):#TODO SETTINGS BUTTON
        #update style stuff
        stylelist.clear()
        themesavailable = os.listdir("./Themes")
        for theme in themesavailable:
            if theme.endswith(".txt"):
                modifiedname = theme[0:len(theme)-4]
                stylelist.addItem(modifiedname)

        win.hide()
        settingswin.show()

    def ShowMainWindow(self):
        win.show()
        settingswin.hide()

    def FindMatchingTextWithPrompt(self):
        text,yuhhuh = QInputDialog.getText(win,wtitle+" - Find Matching Text","Enter text to find:")
        if text and yuhhuh:
            cursor = NoteTextBox.textCursor()
            cursor.setPosition(0)
            NoteTextBox.setTextCursor(cursor)
            findResult = NoteTextBox.find(text)

#do the rest here
SN = SNFuncs()

#MAIN UI 🔥🔥🔥
BigHoriz = SN.addLayout({"layout":QHBoxLayout(win),"name":"BigHoriz1"})
BigHoriz.addStretch() # ---
#1st bighoriz
BiggerVert = SN.addLayout({"layout":QVBoxLayout(win),"name":"BiggerVert"})
BigHoriz.addLayout(BiggerVert)
BiggerVert.addStretch() # ---

CurrentEditingLabel = SN.addWidget({"widget":QLabel(win),"name":"CurrentEditingLabel","layout":"BiggerVert"})
CurrentEditingLabel.setText("Currently Editing: ???")
CurrentEditingLabel.setWordWrap(True)

NoteTextBox = SN.addWidget({"widget":QTextEdit(win),"name":"NoteTextBox","layout":"BiggerVert"})
NoteTextBox.setFixedSize(int(sx/2),int(sy))
NoteTextBox.textChanged.connect(SN.SaveNoteContents)#autosave

BiggerVert.addStretch() # ---
#2nd part of bighoriz
#title, input, smalled input, h
BigVert = SN.addLayout({"layout":QVBoxLayout(win),"name":"BigVert"})
BigHoriz.addLayout(BigVert)
BigVert.addStretch() # ---

ListOfNotesLabel = SN.addWidget({"widget":QLabel(win),"name":"ListOfNotesLabel","layout":"BigVert"})
ListOfNotesLabel.setText("List of Notes")

ListOfNotes = SN.addWidget({"widget":QListWidget(win),"name":"ListOfNotes","layout":"BigVert"})
ListOfNotes.setFixedSize(int((sx/2)+getscaledsize("x",25)),getscaledsize("y",200))
ListOfNotes.itemClicked.connect(SN.changeChosenItem) # get note
ListOfNotes.itemDoubleClicked.connect(SN.listItemDoubleClicked) # prompt rename

#2b
SmallHoriz = SN.addLayout({"layout":QHBoxLayout(win),"name":"SmallHoriz"})
BigVert.addLayout(SmallHoriz)
SmallHoriz.addStretch() # ---

CreateNoteButton = SN.addWidget({"widget":QPushButton(win),"name":"CreateNoteButton","layout":"SmallHoriz"})
CreateNoteButton.setText("Create Note")
CreateNoteButton.setFixedSize(int(sx/4)+getscaledsize("x",10),getscaledsize("y",25))
DeleteNoteButton = SN.addWidget({"widget":QPushButton(win),"name":"DeleteNoteButton","layout":"SmallHoriz"})
DeleteNoteButton.setText("Delete Selected Note")
DeleteNoteButton.setFixedSize(int(sx/4)+getscaledsize("x",10),getscaledsize("y",25))
#b
SmallHoriz.addStretch() # ---

#title + input
ListOfNotesLabel2 = SN.addWidget({"widget":QLabel(win),"name":"ListOfNotesLabel2","layout":"BigVert"})
ListOfNotesLabel2.setText("List of Tags")

taglist = SN.addWidget({"widget":QListWidget(win),"name":"taglist","layout":"BigVert"})
taglist.setFixedSize(int(sx/2)+getscaledsize("x",25),getscaledsize("y",200))
taglist.itemClicked.connect(SN.changeChosenTag) # change chosen tag for qol
#small input
TagTextBox = SN.addWidget({"widget":QLineEdit(win),"name":"TagTextBox","layout":"BigVert"})
TagTextBox.setFixedSize(int(sx/2)+getscaledsize("x",25),getscaledsize("y",30))
TagTextBox.setPlaceholderText("Enter a Tag...")

#2b
SmallHoriz2 = SN.addLayout({"layout":QHBoxLayout(win),"name":"SmallHoriz2"})
BigVert.addLayout(SmallHoriz2)
SmallHoriz2.addStretch() # ---

AddTagButton = SN.addWidget({"widget":QPushButton(win),"name":"AddTagButton","layout":"SmallHoriz2"})
AddTagButton.setText("Add to the Note")
AddTagButton.setFixedSize(int(sx/4)+getscaledsize("x",10),getscaledsize("y",25))
RemoveTagButton = SN.addWidget({"widget":QPushButton(win),"name":"RemoveTagButton","layout":"SmallHoriz2"})
RemoveTagButton.setText("Remove from the Note")
RemoveTagButton.setFixedSize(int(sx/4)+getscaledsize("x",10),getscaledsize("y",25))
#b
ShowNotesWithTagButton = SN.addWidget({"widget":QPushButton(win),"name":"ShowNotesWithTagButton","layout":"BigVert"})
ShowNotesWithTagButton.setText("Search Notes by Tag")
ShowNotesWithTagButton.setFixedSize(int(sx/2)+getscaledsize("x",25),getscaledsize("y",25))
SmallHoriz2.addStretch() # ---

#settings button
SmallHoriz3 = SN.addLayout({"layout":QHBoxLayout(win),"name":"SmallHoriz3"})
BigVert.addLayout(SmallHoriz3)
SmallHoriz3.addStretch() # ---

ShowSettingsWindowButton = SN.addWidget({"widget":QPushButton(win),"name":"AddTagButton","layout":"SmallHoriz3"})
ShowSettingsWindowButton.setText("⚙Settings")
ShowSettingsWindowButton.setFixedSize(int(sx/4)+getscaledsize("x",10),getscaledsize("y",25))

SmallHoriz3.addStretch() # ---
BigHoriz.addStretch() # ---

#SETTINGS UI ⚙⚙⚙
settingswin.setWindowTitle(wtitle+" - Settings")
settingswin.setWindowIcon(wicon)

settingswin.move(int((ssx/2)-(sx/4)),int((ssy/2)-(sy/2)))
settingswin.setFixedSize(int(sx/2),int(sy/1.5))

BVert1 = SN.addLayout({"layout":QVBoxLayout(settingswin),"name":"BVert1"})
#BigVert.addLayout(SmallHoriz2)
BVert1.addStretch() # ---
#return to main button
ReturnToMainWindowButton = SN.addWidget({"widget":QPushButton(win),"name":"ReturnToMainWindowButton","layout":"BVert1"})
ReturnToMainWindowButton.setText("Return to "+wtitle)
ReturnToMainWindowButton.setFixedSize(int(sx/2)-getscaledsize("x",25),getscaledsize("y",25))
#style list
textsl = SN.addWidget({"widget":QLabel(win),"name":"textsl","layout":"BVert1"})
textsl.setText("List of Styles")

stylelist = SN.addWidget({"widget":QListWidget(win),"name":"stylelist","layout":"BVert1"})
stylelist.setFixedSize(int(sx/2)-getscaledsize("x",25),getscaledsize("y",200))
stylelist.itemClicked.connect(SN.settings_style)

SelectedStyleLabel = SN.addWidget({"widget":QLabel(win),"name":"SelectedStyleLabel","layout":"BVert1"})
SelectedStyleLabel.setText("Chosen Style: "+settings["theme"])

sizetoggle = SN.addWidget({"widget":QCheckBox(win),"name":"sizetoggle","layout":"BVert1"})
sizetoggle.setText("Toggle letters counter while editing.")
sizetoggle.setChecked(settings["lettercount"])
sizetoggle.stateChanged.connect(lambda: changeSetting("lettercount",sizetoggle.isChecked()))

StartingNoteTextLabel = SN.addWidget({"widget":QLabel(win),"name":"StartingNoteTextLabel","layout":"BVert1"})
StartingNoteTextLabel.setText("Starting Note Text (on creation):")

starttextedit = SN.addWidget({"widget":QLineEdit(win),"name":"starttextedit","layout":"BVert1"})
starttextedit.setFixedSize(int(sx/2)-getscaledsize("x",25),getscaledsize("y",30))
starttextedit.setPlaceholderText("...")
starttextedit.setText(settings["starttext"])
starttextedit.textChanged.connect(lambda: changeSetting("starttext",starttextedit.text()))

rpctoggle = SN.addWidget({"widget":QCheckBox(win),"name":"rpctoggle","layout":"BVert1"})
rpctoggle.setText("Toggle Discord Rich Presence.")
rpctoggle.setChecked(settings["rpc"])
rpctoggle.stateChanged.connect(lambda: changeSetting("rpc",rpctoggle.isChecked()))

BVert1.addStretch() # ---
# CONNECT FUNCTIONS
CreateNoteButton.clicked.connect(SN.CreateNewNoteWithPrompt)
DeleteNoteButton.clicked.connect(SN.DeleteNoteWithPrompt)
#b1.clicked.connect(SN.SaveNoteContents)
AddTagButton.clicked.connect(SN.AddTagToNote)
RemoveTagButton.clicked.connect(SN.RemoveTagFromNote)
ShowNotesWithTagButton.clicked.connect(SN.ShowNotesWithTag)
ShowSettingsWindowButton.clicked.connect(SN.ShowSettingsWindow)
ReturnToMainWindowButton.clicked.connect(SN.ShowMainWindow)

SN.showALLnotes("")

BigVert.addStretch() # ---

#shortcuts
FindWordsShortcut = QShortcut('Ctrl+F',win,SN.FindMatchingTextWithPrompt)

#RUN
win.show()
app.exec_()