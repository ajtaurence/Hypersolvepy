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
        new_cube.state = Stickercube()

        for twist in new_cube.log.scramble:
            new_cube.state.twist(twist)
        for twist in new_cube.log.solution:
            new_cube.state.twist(twist)
        
        return new_cube
    
    def solve(self, terminate_time: float or None = None):
        '''
        Solves the cube

        terminate_time: if the time since the last solution is greater than this then the solution is returned
        '''
        #set scrambling to false
        self.log.scrambling = False

        solution = solver.solve(self.state, terminate_time)

        for move_string in " ".join(defs.TWIST_MC4D_NAMES[move] for move in solution).split():
            self.twist(Twist.from_mc4d_string(move_string))

    