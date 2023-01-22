from log import Log
from cube_internal import Stickercube, Cubiecube
from twist import Twist
import solver
import defs

'''
High level wrapper for Stickercube.
'''


class Cube:

    def __init__(self) -> None:
        self.log = Log()
        self.state = Stickercube()
    
    def copy(self):
        new = Cube()
        new.log = self.log.copy()
        new.state = self.state.copy()

        return new

    def twist(self, twist: Twist):
        '''
        Appplies the given twist to the cube
        '''
        self.state.twist(twist)
        self.log.append_twist(twist)
    
    @classmethod
    def from_stickercube(cls, stickercube: Stickercube):
        '''
        Creates a Cube from a scrambled Stickercube definition
        '''
        cube = cls.__new__(cls)
        cube.log = Log()
        cube.state = stickercube
        cube.log.scrambling = False
        
        return cube
    
    @classmethod
    def from_log(cls):
        '''
        Creates a cube from a log file
        '''
        new_cube = cls.__new__(cls)
        new_cube.log = Log.open()

        if new_cube.log is None:
            return None

        new_cube.state = Stickercube()

        for twist in new_cube.log.scramble:
            new_cube.state.twist(twist)
        for twist in new_cube.log.solution:
            new_cube.state.twist(twist)
        
        return new_cube
    
    def solve(self, search_depth = None):
        '''
        Solves the cube

        search_depth: maximum solution length desired
        '''
        #set scrambling to false
        self.log.scrambling = False

        
        try:
            #for every solution
            for solution in solver.solve(self.state, search_depth):
                print("Found solution length:", len(solution))
                
                newcube = self.copy()

                #apply the moves
                for move_string in " ".join(defs.TWIST_MC4D_NAMES[move] for move in solution).split():
                    newcube.twist(Twist.from_mc4d_string(move_string))
                
                #save the log file
                newcube.log.save()
        except KeyboardInterrupt:
            return
        
        print("Optimal solution length:", len(solution))
        



    def optimal_solve(self):
        '''
        Solves the cube optimally via iterative deepening A*
        '''

        #set scrambling to false
        self.log.scrambling = False

        try:
            depth = 0
            while True:
                #find solution
                for solution in solver.solve(self.state, depth):
                    print("Found optimal solution of length:", len(solution))
                    
                    newcube = self.copy()

                    #apply the moves
                    for move_string in " ".join(defs.TWIST_MC4D_NAMES[move] for move in solution).split():
                        newcube.twist(Twist.from_mc4d_string(move_string))
                    
                    #save the log file
                    newcube.log.save()

                    #optimal solution was found so return
                    return
                
                depth += 1
                print("Lower bound:", depth)

        except KeyboardInterrupt:
            return