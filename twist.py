import numpy as np
from scipy.linalg import expm
import itertools

#relative signs of the axes in this program as in MC4D
dir_axis_signs = np.array([1,-1,1,-1])

def get_mc4d_twist_parameters():
    '''
    Returns a list of tuples (axis, direction, side) defining twists in the order that they are defined in MC4D
    '''
    #initialize empty list to be returned 
    mc4d_axis_dir_side = []

    #order of axes as defined in MC4D
    axis_list = [3,2,1,0,0,1,2,3]

    #positive and negative axis side order as defined in MC4D
    axis_side_list = [1,-1,1,-1,1,-1,1,-1]

    for i in range(8):
        #empty list for sorting pieces
        twist_dir = [[],[],[],[]]

        for coord in list(itertools.product((-1,0,1),(-1,0,1),(-1,0,1))):
            
            #adjust signs based on new definition and negating positive axis
            coord = np.flip(coord)*np.delete(dir_axis_signs, axis_list[i]) * (dir_axis_signs[axis_list[i]])

            #append the direction to the list
            twist_dir[3-sum(np.abs(coord))].append(coord)

        #flatten the list
        twist_dir = np.array([sticker for piece_type in twist_dir for sticker in piece_type])
    
        #pack twist axis, direction, and side into tuple and append to list
        mc4d_axis_dir_side += zip(np.repeat(axis_list[i], 27), twist_dir, np.repeat(axis_side_list[i], 27))


    return tuple(mc4d_axis_dir_side)

'''
Coordinate system: X Y Z W
X: L R axis
Y: B F axis
Z: D U axis
W: O I axis
'''

class Direction:
    def __init__(self, vector: np.ndarray) -> None:
        '''
        Defines a twist direction which is a 3D rotation axis that preserves cubic symmetry under rotations other than 360 degrees.

        vector: 3 component vector representing a 3D twist axis
        '''

        #rotation axis
        self.vec = np.asarray(vector, dtype=int)

        #sum of the vector
        self.sum = np.sum(vector)

        #L1 norm of the vector
        self.l1_norm = np.sum(np.abs(vector))

        #L2 norm of the vector
        self.l2_norm = np.sqrt(np.sum(vector**2))

        #define order to be the number of rotations which preserve cubic symmetry in 360 degrees
        if self.l1_norm == 1:
                self.order = 4
        else: self.order = self.l1_norm
    
    def copy(self):
        '''
        Returns a copy of the direction
        '''
        return Direction(self.vec)

    def flip(self):
        '''
        Flips the rotation axis
        '''
        self.vec = -self.vec
    
    def __eq__(self, other: object) -> bool:
        if type(other) != Direction:
            raise NotImplementedError
        return np.all(self.vec == other.vec)
    
    def __repr__(self) -> str:
        return str(self.vec)

    def __str__(self) -> str:
        return repr(self)


class Twist:
    mc4d_order_twist_parameters = get_mc4d_twist_parameters()

    def __init__(self, axis: int, direction: Direction, side: int, amount: int) -> None:
        '''
        Creates a twist definition. Twist properties should not be modified once instance is created.

        axis: axis which is unchanged by the twist
        direction: 3D axis of rotation in hyperplane
        amount: number of times to apply the base twist (can be negative)
        side: 1, -1, or 0 for which side of the axis to twist (0 is both)
        '''
        self.axis=axis
        self.dir=direction
        self.amount=amount
        self.side=side

        self.normalize_amount()

        #create the rotation matrix
        self.matrix = self.get_rotation_matrix()
    
    def __eq__(self, other: object) -> bool:
        if type(other) != Twist:
            raise NotImplementedError
        return np.all(self.matrix == other.matrix) and self.side == other.side
    
    def __str__(self) -> str:
        return self.to_piece_notation()

    def __repr__(self) -> str:
        return self.to_piece_notation()
    
    def does_nothing(self) -> bool:
        return self.dir.l1_norm == 0 or self.amount % self.dir.order == 0
    
    def normalize_amount(self):
        '''
        Normalizes the twist amount to -1, 0, 1, or 2
        '''
        #get the positive amount
        self.amount = self.amount % self.dir.order
        #if the reverse amount is shorter then choose that
        if np.abs(self.amount - self.dir.order) < self.amount:
            self.amount -= self.dir.order
    
    @classmethod
    def random_mc4d(cls):
        '''
        Creates a random twist with the same random distribution as MC4D
        '''

        #get a random sticker vector within a face
        rand_dir = np.random.randint(-1, 2, 3)
        while np.all(rand_dir == 0):
            rand_dir = np.random.randint(-1, 2, 3)
        rand_dir = Direction(rand_dir)

        #get a random axis
        rand_axis = np.random.randint(0, 4)

        #get a random amount to twist (-1 or 1)
        rand_amount = np.random.randint(0, 2)*2 - 1

        # no need to choose a random side (slice mask) since the random 
        # sticker choice already covers that
        
        return cls(rand_axis, rand_dir, 1, rand_amount)

    @classmethod
    def random(cls):
        '''
        Creates a random twist
        '''
        #get a random sticker vector within a face
        rand_dir = np.random.randint(-1, 2, 3)
        while np.all(rand_dir == 0):
            rand_dir = np.random.randint(-1, 2, 3)
        rand_dir = Direction(rand_dir)

        #get a random axis
        rand_axis = np.random.randint(0, 4)

        #get a random amount to twist
        rand_amount = np.random.randint(1, rand_dir.order)       
        
        return cls(rand_axis, rand_dir, 1, rand_amount)
    
    @classmethod
    def from_mc4d(cls, mc4d_code: int, amount: int, layer: int):
        '''
        Creates a twist from MC4D definition
        mc4d_code: code that mc4d uses to define twists
        amount: number of times to apply the base twist
        '''
        #get parameters of the twist
        axis, dir, side = Twist.mc4d_order_twist_parameters[mc4d_code]

        #if the layer is the second layer then swap the side and the direction (alternatively you could swap the amount instead of the dir)
        if layer == 2:
                side = -side
                dir = -dir

        #3 corresponds to both layers (cube rotation)
        elif layer == 3:
                #make cube rotations happen from positive side so when we search for them we can just choose the positive one
                if side == -1:
                    side = -side
                    dir = -dir
                side = 0

        #create the twist object
        return cls(axis, Direction(dir), side, amount)
    
    @classmethod
    def from_mc4d_string(cls, string: str):
        return cls.from_mc4d(*tuple(int(string.split(",")[i]) for i in range(3)))

    def to_mc4d(self):
        '''
        Returns the MC4D move parameters for the twist as: mc4d_code, amount, layer. Two moves are returned as a list if necessary
        '''
        #search for the mc4d code
        for i in range(len(Twist.mc4d_order_twist_parameters)):
            if (Twist.mc4d_order_twist_parameters[i][0] == self.axis and np.all(Twist.mc4d_order_twist_parameters[i][1] == self.dir.vec) and (Twist.mc4d_order_twist_parameters[i][2] == np.sign(self.side + 0.5))):
                mc4d_code = i
                break

        #twist just one layer or both
        if self.side == 0:
                layer = 3
        else: layer = 1

        #if it's a double move then return two moves
        if self.amount == 2:
                return 2*[(mc4d_code, 1, layer)]
        
        #otherwise return just one
        else: return [(mc4d_code, self.amount, layer)]
    
    def to_mc4d_string(self):
        '''
        Returns the MC4D move parameters for the twist as a string: 'mc4d_code, amount, layer'. The string contains two moves if necessary.
        '''
        return " ".join([",".join([str(item) for item in mov]) for mov in self.to_mc4d()])
    
    def to_piece_notation(self):
        '''
        Returns the piece notation for the twist
        '''

        #if the move does nothing then return an empty string
        if self.does_nothing():
            return ""

        #names for the axes indexed as (side, axis)
        axis_names = np.array([['L','B','D','O'],['R','F','U','I']])

        
        #variables different from class values
        amount = self.amount
        direction = self.dir.copy()
        #flip the axis depending on its relative sign
        if dir_axis_signs[self.axis] < 0:      
            direction.flip()
            amount = -amount


        #normalize the amount to -1, 0, 1, 2
        #get the positive amount
        amount = self.amount % direction.order
        #if the reverse amount is shorter then choose that
        if np.abs(amount - direction.order) < amount:
            amount -= direction.order

        #get the first letter as the axis
        first = axis_names[round((self.side+1.1)/2), self.axis]       

        #get the subsequent letters based on the axis of rotation
        next = axis_names[np.array((direction.vec + 1)/2, dtype=int), np.delete(np.arange(4), self.axis)]
        
        #delete the unused axis letters
        next = np.delete(next, np.where(direction.vec == 0)).tolist()
        
        #full move name
        move = first + "".join(next)

        #denote cube rotations by starting with lowercase letters
        if self.side == 0:
            move = move.lower()
                               
        #calculate the amount of the move
        if amount == -1:
            modifier = ""
        elif amount == 2:
            modifier = '2'
        elif amount == 1:
            modifier = "'"
        elif amount == 0:
            return ""

        return move + modifier

    def get_rotation_matrix(self):
        '''
        Return the rotation matrix associated with this twist
        '''

        #if the twist does nothing then return the identity matrix
        if self.does_nothing():
            return np.eye(4, dtype=int)

        #get 3D rotation matrix for the hyperplane #for some reason we need to manipulate the sign of the twist (probably because this is a left handed coordinate system and I'm not sure how to define the 4th axis anyway)
        matrix3 = np.round(expm(np.cross(np.eye(3), np.sign(self.side + 0.1) * self.dir.vec/self.dir.l2_norm * (self.amount*2*np.pi/self.dir.order)))).astype(int)

        #identity vector for the twist axis
        identity_axis = np.zeros(4)
        identity_axis[self.axis] = 1

        #insert an identity row/column on the twist axis
        matrix4 = np.insert(matrix3, self.axis, np.zeros(3), axis=0)
        matrix4 = np.insert(matrix4, self.axis, identity_axis, axis=1)

        return matrix4.astype(np.matrix)

    def rotate_vector(self, vector: np.ndarray):
        '''
        Returns the vector rotated by the twist object. Does not account for side.
        '''
        return np.dot(self.matrix, vector)


