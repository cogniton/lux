#!/usr/bin/python
# -*- coding: utf-8 -*-

"""
Visualization of LUX results.
Adapted from ZetCode Tkinter tkColorChooser tutorial
(author: Jan Bodnar, website: www.zetcode.com)
"""
import matplotlib
matplotlib.use('TkAgg')

from numpy import arange, sin, pi
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg, NavigationToolbar2TkAgg
# implement the default mpl key bindings
from matplotlib.backend_bases import key_press_handler
from Tkinter import Tk, Frame, Button, Text, BOTH, SUNKEN, NORMAL, END, DISABLED, TOP, LEFT, BOTTOM, RIGHT, X, Y
import tkColorChooser 
import lux
import colorsys
from matplotlib.pyplot import Figure
from scipy.stats import gamma as gam_dist
import numpy as np

class Example(Frame):
  
    def __init__(self, parent):
        Frame.__init__(self, parent)   
         
        self.hsv_color = colorsys.rgb_to_hsv(0.0, 0.0, 1.0)
        self.hex_color = '#0000ff'
        self.color_list = ["red","blue","green","orange","purple"]
        self.parent = parent        
        print "Getting Model"
        self.lux = lux.LUX("lux.xml")
        print "Creating UI"
        self.initUI()
        self.update_output()

    def update_output(self):
        (h, s, v) = self.hsv_color
        items = self.lux.full_posterior((h * 360, s * 100, v * 100))
        self.current_post = items
        desc = [ '{} ({:.3f})\n'.format(items[i][0], items[i][1]) for i in range(25) ]
        self.display.config(state=NORMAL)
        self.display.delete(1.0, END)
        self.display.insert(END, ''.join(desc))
        self.display.config(state=DISABLED)        
    
    def make_plotter(self, params,ax1,label,cur_color,support):
        mu1,sh1,sc1,mu2,sh2,sc2 = params
        left_stach=gam_dist(sh1,scale=sc1); lbounds=left_stach.interval(0.99)
        right_stach=gam_dist(sh2,scale=sc2); rbounds=right_stach.interval(0.99)
        lx=np.linspace(mu1,-180); rx=np.linspace(mu2,360)
        s=3; #cur_color='black'
        ax1.plot(rx, [1-right_stach.cdf(abs(y-mu2)) for y in rx],linewidth=s,c=cur_color);
        ax1.plot([1.01*mu1,0.99*mu2], [1,1], linewidth=s,c=cur_color)
        return ax1.plot(lx,[1-left_stach.cdf(abs(y-mu1)) for y in lx],c=cur_color, label=r"$\phi^{Hue}_{%s}$" % label,linewidth=s);
        
        
        
    def initUI(self):
      
        self.parent.title("Interactive LUX visualization")      
        self.pack(fill=BOTH, expand=1)
        
        self.color_frame = Frame(self, border=1)
        self.color_frame.pack(side=LEFT)
        
        
        self.frame = Frame(self.color_frame, border=1, 
            relief=SUNKEN, width=100, height=100)
        #self.frame.place(x=160, y=30)
        self.frame.pack(side=TOP)
        self.frame.config(bg=self.hex_color)
                
        
        self.btn = Button(self.color_frame, text="Select Color", 
            command=self.onChoose)
        self.btn.pack(side=TOP)
        #self.btn.place(x=30, y=30)
        

        self.display = Text(self, border=1, 
            relief=SUNKEN, width=30, height=5)
        #self.display.place(x=280, y=30)
        self.display.pack(side=LEFT,fill=Y,expand=1)
        self.update_output()
        
        self.fig = Figure(figsize=(10,4), dpi=100)
        self.replot()
        self.canvas = FigureCanvasTkAgg(self.fig, master=self)
        self.canvas.show()
        self.canvas.get_tk_widget().pack(side=LEFT, fill=BOTH, expand=1)
        self.canvas._tkcanvas.pack(side='top', fill='both', expand=1)

    def replot(self):
        hsv_title = []
        for i in range(3):
            if self.lux.get_adj(self.current_post[0][0]): 
                support = [[-180,180], [0,100],[0,100]][i]
                pp = lambda x,i: x-360 if i==0 and x>180 else x
            else: 
                support = [[0,360], [0,100],[0,100]][i]
                pp = lambda x,*args: x
            subplot = self.fig.add_subplot(3,1,i+1) 
            subplot.set_xlim(support[0],support[1])   
            subplot.set_ylabel("%s" % ["Hue", "Saturation","Value"][i])
            point = pp(self.hsv_color[i]*[360,100,100][i],i)
            hsv_title.append(point)
            probeplot = subplot.plot([point,point], [0,1],linewidth=3,c='black',label="Probe")
            legend_set = []
            for j in range(5):
                test = self.make_plotter(self.lux.get_params(self.current_post[j][0])[i], subplot, self.current_post[j][0],self.color_list[j],support)
                if type(test)==type([]): legend_set+=test
                else: legend_set.append(test)
        
        self.fig.legend(legend_set, [r"$\phi_{%s}$; $\alpha=%2.4f$" % (x[0],self.lux.get_avail(x[0])) for x in self.current_post[:5]], loc=1)
        self.fig.suptitle("HSV (%2.2f,%2.2f,%2.2f) top 5 Phi curves" % (hsv_title[0],hsv_title[1],hsv_title[2]))

    def onChoose(self):
      
        ((red,green,blue), hx) = tkColorChooser.askcolor()
        self.hex_color = hx
        self.hsv_color = colorsys.rgb_to_hsv(red/255.0, green/255.0, blue/255.0)
        self.frame.config(bg=hx)
        self.update_output()
        self.fig.clear()
        self.replot()
        self.canvas.draw()

def main():
  
    root = Tk()
    ex = Example(root)
    root.geometry("450x200+300+300")
    root.mainloop()  


if __name__ == '__main__':
    main()  
