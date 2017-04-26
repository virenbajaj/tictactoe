from math import *

def rotate(x,y,dx,dy,q)
    return (x+dx*cos(q)+dy*sin(q),y-dx*sin(q)+dy*cos(q))

def MapXChips(corner,x,y,q):
    l = 100 # box length
    m = 40  # marker length
    cozmo_width = 100 #mm
    start_diff = 150 #distance used to get start position
    
    #x,y,q = pose #x and y are the position of the markers
                 #q is the rotation of the marker
    
    #scale factors for center of different boxes
    x1 = y1 = 0.5*(m+l) 
    x2 = y2 = 0.5*(m+3*l)
    x3 = y3 = 0.5*(m+5*l)
    
    x4 = y4 = (m+3*l) #other marker
    gap = m*0.5+cozmo_width*1.25 #between chips
    
    if corner == 1:
        xchips_pos = [rotate(x,y,gap,-y1,q),
                      rotate(x,y,2*gap,-y1,q),
                      rotate(x,y,3*gap,-y1,q),
                      rotate(x,y,4*gap,-y1,q),
                      rotate(x,y,5*gap,-y1,q)]
        xpickup_pos = [rotate(x,y,gap,-y2,q),
                       rotate(x,y,2*gap,-y2,q),
                       rotate(x,y,3*gap,-y2,q),
                       rotate(x,y,4*gap,-y2,q),
                       rotate(x,y,5*gap,-y2,q)]
    if corner == 3:
        xchips_pos = [rotate(x,y,x4-gap,y4+y1,q),
                      rotate(x,y,x4-2*gap,y4+y1,q),
                      rotate(x,y,x4-3*gap,y4+y1,q),
                      rotate(x,y,x4-4*gap,y4+y1,q),
                      rotate(x,y,x4-5*gap,y4+y1,q)]

        xpickup_pos = [rotate(x,y,x4-gap,y4+y2,q),
                       rotate(x,y,x4-2*gap,y4+y2,q),
                       rotate(x,y,x4-3*gap,y4+y2,q),
                       rotate(x,y,x4-4*gap,y4+y2,q),
                       rotate(x,y,x4-5*gap,y4+y2,q)]
    return (xchips_pos,xpickup_pos)
    
def MapOChips(corner,x,y,q):
    l = 100 # box length
    m = 40  # marker length
    cozmo_width = 100 #mm
    #start_diff = 150 #distance used to get start position
    
    #x,y,q = pose #x and y are the position of the markers
                 #q is the rotation of the marker
    
    #scale factors for center of different boxes
    x1 = y1 = 0.5*(m+l) 
    x2 = y2 = 0.5*(m+3*l)
    #x3 = y3 = 0.5*(m+5*l)
    
    x4 = y4 = (m+3*l) #other marker
    gap = m*0.5+cozmo_width*1.25 #between chips
    
    if corner == 1:
        ochips_pos = [rotate(x,y,x4-gap,y4+y1,q),
                      rotate(x,y,x4-2*gap,y4+y1,q),
                      rotate(x,y,x4-3*gap,y4+y1,q),
                      rotate(x,y,x4-4*gap,y4+y1,q)]
        
        opickup_pos = [rotate(x,y,x4-gap,y4+y2,q),
                      rotate(x,y,x4-2*gap,y4+y2,q),
                      rotate(x,y,x4-3*gap,y4+y2,q),
                      rotate(x,y,x4-4*gap,y4+y2,q)]
    if corner == 3:
        ochips_pos = [rotate(x,y,gap,-y1,q),
                      rotate(x,y,2*gap,-y1,q),
                      rotate(x,y,3*gap,-y1,q),
                      rotate(x,y,4*gap,-y1,q)]
        opickup_pos = [rotate(x,y,gap,-y2,q),
                      rotate(x,y,2*gap,-y2,q),
                      rotate(x,y,3*gap,-y2,q),
                      rotate(x,y,4*gap,-y2,q)]
    return (ochips_pos,opickup_pos)


def MapStart(corner,x,y,q):
    l = 100 # box length
    m = 40  # marker length
    #cozmo_width = 100 #mm
    start_diff = 150 #distance used to get start position
    
    #x,y,q = pose #x and y are the position of the markers
                 #q is the rotation of the marker
    
    #scale factors for center of different boxes
    #x1 = y1 = 0.5*(m+l) 
    #x2 = y2 = 0.5*(m+3*l)
    #x3 = y3 = 0.5*(m+5*l)
    
    x4 = y4 = (m+3*l) #other marker
    #gap = m*0.5+cozmo_width*1.25 #between chips
    
    if corner == 1:
        start1 = rotate(x,y,-start_diff,-start_diff,q)
        start2 = rotate(x,y,x4+start_diff,y4+start_diff,q)
    if corner == 3:
        start2 = rotate(x,y,-start_diff,-start_diff,q)
        start1 = rotate(x,y,x4+start_diff,y4+start_diff,q)
    return (start1,start2)
    
def MapBoard(corner,x,y,q):
    l = 100 # box length
    m = 40  # marker length
    cozmo_width = 100 #mm
    start_diff = 150 #distance used to get start position
    
    #x,y,q = pose #x and y are the position of the markers
                 #q is the rotation of the marker
    
    #scale factors for center of different boxes
    x1 = y1 = 0.5*(m+l) 
    x2 = y2 = 0.5*(m+3*l)
    x3 = y3 = 0.5*(m+5*l)
    
    x4 = y4 = (m+3*l) #other marker
    gap = m*0.5+cozmo_width*1.25 #between chips

    if corner == 1:
        #bottom left
        p11 = rotate(x,y,x1,y3,q) #(x+x1*cos(q)+y3*sin(q),y-x1*sin(q)+y3*cos(q))
        p12 = rotate(x,y,x2,y3,q) #(x+x2*cos(q)+y3*sin(q),y-x2*sin(q)+y3*cos(q))
        p13 = rotate(x,y,x3,y3,q) #(x+x3*cos(q)+y3*sin(q),y-x3*sin(q)+y3*cos(q))

        p21 = rotate(x,y,x1,y2,q) #(x+x1*cos(q)+y2*sin(q),y-x1*sin(q)+y2*cos(q))
        p22 = rotate(x,y,x2,y2,q) #(x+x2*cos(q)+y2*sin(q),y-x2*sin(q)+y2*cos(q))
        p23 = rotate(x,y,x3,y2,q) #(x+x3*cos(q)+y2*sin(q),y-x3*sin(q)+y2*cos(q))

        p31 = rotate(x,y,x1,y1,q) #(x+x1*cos(q)+y1*sin(q),y-x1*sin(q)+y1*cos(q))
        p32 = rotate(x,y,x2,y1,q) #(x+x2*cos(q)+y1*sin(q),y-x2*sin(q)+y1*cos(q))
        p33 = rotate(x,y,x3,y1,q) #(x+x3*cos(q)+y1*sin(q),y-x3*sin(q)+y1*cos(q))

        board_pose = [[(x+x1,y+y3),(x+x2,y+y3),(x+x3,y+y3)],
                      [(x+x1,y+y2),(x+x2,y+y2),(x+x3,y+y2)],
                      [(x+x1,y+y1),(x+x2,y+y1),(x+x3,y+y1)]]

     

        xchips_pos = [rotate(x,y,gap,-y1,q),
                      rotate(x,y,2*gap,-y1,q),
                      rotate(x,y,3*gap,-y1,q),
                      rotate(x,y,4*gap,-y1,q),
                      rotate(x,y,5*gap,-y1,q)]
        xpickup_pos = [rotate(x,y,gap,-y2,q),
                       rotate(x,y,2*gap,-y2,q),
                       rotate(x,y,3*gap,-y2,q),
                       rotate(x,y,4*gap,-y2,q),
                       rotate(x,y,5*gap,-y2,q)]

        ochips_pos = [rotate(x,y,x4-gap,y4+y1,q),
                      rotate(x,y,x4-2*gap,y4+y1,q),
                      rotate(x,y,x4-3*gap,y4+y1,q),
                      rotate(x,y,x4-4*gap,y4+y1,q)]
        
        opickup_pos = [rotate(x,y,x4-gap,y4+y2,q),
                      rotate(x,y,x4-2*gap,y4+y2,q),
                      rotate(x,y,x4-3*gap,y4+y2,q),
                      rotate(x,y,x4-4*gap,y4+y2,q)]
        
        start1 = rotate(x,y,-start_diff,-start_diff,q)
        start2 = rotate(x,y,x4+start_diff,y4+start_diff,q)

    # elif corner == 2:
    #     #bottom right
    #     p11 = (x+x3*cos(q)+y3*sin(q),y-x3*sin(q)+y3*cos(q))
    #     p12 = (x+x3*cos(q)+y2*sin(q),y-x3*sin(q)+y2*cos(q))
    #     p13 = (x+x3*cos(q)+y1*sin(q),y-x3*sin(q)+y1*cos(q))

    #     p21 = (x+x2*cos(q)+y3*sin(q),y-x2*sin(q)+y3*cos(q))
    #     p22 = (x+x2*cos(q)+y2*sin(q),y-x2*sin(q)+y2*cos(q))
    #     p23 = (x+x2*cos(q)+y1*sin(q),y-x2*sin(q)+y1*cos(q))

    #     p31 = (x+x1*cos(q)+y3*sin(q),y-x1*sin(q)+y3*cos(q))
    #     p32 = (x+x1*cos(q)+y2*sin(q),y-x1*sin(q)+y2*cos(q))
    #     p33 = (x+x1*cos(q)+y1*sin(q),y-x1*sin(q)+y1*cos(q))


    #     board_pose = [[(x+x3,y+y3),(x+x3,y+y2),(x+x3,y+y1)],
    #                   [(x+x2,y+y3),(x+x2,y+y2),(x+x2,y+y1)],
    #                   [(x+x1,y+y3),(x+x1,y+y2),(x+x1,y+y1)]]
    elif corner == 3:
        p11 = (x+x3*cos(q)+y1*sin(q),y-x3*sin(q)+y1*cos(q))
        p12 = (x+x2*cos(q)+y1*sin(q),y-x2*sin(q)+y1*cos(q))
        p13 = (x+x1*cos(q)+y1*sin(q),y-x1*sin(q)+y1*cos(q))

        p21 = (x+x3*cos(q)+y2*sin(q),y-x3*sin(q)+y2*cos(q))
        p22 = (x+x2*cos(q)+y2*sin(q),y-x2*sin(q)+y2*cos(q))
        p23 = (x+x1*cos(q)+y2*sin(q),y-x1*sin(q)+y2*cos(q))

        p31 = (x+x3*cos(q)+y3*sin(q),y-x3*sin(q)+y3*cos(q))
        p32 = (x+x2*cos(q)+y3*sin(q),y-x2*sin(q)+y3*cos(q))
        p33 = (x+x1*cos(q)+y3*sin(q),y-x1*sin(q)+y3*cos(q))


        board_pose = [[(x+x3,y+y1),(x+x2,y+y1),(x+x1,y+y1)],
                      [(x+x3,y+y2),(x+x2,y+y2),(x+x1,y+y2)],
                      [(x+x3,y+y3),(x+x2,y+y3),(x+x1,y+y3)]]



        ochips_pos = [rotate(x,y,gap,-y1,q),
                      rotate(x,y,2*gap,-y1,q),
                      rotate(x,y,3*gap,-y1,q),
                      rotate(x,y,4*gap,-y1,q)]
        opickup_pos = [rotate(x,y,gap,-y2,q),
                      rotate(x,y,2*gap,-y2,q),
                      rotate(x,y,3*gap,-y2,q),
                      rotate(x,y,4*gap,-y2,q)]

        xchips_pos = [rotate(x,y,x4-gap,y4+y1,q),
                      rotate(x,y,x4-2*gap,y4+y1,q),
                      rotate(x,y,x4-3*gap,y4+y1,q),
                      rotate(x,y,x4-4*gap,y4+y1,q),
                      rotate(x,y,x4-5*gap,y4+y1,q)]

        xpickup_pos = [rotate(x,y,x4-gap,y4+y2,q),
                       rotate(x,y,x4-2*gap,y4+y2,q),
                       rotate(x,y,x4-3*gap,y4+y2,q),
                       rotate(x,y,x4-4*gap,y4+y2,q),
                       rotate(x,y,x4-5*gap,y4+y2,q)]


        
        start2 = rotate(x,y,-start_diff,-start_diff,q)
        start1 = rotate(x,y,x4+start_diff,y4+start_diff,q)
    # elif corner == 4:
    #     p11 = (x+x1*cos(q)+y1*sin(q),y-x1*sin(q)+y1*cos(q))
    #     p12 = (x+x1*cos(q)+y2*sin(q),y-x1*sin(q)+y2*cos(q))
    #     p13 = (x+x1*cos(q)+y3*sin(q),y-x1*sin(q)+y3*cos(q))

    #     p21 = (x+x2*cos(q)+y1*sin(q),y-x2*sin(q)+y1*cos(q))
    #     p22 = (x+x2*cos(q)+y2*sin(q),y-x2*sin(q)+y2*cos(q))
    #     p23 = (x+x2*cos(q)+y3*sin(q),y-x2*sin(q)+y3*cos(q))

    #     p31 = (x+x3*cos(q)+y1*sin(q),y-x3*sin(q)+y1*cos(q))
    #     p32 = (x+x3*cos(q)+y2*sin(q),y-x3*sin(q)+y2*cos(q))
    #     p33 = (x+x3*cos(q)+y3*sin(q),y-x3*sin(q)+y3*cos(q))

    #     board_pose = [[(x+x1,y+y1),(x+x1,y+y2),(x+x1,y+y3)],
    #                   [(x+x2,y+y1),(x+x2,y+y2),(x+x2,y+y3)],
    #                   [(x+x3,y+y1),(x+x3,y+y2),(x+x3,y+y3)]]

    board_pose = [[p11,p12,p13],[p21,p22,p23],[p31,p32,p33]]
    return [p11,p12,p13,p21,p22,p23,p31,p32,p33]
    #return (board_pose,xchips_pos,ochips_pos,start1,start2,xpickup_pos,opickup_pos)
    print(board_pose)




print(MakeMap(1,(0,0,pi/4)))
