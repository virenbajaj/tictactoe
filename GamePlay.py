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

class GoToStart(PilotToPose):
    def __init__(self,pose = Pose(0,0,0,angle_z= cozmo.util.radians(0))):
        super().__init__(pose)
        self.target_pose = pose

    def start(self,event=None):
        if self.parent != None:
            if self.parent.chip != None: self.parent.chip.obstacle = True
            if self.parent.player=='X':
                x,y = self.parent.start1
            else: 
                x,y = self.parent.start2
            self.target_pose= Pose(x,y,0,angle_z = cozmo.util.radians(self.parent.board_ori))
            print("TARGET POSEEEEEEEEEEEEEEEEEEEEEEEEEE = ",self.target_pose)
        else: print("parent is None")
        super().start()

class Initialize(StateNode):
    def start(self,event=None):
        print("parent: ",self.parent)
        #get marker postion. precondition: first object in world map is the corner marker 
        mx = list(robot.world.world_map.objects)[0].pose.position.x
        my = list(robot.world.world_map.objects)[0].pose.position.y
        mq = list(robot.world.world_map.objects)[0].pose.rotation.angle_z.radians
        typ = list(robot.world.world_map.objects)[0].object_type
        if typ == CustomObjectTypes.CustomType10: corner = 1
        else: corner = 3

        #(board_pose,xchips_pos,ochips_pos,start1,start2) = MakeMap(corner,(x,y,q))
        self.parent.board_ori = mq
        self.parent.map_board = MapBoard(corner,mx,my,mq)
        self.parent.xpos,self.parent.xpick = MapXChips(corner,mx,my,mq)
        self.parent.opos,self.parent.opick = MapOChips(corner,mx,my,mq)
        self.parent.start1,self.parent.start2 = MapStart(corner,mx,my,mq)
        
        #add chips to world map
        temp_obs = []
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
        
        est_board = self.parent.est_board
        player = self.parent.player
        self.parent.move_made = nextMove(est_board,player) #isWinner, isTied, or tile 0-8
        

        if type(self.parent.move_made)==int: #check game not over
            #want to get next chip pos 
            if player == 'X':
                chip_number = self.parent.move_count # will be max 5 
                chip_pos    = xpickup_pos[chip_number]
                self.parent.chip = robot.world.world_map.objects[1000+chip_number]
                self.parent.chip.obstacle = False
                self.parent.chip.x = self.parent.map_board[self.parent.move_made][0]
                self.parent.chip.y = self.parent.map_board[self.parent.move_made][1]
            else:
                #player = 'O'
                chip_number = self.parent.move_count # will be max 4
                chip_pos    = opickup_pos[chip_number]
                self.parent.chip = robot.world.world_map.objects[1005+chip_number]
                self.parent.chip.obstacle = False
                self.parent.chip.x = self.parent.map_board[self.parent.move_made][0]
                self.parent.chip.y = self.parent.map_board[self.parent.move_made][1]

            self.parent.est_board[self.parent.move_made] = player
            self.parent.move_count += 1
        
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


class PickUpChip(PilotToPose):
    def __init__(self,pose=None):
        super().__init__(pose)

    def start(self,event):
        x,y = event.data 
        q = self.parent.board_ori
        self.target_pose = Pose(x,y,0,angle_z = cozmo.util.radians(math.pi - q))
        super().start(event)

        
class PlaceChip(PilotPushToPose):
    def __init__(self,event=None):
        if type(self.parent.move_made)==int: #check if game not over
            x,y = self.parent.map_board[self.parent.move_made]
        super().__init__(Pose(x,y,0))


class SendMessage(StateNode):
    def __init__(self,msg,recipients=[],client=None):
        self.msg = self.parent.move_made # disregard placeholder -1 
        self.recipients = recipients
        self.client = client
        super().__init__()

    def start(self,event=None):
        if self.running: return
        super().start(event)
        if self.client is None: self.client = self.parent.client
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
            m = self.parent.move_recieved = msgObject["message"]
            self.parent.est_board[self.parent.move_recieved] = self.parent.other
            if self.parent.player == 'X':
                chip = robot.world.world_map.objects[1005+self.parent.move_count-1]
                chip.x,chip.y = self.parent.map_board[m]
            else:
                chip = robot.world.world_map.objects[1000+self.parent.move_count]
                chip.x,chip.y = self.parent.map_board[m]

        #self.post_data(msgObject["message"])
        self.post_completion()

class GamePlay(StateMachineProgram):
    
    def __init__(self):
        print("POSEEEEEEEE : ", cozmo.util.Pose(0,0,0,angle_z=cozmo.util.radians(0)))
        self.player = 'X' # 'O;
        self.other  =  'O' # 'X'
        if self.player == 'X':
            self.server = CozmoServer.Server().startServer() #this will print out the IP Address to connect to
            self.client = CozmoClient.Client().startClient() #this will connect to local server
        else:
            global ip 
            self.client = CozmoClient.Client().startClient(ipaddr=ip)

        self.move_made = -1 # whihc tile to place chip in 
        self.move_recieved = -1
        self.move_count = 0
        self.est_board = [' ']*9
        self.map_board = []
        self.xpos = []
        self.xpick = []
        self.opos = []
        self.opick = []
        self.start1 = (-1,-1)
        self.start2 = (-1,-1)
        self.board_ori = 0
        self.chip = None


        corner1 = robot.world.define_custom_box(CustomObjectTypes.CustomType10,
                                                CustomObjectMarkers.Circles2,
                                                CustomObjectMarkers.Diamonds2,
                                                CustomObjectMarkers.Circles4,
                                                CustomObjectMarkers.Triangles2,
                                                CustomObjectMarkers.Circles3,
                                                CustomObjectMarkers.Diamonds3,
                                                40,40,0.1,40,40,True)

        corner2 = robot.world.define_custom_box(CustomObjectTypes.CustomType11,
                                                CustomObjectMarkers.Hexagons3,
                                                CustomObjectMarkers.Triangles3,
                                                CustomObjectMarkers.Hexagons2,
                                                CustomObjectMarkers.Diamonds4,
                                                CustomObjectMarkers.Hexagons4,
                                                CustomObjectMarkers.Triangles4,
                                                40,40,0.1,40,40,True)

        super().__init__()

    def setup(self):
        """
    
            start: StateNode() =T(1)=> Initialize() 
                               =C=> GoToStart() 
                               =C=> plan: PlanMove()
            plan =D(int)=> move
            # #never happens - plan =D('X')=> SendMessage(-1,"all")=C=>#yay
            # plan =D('O')=> SendMessage(-1,"all")=C=>#nay
            # plan =D('XO')=> SendMessage(-1,"all")=C=>#meh
    
            move: PickUpChip() =C=> Say("Done")#Forward(100) 
            #                  =CNext=> PlaceChip()
            #                  =C=> GoToStart() 
            #                  =C=> tellr2
            
            # tellr2: SendMessage(-1,"all") =C=> wait: AwaitMessage("all") 
            # wait =C=> plan
            # wait =D('X')=> # yay
            # wait =D('0')=> # nay
            # wait =D('XO')=> # meh
    
    
        """
        
        # Code generated by genfsm on Tue May  2 23:19:52 2017:
        
        start = StateNode() .set_name("start") .set_parent(self)
        initialize1 = Initialize() .set_name("initialize1") .set_parent(self)
        gotostart1 = GoToStart() .set_name("gotostart1") .set_parent(self)
        plan = PlanMove() .set_name("plan") .set_parent(self)
        move = PickUpChip() .set_name("move") .set_parent(self)
        say1 = Say("Done") .set_name("say1") .set_parent(self)
        
        timertrans1 = TimerTrans(1) .set_name("timertrans1")
        timertrans1 .add_sources(start) .add_destinations(initialize1)
        
        completiontrans1 = CompletionTrans() .set_name("completiontrans1")
        completiontrans1 .add_sources(initialize1) .add_destinations(gotostart1)
        
        completiontrans2 = CompletionTrans() .set_name("completiontrans2")
        completiontrans2 .add_sources(gotostart1) .add_destinations(plan)
        
        datatrans1 = DataTrans(int) .set_name("datatrans1")
        datatrans1 .add_sources(plan) .add_destinations(move)
        
        completiontrans3 = CompletionTrans() .set_name("completiontrans3")
        completiontrans3 .add_sources(move) .add_destinations(say1)
        
        return self


