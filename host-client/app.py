import tkinter as tk
from threading import *
import random
import time
import ctypes

from host import *

bgC = "#242424"
bgC2 = "#575a61"
fgC = "#f3f3f3"
b = "#09fa9a"

attendanceTime = 10

def fromRgb(rgb):
    return "#%02x%02x%02x" % rgb  

class ColorAnimation(Thread):
    def run(self):
        while(True):
            r = 9
            g = 250
            b = 153
            while (r < 255 or g < 255 or b < 255):
                global canvas
                global root
                global Title1Frame
                canvas.configure(bg=fromRgb((r,g,b)))
                canvas.configure(highlightbackground=fromRgb((r,g,b)))
                root.configure(background=fromRgb((r,g,b)))
                TitleCanvas.configure(bg=fromRgb((r,g,b)))
                TitleCanvas.configure(highlightbackground=fromRgb((r,g,b)))
                r = min(r + 1, 255)
                g = min(g + 1, 255)
                b = min(b + 1, 255)
                time.sleep(0.005)
            while (r > 9 or g > 250 or b > 153):
                canvas.configure(bg=fromRgb((r,g,b)))
                canvas.configure(highlightbackground=fromRgb((r,g,b)))
                root.configure(background=fromRgb((r,g,b)))
                TitleCanvas.configure(bg=fromRgb((r,g,b)))
                TitleCanvas.configure(highlightbackground=fromRgb((r,g,b)))
                r = max(r - 1, 9)
                g = max(g - 1, 250)
                b = max(b - 1, 153)
                time.sleep(0.005)

class Driver(Thread):

    def run(self):
        count = 0
        while(True):
            if (count >= attendanceTime):
                global maxa
                maxa += 1
                # attendanceList = ##Get Attendance ex: ["Seth", "Max", "Quinn"]
                # save curr students attending to attendanceList
                attendanceList = take_attendance(webdriver)
                totalStudents.set(str(len(attendanceList)))
                room.updateAttendance(attendanceList)
                updateTable()
                count = 0
            global maxp
            maxp +=1
            # handsList = ##Get list of students with hands raised ex: ["Seth", "Max"]
            # save ppl with hands raised to handsList
            handsList = who_participates(webdriver)
            raisedHands.set(len(handsList))
            room.updateParticipation(handsList)
            time.sleep(1)
            count += 1

def updateTable():
    studentTable.delete(0, tk.END)
    for i in range(len(room.students)):
        global maxa
        global maxp
        if (maxa == 0 or maxp == 0):
            studentTable.insert(0, "")
            studentTable.insert(0, "")
            studentTable.insert(0, room.students[i].name)
            
        else:
            studentTable.insert(0, "")
            studentTable.insert(0, "Participation Score: " + str(int(100 * room.students[i].pscore/maxp)) + "%")
            studentTable.insert(0, "Attendance Percentage: " + str(int( 100 * room.students[i].ascore/maxa)) + "%")
            studentTable.insert(0, room.students[i].name)
            

def handleInsert():
    table.insert(0, inputVal.get() + " | hands: " + raisedHands.get())


class Student():
    def __init__(self, name):
        #Participation
        self.pscore = 0
        self.ascore = 0
        self.name = name

class Room():
    def __init__(self):
        self.students = []

    def updateParticipation(self, list):
        for i in range(len(list)):
            studentFound = False
            for j in range(len(self.students)):
                if (self.students[j].name == list[i]):
                    studentFound = True
                    self.students[j].pscore = self.students[j].pscore + 1
                    break
            if (studentFound == False):
                self.students.append(Student(list[i]))
    
    def updateAttendance(self, list):
        for i in range(len(list)):
            studentFound = False
            for j in range(len(self.students)):
                if (self.students[j].name == list[i]):
                    studentFound = True
                    self.students[j].ascore = self.students[j].ascore + 1
                    break
            if (studentFound == False):
                self.students.append(Student(list[i]))

room = Room()

def timeFunc():
    global attendanceTime
    attendanceTime = int(timeInputVal.get())
    print(attendanceTime)

def setCCFunc():
    #Spot for Tilden
    print("not implemented")

def main():
    global maxa
    maxa= 0
    global maxp
    maxp = 0

    # get selenium data collector going
    # set launch options
    room_link = "https://virginia.zoom.us/j/312504706"
    headless = True
    # declare webdriver to store chrome driver
    global webdriver
    # launch and store it (with the selected options)
    webdriver = launch(room_link, headless)
    
    #GUI
    global root
    root = tk.Tk()
    root.title("Zoom Manager")
    root.configure(background=b)
    global canvas
    canvas = tk.Canvas(root, highlightbackground=b, height=1000, width=200, bg=b)
    canvas.pack()

    
    #Title1Frame
    global TitleCanvas
    Title1Frame = tk.Frame(root, bg=b)
    Title1Frame.place(width=200, height=100, x=2, y=0)
    TitleCanvas = tk.Canvas(Title1Frame, highlightbackground=b, bg=b, width = 200, height = 100)      
    TitleCanvas.pack()      
    img = tk.PhotoImage(file="assets/logo.png")      
    TitleCanvas.create_image(1,1, anchor=tk.NW, image=img)
    
    #HandRaisedFrame
    global raisedHands
    raisedHands = tk.StringVar()
    HRFrame = tk.Frame(root, bg=bgC)
    HRFrame.place(width=200, height=200, x=2, y=100)
    raisedHands.set(10)
    HRLabel = tk.Label(HRFrame, text="Number of Raised Hands", fg=fgC, bg=bgC, font=("Helvetica", 15)).pack(fill=tk.X, pady=10)
    HRLabelVal = tk.Label(HRFrame, textvariable=raisedHands, fg=fgC, bg=bgC, font=("Helvetica", 30)).pack(fill=tk.X)
    HRLogLabel = tk.Label(HRFrame, text="Log number:", fg=fgC, bg=bgC, font=("Helvetica", 10)).pack(fill=tk.X, pady=5)
    InputHRFrame = tk.Frame(HRFrame, bg=bgC)
    InputHRFrame.pack(fill=tk.X, padx=10, pady=1)
    global inputVal
    inputVal = tk.StringVar()
    inputBox = tk.Entry(InputHRFrame, bg=bgC, width = 10, textvariable = inputVal, fg=fgC, font=("Helvetica", 16))
    inputBox.pack(padx=5, side=tk.LEFT)
    func = lambda: table.insert(0, inputVal.get() + " | hands: " + raisedHands.get())
    photo = tk.PhotoImage(file = "assets/plus.png") 
    insertButton = tk.Button(InputHRFrame, highlightbackground="black", height=30, width=30, image=photo, command = func).pack()

    global table
    table = tk.Listbox(HRFrame, borderwidth=0, fg=fgC, bg=bgC2, font=("Helvetica", 12))
    table.pack(fill=tk.X, padx=10, pady=10)


    #StudentsFrame
    global totalStudents
    totalStudents = tk.StringVar()
    totalStudents.set(0) # changed default num of students to 0 (starting value, updates)
    SFrame = tk.Frame(root, bg=bgC)
    SFrame.place(width=200, height=300, x=2, y=310)
    SLabel = tk.Label(SFrame, text="Students", fg=fgC, bg=bgC, font=("Helvetica", 15)).pack(fill=tk.X, pady=10)
    SLabelVal = tk.Label(SFrame, textvariable=totalStudents, fg=fgC, bg=bgC, font=("Helvetica", 30)).pack(fill=tk.X)
    SALabel = tk.Label(SFrame, text="Set Attendance Interval:", fg=fgC, bg=bgC, font=("Helvetica", 10)).pack(fill=tk.X, pady=5)
    global attendanceTime
    attendanceTime = 10
    global timeInputVal
    InputSFrame = tk.Frame(SFrame, bg=bgC)
    InputSFrame.pack(fill=tk.X, padx=10, pady=1)
    timeInputVal = tk.StringVar()
    timeInputBox = tk.Entry(InputSFrame, bg=bgC, width = 10, textvariable = timeInputVal, fg=fgC, font=("Helvetica", 16))
    timeInputBox.pack(padx=5, side=tk.LEFT)
    setPhoto = tk.PhotoImage(file = "assets/set.png") 
    setButton = tk.Button(InputSFrame, highlightbackground='black', height=30, width=30, image=setPhoto, command = timeFunc).pack()
    global studentTable
    studentTable = tk.Listbox(SFrame, borderwidth=0, fg=fgC, bg=bgC2, font=("Helvetica", 12))
    studentTable.pack(fill=tk.X, padx=10, pady=10)

    #CCFrame
    CCFrame = tk.Frame(root, bg=bgC)
    CCFrame.place(width=200, height=170, x=2, y=620)
    CCLabel = tk.Label(CCFrame, text="Closed Captioning", fg=fgC, bg=bgC, font=("Helvetica", 15)).pack(fill=tk.X, pady=2)
    CC1Label = tk.Label(CCFrame, text="Set Link:", fg=fgC, bg=bgC, font=("Helvetica", 10)).pack(fill=tk.X, pady=2)
    linkInputVal = tk.StringVar()
    linkInputBox = tk.Entry(CCFrame, bg=bgC, textvariable = linkInputVal, fg=fgC, font=("Helvetica", 16))
    linkInputBox.pack(fill=tk.X, padx=10)
    CC2Label = tk.Label(CCFrame, text="Set Phone Number:", fg=fgC, bg=bgC, font=("Helvetica", 10)).pack(fill=tk.X, pady=2)
    phoneInputVal = tk.StringVar()
    phoneInputBox = tk.Entry(CCFrame, bg=bgC, textvariable = phoneInputVal, fg=fgC, font=("Helvetica", 16))
    phoneInputBox.pack(fill=tk.X, padx=10)
    CCButton = tk.Button(CCFrame, text="Set CC", font=("Helvetica", 16), command = setCCFunc).pack(pady=5)

    #Thread
    t1 = Driver()
    t1.start()

    t2 = ColorAnimation()
    t2.start()


    root.mainloop()

if __name__ == '__main__':
    main()