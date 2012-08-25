#!/usr/bin/env python
# -*- coding: utf-8 -*-

import xmltodict, json, re, time, datetime, sys, os


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


def writeHeaderOfFile(filePath, file):
	headerLines = []
	with open(filePath,'r') as f:
		for line in f.readlines():
			file.write(line)
			if '<trkseg>' in line:
				break


def gpxFileEnd(file):
	file.write('    </trkseg>\n')
	file.write('  </trk>\n')
	file.write('</gpx>\n')




newGPX = open('out.'+sys.argv[1],'w')
writeHeaderOfFile(sys.argv[1],newGPX)


trackPoints = getTrackpointsOfGPXFile(sys.argv[1])
trackPoints = trackPoints


newGPX.write('      <trkpt lat="' + trackPoints[0]['@lat'] + '" lon="' + trackPoints[0]['@lon'] + '">\n')
newGPX.write('        <ele>' + trackPoints[0]['ele'] + '</ele>\n')
newGPX.write('        <time>' + trackPoints[0]['time'] + '</time>\n')
newGPX.write('      </trkpt>\n')


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
	
	
	
	if differenceTime > 3:
		newPoints = (differenceTime/3)-1
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
				newGPX.write('      <trkpt lat="' + lat + '" lon="' + lon + '">\n')
				newGPX.write('        <ele>' + ele + '</ele>\n')
				newGPX.write('        <time>' + timeOfPoint + '</time>\n')
				newGPX.write('      </trkpt>\n')
	
	newGPX.write('      <trkpt lat="' + trackPoints[ID]['@lat'] + '" lon="' + trackPoints[ID]['@lon'] + '">\n')
	newGPX.write('        <ele>' + trackPoints[ID]['ele'] + '</ele>\n')
	newGPX.write('        <time>' + trackPoints[ID]['time'] + '</time>\n')
	newGPX.write('      </trkpt>\n')

gpxFileEnd(newGPX)
newGPX.flush()
newGPX.close()
