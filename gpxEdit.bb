Graphics 754,796,32,2
SetBuffer BackBuffer()





map = LoadImage("map.PNG")


mapInfo = ReadFile("map.ini")
While Not Eof(mapInfo)
	ReadLine(mapInfo)
	Lines = Lines + 1
Wend
CloseFile mapInfo 
points = Lines/4


Dim point#(points-1, 3)

mapInfo = ReadFile("map.ini")
pID = 0
While Not Eof(mapInfo)
	point(pID, 0) = ReadLine(mapInfo)
	point(pID, 1) = ReadLine(mapInfo)
	point(pID, 2) = ReadLine(mapInfo)
	point(pID, 3) = ReadLine(mapInfo)
	pID = pID + 1
Wend
CloseFile mapInfo 

Print point(0, 0)
Print point(0, 1)
Print point(0, 2)
Print point(0, 3)
Print 
Print 
Print xTo#(point(0, 0))
Print yTo#(point(0, 1))
Print
Print
Print
Print point(1, 0)
Print point(1, 1)
Print point(1, 2)
Print point(1, 3)
Print 
Print 
Print xTo#(point(1, 0))
Print yTo#(point(1, 1))


WaitKey()
While Not KeyHit(1) : Cls
DrawImage map,0,0


Color 0,0,0
Oval MouseX()-3,MouseY()-3,7,7,1


Text MouseX()+20,MouseY()+20,xTo(MouseX()) + " : " + yTo(MouseY())


Flip Wend End





Function xTo#(posX):
diffX = Abs(point(0, 0)-point(1, 0))
diffLon# = Abs(point(0, 3)-point(1, 3))
lon# = diffLon# / diffX 
zeroXlon# = ((lon#*point(1, 0))*-1)+point(1, 2)
Return zeroXlon#+(posX*lon#)
End Function


Function yTo#(posY):
diffY = Abs(point(0, 1)-point(1, 1))
diffLat# = Abs(point(0, 2)-point(1, 2))
lat# = diffLat# / diffY
zeroYlat# = ((lat#*point(1, 1))*-1)+point(1, 3)
Return zeroYlat#+(posY*lat#)
End Function
