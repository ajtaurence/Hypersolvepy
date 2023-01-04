import numpy as np
import itertools

import defs
from twist import Twist, Direction
from cube_internal import Stickercube, Cubiecube

def gen_twist_order():
    '''
    Returns a list of twist objects in the order they are defined in this program
    '''
    #generate all unique offsets (not negatives of each other)
    uoffsets = list(itertools.product((-1,0,1),(-1,0,1),(-1,0,1)))
    uoffsets = np.array(uoffsets)[int(len(uoffsets)/2)+1:]

    #final list of all twists
    twists = [[], [], []]

    working_cube = Stickercube()

    for twist_axis in range(4):
        for offset in uoffsets:
            #number of twists to return to solved
            twist_identity = np.sum(np.abs(offset))  

            #twist different number of times depending on move type
            for i in range([3,1,2][twist_identity-1]):  
                tw = Twist(twist_axis, Direction(offset), 1, i+1)

                cubiecube = working_cube.twist_new(tw).to_cubiecube()

                IO_permutation_coord = cubiecube.get_IO_coord()

                #if the cube preserves IO permutation and orientation then save it for Phase 3
                if IO_permutation_coord == 0 and np.all(cubiecube.a4 == 0):
                    phaseIndex = 0
                #if the cube does not destroy k4 orientation then save it for phase 2
                elif np.all(cubiecube.get_k4_list() == 0):
                    phaseIndex = 1
                else:
                    phaseIndex = 2

                twists[phaseIndex].append(tw)

    #return flattened list
    return  [j for i in twists for j in i]


def gen_twist_mc4d_names():
    '''
    Generates the mc4d names in the log file for each move
    '''

    twists = gen_twist_order()
    
    names = []

    for i in range(defs.N_PHASE1_MOVES):
        twist = twists[i].to_mc4d()

        names.append(" ".join([",".join([str(item) for item in mov]) for mov in twist]))
    
    return tuple(names)
      

def gen_twist_names():
    '''
    Generates the mc4d codes in the log file for each move
    '''

    twists = gen_twist_order()[1]
    
    names = []

    for i in range(defs.N_PHASE1_MOVES):
        names.append(twists[i].to_piece_notation())
    
    return tuple(names)

def gen_twist_composition_table():
    '''
    Creates a table which gives the result of applying a move and then another
    '''
    #255 means no cancel
    table = np.full((defs.N_PHASE1_MOVES, defs.N_PHASE1_MOVES), 255, dtype=np.uint8)

    cube = Cubiecube()

    for i in range(defs.N_PHASE1_MOVES):

        cube1 = cube.apply_move_new(i)

        for j in range(defs.N_PHASE1_MOVES):
            
            cube2 = cube1.apply_move_new(j)

            #if the moves cancel to nothing then encode with 254
            if cube2 == cube:
                table[i, j] = 254
                break

            for k in range(defs.N_PHASE1_MOVES):
                if cube2 == cube.apply_move_new(k):
                    table[i, j] = k
                    break
    return table

#print(gen_twist_composition_table().tolist())
#print(gen_twist_names())
#ALL_TWIST_AXES, ALL_TWISTS_TWIST, ALL_TWIST_CUBIECUBES = gen_twist_data()



