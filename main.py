import numpy as np
import cv2
from tkinter import *
from PIL import Image
from PIL import ImageTk
import sqlite3
import os
import serial
from train import Trainer

ser = serial.Serial('/dev/cu.usbmodem1411', 9600, timeout=1)

def write(string):
    textBox.config(state=NORMAL)
    textBox.insert('end', string + '\n')
    textBox.see('end')
    textBox.config(state=DISABLED)

def addPerson():
    conn = sqlite3.connect('database.db')
    if not os.path.exists('./dataset'):
        os.makedirs('./dataset')
        
    c = conn.cursor()
    uname = e1.get() #Get value from name entry
    c.execute('INSERT INTO users (name) VALUES (?)', (uname,))
    uid = c.lastrowid
    sampleNum = 0

    while True:
        img = getFrame()
        gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
        face_cascade = cv2.CascadeClassifier('haarcascade_frontalface_default.xml')
        faces = face_cascade.detectMultiScale(gray, 1.3, 5)
        for (x,y,w,h) in faces:
            sampleNum = sampleNum + 1
            cv2.imwrite('dataset/User.'+str(uid)+'.'+str(sampleNum)+'.jpg',gray[y:y+h,x:x+w])
        if sampleNum > 20:
            break

    conn.commit()
    conn.close()
    write('%s added' % (e1.get()))

    Trainer()

def Detector(frame):
    # open port if not already open
    if ser.isOpen() == False:
        ser.open()

    conn = sqlite3.connect('database.db')
    c = conn.cursor()
    fname = "recognizer/trainingData.yml"
    if not os.path.isfile(fname):
        write("Please add one person first")
        exit(0)

    face_cascade = cv2.CascadeClassifier('haarcascade_frontalface_default.xml')
    recognizer = cv2.face.LBPHFaceRecognizer_create()
    recognizer.read(fname)

    gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
    faces = face_cascade.detectMultiScale(gray, 1.3, 5)
    for (x,y,w,h) in faces:
        cv2.rectangle(frame,(x,y),(x+w,y+h),(0,255,0),3)
        ids,conf = recognizer.predict(gray[y:y+h,x:x+w])
        c.execute("select name from users where id = (?);", (ids,))
        result = c.fetchall()
        name = result[0][0]
        if conf < 50:
            ser.write(b'1')
            write('Welcome %s! Door unlocked.' % (name))
        else:
            write('Unknown person!')

def Lock():
    # open port if not already open
    if ser.isOpen() == False:
        ser.open()
    ser.write(b'2')
    write('Door locked.')

#Set up GUI
window = Tk()  #Makes main window
window.wm_title('Door cam')
window.config(background='#FFFFFF')

#Graphics section
imageFrame = Frame(window)
imageFrame.grid(row=0, column=0)

#Capture video frames
cap = cv2.VideoCapture(0)
def getFrame():
    ret, frame = cap.read()
    frame = cv2.resize(frame, (0, 0), fx=0.5, fy=0.5)
    cv2image = cv2.cvtColor(frame, cv2.COLOR_BGR2RGBA)
    img = Image.fromarray(cv2image)
    imgtk = ImageTk.PhotoImage(image=img)
    display.imgtk = imgtk #Shows frame for display
    display.configure(image=imgtk)
    return cv2image

display = Label(imageFrame)
display.grid(row=0, column=0)  #Display

#Button section
buttonFrame = Frame(window)
buttonFrame.grid(row=1, column=0)

Label(buttonFrame, text='Name').grid(row=0,column=3)

e1 = Entry(buttonFrame)
e1.grid(row=0,column=4)

textBox = Text(buttonFrame, state=DISABLED)
textBox.grid(row=1, column=0, columnspan=5, padx=10)

Button(buttonFrame, text='Picture', command=getFrame).grid(row=0, column=0)
Button(buttonFrame, text='Unlock', command=lambda: Detector(getFrame())).grid(row=0, column=1)
Button(buttonFrame, text='Lock', command=Lock).grid(row=0, column=2)
Button(buttonFrame, text='Add', command=addPerson).grid(row=0, column=5)

getFrame() #Display
window.mainloop()  #Starts GUI
