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
#import socket
#ip = socket.gethostbyname(socket.gethostname())


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
            self.target_pose= Pose(x,y,0,angle_z=cozmo.util.radians(self.parent.board_ori-pi))
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
            x,y = self.parent.place_board[self.parent.move_made]
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
    def __init__(self):
        super().__init__()
        self.ready = False

    def start(self,event=None):
        if self.running: return
        super().start(event)
        if not self.ready:
            self.parent.message = None
            self.ready = True
            self.post_failure()
        else:
            if self.parent.message is None:
                self.post_failure()
            else:
                if self.parent.message == "X":
                    print("game over: X wins")
                    self.post_data("X")
                    return
                elif self.parent.message == "O":
                    print("game over: O wins")
                    self.post_data("O")
                    return
                elif self.parent.message == "XO":
                    print("game over: TIED")
                    self.post_data("XO")
                    return
                else:
                    #msg has the tile other guy moved to
                    m,chip_angle_rec = self.parent.message
                    print(m,chip_angle_rec)
                    self.parent.move_recieved = m 
                    self.parent.est_board[self.parent.move_recieved] = self.parent.other
                    if self.parent.player == 'X':
                        chip = robot.world.world_map.objects[1005+self.parent.move_count-1]
                        chip.x,chip.y = self.parent.map_board[m]
                        chip.x -= 35*cos(chip_angle_rec)
                        chip.y -= 35*sin(chip_angle_rec)
                    else:
                        chip = robot.world.world_map.objects[1000+self.parent.move_count]
                        chip.x,chip.y = self.parent.map_board[m]
                        chip.x -= 35*cos(chip_angle_rec)
                        chip.y -= 35*sin(chip_angle_rec)
                        #self.post_data(msgObject["message"])
                self.post_completion()

# class AwaitMessage(StateNode):
#     def __init__(self,senders=[],client=None):
#         self.senders = senders
#         self.client = client
#         super().__init__()
  
#     def start(self,event=None):
#         if self.running: return
#         super().start(event)
#         if self.client is None: self.client = self.parent.client
#         msgObject = self.client.awaitMessage(senders=self.senders)
    
#         if msgObject["message"] == "X":
#             print("game over: X wins")
#             self.post_data("X")

#         elif msgObject["message"] == "O":
#             print("game over: O wins")
#             self.post_data("O")

#         elif msgObject["message"] == "XO":
#             print("game over: TIED")
#             self.post_data("XO")
#         else:
#             #msg has the tile other guy moved to
#             m,chip_angle_rec =  msgObject["message"]
#             print(m,chi[_angle_rec])
#             self.parent.move_recieved = m 
#             self.parent.est_board[self.parent.move_recieved] = self.parent.other
#             if self.parent.player == 'X':
#                 chip = robot.world.world_map.objects[1005+self.parent.move_count-1]
#                 chip.x,chip.y = self.parent.map_board[m]
#                 chip.x -= 35*cos(chip_angle_rec)
#                 chip.y -= 35*sin(chip_angle_rec)
#             else:
#                 chip = robot.world.world_map.objects[1000+self.parent.move_count]
#                 chip.x,chip.y = self.parent.map_board[m]
#                 chip.x -= 35*cos(chip_angle_rec)
#                 chip.y -= 35*sin(chip_angle_rec)

#         #self.post_data(msgObject["message"])
#         self.post_completion()


class GamePlayO(StateMachineProgram):
    def overrideFunc(self,client,msgObj):
        if self.message is None:
            self.message = msgObj["message"]

    def __init__(self):
        self.player = 'O' # 'X'
        self.other  =  'X' # 'O'
        self.level  = 70 
        if self.player == 'X':
            self.server = CozmoServer.Server().startServer() #this will print out the IP Address to connect to
            self.client = CozmoClient.Client().startClient() #this will connect to local server
        else:
            #global ip 
            self.client = CozmoClient.Client(mute=False).startClient(ipaddr="128.2.178.47")

        self.message = None
        self.client.processFunction = self.overrideFunc

        self.move_made = -1 # whihc tile to place chip in 
        self.move_recieved = -1
        self.move_count = 0
        self.est_board = [' ']*9
        self.map_board = []
        self.place_board = []
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

        corner2 = robot.world.define_custom_box(CustomObjectTypes.CustomType11,
                                                CustomObjectMarkers.Hexagons3,
                                                CustomObjectMarkers.Triangles3,
                                                CustomObjectMarkers.Hexagons2,
                                                CustomObjectMarkers.Diamonds4,
                                                CustomObjectMarkers.Hexagons4,
                                                CustomObjectMarkers.Triangles4,
                                                40,40,0.1,40,40,True)

        # self.pf = SLAMParticleFilter(robot, num_particles=100,
        #                              landmark_test=SLAMSensorModel.is_aruco)
        super().__init__(worldmap_viewer = True)

    def setup(self):
        """
    
    
            # StateNode() =N=> wait: AwaitMessage() =F=> StateNode() =T(0.2)=> wait
            # wait =C=> Say('Gottem')
            start: SetHeadAngle(-25) =C=> StateNode() =T(1)=> Initialize() 
                               =C=> GoToStart() 
                               =C=> wait: AwaitMessage() =F=> StateNode()
                                                              =T(0.2)=> wait
    
            wait =C=> plan: PlanMove()
            wait =D('O')=> Say('Yay')
            wait =D('X')=> Say('Crap')
            wait =D('XO')=> Say('Oh well')
    
            plan =C=> move
            # #never happens - plan =D('O')=> SendMessage(-1,"all")=C=>#yay
            plan =D('X')=> SendMessage(-1,"all") =C=> Say('Crap')
            plan =D('XO')=> SendMessage(-1,"all") =C=> Say('Oh well')
    
            move: PickUpChip() =C=> Forward(100) 
                               =CNext=> PlaceChip() =C=> UpdateChip()
                               =C=> Forward(-75)
                               =CNext=> GoToStart()
                               =C=> tellr2
            
            tellr2: SendMessage(-1,"all") =C=> wait
            wait =C=> plan
            wait =D('O')=> Say('Yay')
            wait =D('X')=> Say('Crap')
            wait =D('XO')=> Say('Oh well')
    
    
        """
        
        # Code generated by genfsm on Fri May  5 00:38:23 2017:
        
        start = SetHeadAngle(-25) .set_name("start") .set_parent(self)
        statenode1 = StateNode() .set_name("statenode1") .set_parent(self)
        initialize1 = Initialize() .set_name("initialize1") .set_parent(self)
        gotostart1 = GoToStart() .set_name("gotostart1") .set_parent(self)
        wait = AwaitMessage() .set_name("wait") .set_parent(self)
        statenode2 = StateNode() .set_name("statenode2") .set_parent(self)
        plan = PlanMove() .set_name("plan") .set_parent(self)
        say1 = Say('Yay') .set_name("say1") .set_parent(self)
        say2 = Say('Crap') .set_name("say2") .set_parent(self)
        say3 = Say('Oh well') .set_name("say3") .set_parent(self)
        sendmessage1 = SendMessage(-1,"all") .set_name("sendmessage1") .set_parent(self)
        say4 = Say('Crap') .set_name("say4") .set_parent(self)
        sendmessage2 = SendMessage(-1,"all") .set_name("sendmessage2") .set_parent(self)
        say5 = Say('Oh well') .set_name("say5") .set_parent(self)
        move = PickUpChip() .set_name("move") .set_parent(self)
        forward1 = Forward(100) .set_name("forward1") .set_parent(self)
        placechip1 = PlaceChip() .set_name("placechip1") .set_parent(self)
        updatechip1 = UpdateChip() .set_name("updatechip1") .set_parent(self)
        forward2 = Forward(-75) .set_name("forward2") .set_parent(self)
        gotostart2 = GoToStart() .set_name("gotostart2") .set_parent(self)
        tellr2 = SendMessage(-1,"all") .set_name("tellr2") .set_parent(self)
        say6 = Say('Yay') .set_name("say6") .set_parent(self)
        say7 = Say('Crap') .set_name("say7") .set_parent(self)
        say8 = Say('Oh well') .set_name("say8") .set_parent(self)
        
        completiontrans1 = CompletionTrans() .set_name("completiontrans1")
        completiontrans1 .add_sources(start) .add_destinations(statenode1)
        
        timertrans1 = TimerTrans(1) .set_name("timertrans1")
        timertrans1 .add_sources(statenode1) .add_destinations(initialize1)
        
        completiontrans2 = CompletionTrans() .set_name("completiontrans2")
        completiontrans2 .add_sources(initialize1) .add_destinations(gotostart1)
        
        completiontrans3 = CompletionTrans() .set_name("completiontrans3")
        completiontrans3 .add_sources(gotostart1) .add_destinations(wait)
        
        failuretrans1 = FailureTrans() .set_name("failuretrans1")
        failuretrans1 .add_sources(wait) .add_destinations(statenode2)
        
        timertrans2 = TimerTrans(0.2) .set_name("timertrans2")
        timertrans2 .add_sources(statenode2) .add_destinations(wait)
        
        completiontrans4 = CompletionTrans() .set_name("completiontrans4")
        completiontrans4 .add_sources(wait) .add_destinations(plan)
        
        datatrans1 = DataTrans('O') .set_name("datatrans1")
        datatrans1 .add_sources(wait) .add_destinations(say1)
        
        datatrans2 = DataTrans('X') .set_name("datatrans2")
        datatrans2 .add_sources(wait) .add_destinations(say2)
        
        datatrans3 = DataTrans('XO') .set_name("datatrans3")
        datatrans3 .add_sources(wait) .add_destinations(say3)
        
        completiontrans5 = CompletionTrans() .set_name("completiontrans5")
        completiontrans5 .add_sources(plan) .add_destinations(move)
        
        datatrans4 = DataTrans('X') .set_name("datatrans4")
        datatrans4 .add_sources(plan) .add_destinations(sendmessage1)
        
        completiontrans6 = CompletionTrans() .set_name("completiontrans6")
        completiontrans6 .add_sources(sendmessage1) .add_destinations(say4)
        
        datatrans5 = DataTrans('XO') .set_name("datatrans5")
        datatrans5 .add_sources(plan) .add_destinations(sendmessage2)
        
        completiontrans7 = CompletionTrans() .set_name("completiontrans7")
        completiontrans7 .add_sources(sendmessage2) .add_destinations(say5)
        
        completiontrans8 = CompletionTrans() .set_name("completiontrans8")
        completiontrans8 .add_sources(move) .add_destinations(forward1)
        
        cnexttrans1 = CNextTrans() .set_name("cnexttrans1")
        cnexttrans1 .add_sources(forward1) .add_destinations(placechip1)
        
        completiontrans9 = CompletionTrans() .set_name("completiontrans9")
        completiontrans9 .add_sources(placechip1) .add_destinations(updatechip1)
        
        completiontrans10 = CompletionTrans() .set_name("completiontrans10")
        completiontrans10 .add_sources(updatechip1) .add_destinations(forward2)
        
        cnexttrans2 = CNextTrans() .set_name("cnexttrans2")
        cnexttrans2 .add_sources(forward2) .add_destinations(gotostart2)
        
        completiontrans11 = CompletionTrans() .set_name("completiontrans11")
        completiontrans11 .add_sources(gotostart2) .add_destinations(tellr2)
        
        completiontrans12 = CompletionTrans() .set_name("completiontrans12")
        completiontrans12 .add_sources(tellr2) .add_destinations(wait)
        
        completiontrans13 = CompletionTrans() .set_name("completiontrans13")
        completiontrans13 .add_sources(wait) .add_destinations(plan)
        
        datatrans6 = DataTrans('O') .set_name("datatrans6")
        datatrans6 .add_sources(wait) .add_destinations(say6)
        
        datatrans7 = DataTrans('X') .set_name("datatrans7")
        datatrans7 .add_sources(wait) .add_destinations(say7)
        
        datatrans8 = DataTrans('XO') .set_name("datatrans8")
        datatrans8 .add_sources(wait) .add_destinations(say8)
        
        return self


