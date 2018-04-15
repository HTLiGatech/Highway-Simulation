import math
import matplotlib as plt
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
from matplotlib.figure import Figure
from Tkinter import *
import settings

import Queue
import threading
import warnings

from numpy import arange, sin, pi
from time import sleep

import highway
import multilane
import time
import random

class UI (object):
    # UI config
    programTitle = "Traffic Simulation Software Version 1.0"
    animationSize = (8, 8)
    animationDpi = 100
    refreshInterval = 0.2  # refresh frame interval in second
    
    def __init__(self):
        # UI preparation
        warnings.filterwarnings ("ignore")  # ignore warnings
        plt.use ('TKAgg')  # use matplotlib in Tkinter
        self.root = Tk ()
        self.root.resizable (False, False)  # disable window size change
        self.root.title (self.programTitle)  # program title
        
        # set frames
        f1 = Frame(self.root,bd=4,relief='groove')
        f2 = Frame(self.root,bd=4,relief='groove')
        f3 = Frame(self.root,bd=4,relief='groove')
        f4 = Frame(self.root,bd=4,relief='groove')
        f1.grid(row=1,column=0,rowspan=26)
        f2.grid(row=1,column=1,rowspan=8,columnspan=3)
        f3.grid(row=10,column=1,rowspan=12,columnspan=3)
        f4.grid(row=23,column=1,columnspan=3)

        # set views
        Label(self.root,text='Display Window:').grid(row=0,column=0,sticky=W)

        Label(self.root,text='Current Status:').grid(row=0,column=1,sticky=W)

        Label(f2,text='Current Iteration:').grid(row=0,column=0,sticky=W)
        self.curr_iter = Label(f2,text='0/0')
        self.curr_iter.grid(row=1,column=0,sticky=W)

        Label(f2,text='Traffic Light Interval:').grid(row=2,column=0,sticky=W)
        self.traffic_light_interval = Label(f2,text='OFF')
        self.traffic_light_interval.grid(row=3,column=0,sticky=W)
        
        Label(f2,text='Traffic Light Duration:').grid(row=4,column=0,sticky=W)
        self.traffic_light_duration = Label(f2,text='OFF')
        self.traffic_light_duration.grid(row=5,column=0,sticky=W)

        Label(f2,text='Traffic Jam Duration:').grid(row=6,column=0,sticky=W)
        self.traffic_jam_duration = Label(f2,text='OFF')
        self.traffic_jam_duration.grid(row=7,column=0,sticky=W)

        Label(self.root,text='Settings:').grid(row=9,column=1,sticky=W)

        Label(f3,text='Set Iteration:').grid(row=0,column=0,sticky=W)
        self.set_iter = Entry(f3)
        self.set_iter.grid(row=1,column=0,columnspan=3,sticky=N)

        Label(f3,text='Traffic Light Mode:').grid(row=2,column=0,sticky=W)
        self.set_traffic_light_mode = Label(f3,text='ON')
        self.set_traffic_light_mode.grid(row=2,column=0,sticky=E)
        self.set_traffic_light_mode_btn = Button(f3,text='Toggle',command=self.traffic_light_mode_toggle)
        self.set_traffic_light_mode_btn.grid(row=3,column=0,columnspan=3)

        Label(f3,text='Set Traffic Light Interval:').grid(row=4,column=0,sticky=NW)
        self.set_traffic_light_interval = Entry(f3)
        self.set_traffic_light_interval.grid(row=5,column=0,columnspan=3,sticky=N)

        Label(f3,text='Set Traffic Light Duration:').grid(row=6,column=0,sticky=NW)
        self.set_traffic_light_duration = Entry(f3)
        self.set_traffic_light_duration.grid(row=7,column=0,columnspan=3,sticky=N)

        Label(f3,text='Traffic Jam Mode:').grid(row=8,column=0,sticky=NW)
        self.set_traffic_jam_mode = Label(f3,text='ON')
        self.set_traffic_jam_mode.grid(row=8,column=0,sticky=E)
        self.set_traffic_jam_mode_btn = Button(f3,text='Toggle',command=self.traffic_jam_mode_toggle)
        self.set_traffic_jam_mode_btn.grid(row=9,column=0,columnspan=3)

        Label(f3,text='Set Traffic Jam:').grid(row=10,column=0,sticky=NW)
        self.set_traffic_jam_start = Entry(f3,width = 8)
        self.set_traffic_jam_start.grid(row=11,column=0,columnspan=3,sticky=NW)
        Label(f3,text='To').grid(row=11,column=0,columnspan=3,sticky=N)
        self.set_traffic_jam_end = Entry(f3,width = 8)
        self.set_traffic_jam_end.grid(row=11,column=0,columnspan=3,sticky=NE)

        Label(self.root,text='Animation Control:').grid(row=22,column=1,sticky=NW)
        self.play = Button(f4,text='Play',command=self.play)
        self.play.grid(row=0,column=0,sticky=NW)
        # self.pause = Button(f4,text='Pause',state="disabled")
        # self.pause.grid(row=0,column=1,sticky=N)
        self.stop = Button(f4,text='Stop',command=self.stop)
        self.stop.grid(row=0,column=2,sticky=E)

        Label(self.root,text='Error Message:').grid(row=24,column=1,sticky=NW)
        self.message = Label(self.root,text='Normal',fg="black")
        self.message.grid(row=25,column=1,columnspan=3,sticky=N)


        # draw matplotlib output to Tkinter
        self.figure = Figure (figsize=(self.animationSize[0], self.animationSize[1]), dpi=self.animationDpi)  # set figure
        self.canvas = FigureCanvasTkAgg (self.figure, master=f1)  # TODO: subject to change root to frame
        self.canvas.get_tk_widget ().grid (row=1, column=0, rowspan=26)  # TODO: subject to change canvas position
        
        # set window in the center of the screen
        # ===== quote http://www.jb51.net/article/61962.htm =====
        self.root.update ()  # update window (must do)
        curWidth = self.root.winfo_reqwidth ()  # get current width
        curHeight = self.root.winfo_height ()  # get current height
        scnWidth, scnHeight = self.root.maxsize ()  # get screen width and height
        # now generate configuration information
        tmpcnf = '%dx%d+%d+%d' % (curWidth, curHeight, (scnWidth - curWidth) / 2, (scnHeight - curHeight) / 2)
        self.root.geometry (tmpcnf)
        # ===== end quote =====
        
        # set message queue
        self.messageQueue = Queue.Queue ()
        self.masterMessageQueue = Queue.Queue()
        

    def drawFrame(self, x, y, num):
        self.figure.clf()
        colors = ['red', 'orange', 'yellow', "green", "blue", 'purple', 'pink', "black"]
        for i in range(num):
            self.figure.add_subplot (111).scatter (x[i], y[i], s=4, color=colors[i])
        if self.set_traffic_jam_mode.cget("text") == "ON":
            self.figure.add_subplot (111).scatter ([1206.8699186991871],[1739.065040650406], s=25, color="black", marker="X")
            self.figure.legend(["Lane 0","Lane 1","Lane 2","Lane 3","Lane 4","Merge 0","Merge 1","Exit", "Accident"], loc="lower left", bbox_to_anchor=(0.13,0.12))
        else:
            self.figure.legend(["Lane 0","Lane 1","Lane 2","Lane 3","Lane 4","Merge 0","Merge 1","Exit"], loc="lower left", bbox_to_anchor=(0.13,0.12))
        fig = self.figure.gca()
        # ax.spines['right'].set_visible(False)
        fig.set_ylim ([-200, 3500])
        fig.set_xlim ([-300, 3500])
        fig.xaxis.set_visible(False)
        fig.yaxis.set_visible(False)

        self.canvas.show ()

    def processMessage(self):
        while True:
            if not self.messageQueue.empty ():
                x, y, i = self.messageQueue.get ()
                num = len(x)
                self.drawFrame (x, y, num)
                self.curr_iter.config(text=str(i+1) + "/" + self.curr_iter.cget("text").split("/")[1])
                if self.curr_iter.cget("text").split("/")[0] == self.curr_iter.cget("text").split("/")[1]:
                    self.masterMessageQueue.put(1)
                    self.play.config(state="normal")
            if not self.masterMessageQueue.empty():
                self.messageQueue = Queue.Queue()
                self.figure.clf()
            sleep(self.refreshInterval)

    def sendMessage(self, x, y, i):
        # x, y = self.processData (highways)
        self.messageQueue.put ((x, y, i))

    def mainloop(self):
        self.root.mainloop ()

    def traffic_light_mode_toggle(self):
        if self.set_traffic_light_mode.cget("text") == "ON":
            self.set_traffic_light_mode.config(text="OFF")
            self.set_traffic_light_duration.config(state=DISABLED)
            self.set_traffic_light_interval.config(state=DISABLED)
        else:
             self.set_traffic_light_mode.config(text="ON")
             self.set_traffic_light_duration.config(state=NORMAL)
             self.set_traffic_light_interval.config(state=NORMAL)

    def traffic_jam_mode_toggle(self):
        if self.set_traffic_jam_mode.cget("text") == "ON":
            self.set_traffic_jam_mode.config(text="OFF")
            self.set_traffic_jam_start.config(state=DISABLED)
            self.set_traffic_jam_end.config(state=DISABLED)
        else:
             self.set_traffic_jam_mode.config(text="ON")
             self.set_traffic_jam_start.config(state=NORMAL)
             self.set_traffic_jam_end.config(state=NORMAL)

    def play(self):
        try:
            iteration = int(self.set_iter.get())
        except:
            self.message.config(text="Invalid iteration value.",fg="red")
            return
        if iteration <= 0:
            self.message.config(text="Invalid iteration value.",fg="red")
            return

        if self.set_traffic_light_mode.cget("text") == "OFF":
            interval = -1
            duration = -1
        else:
            try:
                interval = int(self.set_traffic_light_interval.get())
            except:
                self.message.config(text="Invalid interval value.",fg="red")
                return
            if interval <= 0:
                self.message.config(text="Invalid interval value.",fg="red")
                return

            try:
                duration = int(self.set_traffic_light_duration.get())
            except:
                self.message.config(text="Invalid duration value.",fg="red")
                return
            if duration <= 0:
                self.message.config(text="Invalid duration value.",fg="red")
                return

        if self.set_traffic_jam_mode.cget("text") == "OFF":
            jam_start = -1
            jam_end = -1
        else:
            try:
                jam_start = int(self.set_traffic_jam_start.get())
            except:
                self.message.config(text="Invalid start value.",fg="red")
                return
            if jam_start <= 0:
                self.message.config(text="Invalid start value.",fg="red")
                return

            try:
                jam_end = int(self.set_traffic_jam_end.get())
            except:
                self.message.config(text="Invalid end value.",fg="red")
                return
            if jam_end <= 0 or jam_end <= jam_start:
                self.message.config(text="Invalid end value.",fg="red")
                return

        # config
        self.message.config(text="Normal",fg="black")
        self.masterMessageQueue = Queue.Queue()
        self.messageQueue = Queue.Queue()
        self.curr_iter.config(text="0/"+str(iteration))
        self.play.config(state="disabled")

        if jam_start == -1:
            self.traffic_jam_duration.config(text="OFF")
        else:
            self.traffic_jam_duration.config(text=self.set_traffic_jam_start.get()+" to "+self.set_traffic_jam_end.get())

        if interval == -1:
            self.traffic_light_interval.config(text="OFF")
            self.traffic_light_duration.config(text="OFF")
        else:
            self.traffic_light_interval.config(text=str(interval))
            self.traffic_light_duration.config(text=str(duration))

        workerThread = threading.Thread(target=self.run, args=(iteration, interval, duration, jam_start, jam_end))
        workerThread.setDaemon(True)
        workerThread.start()

    def stop(self):
        self.masterMessageQueue.put(1)
        self.play.config(state="normal")

    def run(self, iteration_num, interval, duration, jam_start, jam_end):
        iteration = iteration_num
        acc_start = jam_start
        print jam_start
        acc_stop = jam_end
        hwy = highway.Highway ()
        basemap = settings.UI_BASEMAP
        accident = "ON"                 # toggle between ON and OFF
        traffic_light = "ON"            # toggle between ON and OFF

        if interval == -1:
            traffic_light = "OFF"
        if jam_start == -1:
            accident = "OFF"

        traff_intv = interval
        traff_dura = duration
        for itr in range (iteration):

            if accident == "ON":
                # Interface for calling traffic accidents: hwy.update_states(itr, flag)
                # flag = 1: traffic accident; flag = 0: no accident
                if itr > acc_start or itr < acc_stop:
                    hwy.update_states(itr, 1)
                else:
                    hwy.update_states(itr, 0)
            
            if traffic_light == "ON":
                if itr % (traff_intv + traff_dura) == 0:
                    hwy.mergelane.e_prob1 = 0
                elif itr % (traff_intv + traff_dura) == traff_intv:
                    hwy.mergelane.e_prob1 = 0.8
                if itr == iteration - 1:
                    hwy.mergelane.e_prob1 = 0.5
            
            if accident == "OFF":
                hwy.update_states (itr, 0)
            
            res1 = hwy.multiway.lanes
            res2 = hwy.mergelane.lanes
            res3 = hwy.exitway.lanes
            
            x = [[] for _ in range (8)]
            y = [[] for _ in range (8)]
            for i, lanex in enumerate (res1):
                for j, c in enumerate (lanex.cells):
                    if c != None:
                        id = c.id
                        xi, yi = basemap[i][j]
                        x[id].append (xi)
                        y[id].append (yi)
                        
            for i, lanex in enumerate (res2):
                for j, c in enumerate (lanex.cells):
                    if c != None:
                        id = c.id
                        xi, yi = basemap[i+5][j]
                        x[id].append (xi)
                        y[id].append (yi)
                        
            for j, c in enumerate(res3.cells):
                if c != None:
                    id = c.id
                    xi, yi = basemap[7][j]
                    x[id].append (xi)
                    y[id].append (yi)
                    
            # send data to UI
            self.sendMessage (x, y, itr)
            if not self.masterMessageQueue.empty():
                return
