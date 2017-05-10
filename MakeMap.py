"""
MakeMap.py

Viren Bajaj and Luka Jelenak

This file returns the positions of the center of each box in the board,
the positions of where the X and O chips will be when the game starts,
and where cozmo will need to go in order to move forward 100 mm and 
pick up the corresponding chip. It is all based off of the location
and rotation of the custom object marker.

Corner 1 is the diamonds3 marker while corner 3 is the hexagons2 marker.
Corner 1 is bottom left and corner 3 is top right
"""

from math import *

#Function that rotates coordinates about point x,y by angle q
def rotate(x,y,dx,dy,q):
    if q > 0:
        return (x+dx*cos(q)-dy*sin(q),y+dx*sin(q)+dy*cos(q))
    return (x+dx*cos(q)-dy*sin(q),y+dx*sin(q)+dy*cos(q))

#this function takes in which marker was seen, and gives the positions of the
#X chips relative to each cozmo and the pick up positions
def MapXChips(corner,x,y,q):
    l = 200 # box length
    m = 40  # marker length
    cozmo_width = 70 #mm

    #Offsets for the chip positions
    off1 = 100
    off2 = 200
    
    x4 = y4 = (m+3*l) #other marker
    gap = cozmo_width*1.25 #between chips
    
    if corner == 1:
        xchips_pos  = [rotate(x,y,m+  gap,-m/2-off1,q),
                       rotate(x,y,m+2*gap,-m/2-off1,q),
                       rotate(x,y,m+3*gap,-m/2-off1,q),
                       rotate(x,y,m+4*gap,-m/2-off1,q),
                       rotate(x,y,m+5*gap,-m/2-off1,q)]

        xpickup_pos = [rotate(x,y,m+  gap,-m/2-off2,q),
                       rotate(x,y,m+2*gap,-m/2-off2,q),
                       rotate(x,y,m+3*gap,-m/2-off2,q),
                       rotate(x,y,m+4*gap,-m/2-off2,q),
                       rotate(x,y,m+5*gap,-m/2-off2,q)]
    if corner == 3:
        xchips_pos  = [rotate(x,y,x4-m-  gap,y4+m/2+off1,q),
                       rotate(x,y,x4-m-2*gap,y4+m/2+off1,q),
                       rotate(x,y,x4-m-3*gap,y4+m/2+off1,q),
                       rotate(x,y,x4-m-4*gap,y4+m/2+off1,q),
                       rotate(x,y,x4-m-5*gap,y4+m/2+off1,q)]

        xpickup_pos = [rotate(x,y,x4-m-  gap,y4+m/2+off2,q),
                       rotate(x,y,x4-m-2*gap,y4+m/2+off2,q),
                       rotate(x,y,x4-m-3*gap,y4+m/2+off2,q),
                       rotate(x,y,x4-m-4*gap,y4+m/2+off2,q),
                       rotate(x,y,x4-m-5*gap,y4+m/2+off2,q)]
    return (xchips_pos,xpickup_pos)

#this function takes in which marker was seen, and gives the positions of the
#O chips relative to each cozmo and the pick up positions
def MapOChips(corner,x,y,q):
    l = 200 # box length
    m = 40  # marker length
    cozmo_width = 70 #mm

    #Offsets for the chip positions
    off1 = 100
    off2 = 200
    
    x4 = y4 = (m+3*l) #other marker
    gap = cozmo_width*1.25 #between chips
    
    if corner == 3:
        ochips_pos  = [rotate(x,y,m+  gap,-m/2-off1,q),
                       rotate(x,y,m+2*gap,-m/2-off1,q),
                       rotate(x,y,m+3*gap,-m/2-off1,q),
                       rotate(x,y,m+4*gap,-m/2-off1,q)]

        opickup_pos = [rotate(x,y,m+  gap,-m/2-off2,q),
                       rotate(x,y,m+2*gap,-m/2-off2,q),
                       rotate(x,y,m+3*gap,-m/2-off2,q),
                       rotate(x,y,m+4*gap,-m/2-off2,q)]
    if corner == 1:
        ochips_pos  = [rotate(x,y,x4-m-  gap,y4+m/2+off1,q),
                       rotate(x,y,x4-m-2*gap,y4+m/2+off1,q),
                       rotate(x,y,x4-m-3*gap,y4+m/2+off1,q),
                       rotate(x,y,x4-m-4*gap,y4+m/2+off1,q)]

        opickup_pos = [rotate(x,y,x4-m-  gap,y4+m/2+off2,q),
                       rotate(x,y,x4-m-2*gap,y4+m/2+off2,q),
                       rotate(x,y,x4-m-3*gap,y4+m/2+off2,q),
                       rotate(x,y,x4-m-4*gap,y4+m/2+off2,q)]
    return (ochips_pos,opickup_pos)


#Based on which corner was seen, we know the start positions of where each cozmo
#will go. O goes to start 2, and X goes to start 1
def MapStart(corner,x,y,q):
    l = 200 # box length
    m = 40  # marker length
    start_diff = 150 #distance used to get start position
    
    x4 = y4 = (m+3*l) #other marker
    
    if corner == 1:
        start1 = rotate(x,y,-start_diff,-start_diff,q)
        start2 = rotate(x,y,x4+start_diff,y4+start_diff,q)
    if corner == 3:
        start2 = rotate(x,y,-start_diff,-start_diff,q)
        start1 = rotate(x,y,x4+start_diff,y4+start_diff,q)
    return (start1,start2)

#Based on the marker that was seen and the orientation, this function calculates
#the center position of each box on the tic tac toe board
def MapBoard(corner,x,y,q):
    l = 200 # box length
    m = 40  # marker length
    
    #scale factors for center of different boxes
    x1 = y1 = 0.5*(m+l) 
    x2 = y2 = 0.5*(m+3*l)
    x3 = y3 = 0.5*(m+5*l)

    if corner == 1:
        #bottom left - Diamonds3
        chip_goal = [rotate(x,y,x1,y3,q),
                     rotate(x,y,x2,y3,q),
                     rotate(x,y,x3,y3,q),
                     rotate(x,y,x1,y2,q),
                     rotate(x,y,x2,y2,q),
                     rotate(x,y,x3,y2,q),
                     rotate(x,y,x1,y1,q),
                     rotate(x,y,x2,y1,q),
                     rotate(x,y,x3,y1,q)]
    elif corner == 3:
      #top right - Hexagons2
        chip_goal = [rotate(x,y,x3,y1,q),
                     rotate(x,y,x2,y1,q),
                     rotate(x,y,x1,y1,q),
                     rotate(x,y,x3,y2,q),
                     rotate(x,y,x2,y2,q),
                     rotate(x,y,x1,y2,q),
                     rotate(x,y,x3,y3,q),
                     rotate(x,y,x2,y3,q),
                     rotate(x,y,x1,y3,q)]

    return chip_goal