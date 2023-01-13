import numpy as np
import itertools
from random import randrange

from twist import Twist
import defs
import utils
import phase1
import phase2
import phase3


class Stickercube:
    #solved position of the cube
    solved = np.flip(np.array(list(itertools.product((-4,4),(-3,3),(-2,2),(-1,1)))))

    def __init__(self, position: np.ndarray=None):
        '''
        Creates a cube definition whose representation is computed by the coordinates of the stickers. Able to compute moves on negative axes.
        position: ndarray of 16 slots which contain oriented vectors of the positions of the corresponding pieces
        '''
        self.position = position

        #default to solved
        if self.position is None:
                self.position = np.copy(Stickercube.solved)
    
    def __str__(self) -> str:
        return str(self.position)
    
    def __eq__(self, other) -> bool:
        '''
        Returns true if the cubes have the same state including cube rotation
        '''
        if type(other) != Stickercube:
            raise NotImplementedError
        
        return np.all(self.position == other.position)
    
    def is_solved(self) -> bool:
        '''
        Returns whether the cube is solved in any cube rotation
        '''
        return np.all(self.reposition_new().position == Stickercube.solved)
    
    def copy(self):
        '''
        Returns a copy of the stickercube object
        '''

        return Stickercube(self.position.copy())

    def reset(self):
        '''
        Resets the cube to solved
        '''
        self.position = np.copy(Stickercube.solved)
    
    def reposition(self):
        '''
        Repositions the internal state of the cube so that the piece in all negative axes is considered solved
        '''

        #get the index of the piece in all negative axes to be the reference piece
        index = np.nonzero(np.all(np.sign(self.position) == -1, axis=1))[0][0]

        reference_piece = np.copy(self.position[index])

        #create a map for where the axes should go
        axis_map = np.empty_like(reference_piece)
        axis_map[np.abs(reference_piece)- 1] = np.arange(4)

        #resticker the cube by the reference piece (replace axes with the correct order from reference sticker)
        new_position = np.sign(self.position)
        for i in range(16):
            for j in range(4):
                new_position[i, j] *= axis_map[np.abs(self.position[i, j]) - 1] + 1


        #calculate the new positions that should be considered solved
        new_solved_position = np.empty_like(Stickercube.solved)
        new_solved_position[:, axis_map] = (np.multiply(Stickercube.solved, -np.sign(Stickercube.solved[index])))
        
        #find the permutation going from the old solved position to the new solved position
        permutation = np.empty(16, dtype=np.uint8)
        for i, piece in enumerate(np.sign(Stickercube.solved)):
            permutation[i] = [np.all(np.sign(new_solved_position)[j,:]==piece) for j in range(16)].index(True)
        
        #apply the permutation
        new_position = new_position[permutation, :]

        self.position = new_position
    
    def reposition_new(self):
        '''
        Returns a new cube with the internal state of the cube repositioned so that the piece in all negative axes is considered solved
        '''
        new_cube = self.copy()
        new_cube.reposition()
        return new_cube

    
    def twist(self, twist: Twist):
        '''
        Applies the twist to the cube
        '''
        #update the position of each piece
        for i in range(16):
            #if the piece is on the correct side then turn it
            if self.position[i, twist.axis]*twist.side >= 0:
                    self.position[i,:] = twist.rotate_vector(self.position[i])
    
    def twist_new(self, twist: Twist):
        '''
        Returns the result of applying the twist to the cube
        '''
        new_cube = self.copy()
        new_cube.twist(twist)
        return new_cube
    
    def get_permutation_list(self):
        '''
        Returns the permutation list of the pieces of the cube in the "is replaced by" format
        '''
        permutation = np.empty(15, dtype=np.uint8)

        position_sign = np.sign(self.position)[:-1]

        for i, piece in enumerate(np.sign(Stickercube.solved)[:-1]):
                permutation[i] = [np.all(position_sign[j,:]==piece) for j in range(15)].index(True)
        
        return permutation
    
    def get_a4_list(self):
        '''
        Returns the a4 orientation list of the pieces of the cube
        '''

        #remove permutation information (parity is not fixed but we only need information from two of the stickers so the parity does not matter)
        reduced = np.abs(self.position)-1

        #fix the parity of axes 0 and 1
        cond = np.prod(np.sign(self.position), axis=1) == -1
        reduced[cond, :2] = reduced[cond, 1::-1]

        #permute the orientation list so index zero holds the orientation of the piece that is in index zero
        reduced = reduced[self.get_permutation_list()]

        #get the locations of the stickers from axes 2 and 3
        sticker3 = np.where(reduced == 3)[1]
        sticker2 = np.where(reduced == 2)[1]

        #get the a4 element for each permutation list
        return utils.permutation_list_to_a4[sticker2, sticker3]
    
    @classmethod
    def from_a4_list(cls, a4_list):
        '''
        Creates a cube definition with the specified orientation
        '''

        #update the last piece which is known to be solved
        a4_list = np.append(a4_list, 0)

        #get the position from the inverse orientation matrix
        sticker_position = utils.a4_to_permutation_list[a4_list]

        #save the signs of the stickers
        signs = np.sign(Stickercube.solved)

        #fix parity of axes 0 and 1 by swapping stickers
        cond = np.prod(signs, axis=1) == -1
        sticker_position[cond, :2] = sticker_position[cond, 1::-1]

        #get the full position
        position = signs * sticker_position

        return cls(position)
    
    def to_cubiecube(self):
        '''
        Creates a cubiecube definition from this stickercube
        '''
        #reposition this cube
        new_cube = self.reposition_new()

        #convert it to a cubiecube
        return Cubiecube(new_cube.get_a4_list(), new_cube.get_permutation_list())
    
class Cubiecube:
    
    def __init__(self, a4: np.ndarray=None, permutation: np.ndarray=None):
        '''
        A cube definition represented by arrays for permutation and orientation. Provides much faster operations than stickercube but with the restriction
        that the sticker on all negative axes is fixed. Provides many method for converting to and from low level node and coordinate representations.


        a4: ndarray of the a4 orientation of 15 pieces on the cube
        permutation: ndarray of 15 pieces of the cube in the "is replaced by" format
        '''
        
        #default to solved
        if a4 is None:
            self.a4 = np.zeros(15, dtype=np.uint8)
        else: self.a4 = a4.astype(np.uint8)
        if permutation is None:
            self.permutation = np.arange(15, dtype=np.uint8)
        else: self.permutation = permutation.astype(np.uint8)
    
    def __str__(self) -> str:
        return "A4:" + str(self.a4) + " Permutation:" + str(self.permutation)
    
    def __eq__(self, other: object) -> bool:
        if type(other) != Cubiecube:
            raise NotImplementedError
        
        return np.all(self.a4 == other.a4) and np.all(self.permutation == other.permutation)
    
    def reset(self):
        '''
        Resets the cube to solved
        '''
        self.a4 = np.zeros(15, dtype=np.uint8)
        self.permutation = np.arange(15, dtype=np.uint8)

    def copy(self):
        '''
        Returns a copy of the cubeiecube object
        '''

        return Cubiecube(self.a4.copy(), self.permutation.copy())
    
    def to_int(self):
        '''
        Returns a unique integer in the range [0, 3,357,894,533,384,932,272,635,904,000) representing the cube
        '''

        index = int(self.get_O_coord()) * defs.N_HALF_I_COORD_STATES + int(self.get_I_coord()) % defs.N_HALF_I_COORD_STATES

        index = index * defs.N_IO_COORD_STATES + self.get_IO_coord()

        index = index * defs.N_C3_COORD_STATES + self.get_c3_coord()

        return index * defs.N_PHASE1_STATES + self.get_k4_coord()

    @classmethod
    def from_int(cls, int: int):
        '''
        Creates a unique cubiecube from an integer in the range [0, 3,357,894,533,384,932,272,635,904,000)
        '''

        remaining_int, k4_coord = divmod(int, defs.N_PHASE1_STATES)

        k4_list = utils.int_to_base(k4_coord, 4, 15)

        remaining_int, c3_coord = divmod(remaining_int, defs.N_C3_COORD_STATES)

        c3_list = utils.int_to_base(c3_coord, 3, 15)
        c3_list[-1] = np.mod(-np.sum(c3_list, dtype=np.int32), 3)

        remaining_int, IO_coord = divmod(remaining_int, defs.N_IO_COORD_STATES)
        O_coord, I_coord = divmod(remaining_int, defs.N_HALF_I_COORD_STATES)
        
        IO_list = utils.coord_to_IO_permutation(IO_coord)
        I_list = utils.coord_to_I_permutation(I_coord)
        O_list = utils.coord_to_O_permutation(O_coord)

        permutation = np.empty(15, dtype=np.uint8)
        permutation[IO_list] = O_list + 8
        permutation[~IO_list] = I_list

        #guarantee even permutation parity
        if not utils.permutation_parity(permutation):
            I_coord += defs.N_HALF_I_COORD_STATES
            I_list = utils.coord_to_I_permutation(I_coord)
            permutation[~IO_list] = I_list

        a4_list = k4_list * 3 + c3_list

        return cls(a4 = a4_list, permutation = permutation)
    
    @classmethod
    def random(cls):
        '''
        Returns a random cubiecube
        '''

        return cls.from_int(randrange(0, defs.N_STATES))

    def apply_move(self, move: int):
        '''
        Applies the given move to this cube
        '''

        #permute all arrays
        self.permutation = self.permutation[defs.PERMUTATION_LIST_MOVE_TABLE[move]]
        self.a4 = self.a4[defs.PERMUTATION_LIST_MOVE_TABLE[move]]

        #update orientations
        self.a4 = utils.a4_table[self.a4, defs.A4_LIST_MOVE_TABLE[move]]
    
    def apply_move_new(self, move: int):
        '''
        Returns the result of applying the given move to this cube
        '''
        new_cube = self.copy()
        new_cube.apply_move(move)

        return new_cube
    
    def apply_move_list(self, moves: list):
        '''
        Applies the moves to this cube
        '''
        for move in moves:
            self.apply_move(move)
    
    def apply_move_list_new(self, moves: list):
        '''
        Returns the result of applying the given moves to this cube
        '''
        new_cube = self.copy()

        for move in moves:
            new_cube.apply_move(move)
        
        return new_cube

    def multiply(self, other):
        '''
        Multiplies the cube state by another cube state (applies the position of another cube to this cube).
        '''

        #permute all arrays
        self.permutation = self.permutation[other.permutation]
        self.a4 = self.a4[other.permutation]

        #update orientations
        self.a4 = utils.a4_table[self.a4, other.a4]

        return

    def multiply_new(self, other):
        '''
        Returns the result of multiplying the cube state by another cube state (applies the position of another cube to this cube).
        '''
        #get a copy of this cube
        new_cube = self.copy()

        #apply the multiplication
        new_cube.multiply(other)

        return new_cube
    
    def get_k4_list(self):
        '''
        Returns the K4 orientation list for the cube
        '''

        return self.a4 // 3
    
    def get_phase1_node(self):
        '''
        Returns the phase 1 node for this state
        '''
        return phase1.Node.from_list(self.get_k4_list())
    
    @classmethod
    def from_phase1_node(cls, node: phase1.Node):
        '''
        Creates a cubiecube from the phase 1 node
        '''
        return cls(a4 = node.list * 3)
    
    def get_phase2_node(self):
        '''
        Returns the phase 2 node for this state
        '''
        return phase2.Node.from_coords(self.get_c3_coord(), self.get_IO_coord())
    
    @classmethod
    def from_phase2_node(cls, node: phase2.Node):
        '''
        Creates a cubiecube from the phase 2 node
        '''
        return cls.from_coords(node.c3, node.io, 0, 0)
    
    def get_phase3_node(self):
        '''
        Returns the phase 3 node for this state
        '''
        return phase3.Node.from_coords(self.get_I_coord(), self.get_O_coord())
    
    @classmethod
    def from_phase3_node(cls, node: phase3.Node):
        '''
        Creates a cubiecube from the phase 3 node
        '''
        return cls.from_permutation_coords(0, node.i, node.o)

    def get_c3_coord(self):
        '''
        Returns the C3 orientation coordinates for the cube
        '''

        return utils.base_to_int(self.a4[:-1] % 3, 3)
    
    @classmethod
    def from_c3_coord(cls, c3_coord):
        '''
        Creates a cubiecube definition with the given c3 orientation and solved k4 orientation and permutation
        '''

        #convert the coord to a list
        c3_list = utils.int_to_base(c3_coord, 3, 15)

        #update the second last piece with known parity
        c3_list[-1] = np.mod(-np.sum(c3_list, dtype=np.int32), 3)

        return cls(a4 = c3_list)
    
    def get_k4_coord(self):
        '''
        Returns the K4 coordinate for the state
        '''

        return utils.base_to_int(self.get_k4_list(), 4)
    
    @classmethod
    def from_k4_coord(cls, k4_coord: int):
        '''
        Creates a cubiecube with the K4 coordinate
        '''

        return cls(a4 = utils.int_to_base(k4_coord, 4, 15) * 3)
    
    def get_IO_coord(self):
        '''
        Returns the coordinate for which pieces are in the correct W axis layer
        '''

        #get indices of K pieces
        indices = np.arange(15, dtype=np.int64)[self.permutation > 7]

        #compute the id
        return int(6434 - indices[0] - (-1 + indices[1])*indices[1]/2 - (-2 + indices[2])*(-1 + indices[2])*indices[2]/6 - (-3 + indices[3])*(-2 + indices[3])*(-1 + indices[3])*indices[3]/24 - (-4 + indices[4])*(-3 + indices[4])*(-2 + indices[4])*(-1 + indices[4])*indices[4]/120 - (-5 + indices[5])*(-4 + indices[5])*(-3 + indices[5])*(-2 + indices[5])*(-1 + indices[5])*indices[5]/720 - (-6 + indices[6])*(-5 + indices[6])*(-4 + indices[6])*(-3 + indices[6])*(-2 + indices[6])*(-1 + indices[6])*indices[6]/5040)
    
    def get_I_coord(self):
        '''
        Returns the I permutation coordinate
        '''
        #remove IO information
        permutation = self.permutation[self.permutation < 8]

        #compute the I permutation coordinate and account for known parity
        coordI = 0
        
        for i in range(2, 8):
            coordI += np.sum(permutation[:i] > permutation[i]) * int(utils.factorial[i]/2)
        
        #encode the parity of the I cell as which half of the coordinates it is
        #since the parity of the cells is linked, when the coords are combined we can ignore the parity of the I cell and only use the O cell parity
        if not utils.permutation_parity(permutation[:8]):
            coordI += 20160

        return coordI
    
    def get_O_coord(self):
        '''
        Returns the O permutation coordinate
        '''
        #remove IO information
        permutation = self.permutation[self.permutation > 7] - 8
        
        #compute the O permutation coordinate
        coordO = 0
        for i in range(2, 7):
            coordO += np.sum(permutation[:i] > permutation[i]) * int(utils.factorial[i]/2)

        #encode the parity
        if not utils.permutation_parity(permutation):
            coordO += 2520

        return coordO
    
    @classmethod
    def from_permutation_coords(cls, IO_coord, I_coord, O_coord):
        '''
        Creates a cubiecube definition with solved orientation and the given permutation
        '''

        IO_list = utils.coord_to_IO_permutation(IO_coord)
        I_list = utils.coord_to_I_permutation(I_coord)
        O_list = utils.coord_to_O_permutation(O_coord)

        permutation = np.empty(15, dtype=np.uint8)
        permutation[IO_list] = O_list + 8
        permutation[~IO_list] = I_list

        return cls(permutation = permutation)
    
    @classmethod
    def from_coords(cls, c3_coord: int, IO_coord: int, I_coord: int, O_coord: int):
        '''
        Creates a cubiecube definition with orientation specified by c3 and the given permutation
        '''

        IO_list = utils.coord_to_IO_permutation(IO_coord)
        I_list = utils.coord_to_I_permutation(I_coord)
        O_list = utils.coord_to_O_permutation(O_coord)


        permutation = np.empty(15, dtype=np.uint8)
        permutation[IO_list] = O_list + 8
        permutation[~IO_list] = I_list

        #convert the coord to a list
        c3_list = utils.int_to_base(c3_coord, 3, 15)

        #update the second last piece with known parity
        c3_list[-1] = np.mod(-np.sum(c3_list, dtype=np.int32), 3)

        return cls(a4 = c3_list, permutation = permutation)