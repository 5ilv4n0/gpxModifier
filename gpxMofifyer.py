#!/usr/bin/env python
# -*- coding: utf-8 -*-

import xmltodict
import pyglet
from pyglet.window import mouse
from pyglet.gl import *
import os, sys, urllib,thread, time, re, datetime


def timeStampPlusSeconds(timestamp, seconds=0):
	timeObject = re.match(r'(\d+)-(\d+)-(\d+)T(\d+):(\d+):(\d+)Z', timestamp)
	times = timeObject.groups()
	second = int(times[5])
	minute = int(times[4])
	hour = int(times[3])
	day = int(times[2])	
	month = int(times[1])
	year = int(times[0])
	for s in range(0, seconds):
		second += 1
		if second > 59:
			second = 0
			minute += 1
			if minute > 59:
				minute = 0
				hour += 1
	return str(year).rjust(4,'0')+'-'+str(month).rjust(2,'0')+'-'+str(day).rjust(2,'0')+'T'+str(hour).rjust(2,'0')+':'+str(minute).rjust(2,'0')+':'+str(second).rjust(2,'0')+'Z'

def getTimeDifferrence(before, after):
	at = re.match(r'\d+-\d+-\d+T(\d+:\d+:\d+)Z', after)
	atime = time.strptime(at.groups()[0], "%H:%M:%S")	
	atime = datetime.datetime(*atime[:6])	
	bt = re.match(r'\d+-\d+-\d+T(\d+:\d+:\d+)Z', before)
	btime = time.strptime(bt.groups()[0], "%H:%M:%S")
	btime = datetime.datetime(*btime[:6])				
	differenceTime = atime-btime
	differenceTime = str(differenceTime)
	t = re.match(r'(\d+):(\d+):(\d+)',differenceTime)
	hour, minute, second = t.groups()
	hour = int(hour)
	minute = int(minute)
	second = int(second)	
	differenceSeconds = (hour*3600)+(minute*60)+second
	return differenceSeconds

def getTrackpointsOfGPXFile(filename):
	trackPoints = []
	with open(filename,'r') as f:
		buf = f.read()
		o = xmltodict.parse(buf)
		for e in o['gpx']['trk']['trkseg']['trkpt']:
			try:
				elevation = e['ele']
			except KeyError:
				e['ele'] = '0.0'
			trackPoints.append(e)
	return trackPoints

def readHeaderOfFile(filePath):
	headerLines = []
	with open(filePath,'r') as f:
		for line in f.readlines():
			headerLines.append(line.replace(os.linesep,''))
			if '<trkseg>' in line:
				break
	return headerLines

def gpxFileEnd():
	endLines = []
	endLines.append('    </trkseg>')
	endLines.append('  </trk>')
	endLines.append('</gpx>')
	return endLines

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
            self.textes[ID] = pyglet.text.Label(txt, font_name=font,x=x, y=y, font_size=fsize, color=(0, 0, 0, 220))
        else: 
            self.textes[ID] = pyglet.text.Label(txt, font_name=font,x=x, y=y, font_size=fsize, anchor_x=center_x, anchor_y=center_y,color=(0, 0, 0, 200))

    def line(self, x1, y1, x2, y2):
        pyglet.graphics.draw(2, pyglet.gl.GL_LINE_LOOP,('v2f', (x1, y1, x2, y2)))

    def rect(self, x1, y1, x2, y2, fill=0):
        if fill==1:
            pyglet.graphics.draw(4, pyglet.gl.GL_QUADS, ('v2f', (x1, y1, x1, y2, x2, y2, x2, y1)))
        else:
            pyglet.graphics.draw(4, pyglet.gl.GL_LINE_LOOP, ('v2f', (x1, y1, x1, y2, x2, y2, x2, y1)))

class gpsPoint(object):
    def __init__(self, lon=0.0, lat=0.0, ele=0.0, tim=0):
        self.lon = lon
        self.lat = lat
        self.ele = ele
        self.tim = tim
        self.viewed = False
        self.marked = False

    def draw(self):
        posX, posY = gpsToPos(self.lon, self.lat)
        window.color(1,0,0)
        window.rect(posX-4+move[0], posY-4+move[1], posX+5+move[0], posY+5+move[1], 1)
        colorValue =  eleColor*(self.ele/10.0)
        window.color(colorValue,colorValue,colorValue)
        window.rect(posX-2+move[0], posY-2+move[1], posX+3+move[0], posY+3+move[1], 1)        
        if self.marked == True: 
            window.color(1,1,0)
            window.rect(posX-8+move[0], posY-8+move[1], posX+10+move[0], posY+10+move[1], 0)   

    def mouseOn(self): 
        posX, posY = gpsToPos(self.lon, self.lat)
        if (window.mousePos[0] > posX-4+move[0]) and (window.mousePos[0] < posX+4+move[0]) and (window.mousePos[1] > posY-4+move[1]) and (window.mousePos[1] < posY+4+move[1]):
            return True
        else:
            return False

class gpsRoute(object):
    def __init__(self):
        self.points = []

    def addPoint(self, lon=0.0, lat=0.0, ele=0.0, tim=0):
        self.points.append(gpsPoint(lon, lat, ele, tim))

    def draw(self):
        p = len(self.points)
        if p == 0:
            return
        colorMultiplicator = 1.0/p        
        for ID in xrange(1,p):
            window.color(ID*colorMultiplicator,ID*colorMultiplicator,0)          
            x1, y1 = gpsToPos(self.points[ID].lon, self.points[ID].lat)
            x2, y2 = gpsToPos(self.points[ID-1].lon, self.points[ID-1].lat)
            window.line(x1+move[0], y1+move[1], x2+move[0], y2+move[1])
            window.line(x1+move[0]-1, y1+move[1], x2+move[0]-1, y2+move[1])
            window.line(x1+move[0]+1, y1+move[1], x2+move[0]+1, y2+move[1])
            window.line(x1+move[0], y1+move[1]-1, x2+move[0], y2+move[1]-1)                  
            window.line(x1+move[0], y1+move[1]+1, x2+move[0], y2+move[1]+1)
        for point in self.points:
            point.draw()

    def mouseOn(self):
         for point in self.points:
            point.mouseOn()

    def unmarkAll(self):
         for point in self.points:
            point.marked = False

    def next(self):
         for ID, point in enumerate(self.points):
            if point.marked == True:
                point.marked = False
                if not ID == len(self.points)-1:
                    point.marked == False
                    self.points[ID+1].marked = True
                    break

    def before(self):
        for ID, point in enumerate(self.points):
            if point.marked == True:
                point.marked = False
                if not ID == 0:
                    point.marked == False
                    self.points[ID-1].marked = True
                    break                   


    

def download(url, fileName):
    content = "Error"
    while "Error" in content:
        webFile = urllib.urlopen(url)
        content = webFile.read()
        webFile.close()
        if "Error" in content:
            print fileName+"....sleep for a minute"
            time.sleep(60)
        else: 
            break
    if not "Error" in content:
        localFile = open(fileName+'.tmp', 'w')
        localFile.write(content)
        localFile.flush()
        localFile.close() 
        os.rename(fileName+'.tmp',fileName)

def gpsToPos(lon, lat):
    x = int((lon-mapZero[0])/coorsPerPixel[0])
    y = int((lat-mapZero[1])/coorsPerPixel[1])
    return x,y

def posToGPS(x,y):
    lon = (x*coorsPerPixel[0])+mapZero[0]
    lat = (y*coorsPerPixel[1])+mapZero[1]
    return lon, lat

def setPosLabel(x,y):
    window.mousePos = [x, y]
    mouseLon = float(((window.mousePos[0]-move[0])*coorsPerPixel[0])+mapZero[0])
    mouseLat = float(((window.mousePos[1]-move[1])*coorsPerPixel[1])+mapZero[1])
    mouseLonString = "%.6f" % mouseLon 
    mouseLatString = "%.6f" % mouseLat
    window.textes['mouseCoorText'].text	= "Lon: " + mouseLonString.rjust(11,' ') + " - Lat: " + mouseLatString.rjust(11,' ')





winX			= 1280
winY			= 768
viewPort		= [0,0,winX/256,winY/256]
move			= [winX/2, winY/2]
mouse			= [0, 0]
coorsPerPixel	= (0.003422/256.0, 0.002039/256.0)
mapZero			= (9.977000, 53.446250)
loadThreads		= {}
window = Graphics(winX,winY)
window.clsColor(0.4,0.8,0.4)
window.text('mouseCoorText', 5,winY-20, '', 'Courier New', 12)
images = {}


trackPoints = getTrackpointsOfGPXFile(sys.argv[1])
newTrackPoints = []
newTrackPoints.append(trackPoints[0])
for ID in range(1, len(trackPoints)):
    oldTime = trackPoints[ID-1]['time']
    newTime = trackPoints[ID]['time']
    differenceTime = getTimeDifferrence(oldTime, newTime)
    oldLat = trackPoints[ID-1]['@lat']
    newLat = trackPoints[ID]['@lat']	
    differenceLat = float(newLat)-float(oldLat)
    oldLon = trackPoints[ID-1]['@lon']
    newLon = trackPoints[ID]['@lon']	
    differenceLon = float(newLon)-float(oldLon)
    oldEle = trackPoints[ID-1]['ele']
    newEle = trackPoints[ID]['ele']	
    differenceEle =	float(newEle)-float(oldEle)
    if '--optimize' in sys.argv:
        if differenceTime > 10:
            newPoints = (differenceTime/10)-1
            if newPoints > 0:
                differenceTimePerPoint = differenceTime/(newPoints+1)
                differenceLatPerPoint = differenceLat/(newPoints+1)
                differenceLonPerPoint = differenceLon/(newPoints+1)			
                differenceElePerPoint = differenceEle/(newPoints+1)
                for tID in range(1,(newPoints+1)):
                    timeOfPoint = timeStampPlusSeconds(trackPoints[ID-1]['time'], tID*3)
                    eleOfPoint = float(oldEle)+(differenceElePerPoint*tID)
                    latOfPoint = float(oldLat)+(differenceLatPerPoint*tID)
                    lonOfPoint = float(oldLon)+(differenceLonPerPoint*tID)
                    ele = ('%.1f' % eleOfPoint)
                    lat = ('%.6f' % latOfPoint)
                    lon = ('%.6f' % lonOfPoint)
                    newPoint = {}
                    newPoint['@lat'] = lat
                    newPoint['@lon'] = lon
                    newPoint['ele'] = ele
                    newPoint['time'] = timeOfPoint
                    newTrackPoints.append(newPoint)
    newTrackPoints.append(trackPoints[ID])








route = gpsRoute()
lEle = 9999.9
hEle = 0.0
for point in newTrackPoints:
    if hEle < float(point['ele']): hEle = float(point['ele'])
    if not float(point['ele']) == 0.0:
        if lEle > float(point['ele']): lEle = float(point['ele'])    
    route.addPoint(float(point['@lon']), float(point['@lat']), float(point['ele']), str(point['time']))
diffEle = hEle-lEle
eleColor = (diffEle/255)




@window.window.event
def on_draw():
    glEnable(GL_BLEND)
    glBlendFunc(GL_SRC_ALPHA, GL_ONE_MINUS_SRC_ALPHA) 
    window.cls()
    drawMap(winX, winY, move)
    drawRouteIfExists() 
    window.textes['mouseCoorText'].draw()



def drawRouteIfExists():
    try:
        route.draw()
    except NameError:
        pass    


def drawMap(winX, winY, move):
    viewPort = [(-move[0]/256),(-move[1]/256),((winX-move[0])/256),((winX-move[1])/256)]
    for y in xrange(viewPort[1],viewPort[3]+1):
        for x in xrange(viewPort[0],viewPort[2]+1):
            pos = [x*256 ,y*256]
            fileName = getFileName(x, y, coorsPerPixel, mapZero)
            if os.path.exists(fileName):
                window.color(0.9,0.9,1)
                drawMapSegment_deleteIfNotReadable(fileName, pos, move)
            else:
                drawReplacement(fileName, x, y, move, coorsPerPixel, mapZero)
                url = getURL(x, y, coorsPerPixel, mapZero)
                downloadMapSegment(loadThreads, url, fileName)


def downloadMapSegment(loadThreads, url, fileName):
    try:
        a = loadThreads[url]
    except KeyError:
        loadThreads[url] = thread.start_new_thread(download, (url, fileName))
        print url    


def getFileName(x, y, coorsPerPixel, mapZero):
    pos = [x*256 ,y*256]
    lLon = "%.6f" % ((x*256*coorsPerPixel[0])+mapZero[0])
    lLat= "%.6f" % ((y*256*coorsPerPixel[1])+mapZero[1])
    hLon  = "%.6f" % (((x*256*coorsPerPixel[0])+mapZero[0])+(coorsPerPixel[0]*256))
    hLat = "%.6f" % (((y*256*coorsPerPixel[1])+mapZero[1])+(coorsPerPixel[1]*256))
    fileName = str(lLon)+","+str(lLat)+","+str(hLon)+","+str(hLat)+'.png'    
    return fileName

def getURL(x, y, coorsPerPixel, mapZero):
    pos = [x*256 ,y*256]
    lLon = "%.6f" % ((x*256*coorsPerPixel[0])+mapZero[0])
    lLat= "%.6f" % ((y*256*coorsPerPixel[1])+mapZero[1])
    hLon  = "%.6f" % (((x*256*coorsPerPixel[0])+mapZero[0])+(coorsPerPixel[0]*256))
    hLat = "%.6f" % (((y*256*coorsPerPixel[1])+mapZero[1])+(coorsPerPixel[1]*256))  
    url = 'http://parent.tile.openstreetmap.org/cgi-bin/export?bbox='+lLon+','+lLat+','+hLon+','+hLat+'&scale=5310&format=png'
    return url


def drawMapSegment_deleteIfNotReadable(fileName, pos, move):
    try:
        i = pyglet.image.load(fileName)
        i.blit(pos[0]+move[0], pos[1]+move[1])
    except pyglet.image.codecs.ImageDecodeException: 
        os.remove(fileName)
  
def drawReplacement(fileName, x, y, move, coorsPerPixel, mapZero):
    rasterCoor = [x*256+move[0],y*256+move[1]]
    textID = str((x*256*coorsPerPixel[0])+mapZero[0])+":"+str((y*256*coorsPerPixel[1])+mapZero[1])
    window.text(textID, rasterCoor[0]+128, rasterCoor[1]+128, fileName,'Arial', 7, False, False, True, True)
    window.textes[textID].draw()
    window.color(0,0,0)
    window.rect(rasterCoor[0],rasterCoor[1],x*256+256+move[0],y*256+256+move[1])



@window.window.event
def on_mouse_motion(x, y, dx, dy):
    setPosLabel(x,y)
    try:
        for point in route.points:
            point.mouseOn()
    except NameError:
        pass

@window.window.event
def on_mouse_drag(x, y, dx, dy, buttons, modifiers):
    setPosLabel(x,y)
    if buttons == pyglet.window.mouse.LEFT:
        try:
            for point in route.points:
                if point.marked == True:
                    point.lon, point.lat = posToGPS(x-move[0],y-move[1])
        except NameError:
            pass

    if buttons == pyglet.window.mouse.RIGHT:
        move[0] += dx
        move[1] += dy


@window.window.event
def on_mouse_press(x, y, buttons, modifiers):  
    if buttons == pyglet.window.mouse.LEFT:
        try:
            route.unmarkAll()
            for point in route.points:
                m = point.mouseOn()
                point.marked = m
                if m == True:
                    break
        except NameError:
            pass

@window.window.event
def on_key_press(symbol, modifiers):
    if symbol == pyglet.window.key.N:
        route.next()
    if symbol == pyglet.window.key.B:
        route.before()





def writeRouteToGPXFile(filePath, route):
    fileHeader = readHeaderOfFile(sys.argv[1])
    fileFooter = gpxFileEnd()
    os.remove(sys.argv[1])
    outFile = open(sys.argv[1],'w')
    
    for line in fileHeader:
        outFile.write(line+os.linesep)

    for point in route.points:
        outFile.write('      <trkpt lat="' + str(point.lat) + '" lon="' + str(point.lon) + '">'+os.linesep)
        outFile.write('        <ele>' + str(point.ele) + '</ele>'+os.linesep)
        outFile.write('        <time>' + point.tim + '</time>'+os.linesep)
        outFile.write('      </trkpt>'+os.linesep)
        
    for line in fileFooter:
        outFile.write(line+os.linesep)
    outFile.flush()
    outFile.close()
        
        
pyglet.app.run()        
writeRouteToGPXFile('out.gpx', route)
