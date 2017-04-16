from math import *

def MakeMap(corner,pose):
    l = 100 # box length
    m = 40  # marker length
    x,y,q = pose #x and y are the position of the markers
                 #q is the rotation of the marker
    x1 = y1 = 0.5*(m+l)
    x2 = y2 = 0.5*(m+3*l)
    x3 = y3 = 0.5*(m+5*l)
    if corner == 1:
        #bottom left
        p11 = (x+x1*cos(q)+y3*sin(q),y-x1*sin(q)+y3*cos(q))
        p12 = (x+x2*cos(q)+y3*sin(q),y-x2*sin(q)+y3*cos(q))
        p13 = (x+x3*cos(q)+y3*sin(q),y-x3*sin(q)+y3*cos(q))

        p21 = (x+x1*cos(q)+y2*sin(q),y-x1*sin(q)+y2*cos(q))
        p22 = (x+x2*cos(q)+y2*sin(q),y-x2*sin(q)+y2*cos(q))
        p23 = (x+x3*cos(q)+y2*sin(q),y-x3*sin(q)+y2*cos(q))

        p31 = (x+x1*cos(q)+y1*sin(q),y-x1*sin(q)+y1*cos(q))
        p32 = (x+x2*cos(q)+y1*sin(q),y-x2*sin(q)+y1*cos(q))
        p33 = (x+x3*cos(q)+y1*sin(q),y-x3*sin(q)+y1*cos(q))

        board_pose = [[(x+x1,y+y3),(x+x2,y+y3),(x+x3,y+y3)],
                      [(x+x1,y+y2),(x+x2,y+y2),(x+x3,y+y2)],
                      [(x+x1,y+y1),(x+x2,y+y1),(x+x3,y+y1)]]
    elif corner == 2:
        #bottom right
        p11 = (x+x3*cos(q)+y3*sin(q),y-x3*sin(q)+y3*cos(q))
        p12 = (x+x3*cos(q)+y2*sin(q),y-x3*sin(q)+y2*cos(q))
        p13 = (x+x3*cos(q)+y1*sin(q),y-x3*sin(q)+y1*cos(q))

        p21 = (x+x2*cos(q)+y3*sin(q),y-x2*sin(q)+y3*cos(q))
        p22 = (x+x2*cos(q)+y2*sin(q),y-x2*sin(q)+y2*cos(q))
        p23 = (x+x2*cos(q)+y1*sin(q),y-x2*sin(q)+y1*cos(q))

        p31 = (x+x1*cos(q)+y3*sin(q),y-x1*sin(q)+y3*cos(q))
        p32 = (x+x1*cos(q)+y2*sin(q),y-x1*sin(q)+y2*cos(q))
        p33 = (x+x1*cos(q)+y1*sin(q),y-x1*sin(q)+y1*cos(q))


        board_pose = [[(x+x3,y+y3),(x+x3,y+y2),(x+x3,y+y1)],
                      [(x+x2,y+y3),(x+x2,y+y2),(x+x2,y+y1)],
                      [(x+x1,y+y3),(x+x1,y+y2),(x+x1,y+y1)]]
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
    elif corner == 4:
        p11 = (x+x1*cos(q)+y1*sin(q),y-x1*sin(q)+y1*cos(q))
        p12 = (x+x1*cos(q)+y2*sin(q),y-x1*sin(q)+y2*cos(q))
        p13 = (x+x1*cos(q)+y3*sin(q),y-x1*sin(q)+y3*cos(q))

        p21 = (x+x2*cos(q)+y1*sin(q),y-x2*sin(q)+y1*cos(q))
        p22 = (x+x2*cos(q)+y2*sin(q),y-x2*sin(q)+y2*cos(q))
        p23 = (x+x2*cos(q)+y3*sin(q),y-x2*sin(q)+y3*cos(q))

        p31 = (x+x3*cos(q)+y1*sin(q),y-x3*sin(q)+y1*cos(q))
        p32 = (x+x3*cos(q)+y2*sin(q),y-x3*sin(q)+y2*cos(q))
        p33 = (x+x3*cos(q)+y3*sin(q),y-x3*sin(q)+y3*cos(q))

        board_pose = [[(x+x1,y+y1),(x+x1,y+y2),(x+x1,y+y3)],
                      [(x+x2,y+y1),(x+x2,y+y2),(x+x2,y+y3)],
                      [(x+x3,y+y1),(x+x3,y+y2),(x+x3,y+y3)]]

    board_pose = [[p11,p12,p13],[p21,p22,p23],[p31,p32,p33]]
    print(board_pose)




print(MakeMap(1,(0,0,pi/4)))
