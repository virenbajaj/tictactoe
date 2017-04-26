#GamePlay.fsm

from cozmo_fsm import *
def dummy(a,b):pass
custom_objs.declare_objects = dummy 
from cozmo_objects import CustomObject,CustomObjectTypes, CustomObjectMarkers
from MakeMap import *


class GoToStart(PilotToPose):
	def __init__(self,pose=None):
		super().__init__(pose)
		x,y = self.parent.start1
		self.target_pose=Pose(x,y,0,angle_z = cozmo.util.radians(self.parent.board_ori))

class Initialize(StateNode):
	def start(self,event=None):
		#(board_pose,xchips_pos,ochips_pos,start1,start2) = MakeMap(corner,(x,y,q))
		self.parent.board_ori = q
		self.parent.map_board = MapBoard(corner,x,y,q)
		self.parent.xpos,self.parent.xpick = MapXChips(corner,x,y,q)
		self.parent.opos,self.parent.opick = MapOChips(corner,x,y,q)
		self.parent.start1,self.parent.start2 = MapStart(corner,x,y,q)
		
		robot.world.rrt.auto_obstacles = False
		
		temp_obs = []
		for i in range(0,5):
			temp_obs.append(Circle(center = transform.point(self.parent.xpos[i]),radius=10))
		for i in range(0,4):
			temp_obs.append(Circle(center = transform.point(self.parent.opos[i]),radius=10))


class GamePlay(StateMachineProgram):
	def start(self):
		self.move_made = -1
		self.move_recieved = -1
		self.move_count = 0
		self.est_board = [' ']*9
		self.map_board = []
		self.xpos = []
		self.opos = []
		self.start1 = (-1,-1)
		self.start2 = (-1,-1)
		self.board_ori = 0

		corner1 = robot.world.define_custom_box(CustomObjectTypes.CustomType10,
												CustomObjectMarkers.Cirlces2,
												CustomObjectMarkers.Diamonds2,
												CustomObjectMarkers.Hexagons2,
												CustomObjectMarkers.Triangles2,
												CustomObjectMarkers.Circles3,
												CustomObjectMarkers.Diamonds3,
												40,40,0,1,40,40,True)

		corner2 = robot.world.define_custom_box(CustomObjectTypes.CustomType11,
												CustomObjectMarkers.Hexagons3,
												CustomObjectMarkers.Triangles3,
												CustomObjectMarkers.Circles4,
												CustomObjectMarkers.Diamonds4,
												CustomObjectMarkers.Hexagons4,
												CustomObjectMarkers.Triangles4,
												40,40,0,1,40,40,True)

		super().start()

 def setup(self):
     """
    
    		start: StateNode() =T(1)=> Initialize() =C=> GoToStart() =C=> plan
    		plan: PlanMove() =D()=> move 
    		move: PickUpChip() =C=> PlaceChip() =C=> GoToStart() =C=> TellR2()
     """
     
     # Code generated by genfsm on Mon Apr 24 15:39:54 2017:
     
     start = StateNode() .set_name("start") .set_parent(self)
     initialize1 = Initialize() .set_name("initialize1") .set_parent(self)
     gotostart1 = GoToStart() .set_name("gotostart1") .set_parent(self)
     plan = PlanMove() .set_name("plan") .set_parent(self)
     move = PickUpChip() .set_name("move") .set_parent(self)
     placechip1 = PlaceChip() .set_name("placechip1") .set_parent(self)
     gotostart2 = GoToStart() .set_name("gotostart2") .set_parent(self)
     tellr21 = TellR2() .set_name("tellr21") .set_parent(self)
     
     timertrans1 = TimerTrans(1) .set_name("timertrans1")
     timertrans1 .add_sources(start) .add_destinations(initialize1)
     
     completiontrans1 = CompletionTrans() .set_name("completiontrans1")
     completiontrans1 .add_sources(initialize1) .add_destinations(gotostart1)
     
     completiontrans2 = CompletionTrans() .set_name("completiontrans2")
     completiontrans2 .add_sources(gotostart1) .add_destinations(plan)
     
     datatrans1 = DataTrans() .set_name("datatrans1")
     datatrans1 .add_sources(plan) .add_destinations(move)
     
     completiontrans3 = CompletionTrans() .set_name("completiontrans3")
     completiontrans3 .add_sources(move) .add_destinations(placechip1)
     
     completiontrans4 = CompletionTrans() .set_name("completiontrans4")
     completiontrans4 .add_sources(placechip1) .add_destinations(gotostart2)
     
     completiontrans5 = CompletionTrans() .set_name("completiontrans5")
     completiontrans5 .add_sources(gotostart2) .add_destinations(tellr21)
     
     return self

