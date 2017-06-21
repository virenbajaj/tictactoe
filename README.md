# Cozmo vs Cozmo Tic Tac Toe
Viren Bajaj and Luka Jelenak
## Watch it in action
https://www.youtube.com/watch?v=KWnk6U6LCTM&t=24s. 

And take a look at our presentation attached as presentation.pdf 

## Goals
The goal of this project is to succesfully have two cozmos play each other in a
game of tic tac toe without any human intervention. This means the two cozmos
would have to be able to communicate, know the positions they want to go to,
and be able to choose which move would be the best.

## How it was done
For our game, we assumed the the board would be made up of 20 mm x 20 mm squares
with a custom object marker in the bottom left corner, and one in the top right
corner. From these markers, when cozmo sees them, he would be able to find the 
relative positions of the board, and the chips, and a start position. We had a 
file called MakeMap.py which did all the mapping.

The cozmos would go to their start positions. Then, using code written by
Jordan, one cozmo would decide which move he would make based on the state of 
the game using our GameEst.py file, which contained an estimator in which you 
could vary the AI intelligence.

Then using our State Machine Program, in either GamePlayX.fsm or GamePlayO.fsm
based on which cozmo is playing as which player. The FSM will make cozmo go to
start before each move, and while one cozmo is waiting for communication,
the other is choosing a move, executing it after catching a chip, and finally
returning to start before telling the other cozmo which move was made and where
it was made. The paths that cozmo executes is calculated and executed by
professor Touretzky's path planner.

We had to have our own local version of simple_cli, since the general one 
imported some premade custom object markers, which took precedence over the
markers we used, and thus had incorrect values used for the mapping.


