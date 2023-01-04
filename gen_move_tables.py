import numpy as np
from tqdm import trange

import defs
from cube_internal import Cubiecube, Stickercube
import gen_twist_data
import utils

#coordinate move tables are only possible for the entire A4 group but this is too large so just save the a4 and permutation list for each move instead 
def gen_k4_and_permutation_move_table():
    print("Generating A4 and Permutation list move table...")

    #get the cubiecubes
    twistcubes = gen_twist_data.gen_twist_order()
    cubiecubes = [Stickercube().twist_new(twistcubes[i]).to_cubiecube() for i in range(len(twistcubes))]

    #initialize empty move table for the k4 and permutation list in phase 1
    a4_list_table = np.empty((defs.N_PHASE1_MOVES, 15), dtype=np.uint8)
    permutation_list_table = np.empty((defs.N_PHASE1_MOVES, 15), dtype=np.uint8)

    for i in trange(defs.N_PHASE1_MOVES, desc="Moves"):
        #get the twist
        twistCube = cubiecubes[i]

        a4_list_table[i] = twistCube.a4
        permutation_list_table[i] = twistCube.permutation
    
    #save the data
    defs.PERMUTATION_LIST_MOVE_TABLE = permutation_list_table
    defs.A4_LIST_MOVE_TABLE = a4_list_table
    utils.write_data(permutation_list_table, defs.PERMUTATION_LIST_MOVE_TABLE_FILENAME)
    utils.write_data(a4_list_table, defs.A4_LIST_MOVE_TABLE_FILENAME)

def gen_c3_move_table():
    print("Generating C3 move table...")
    #initialize empty move table for the c3 coordinate in phase 2
    c3_move_table = np.empty((defs.N_PHASE2_MOVES, defs.N_C3_COORD_STATES), dtype=np.uint32)

    for i in trange(defs.N_C3_COORD_STATES, leave=False, desc="C3 states"):

        #get a cube with the desired orientation
        cube = Cubiecube.from_c3_coord(i)

        #for every coordinate
        for j in range(defs.N_PHASE2_MOVES):
    
            #apply the twist
            new_cube = cube.apply_move_new(j)

            #save the resulting orientation in the move table
            c3_move_table[j, i] = new_cube.get_c3_coord()
    
    #save the data
    defs.C3_MOVE_TABLE = c3_move_table
    utils.write_data(c3_move_table, defs.C3_MOVE_TABLE_FILENAME)

def gen_IO_move_table():
    print("Generating IO move table...")
    #initialize empty move table for the IO coordinate in phase 2
    IO_move_table = np.empty((defs.N_PHASE2_MOVES, defs.N_IO_COORD_STATES), dtype=np.uint16)

    for i in trange(defs.N_IO_COORD_STATES, leave=False, desc="IO states"):

        #get a cube with the desired orientation
        cube = Cubiecube.from_permutation_coords(i, 0, 0)

        #for every coordinate
        for j in range(defs.N_PHASE2_MOVES):
        
            #apply the twist
            new_cube = cube.apply_move_new(j)

            #save the resulting orientation in the move table
            IO_move_table[j, i] = new_cube.get_IO_coord()
    
    #save the data
    defs.IO_MOVE_TABLE = IO_move_table
    utils.write_data(IO_move_table, defs.IO_MOVE_TABLE_FILENAME)

def gen_I_move_table():
    print("Generating I move table...")
    #initialize empty move table for the IO coordinate in phase 3
    I_move_table = np.empty((defs.N_PHASE3_MOVES, defs.N_I_COORD_STATES), dtype=np.uint16)

    #for every coordinate
    for i in trange(defs.N_I_COORD_STATES, desc="I states"):
        
        #get a cube with the desired orientation
        cube = Cubiecube.from_permutation_coords(0, i, 0)

        for j in range(defs.N_PHASE3_MOVES):

            #apply the twist
            new_cube = cube.apply_move_new(j)

            #save the resulting orientation in the move table
            I_move_table[j, i] = new_cube.get_I_coord()
    
    #save the data
    defs.I_MOVE_TABLE = I_move_table
    utils.write_data(I_move_table, defs.I_MOVE_TABLE_FILENAME)

def gen_O_move_table():
    print("Generating O move table...")
    #initialize empty move table for the IO coordinate in phase 3
    O_move_table = np.empty((defs.N_PHASE3_MOVES, defs.N_O_COORD_STATES), dtype=np.uint16)

    for i in trange(defs.N_O_COORD_STATES, desc="O States"):

        #get a cube with the desired orientation
        cube = Cubiecube.from_permutation_coords(0, 0, i)

        #for every move
        for j in range(defs.N_PHASE3_MOVES):

            #apply the twist
            new_cube = cube.apply_move_new(j)

            #save the resulting orientation in the move table
            O_move_table[j, i] = new_cube.get_O_coord()
    
    #save the data
    defs.O_MOVE_TABLE = O_move_table
    utils.write_data(O_move_table, defs.O_MOVE_TABLE_FILENAME)

