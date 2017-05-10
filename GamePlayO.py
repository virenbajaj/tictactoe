"""
GamePlayO.fsm

Viren Bajaj and Luka Jelenak

In this file we have the FSM for the Cozmo that will play as the O player. 
First the robot finds a custom object marker, and orients/maps out the board 
and all the chips, then heads to start. He then waits for the X cozmo to 
make his move until he get a message from cozmoX. He will then decide which
move he will make and goes to pick up the first chip, places it in the correct
box, then heads back to start and sends the other cozmo a message and 
waits for his reply. While waiting cozmoX makes his move.
"""

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


#This StateNode maps out board positions/chip positions/chip pickup positions once it
#sees a custom object marker
class Initialize(StateNode):
    def start(self,event=None):
        if self.running: return
        print("parent: ",self.parent)
        #get marker postion. 
        #precondition: first object in world map is the corner marker 
        mx = list(robot.world.world_map.objects)[0].pose.position.x
        my = list(robot.world.world_map.objects)[0].pose.position.y
        mq = wrap_angle(
          list(robot.world.world_map.objects)[0].pose.rotation.angle_z.radians)
        typ = list(robot.world.world_map.objects)[0].object_type
        if typ == CustomObjectTypes.CustomType10: corner = 1
        else: corner = 3

        #get board/chip/chip pickup/ and start positions
        if corner == 1: self.parent.board_ori = mq
        else: self.parent.board_ori = mq + math.pi
        self.parent.map_board,self.parent.place_board = MapBoard(corner,mx,my,mq)
        self.parent.xpos,self.parent.xpick = MapXChips(corner,mx,my,mq)
        self.parent.opos,self.parent.opick = MapOChips(corner,mx,my,mq)
        self.parent.start1,self.parent.start2 = MapStart(corner,mx,my,mq)
        
        #add chips to world map
        for i in range(0,5):
            x,y = self.parent.xpos[i]
            chid = 1000+i #it starts on 1000 in piazza post
            robot.world.world_map.objects[chid] = ChipObj(chid,x,y)
        for i in range(0,4):
            x,y = self.parent.opos[i]
            chid = 1005+i
            robot.world.world_map.objects[chid] = ChipObj(chid,x,y)
        
        super().start()
        self.post_completion()
'''
This node uses a tictactoe estimator based on the state of the game to choose
which move would be the best next. Sends a completion event if the game is
still in play and a data event if its over
'''
class PlanMove(StateNode):
    def start(self,event=None):
        if self.running: return
        super().start()
        print('start plan move')
        est_board = self.parent.est_board
        player    = self.parent.player
        level     = self.parent.level
        #isWinner, isTied, or tile 0-8
        self.parent.move_made = nextMove(est_board,player,level) 

        if type(self.parent.move_made)==int: #check game not over
            #want to get next chip pos 
            if player == 'X':
                chip_number = self.parent.move_count # will be max 5 
                self.parent.chip =\
                                robot.world.world_map.objects[1000+chip_number]
                self.parent.chip.obstacle = False
                self.parent.chip.x =\
                                 self.parent.map_board[self.parent.move_made][0]
                self.parent.chip.y =\
                                 self.parent.map_board[self.parent.move_made][1]
            else:
                #player = 'O'
                chip_number = self.parent.move_count # will be max 4
                self.parent.chip =\
                                 robot.world.world_map.objects[1005+chip_number]
                self.parent.chip.obstacle = False
                self.parent.chip.x =\
                                 self.parent.map_board[self.parent.move_made][0]
                self.parent.chip.y =\
                                 self.parent.map_board[self.parent.move_made][1]

            self.parent.est_board[self.parent.move_made] = player
            self.parent.move_count += 1
            self.post_completion()
        
        else:
            #game is over because next move is a str
            if self.parent.move_made == "X":
                print("game over: X wins")
                self.post_data("X")
            # we dont check for if O wins because we get that info from X 
            elif self.parent.move_made == "XO":
                print("game over: TIED")
                self.post_data("XO")

'''
This node always makes cozmo go back to start after making his move,
and if it is after making a move, cozmo will update the moved chip
so that it is an obstacle again       
'''
class GoToStart(PilotToPose):
    def __init__(self,pose = Pose(0,0,0,angle_z=cozmo.util.radians(0))):
        super().__init__(pose)
        self.target_pose = pose

    def start(self,event=None):
        if self.running: return
        if self.parent.player=='X':
            x,y = self.parent.start1
        else: 
            x,y = self.parent.start2
        self.target_pose= Pose(x,y,0,
                        angle_z=cozmo.util.radians(self.parent.board_ori-pi))
            
        super().start()
'''
Based on which move it is 0-4 for X or 0-3 for O, we go to the 
corresponding chip to pick it up
'''
class PickUpChip(PilotToPose):
    def __init__(self,pose=Pose(0,0,0,angle_z= cozmo.util.radians(0))):
        super().__init__(pose)
        self.target_pose = pose

    def start(self,event=None):
        if self.running: return
        if self.parent.player == 'X':
            x,y = self.parent.xpick[0]
        else:
            x,y = self.parent.opick[self.parent.move_count-1]
        q = self.parent.board_ori

        self.target_pose = Pose(x,y,0,angle_z = cozmo.util.radians(q-math.pi/2))
        super().start(event)
'''
This assumes cozmo already has the chip in his lift gate, based on the move that
is made, cozmo will move to the center of the correct box in the board with the
chip still in his gate 
'''       
class PlaceChip(PilotPushToPose):
    def __init__(self,pose=Pose(0,0,0,angle_z= cozmo.util.radians(0))):
        super().__init__(pose)
        self.target_pose = pose

    def start(self,event=None):
        if self.running: return
        if type(self.parent.move_made)==int: #check if game not over
            x,y = self.parent.place_board[self.parent.move_made]
            self.target_pose = Pose(x,y,0,angle_z=cozmo.util.radians(math.nan))
        super().start()
'''
After dropping off the chip, since cozmo should be in the center of the board
update the chip based on cozmos angle in the board
'''
class UpdateChip(StateNode):
    def start(self,event=None):
        if self.running: return
        super().start()
        q = robot.world.particle_filter.pose[2]
        theta = wrap_angle(self.parent.board_ori-q)
        self.parent.chip.x = self.parent.chip.x - 35*cos(theta)
        self.parent.chip.y = self.parent.chip.y - 35*sin(theta)
        self.parent.chip_angle = theta
        self.parent.chip.obstacle = True
        self.post_completion()
'''
Send a message to the awaiting cozmo about the move made and what
angle relative to the board the chip was placed
Will send data event if the game is over or completion if its still going
'''
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

'''
Waits to hear from the other cozmo which move he made based
and to update our state/world maps
'''
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
                    self.parent.est_board[self.parent.move_recieved] =\
                                                             self.parent.other
                    mc = self.parent.move_count
                    #Update worldmap with where chip was placed
                    if self.parent.player == 'X':
                        chip = robot.world.world_map.objects[1005+mc-1]
                        chip.x,chip.y = self.parent.map_board[m]
                        chip.x -= 35*cos(chip_angle_rec)
                        chip.y -= 35*sin(chip_angle_rec)
                    else:
                        chip = robot.world.world_map.objects[1000+mc]
                        chip.x,chip.y = self.parent.map_board[m]
                        chip.x -= 35*cos(chip_angle_rec)
                        chip.y -= 35*sin(chip_angle_rec)

                self.parent.message = None
                self.post_completion()


#StateMachine Program
class GamePlayO(StateMachineProgram):
    def overrideFunc(self,client,msgObj):
        if self.message is None:
            self.message = msgObj["message"]

    def __init__(self):
        self.player = 'O' # 'X'
        self.other  =  'X' # 'O'
        self.level  = 70 
        #global ip 
        self.client =\
              CozmoClient.Client(mute=False).startClient(ipaddr="128.2.178.47")

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

        super().__init__(worldmap_viewer = True)

    def setup(self):
        """
            start: SetHeadAngle(-25) =C=> StateNode() =T(1)=> Initialize() 
                               =C=> GoToStart() 
                               =C=> wait: AwaitMessage() =F=> StateNode()
                                                              =T(0.2)=> wait
            wait =C=> plan: PlanMove()
            wait =D('X')=>AnimationNode(anim_name='anim_cozmosays_badword_01')
            wait =D('0')=> AnimationNode(anim_name='anim_greeting_happy_01')
            wait =D('XO')=> AnimationNode(anim_name='anim_dizzy_reaction_medium_02')
    
            plan =C=> move
            plan =D('X')=> SendMessage(-1,"all") 
                 =C=> AnimationNode(anim_name='anim_cozmosays_badword_01')
            plan =D('XO')=> SendMessage(-1,"all")
                 =C=> AnimationNode(anim_name='anim_dizzy_reaction_medium_02')
    
            move: PickUpChip() =C=> Forward(100) 
                               =CNext=> PlaceChip() =C=> UpdateChip()
                               =C=> Forward(-75)
                               =CNext=> GoToStart()
                               =C=> tellr2
            
            tellr2: SendMessage(-1,"all") =C=> wait
            
    
    
        """
        
        # Code generated by genfsm on Wed May 10 15:39:13 2017:
        
        start = SetHeadAngle(-25) .set_name("start") .set_parent(self)
        statenode1 = StateNode() .set_name("statenode1") .set_parent(self)
        initialize1 = Initialize() .set_name("initialize1") .set_parent(self)
        gotostart1 = GoToStart() .set_name("gotostart1") .set_parent(self)
        wait = AwaitMessage() .set_name("wait") .set_parent(self)
        statenode2 = StateNode() .set_name("statenode2") .set_parent(self)
        plan = PlanMove() .set_name("plan") .set_parent(self)
        animationnode1 = AnimationNode(anim_name='anim_cozmosays_badword_01') .set_name("animationnode1") .set_parent(self)
        animationnode2 = AnimationNode(anim_name='anim_greeting_happy_01') .set_name("animationnode2") .set_parent(self)
        animationnode3 = AnimationNode(anim_name='anim_dizzy_reaction_medium_02') .set_name("animationnode3") .set_parent(self)
        sendmessage1 = SendMessage(-1,"all") .set_name("sendmessage1") .set_parent(self)
        animationnode4 = AnimationNode(anim_name='anim_cozmosays_badword_01') .set_name("animationnode4") .set_parent(self)
        sendmessage2 = SendMessage(-1,"all") .set_name("sendmessage2") .set_parent(self)
        animationnode5 = AnimationNode(anim_name='anim_dizzy_reaction_medium_02') .set_name("animationnode5") .set_parent(self)
        move = PickUpChip() .set_name("move") .set_parent(self)
        forward1 = Forward(100) .set_name("forward1") .set_parent(self)
        placechip1 = PlaceChip() .set_name("placechip1") .set_parent(self)
        updatechip1 = UpdateChip() .set_name("updatechip1") .set_parent(self)
        forward2 = Forward(-75) .set_name("forward2") .set_parent(self)
        gotostart2 = GoToStart() .set_name("gotostart2") .set_parent(self)
        tellr2 = SendMessage(-1,"all") .set_name("tellr2") .set_parent(self)
        
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
        
        datatrans1 = DataTrans('X') .set_name("datatrans1")
        datatrans1 .add_sources(wait) .add_destinations(animationnode1)
        
        datatrans2 = DataTrans('0') .set_name("datatrans2")
        datatrans2 .add_sources(wait) .add_destinations(animationnode2)
        
        datatrans3 = DataTrans('XO') .set_name("datatrans3")
        datatrans3 .add_sources(wait) .add_destinations(animationnode3)
        
        completiontrans5 = CompletionTrans() .set_name("completiontrans5")
        completiontrans5 .add_sources(plan) .add_destinations(move)
        
        datatrans4 = DataTrans('X') .set_name("datatrans4")
        datatrans4 .add_sources(plan) .add_destinations(sendmessage1)
        
        completiontrans6 = CompletionTrans() .set_name("completiontrans6")
        completiontrans6 .add_sources(sendmessage1) .add_destinations(animationnode4)
        
        datatrans5 = DataTrans('XO') .set_name("datatrans5")
        datatrans5 .add_sources(plan) .add_destinations(sendmessage2)
        
        completiontrans7 = CompletionTrans() .set_name("completiontrans7")
        completiontrans7 .add_sources(sendmessage2) .add_destinations(animationnode5)
        
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
        
        return self
