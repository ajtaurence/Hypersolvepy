# About
Hypersolvepy is an efficient 3-phase 2^4 Rubik's cube solver written in python. This is a proof of concept version. A [more optimized version](https://github.com/ajtaurence/Hypersolve) is currently being written in Rust. It takes an MC4D log file containing a scrambled 2^4 and returns another log file containing the solution. It produces iteratively shorter solutions, the more time it is given. Solutions to random state scrambles are typically around 27 moves (STM) after only a few seconds of searching. For short scrambles (less than about 5 moves), an optimal solution can be found and verified within a reasonable amount of time.

# Setup
1. Install Python 3.9 (newer versions should work but v3.9 is known to work).
1. Install the requirements from `requirements.txt` by running the command `pip install -r requirements.txt` from the Hypersolvepy folder.
1. Download the data files from [here](https://drive.google.com/drive/folders/1oIYpc9K3mTgnPWm1wu6VghDQYvtfaavp?usp=share_link) and put them into the Hypersolvepy folder with the python files. Optionally you may generate them yourself. Upon running `main.py`, Hypersolvepy will generate any missing data files. It may take the better part of a day even on a good computer to generate all the files. Even when done generating, large pruning tables can take a while to save to disk since they must be compressed, so be patient. The table sizes for `phase1.prun` and `phase2.prun` are flexible. If they take too long to generate for your liking then you can edit the table size in `defs.py`. The variables controlling this are `PHASE1_PRUNE_DEPTH` and `PHASE2_PRUNE_DEPTH`. Decreasing them by 1 should be sufficient. Do not touch any other variables in this folder. If you change the pruning depth then you must delete the corresponding pruning table file so it may be regenerated. Otherwise you will get an error.
1. Run the `main.py` file. It may take up to several minutes to load all the data into memory. It will prompt you to select an MC4D log file. Then it will ask for a termination time. This is the time that Hypersolvepy will continue searching for a better solution after having found one. The timer restarts upon every solution. Upon completing the search, a save dialog will appear promting you to save the MC4D log file containing the solution.
1. Happy hypercubing!

# Details
Hypersolvepy splits the solving process into 3 phases:

1. Orient pieces along a primary axis.
1. Orient pieces along a secondary axis while permuting pieces to the correct side of the primary axis.
1. Finish solving the cube.

A solution to each phase is found using the iterative deepening A* (IDA*) algorithm. For the heuristic, a pruning tabe is computed for each phase in a breadth first manner to some depth, giving a lower bound on the number of moves required for a solution to that phase for any state. 

To generate full solutions, Hypersolve iterates through every phase 1 solution (in order of increasing move count) and for each solution it will iterate through every phase 2 solution (in order of increasing move count) and look up the length of the phase 3 solution from the phase 3 pruning table which is computed to full depth. Any time a shorter solution is found, the new solution is saved. If the solution up to a certain phase becomes longer than the shortest solution then that branch is terminated and the process starts over with a new solution from the previous phase. If the phase 1 solution becomes longer than the shortest solution, then the shortest solution is known to be optimal and the search can be ended.

For computing moves, the primary method is to use [move tables](http://kociemba.org/math/movetables.htm), explained by Herbert Kociemba for his 2-phase algorithm. Unfortunately the phase 1 cube representation cannot be broken down into multiple independent coordinates which is required if one is to use move tables. So for phase 1, a [cubie level](http://kociemba.org/math/cubielevel.htm) representation is used instead.
