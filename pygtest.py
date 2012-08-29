#!/usr/bin/env python
# -*- coding: utf-8 -*-
import pyglet
from pyglet.window import mouse
import os, sys


import urllib, time
import thread
 
class Graphics(object):
    def __init__(self,winX,winY):
        self.geometry = (winX, winY)
        self.window = pyglet.window.Window(winX,winY)
        self.event = self.window.event
        self.mousePos = [0, 0]
        self.textes = {}




    def clsColor(self,r=0,g=0,b=0,a=255):
        pyglet.gl.glClearColor(r,g,b,a)

    def cls(self):
       self.window.clear()

    def color(self,r=255,g=255,b=255,a=255):
        pyglet.gl.glColor4f(r,g,b,a)

    def text(self,ID, x,y, txt, font='Arial', fsize=10, bold=False, italic=False, center_x=False, center_y=False):
        if center_x == True: center_x='center'
        if center_y == True: center_y='center'
        if center_x == False or center_y == False:         
            self.textes[ID] = pyglet.text.Label(txt, font_name=font,x=x, y=y, font_size=fsize, color=(0, 0, 0, 200))           
        else: 
            self.textes[ID] = pyglet.text.Label(txt, font_name=font,x=x, y=y, font_size=fsize, anchor_x=center_x, anchor_y=center_y,color=(0, 0, 0, 200))



    def line(self, x1, y1, x2, y2):
        pyglet.graphics.draw(2, pyglet.gl.GL_LINE_LOOP,('v2f', (x1, y1, x2, y2)))

    def rect(self, x1, y1, x2, y2, fill=0):
        if fill==1:
            pyglet.graphics.draw(4, pyglet.gl.GL_QUADS, ('v2f', (x1, y1, x1, y2, x2, y2, x2, y1)))
        else:
            pyglet.graphics.draw(4, pyglet.gl.GL_LINE_LOOP, ('v2f', (x1, y1, x1, y2, x2, y2, x2, y1)))

    def oval(self, x1, y1, x2, y2, fill=0):
        if fill==1:
            points = _concat(_iter_ellipse(x1, y1, x2, y2))
            pyglet.graphics.draw(len(points)/2, pyglet.gl.GL_TRIANGLE_FAN, ('v2f', points))
        else:
            points = _concat(_iter_ellipse(x1, y1, x2, y2))
            pyglet.graphics.draw(len(points)/2, pyglet.gl.GL_LINE_LOOP, ('v2f', points))


        
def download(url, fileName):
    webFile = urllib.urlopen(url)
    content = webFile.read()
    webFile.close()
    if not "Error" in content:
        localFile = open(fileName, 'w')
        localFile.write(content)
        localFile.flush()
        localFile.close()  







winX			= 1024
winY			= 768
viewPort		= [0,0,winX/256,winY/256]
move			= [winX/2, winY/2]
mouse			= [0, 0]
coorsPerPixel	= (0.003422/256.0, 0.002039/256.0)
mapZero			= (9.977000, 53.446250)






ourwnd = Graphics(winX,winY)
ourwnd.clsColor(0,0.2,0)
ourwnd.text('mouseCoorText', 5,winY-20, '', 'Courier New', 12)
images = {}











@ourwnd.window.event
def on_draw():
    ourwnd.cls()
    viewPort = [(-move[0]/256),(-move[1]/256),((winX-move[0])/256),((winX-move[1])/256)]
    
    
    
    
    for y in xrange(viewPort[1],viewPort[3]+1):
        for x in xrange(viewPort[0],viewPort[2]+1):
            ourwnd.color(0,0.1,0)
            pos = [x*256 ,y*256]
			
            lLon = "%.6f" % ((x*256*coorsPerPixel[0])+mapZero[0])
            lLat= "%.6f" % ((y*256*coorsPerPixel[1])+mapZero[1])
            hLon  = "%.6f" % (((x*256*coorsPerPixel[0])+mapZero[0])+(coorsPerPixel[0]*256))
            hLat = "%.6f" % (((y*256*coorsPerPixel[1])+mapZero[1])+(coorsPerPixel[1]*256))
            fileName = str(lLon)+","+str(lLat)+","+str(hLon)+","+str(hLat)+'.png'
            rasterCoor = [x*256+move[0],y*256+move[1]]
            
            
            textID = str((x*256*coorsPerPixel[0])+mapZero[0])+":"+str((y*256*coorsPerPixel[1])+mapZero[1])
            ourwnd.text(textID, rasterCoor[0]+128, rasterCoor[1]+128, fileName,'Arial', 7, False, False, True, True)
            ourwnd.textes[textID].draw()
            
            ourwnd.color()
            if os.path.exists(fileName):
                images[str(x)+":"+str(y)] = pyglet.image.load(fileName)
                images[str(x)+":"+str(y)].blit(pos[0]+move[0], pos[1]+move[1])
            else:
                ourwnd.color(0.0,0.0,0.0)
                ourwnd.rect(rasterCoor[0],rasterCoor[1],x*256+256+move[0],y*256+256+move[1])
            
    ourwnd.color(1,1,1)
    ourwnd.line(-50+move[0], +move[1], 50+move[0], move[1])
    ourwnd.line(move[0], -50+move[1], move[0], 50+move[1])              
    ourwnd.textes['mouseCoorText'].draw()



            
    
@ourwnd.window.event
def on_mouse_motion(x, y, dx, dy):
    ourwnd.mousePos = [x, y]
    mouseLon = float(((ourwnd.mousePos[0]-move[0])*coorsPerPixel[0])+mapZero[0])
    mouseLat = float(((ourwnd.mousePos[1]-move[1])*coorsPerPixel[1])+mapZero[1])
    mouseLonString = "%.6f" % mouseLon 
    mouseLatString = "%.6f" % mouseLat
    ourwnd.textes['mouseCoorText'].text	= "Lon: " + mouseLonString.rjust(11,' ') + " - Lat: " + mouseLatString.rjust(11,' ')
    
    
@ourwnd.window.event
def on_mouse_drag(x, y, dx, dy, buttons, modifiers):
    ourwnd.mousePos = [x, y]
    if buttons == pyglet.window.mouse.RIGHT:
        move[0] += dx
        move[1] += dy


@ourwnd.window.event
def on_mouse_press(x, y, buttons, modifiers):                    
    if buttons == pyglet.window.mouse.MIDDLE:
        viewPort = [(-move[0]/256),(-move[1]/256),((winX-move[0])/256),((winX-move[1])/256)]
        for y in xrange(viewPort[1],viewPort[3]+1):
            for x in xrange(viewPort[0],viewPort[2]+1):	
                lLon = "%.6f" % ((x*256*coorsPerPixel[0])+mapZero[0])
                lLat= "%.6f" % ((y*256*coorsPerPixel[1])+mapZero[1])
                hLon  = "%.6f" % (((x*256*coorsPerPixel[0])+mapZero[0])+(coorsPerPixel[0]*256))
                hLat = "%.6f" % (((y*256*coorsPerPixel[1])+mapZero[1])+(coorsPerPixel[1]*256))				
                fileName = str(lLon)+","+str(lLat)+","+str(hLon)+","+str(hLat)+'.png'				
                if not os.path.exists(fileName):
                    url = 'http://parent.tile.openstreetmap.org/cgi-bin/export?bbox='+lLon+','+lLat+','+hLon+','+hLat+'&scale=5310&format=png'
                    print lLon+','+lLat+','+hLon+','+hLat
                    download(url, fileName)


pyglet.app.run()
