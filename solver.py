from time import perf_counter

import defs
import utils
from cube_internal import Stickercube, Cubiecube
import phase1
import phase2
import phase3

def merge_sequences(*args):
    '''
    Combines the sequences into a single list accounting for move cancellations at the merge point
    '''
    #if there are more then two to combine then do it recursively
    if len(args) != 2:
        return merge_sequences(merge_sequences(args[0], args[1]), *args[2:])

    sequence1, sequence2 = args

    try:
        compositionVal = utils.move_composition_table[sequence1[-1], sequence2[0]]
    except IndexError:
        return sequence1 + sequence2
    
    if compositionVal == 255:
        return sequence1 + sequence2
    elif compositionVal == 254:
        return sequence1[:-1] + sequence2[1:]
    else:
        return sequence1[:-1] + [compositionVal] + sequence2[1:]

def sequence_cancellation(sequence1: list, sequence2: list) -> bool:
    '''
    Returns True if the sequence cancels a move and False if it does not (does not account for complete cancellation!)
    '''
    try:
        return utils.move_composition_table[sequence1[-1], sequence2[0]] != 255
    except IndexError:
        return False


def solve(cube: Stickercube or Cubiecube, terminate_time: float or None = None):
    '''
    Solves the given cube stopping after 'terminate_time' seconds have elapsed since the last solution was found.
    This method will eventually find and verify an optimal solution.

    cube: the cube to solve
    terminate_time: if the time since the last solution is greater than this then the solution is returned
    '''
    #convert the cube to a cubiecube
    if type(cube) == Stickercube:
        cube = cube.to_cubiecube()

    #save the time
    time = perf_counter()

    #initialize shortest solution as a very large number
    len_shortest_solution = 99999999999

    #initialize shortest
    shortest_solution = None

    #create a solution generator for phase 1
    phase1_sol_gen = phase1.solution_generator(cube.get_phase1_node())

    #for every phase 1 solution
    for phase1_sol in phase1_sol_gen:
        #get the length of the phase 1 solution
        len_phase1_sol = len(phase1_sol)
        
        #optimal solution found
        if len_phase1_sol >= len_shortest_solution:
            print("Optimal solution length:", len_shortest_solution)
            return shortest_solution

        #get the cubiecube for the beginning of phase 2
        phase2_cube = cube.apply_move_list_new(phase1_sol)

        #get the last axis (defaults to 0)
        try:
            last_axis = defs.TWIST_AXES[phase1_sol[-1]]
        except IndexError: last_axis = 0

        #create a solution generator for phase 2
        phase2_sol_gen = phase2.solution_generator(phase2_cube.get_phase2_node(), last_axis)

        #for every phase 2 solution
        for phase2_sol in phase2_sol_gen:

            #once enough time has passed and we have a solution return the solution
            if terminate_time is not None and perf_counter() - time > terminate_time and shortest_solution is not None:
                return shortest_solution

            #get the length of the phase 2 solution
            len_phase2_sol = len(phase2_sol) + len_phase1_sol - int(sequence_cancellation(phase1_sol, phase2_sol))

            #if the phase 2 solution became maximally long then break into a new phase 1 solution
            if len_phase2_sol >= len_shortest_solution:
                break

            #get the phase 3 node
            phase3_node = phase2_cube.apply_move_list_new(phase2_sol).get_phase3_node()

            #get the last move
            try:
                last_move = phase2_sol[-1]
            except IndexError:
                try:
                    last_move = phase1_sol[-1]
                except IndexError: last_move = None

            #if it is not solvable in less than the shortest solution then get a new phase 2 solution
            if not phase3.can_solve(phase3_node, len_shortest_solution - len_phase2_sol - 1, last_move):
                continue
                
            #get the last axis (defaults to 0)
            try:
                last_axis = defs.TWIST_AXES[last_move]
            except TypeError: last_axis = 0
            
            #get the phase 3 solution
            phase3_sol = next(phase3.solution_generator(phase3_node, last_axis))

            #save the solution
            shortest_solution = merge_sequences(phase1_sol, phase2_sol, phase3_sol)

            #save the new length
            len_shortest_solution = len(shortest_solution)

            #save the time
            time = perf_counter()

            print("Found solution length:", len_shortest_solution)


