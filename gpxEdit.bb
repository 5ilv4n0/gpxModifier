AppTitle "mapViewer v1.0a   -   Copyright 2012 Silvano Wegener"
Dim coor$(1,3)
Global points = 0
Const latPerPixel# = 2039.0/256.0
Const lonPerPixel# = 3422.0/256.0
Global movex, movey
Global marked=-1
Global winX=1024, winY=768
Global mapZeroLat=53446250, mapZeroLon=9977000 ;mapZeroLat=53550330, mapZeroLon=10000750 ;Mitte Hamburg
Global mapDir$="map"
Global play=0
Global fileHeader$





If FileType(mapDir$) = 0 Then CreateDir mapDir$
If FileType(mapDir$+"\home.ini") = 0 Then
	homeFile = WriteFile(mapDir$+"\home.ini")
	WriteLine homeFile,0
	WriteLine homeFile,0
	CloseFile homeFile 
Else
	homeFile = ReadFile(mapDir$+"\home.ini")
	movex = ReadLine(homeFile)
	movey = ReadLine(homeFile)
EndIf


;#####################################################################################################
Graphics winX,winY,16,2
	SetBuffer BackBuffer()
	font = LoadFont("Arial",15,1,0,0)
	SetFont font
	ClsColor 0,0,$FFFFFF


;#########################
While Not KeyHit(1) : Cls
zoom# = (1.0+(1.0*MouseZ()/10))

sViewX = (0-movex)/256
sViewY = (0-movey)/256
eViewX = (0-movex+winX)/256
eViewY = (0-movey+winY)/256
For y = sViewY To eViewY
	lat = (mapZeroLat+(((y)*-1)*2039))
	For x = sViewX To eViewX
		lon = (mapZeroLon+((x)*3422))
		filePath$ = mapDir$+"\"+formatCoor$(lon)+","+formatCoor$(lat)+","+formatCoor$(lon+3422)+","+formatCoor$(lat+2039)+".png"
		posX = lonToX(formatCoor$(lon))
		posY = latToY(formatCoor$(lat))-winY
		i = LoadImage(filePath$)
		
		
		If Not i = 0 Then
			DrawBlock i,posX+1,posY+1
			FreeImage i  
		Else
			Color 64,64,64
			DeleteFile filePath$
			Text posX+128,posY+128,"MapSegment not found",1,1
			Rect posX,posY,256,256,0					
		EndIf

	Next
Next


If MouseDown(1) Then marked=-1
drawRoute()




If KeyDown(203) Then movex = movex +50	
If KeyDown(205) Then movex = movex -50
If KeyDown(200) Then movey = movey +50	
If KeyDown(208) Then movey = movey -50
	 

Origin movex,movey




drawButton(winX-85,5,80,20,"GET",buttonTouch(winX-85,5,80,20))
If buttonHit(winX-85,5,80,20) Then updateMap()

drawButton(winX-85-85,5,80,20,"UPDATE",buttonTouch(winX-85-85,5,80,20))
If buttonHit(winX-85-85,5,80,20) Then updateMap(1)

drawButton(winX-85-85-105,5,100,20,"IMPORT GPX",buttonTouch(winX-85-85-105,5,100,20))
If buttonHit(winX-85-85-105,5,100,20) Then askFilePath()

drawButton(winX-85-85-105-105,5,100,20,"EXPORT GPX",buttonTouch(winX-85-85-105-105,5,100,20))
If buttonHit(winX-85-85-105-105,5,100,20) Then saveGPXFile(filePath$="")


drawButton(300,5,60,20,"PLAY",buttonTouch(300,5,60,20))
If buttonHit(300,5,60,20) Then marked=0:play=1:Delay 100


drawButton(5,5,100,20,"GOTO HOME",buttonTouch(5,5,100,20))
If buttonHit(5,5,100,20) Then gotoHome()

drawButton(5+105,5,100,20,"SAVE HOME",buttonTouch(5+105,5,100,20))
If buttonHit(5+105,5,100,20) Then saveHome()


Color 0,0,0 : Text MouseX()+10-movex, MouseY()+20-movey,"Lon: "+formatCoor$(mouseXCoor())+" Lat: "+formatCoor$(mouseYCoor())


 



If Not marked=-1 Then
	If KeyDown(57) Then
	coor(marked,0) = formatCoor$(mousexCoor())
	coor(marked,1) = formatCoor$(mouseYCoor())
	EndIf
	
	If KeyHit(21) Then
		movex = ((lonToX(coor(marked,0)))*-1)+(winX/2)		
		movey = ((latToY(coor(marked,1))-512)*-1)+(winY/2)
	EndIf	
		
EndIf

If KeyHit(49) And marked < points Then marked = marked + 1
If KeyHit(48) And marked > -1 Then marked = marked - 1

If play=1 Then
marked = marked + 1


	;always center
	;movex = ((lonToX(coor(marked,0)))*-1)+(winX/2)		
	;movey = ((latToY(coor(marked,1))-512)*-1)+(winY/2)


If marked > points Then marked=points : play=0
If MouseDown(1) Then play=0
EndIf






Color 0,0,0 : Text MouseX()+10-movex, MouseY()+20-movey,"Lon: "+formatCoor$(mouseXCoor())+" Lat: "+formatCoor$(mouseYCoor())
scrolling(1)
FlushMouse()
Flip Wend End
;#########################



Function drawRoute():
	For ID = 1 To points
		p2p(coor(ID-1,0),coor(ID-1,1), coor(ID,0),coor(ID,1))
	Next
	For ID = 0 To points
		point(coor(ID,0),coor(ID,1),ID)
	Next
	
End Function



Function saveGPXFile(filePath$=""):
	outFile = WriteFile("out.gpx")
	WriteLine outFile,fileHeader$
	For ID = 0 To points
		WriteLine outFile,"      <trkpt lat="+Chr(34)+coor(ID,1)+Chr(34)+" lon="+Chr(34)+coor(ID,0)+Chr(34)+">"
		If coor(ID,3)="" Then coor(ID,3)="0.0"
		WriteLine outFile,"        <ele>"+coor(ID,3)+"</ele>"
		WriteLine outFile,"        <time>"+coor(ID,2)+"</time>"
		WriteLine outFile,"      </trkpt>"
	Next
	WriteLine outFile,"    </trkseg>"
	WriteLine outFile,"  </trk>"
	WriteLine outFile,"</gpx>"
	
	CloseFile outFile 

End Function










Function loadGPXFile(filePath$):


fileHeader$ = ""
gpxFile = ReadFile(filePath$)
While Not Eof(gpxFile)
	l$ = ReadLine(gpxFile)
	
	
	
	If Instr(l$,"<trkseg") Then
		fileHeader$ = fileHeader$ + l$
		Exit
	Else
		fileHeader$ = fileHeader$ + l$+Chr(13)
	EndIf
Wend
CloseFile gpxFile


points=0
gpxFile = ReadFile(filePath$)
While Not Eof(gpxFile)
	l$ = ReadLine(gpxFile)
	l$ = Trim$(l$) 
	If Instr(l$,"<trkpt") Then 
		points = points + 1
	EndIf
Wend
CloseFile gpxFile 
points = points - 1
Dim coor$(points,3)
p = -1
gpxFile = ReadFile(filePath$)
found = 0
While Not Eof(gpxFile)
	l$ = ReadLine(gpxFile)
	l$ = Trim$(l$)
	If Instr(l$,"<trkpt") Then
		p = p + 1
		lonCoor$ = Replace( Replace(Mid(l$,Instr(l$,"lon")+5),Chr(34),"") ,">","")
		tmp$ = Replace(Replace(Mid(l$,Instr(l$,"lat")+5),Chr(34),""),">","")
		latCoor$ = Mid(tmp$,1,Instr(tmp$," "))
		tmp$ = Mid(lonCoor$,Instr(lonCoor$,".")+1)
		tmp$ = Replace(tmp$," ","") 
		While Len(tmp$) < 6
			tmp$ = tmp$ + "0"	
		Wend 
		While Len(tmp$) > 6
			tmp$ = Left(tmp$,Len(tmp$)-1)
		Wend
		lonBehindDot = Replace(tmp$," ","")
		lon = lonCoor$

		tmp$ = Mid(latCoor$,Instr(latCoor$,".")+1)
		tmp$ = Replace(tmp$," ","") 
		While Len(tmp$) < 6
			tmp$ = tmp$ + "0"	
		Wend 
		While Len(tmp$) > 6
			tmp$ = Left(tmp$,Len(tmp$)-1)
		Wend			
		latBehindDot = tmp$
		lat = latCoor$
		coor(p,0)=lon+"."+lonBehindDot		
		coor(p,1)=lat+"."+latBehindDot
		found=1
	EndIf
	
	If Instr(l$, "<time") And found=1 Then
		coor(p,2)=Replace(  Replace(  Replace(   Replace(l$,"time","")  ,"<","")  ,">","")  ,"/","")
	EndIf
	
	If Instr(l$, "<ele") And found=1 Then
		coor(p,3)=Replace(  Replace(  Replace(   Replace(l$,"ele","")  ,"<","")  ,">","")  ,"/","")
	EndIf
		
	
	
Wend

movex = ((lonToX(coor(0,0)))*-1)+(winX/2)		
movey = ((latToY(coor(0,1))-512)*-1)+(winY/2)
		
CloseFile gpxFile 
End Function




Function pointInfo(ID):
	If ID > -1 Then
	x = pointX(coor(ID,0))
	y = pointY(coor(ID,1))
	If ID = marked Then
		Color 0,0,0
		Rect x+30,y+30,200,70,1
		Line x,y,x+30,y+30
		Line x-1,y,x+30-1,y+30
		Line x+1,y,x+30+1,y+30
		Line x-1,y,x+30-1,y+30
		Line x,y+1,x+30,y+30+1
		Line x,y-1,x+30,y+30-1		
		Color 255,255,255
		Text x+35, y+35,"Point-No.: "+ID	
		Text x+35, y+50,"Lat: "+coor(ID,1)+" - Lon: "+coor(ID,0)
		Text x+35, y+65,"Time: "+coor(ID,2)
		Text x+35, y+80,"Elevation: "+coor(ID,3)
	EndIf
	EndIf
End Function


Function point(lon$,lat$,ID=0):
	x = pointX(lon$)
	y = pointY(lat$)
	
	If ID = marked Then
		Color 0,0,0
		Oval x-8,y-8,17,17,0
		Oval x-9,y-9,19,19,0
		
		Oval x-4,y-4,9,9,1
		Color 255,255,255
		Oval x-2,y-2,5,5,1
		
	EndIf
	
	
	If (MouseX()-movex>x-4 And MouseX()-movex<x+4 And MouseY()-movey>y-4 And MouseY()-movey<y+4) Then 
		pointInfo(ID)
		Color 0,0,255
		If MouseDown(1) Then 
			marked=ID
		EndIf
	Else 
		Color 0,0,0
	EndIf
	
	
	If Not ID=0 Then
		If Not ID = marked Then
		;Oval x-4,y-4,9,9,1
		;Color 255,255,255
		Oval x-2,y-2,5,5,1
		EndIf
	Else
		Color 255,0,0
		Rect x-4,y-4,9,9,1
		Color 0,0,0
		Rect x-1,y-1,3,3,1	
	EndIf
End Function


Function p2p(lon1$,lat1$, lon2$, lat2$):
	x1 = pointX(lon1$)
	y1 = pointY(lat1$)
	x2 = pointX(lon2$)
	y2 = pointY(lat2$)	
	Color 255,0,0
	Line x1,y1,x2,y2
	Line x1-1,y1,x2-1,y2
	Line x1+1,y1,x2+1,y2
	Line x1-1,y1,x2-1,y2
	Line x1,y1+1,x2,y2+1
	Line x1,y1-1,x2,y2-1
End Function


Function pointY(lat$):
	Return latToY(lat$)-512
End Function

Function pointX(lon$)
	Return lonToX(lon$)
End Function






Function gotoCoor(lon,lat):
	movex=lonToX(formatCoor$(lon))
	movey=latToY(formatCoor$(lat))
	Origin movex,movey
End Function

Function saveHome():
	homeFile = WriteFile(mapDir$+"\home.ini")
	WriteLine homeFile,movex
	WriteLine homeFile,movey
	CloseFile homeFile 
End Function

Function gotoHome():
	homeFile = ReadFile(mapDir$+"\home.ini")
	movex = ReadLine(homeFile)
	movey = ReadLine(homeFile)
	CloseFile homeFile 
End Function


Function drawButton(x,y,sizex,sizey,txt$,marked=0):
Color 0,0,0
Rect x-movex,y-movey,sizex,sizey,1
If marked = 0 Then Color 0,0,$FFFFFF Else Color 0,0,$FFFF00
Rect x-movex+2,y-movey+2,sizex-4,sizey-4,0
Color 0,0,$FFFFFF
Text x-movex+(sizex/2),y-movey+(sizey/2),txt$,1,1
End Function

Function buttonTouch(x,y,sizex,sizey):
If x < MouseX() And x+sizex > MouseX() And y < MouseY() And y+sizey > MouseY() Then 
	Return 1
Else
	Return 0
EndIf
End Function


Function buttonHit(x,y,sizex,sizey):
	If buttonTouch(x,y,sizex,sizey) = 1 And MouseDown(1) Then Return 1 Else Return 0
End Function



Function updateMap(force=0):
	sViewX = (0-movex)/256
	sViewY = (0-movey)/256
	eViewX = (0-movex+winX)/256
	eViewY = (0-movey+winY)/256
	count = 0
	For y = sViewY To eViewY
		lat = (mapZeroLat+(((y)*-1)*2039))
		For x = sViewX To eViewX
			Color 0,0,0
			Rect (winX/2)-320-movex,(winY/2)-120-movey,640,240,1
			Color 255,255,255
			Rect (winX/2)-320-movex+5,(winY/2)-120-movey+5,640-10,240-10,0
			Text (winX/2)-320-movex+10,(winY/2)-120-movey+10,"Lade KartenSegmente..."
			Color 255,0,0
			Rect (winX/2)-320-movex+10,(winY/2)-120-movey+200,((640-20)/100)*(5*count),20,1
			Color 255,255,255
			Rect (winX/2)-320-movex+10,(winY/2)-120-movey+200,640-20,20,0
			Text (winX/2)-movex,(winY/2)-120-movey+210,(5*count)+"%",1,1
			Flip		
			lon = (mapZeroLon+((x)*3422))
			getMapSegment(lat,lat+2039,lon,lon+3422,force)
			count = count + 1
		Next
	Next
End Function



Function askFilePath():
			Cls
			FlushKeys()
			Color 0,0,0
			path$ = Input("Dateipfad: ")
			If FileType(path$) = 1 Then
				loadGPXFile(path$)
			EndIf		
End Function




Function formatCoor$(coor):
	Return getIntegerAsCoor$(coor)
End Function



Function mouseXCoor():
	Return xToCoor(MouseX()-movex)
End Function

Function mouseYCoor():
	Return yToCoor(MouseY()-movey)
End Function




Function xToCoor(x):
	Return (x*lonPerPixel#)+mapZeroLon
End Function

Function yToCoor(y):
	Return (((y-256)*-1)*latPerPixel#)+mapZeroLat
End Function

Function lonToX(lon$):
	l = getCoorAsInteger(lon$)
	Return (l-mapZeroLon)/lonPerPixel#
End Function




Function latToY(lat$):
	l = getCoorAsInteger(lat$)
	Return (((l-mapZeroLat)/latPerPixel#)*-1)+Float(winY)
End Function





Function getCoorAsInteger(s$):
	a  = s$
	tmp$ = Right(s$, Len(s$)-Instr(s$, "."))
	While Len(tmp$)<6
		tmp$ = tmp$ +"0"
	Wend
	While Len(tmp$) > 6
		tmp$ = Left(tmp$,Len(tmp$)-1)
	Wend
	t$ = tmp$
	
	Return Str(a)+""+Str(t)
End Function

Function getIntegerAsCoor$(s):
	a$  = Str(s)
	tmp$ = Right(a$,6)
	b$ = Left(a$,Len(a$)-Len(tmp$))
	Return b$+"."+tmp$
End Function

Function isInView(x,y,sx,sy):
	sViewX = 0-movex
	sViewY = 0-movey
	eViewX = sViewX+winX
	eViewY = sViewY+winY
	If (sx >= sViewX) And (x <= eViewX) Then
		If (sy >= sViewY) And (y <= eViewy) Then
			Return 1
		EndIf
	EndIf
	Return 0
End Function

Function scrolling(on):
	msX = MouseXSpeed()
	msY = MouseYSpeed()
	If MouseDown(2) And on=1 Then
		movex = movex + msX
		movey = movey + msY
		Origin movex,movey 
	EndIf
End Function
;#####################################################
Function getMapSegment(sLat,eLat,sLon,eLon,force=0, size=5310):
lLat$ = getIntegerAsCoor(sLat)
hLat$ = getIntegerAsCoor(eLat)
lLon$ = getIntegerAsCoor(sLon)
hLon$ = getIntegerAsCoor(eLon)
targetPath$ = mapDir$+"\"+lLon$+","+lLat$+","+hLon$+","+hLat$+".png"
If force=0 Then
	If Not fileExists(targetPath$) Then
		If Not download_file("http://parent.tile.openstreetmap.org/cgi-bin/export?bbox="+lLon$+","+lLat$+","+hLon$+","+hLat$+"&scale="+5310+"&format=png",targetPath$) = 1 Then
			Bild=CreateImage(256,256)
			SaveImage (Bild, targetPath$)
		EndIf
	EndIf
Else
	DeleteFile targetPath$	
	If Not download_file("http://parent.tile.openstreetmap.org/cgi-bin/export?bbox="+lLon$+","+lLat$+","+hLon$+","+hLat$+"&scale="+5310+"&format=png",targetPath$) = 1 Then
		Bild=CreateImage(256,256)
		SaveImage (Bild, targetPath$)
	EndIf
EndIf
End Function

Function fileExists(path$):
	If ReadFile(path$) = 0 Then Return 0 Else Return 1
End Function

Function download_file(source$,target$)
	Local max_download_bytes = 1024 , host$, file$
	host$=splitt_fqdn(source$,1)
	file$=splitt_fqdn(source$,2)
	tcp=OpenTCPStream(host$,80)
	If Not tcp Then Return -1
	crlf$=Chr(13)+Chr(10)
	WriteLine tcp,"GET "+file$+" HTTP/1.1"+crlf$+"Host: "+host$+crlf$+"Connection:close"+crlf$+"User-Agent: bb-dwnldr"+crlf$+"Cache-Control: no-cache"+crlf$
	If Eof(tcp) Then Return -2
	Repeat
		response$=ReadLine(tcp)
	Until response$=""
	Delay(2)
	file=WriteFile(target$)
	If file=0 Then Return -3
	buffer = CreateBank(max_download_bytes)
	While Not Eof(tcp)
	   Size = ReadBytes(buffer, tcp, 0, max_download_bytes)
	   WriteBytes(buffer, file, 0, Size)
	Wend 
	CloseFile(file)
	Return 1
End Function 

Function splitt_fqdn$(url$,part)
	Local pos=0
	url$=Lower(url$)
	If Left(url$,7)="http://" Then pos=7
	If Left(url$,8)="https://"  Then pos=8
	slash_pos=Instr(url$,"/",pos+1)
	If part=1
		Return Mid(url$,pos+1,slash_pos-pos-1)
	ElseIf part=2
		Return Mid(url$,slash_pos)
	Else
		Return "Invalid part parameter!"
	EndIf 
End Function
