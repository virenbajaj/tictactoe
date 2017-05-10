#GamePlay.fsm

from cozmo_fsm import *
from cozmo.util import *
async def dummy(a):pass
custom_objs.declare_objects = dummy 

from cozmo.objects import CustomObject,CustomObjectTypes, CustomObjectMarkers
from MakeMap import *
from GameEst import *
import math
import CozmoClient,CozmoServer
import sys
import socket
ip = socket.gethostbyname(socket.gethostname())


class Initialize(StateNode):
    def start(self,event=None):
        print("parent: ",self.parent)
        #get marker postion. precondition: first object in world map is the corner marker 
        mx = list(robot.world.world_map.objects)[0].pose.position.x
        my = list(robot.world.world_map.objects)[0].pose.position.y
        mq = wrap_angle(list(robot.world.world_map.objects)[0].pose.rotation.angle_z.radians)
        typ = list(robot.world.world_map.objects)[0].object_type
        if typ == CustomObjectTypes.CustomType10: corner = 1
        else: corner = 3

        #(board_pose,xchips_pos,ochips_pos,start1,start2) = MakeMap(corner,(x,y,q))
        if corner == 1: self.parent.board_ori = mq
        else: self.parent.board_ori = mq + math.pi
        self.parent.map_board,self.parent.place_board = MapBoard(corner,mx,my,mq)
        self.parent.xpos,self.parent.xpick = MapXChips(corner,mx,my,mq)
        self.parent.opos,self.parent.opick = MapOChips(corner,mx,my,mq)
        self.parent.start1,self.parent.start2 = MapStart(corner,mx,my,mq)
        
        #add chips to world map
        for i in range(0,5):
            x,y = self.parent.xpos[i]
            chid = 1000+i #1000 is where Dave starts in the example code in piazza post
            robot.world.world_map.objects[chid] = ChipObj(chid,x,y)
        for i in range(0,4):
            x,y = self.parent.opos[i]
            chid = 1005+i
            robot.world.world_map.objects[chid] = ChipObj(chid,x,y)
        
        super().start()
        self.post_completion()


class PlanMove(StateNode):
    def start(self,event=None):
        super().start()
        print('start plan move')
        est_board = self.parent.est_board
        player    = self.parent.player
        level     = self.parent.level
        self.parent.move_made = 6
        #nextMove(est_board,player,level) #isWinner, isTied, or tile 0-8

        if type(self.parent.move_made)==int: #check game not over
            #want to get next chip pos 
            if player == 'X':
                chip_number = self.parent.move_count # will be max 5 
                #chip_pos    = self.parent.xpick[chip_number]
                self.parent.chip = robot.world.world_map.objects[1000+chip_number]
                self.parent.chip.obstacle = False
                self.parent.chip.x = self.parent.map_board[self.parent.move_made][0]
                self.parent.chip.y = self.parent.map_board[self.parent.move_made][1]
            else:
                #player = 'O'
                chip_number = self.parent.move_count # will be max 4
                #chip_pos    = self.parent.opick[chip_number]
                self.parent.chip = robot.world.world_map.objects[1005+chip_number]
                self.parent.chip.obstacle = False
                self.parent.chip.x = self.parent.map_board[self.parent.move_made][0]
                self.parent.chip.y = self.parent.map_board[self.parent.move_made][1]

            self.parent.est_board[self.parent.move_made] = player
            self.parent.move_count += 1
            print(self.parent.move_made)
            self.post_completion()
        
        else:
            #game is over because next move is a str
            if self.parent.move_made == "X":
                print("game over: X wins")
                self.post_data("X")

            elif self.parent.move_made == "O":
                print("game over: O wins")
                self.post_data("O")

            elif self.parent.move_made == "XO":
                print("game over: TIED")
                self.post_data("XO")


        #go and pick up 
class GoToStart(PilotToPose):
    def __init__(self,pose = Pose(0,0,0,angle_z=cozmo.util.radians(0))):
        super().__init__(pose)
        self.target_pose = pose

    def start(self,event=None):
        if self.parent != None:
            if self.parent.chip != None: self.parent.chip.obstacle = True
            if self.parent.player=='X':
                x,y = self.parent.start1
            else: 
                x,y = self.parent.start2
            self.target_pose= Pose(x,y,0,angle_z=cozmo.util.radians(self.parent.board_ori))
            print("TARGET POSEEEEEEEEEEEEEEEEEEEEEEEEEE = ",self.target_pose)
        else: print("parent is None")
        super().start()


class PickUpChip(PilotToPose):
    def __init__(self,pose=Pose(0,0,0,angle_z= cozmo.util.radians(0))):
        super().__init__(pose)
        self.target_pose = pose

    def start(self,event=None):
        print('yoooo')
        if self.parent.player == 'X':
            x,y = self.parent.xpick[0]
        else:
            x,y = self.parent.opick[self.parent.move_count-1]
        q = self.parent.board_ori

        self.target_pose = Pose(x,y,0,angle_z = cozmo.util.radians(math.pi/2+q))
        super().start(event)

        
class PlaceChip(PilotPushToPose):
    def __init__(self,pose=Pose(0,0,0,angle_z= cozmo.util.radians(0))):
        super().__init__(pose)
        self.target_pose = pose

    def start(self,event=None):
        if type(self.parent.move_made)==int: #check if game not over
            x,y = self.parent.map_board[self.parent.move_made]
            self.target_pose = Pose(x,y,0,angle_z=cozmo.util.radians(math.nan))
        super().start()


class UpdateChip(StateNode):
    def start(self,event=None):
        super().start()
        q = robot.world.particle_filter.pose[2]
        theta = wrap_angle(self.parent.board_ori-q)
        self.parent.chip.x = self.parent.chip.x - 35*cos(theta)
        self.parent.chip.y = self.parent.chip.y - 35*sin(theta)
        self.parent.chip_angle = theta
        self.post_completion()


class SendMessage(StateNode):
    def __init__(self,msg=-1,recipients=[],client=None):
        self.msg = msg # disregard placeholder -1 
        self.recipients = recipients
        self.client = client
        super().__init__()

    def start(self,event=None):
        if self.running: return
        super().start(event)
        if self.client is None: self.client = self.parent.client
        if type(self.parent.move_made) == int:
            self.msg = (self.parent.move_made,self.parent.chip_angle)
        else:
            self.msg = self.parent.move_made
        self.client.sendMessage(self.msg,sendTo=self.recipients)
        self.post_completion()


class AwaitMessage(StateNode):
    def __init__(self,senders=[],client=None):
        self.senders = senders
        self.client = client
        super().__init__()
  
    def start(self,event=None):
        if self.running: return
        super().start(event)
        if self.client is None: self.client = self.parent.client
        msgObject = self.client.awaitMessage(senders=self.senders)
    
        if msgObject["message"] == "X":
            print("game over: X wins")
            self.post_data("X")

        elif msgObject["message"] == "O":
            print("game over: O wins")
            self.post_data("O")

        elif msgObject["message"] == "XO":
            print("game over: TIED")
            self.post_data("XO")
        else:
            #msg has the tile other guy moved to
            m,chip_angle_rec =  msgObject["message"]
            self.parent.move_recieved = m 
            self.parent.est_board[self.parent.move_recieved] = self.parent.other
            if self.parent.player == 'X':
                chip = robot.world.world_map.objects[1005+self.parent.move_count-1]
                chip.x,chip.y = self.parent.map_board[m]
                chip.x += 35*cos(chip_angle_rec)
                chip.y += 35*sin(chip_angle_rec)
            else:
                chip = robot.world.world_map.objects[1000+self.parent.move_count]
                chip.x,chip.y = self.parent.map_board[m]
                chip.x += 35*cos(chip_angle_rec)
                chip.y += 35*sin(chip_angle_rec)

        #self.post_data(msgObject["message"])
        self.post_completion()


class GamePlay(StateMachineProgram): 
    def __init__(self):
        
        self.player = 'X' # 'O;
        self.other  =  'O' # 'X'
        self.level  = 70 
        if self.player == 'X':
            self.server = CozmoServer.Server().startServer() #this will print out the IP Address to connect to
            self.client = CozmoClient.Client().startClient() #this will connect to local server
        else:
            global ip 
            self.client = CozmoClient.Client().startClient()

        self.move_made = -1 # whihc tile to place chip in 
        self.move_recieved = -1
        self.move_count = 0
        self.est_board = [' ']*9
        self.map_board = []
        self.place_board = [] #
        self.xpos = []
        self.xpick = []
        self.opos = []
        self.opick = []
        self.start1 = (-1,-1)
        self.start2 = (-1,-1)
        self.board_ori = 0
        self.chip = None
        self.chip_angle = 0

        corner1 = robot.world.define_custom_box(CustomObjectTypes.CustomType10,
                                                CustomObjectMarkers.Circles2,
                                                CustomObjectMarkers.Diamonds2,
                                                CustomObjectMarkers.Diamonds3,
                                                CustomObjectMarkers.Triangles2,
                                                CustomObjectMarkers.Circles3,
                                                CustomObjectMarkers.Circles4,
                                                40,40,0.1,40,40,True)

        #corner2 = robot.world.define_custom_box(CustomObjectTypes.CustomType11,
        #                                        CustomObjectMarkers.Hexagons3,
        #                                        CustomObjectMarkers.Triangles3,
        #                                        CustomObjectMarkers.Hexagons2,
        #                                        CustomObjectMarkers.Diamonds4,
        #                                        CustomObjectMarkers.Hexagons4,
        #                                        CustomObjectMarkers.Triangles4,
        #                                        40,40,0.1,40,40,True)

        # self.pf = SLAMParticleFilter(robot, num_particles=100,
        #                              landmark_test=SLAMSensorModel.is_aruco)
        super().__init__(worldmap_viewer = True)

    def setup(self):
        """
    
            start: SetHeadAngle(-25) =C=> StateNode() =T(1)=> Initialize() 
                               =C=> GoToStart() 
                               =C=> plan: PlanMove() #PickUpChip() =C=> Say('done')
            plan =C=> move
            # #never happens - plan =D('X')=> SendMessage(-1,"all")=C=>#yay
            #plan =D('O')=> SendMessage(-1,"all")=C=>#nay
            #plan =D('XO')=> SendMessage(-1,"all")=C=>#meh
    
            move: PickUpChip() =C=> Forward(100) 
                               =CNext=> PlaceChip() =C=> UpdateChip()
                               =C=> Forward(-50)
                               =CNext=> GoToStart() =C=> Say('Done')
            
            # tellr2: SendMessage(-1,"all") =C=> wait: AwaitMessage("all") 
            # wait =C=> plan
            # wait =D('X')=> # yay
            # wait =D('0')=> # nay
            # wait =D('XO')=> # meh
    
    
        """
        
        # Code generated by genfsm on Wed May 10 15:45:32 2017:
        
        start = SetHeadAngle(-25) .set_name("start") .set_parent(self)
        statenode1 = StateNode() .set_name("statenode1") .set_parent(self)
        initialize1 = Initialize() .set_name("initialize1") .set_parent(self)
        gotostart1 = GoToStart() .set_name("gotostart1") .set_parent(self)
        plan = PlanMove() .set_name("plan") .set_parent(self)
        move = PickUpChip() .set_name("move") .set_parent(self)
        forward1 = Forward(100) .set_name("forward1") .set_parent(self)
        placechip1 = PlaceChip() .set_name("placechip1") .set_parent(self)
        updatechip1 = UpdateChip() .set_name("updatechip1") .set_parent(self)
        forward2 = Forward(-50) .set_name("forward2") .set_parent(self)
        gotostart2 = GoToStart() .set_name("gotostart2") .set_parent(self)
        say1 = Say('Done') .set_name("say1") .set_parent(self)
        
        completiontrans1 = CompletionTrans() .set_name("completiontrans1")
        completiontrans1 .add_sources(start) .add_destinations(statenode1)
        
        timertrans1 = TimerTrans(1) .set_name("timertrans1")
        timertrans1 .add_sources(statenode1) .add_destinations(initialize1)
        
        completiontrans2 = CompletionTrans() .set_name("completiontrans2")
        completiontrans2 .add_sources(initialize1) .add_destinations(gotostart1)
        
        completiontrans3 = CompletionTrans() .set_name("completiontrans3")
        completiontrans3 .add_sources(gotostart1) .add_destinations(plan)
        
        completiontrans4 = CompletionTrans() .set_name("completiontrans4")
        completiontrans4 .add_sources(plan) .add_destinations(move)
        
        completiontrans5 = CompletionTrans() .set_name("completiontrans5")
        completiontrans5 .add_sources(move) .add_destinations(forward1)
        
        cnexttrans1 = CNextTrans() .set_name("cnexttrans1")
        cnexttrans1 .add_sources(forward1) .add_destinations(placechip1)
        
        completiontrans6 = CompletionTrans() .set_name("completiontrans6")
        completiontrans6 .add_sources(placechip1) .add_destinations(updatechip1)
        
        completiontrans7 = CompletionTrans() .set_name("completiontrans7")
        completiontrans7 .add_sources(updatechip1) .add_destinations(forward2)
        
        cnexttrans2 = CNextTrans() .set_name("cnexttrans2")
        cnexttrans2 .add_sources(forward2) .add_destinations(gotostart2)
        
        completiontrans8 = CompletionTrans() .set_name("completiontrans8")
        completiontrans8 .add_sources(gotostart2) .add_destinations(say1)
        
        return self


