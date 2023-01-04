import numpy as np
from tqdm import trange

import defs
import utils

class Node(utils.BaseNode):
    '''
    Contains the data for a phase 2 node and the functionality to generate new nodes by applying moves.
    '''

    __slots__ = ("c3", "io")

    def __init__(self, index: int) -> None:
        super().__init__(index)
        self.io, self.c3 = divmod(index, defs.N_C3_COORD_STATES)
    
    @classmethod
    def from_coords(cls, c3_coord: int, io_coord: int):
        node = cls.__new__(cls)
        node.c3 = c3_coord
        node.io = io_coord
        node.index = int(io_coord) * defs.N_C3_COORD_STATES + c3_coord
        return node
       
    def apply_move(self, move: int):
        new_c3, new_io = defs.C3_MOVE_TABLE[move, self.c3], defs.IO_MOVE_TABLE[move, self.io]
        new_index = int(new_io) * defs.N_C3_COORD_STATES + new_c3
        
        new_node = Node.__new__(Node)
        new_node.index = new_index
        new_node.c3 = new_c3
        new_node.io = new_io
        return new_node

def prune():
    '''
    Calculates and saves the pruning table
    '''
    print("Generating Phase 2 Pruning Table...")

    #initialize the distance array with all entries as max_depth + 1
    distance = np.full(defs.N_PHASE2_STATES, defs.PHASE2_PRUNE_DEPTH+1, dtype=np.uint8)

    #queue contains a tuple of (c3_coord, IO_coord, last_move_axis)
    #initialize 2 queues with the first one having the solved state in it
    queues = [[(np.uint32(0), np.uint16(0), np.uint8(-1))],[]]

    #set the solved state
    distance[0] = 0

    #defines which queue we are currently working out of
    current_queue = 0

    #current distance from solved
    current_depth = 0

    #while any of the queues are full and we are below the max depth
    while (queues) and (current_depth < defs.PHASE2_PRUNE_DEPTH):

        #for every node in the queue
        for j in trange(len(queues[current_queue]), leave=False, desc="Exploring Depth " + str(current_depth+1)):
            
            #dequeue a node
            node_c3, node_IO, axis = queues[current_queue].pop()

            #for every move in PHASE 2
            for i in defs.PHASE2_MOVES[(axis + 1) % 4]:

                #check if the move is redundant given the last move and break
                if axis == defs.TWIST_AXES[i]:
                    break
                
                #get the new node list
                new_node_c3, new_node_IO = defs.C3_MOVE_TABLE[i, node_c3], defs.IO_MOVE_TABLE[i, node_IO]

                #get the index of this new node
                new_node = int(new_node_IO) * defs.N_C3_COORD_STATES + int(new_node_c3)
               
                #if the node has not been visited
                if distance[new_node] == defs.PHASE2_PRUNE_DEPTH + 1:
                    #update the distance
                    distance[new_node] = current_depth + 1
                    
                    #add the move to a queue if it will be within the maximum depth
                    if current_depth + 1 < defs.PHASE2_PRUNE_DEPTH:
                        queues[np.mod(current_queue + 1, 2)].append((new_node_c3, new_node_IO, defs.TWIST_AXES[i]))
    
        #cycle which queue we are working out of
        current_queue = np.mod(current_queue + 1, 2)

        #add 1 to the current distance
        current_depth += 1

    #write the data
    defs.PHASE2_PRUNING_TABLE = distance
    utils.write_data(distance, defs.PHASE2_PRUNING_TABLE_NAME)

    return

def can_solve(node: Node, moves: int) -> bool:
    '''
    Returns whether or not the node can be solved in the given number of moves.
    Search is performed using depth first algorithm so 'moves' should be reasonably small.

    node: the node to be solved
    moves: the number of moves available
    '''

    #if negative moves must be done then return false
    if moves < 0:
        return False

    #get the value from the pruning table
    pruneVal = defs.PHASE2_PRUNING_TABLE[node.index]

    #the number of moves is less than the lower bound then return false
    if moves < pruneVal:
        return False

    #if the pruning table value is less than or equal to the pruning depth then we can find out easily
    if pruneVal <= defs.PHASE2_PRUNE_DEPTH:
        return pruneVal <= moves
    
    #for every move
    for i in range(defs.N_PHASE2_MOVES):
        #get the new node list
        new_node = node.apply_move(i)

        #if this state is solveable in 1 less move then return true
        if can_solve(new_node, moves - 1):
            return True
    
    #if no new states are solvable in the required number of moves then return false
    return False

def solution_generator(node: Node, last_axis: int = 0):
    '''
    A generator which returns all solutions for the node in order of increasing length

    node: the node to be solved
    '''

    #initialize the maximum search depth to the lower bound from the pruning table
    depth = defs.PHASE2_PRUNING_TABLE[node.index]

    #initialize an empty sequence
    sequence = []

    #create a solution generator
    solutions = search_generator(node, sequence, depth, (last_axis - 1) % 4)

    #while there is no solution
    while not next(solutions):
        #increase the depth of the solution generator
        depth += 1
        solutions = search_generator(node, sequence, depth, (last_axis - 1) % 4)
    
    #yield the first solution found
    yield sequence
    
    #yield all subsequent solutions
    while True:
        #yield each solution
        for _ in solutions:
            yield sequence

        #increase the depth of the generator
        depth += 1
        solutions = search_generator(node, sequence, depth, (last_axis - 1) % 4)


def search_generator(node: Node, sequence: list, depth: int, last_axis: int):
    '''
    A generator which returns false if no solution was found and true if solutions were found. The solution sequence is stored in sequence.

    node: the node which is being searched
    sequence: the sequence of moves which was applied to get to node
    depth: the maximum depth of the search
    last_axis: the axis of the last move performed (sequences beginning with a twist of this axis will be found first)
    '''

    #save the sequence length
    seqLen = len(sequence)

    #get the lower bound for the number of moves required to solve the original node
    distGuess = seqLen + defs.PHASE2_PRUNING_TABLE[node.index]

    #if the minimum distance is more than the bound then yield the distance and then stop the generator
    if distGuess > depth: 
        yield False
        return
    
    #if the node is the solution and we are at the full depth then yield true
    if node.index == 0 and seqLen == depth: 
        yield True
        return

    #no solution has been found yet
    sol_found = False

    #for every move
    for i in defs.PHASE2_MOVES[(last_axis + 1) % 4]:

        #don't try redundant moves
        if (not seqLen == 0) and (defs.TWIST_AXES[i] == last_axis):
            continue
        
        #get the new node
        new_node = node.apply_move(i)

        #append the move to the path
        sequence.append(i)

        #recursively continue searching
        for sol in search_generator(new_node, sequence, depth, defs.TWIST_AXES[i]):

            #if a solution was found then yield true otherwise we can stop searching this node
            if sol:
                sol_found = True
                yield True
            else: 
                break

        #remove the last move from the sequence since no solution was found
        del sequence[-1]

    #if no solution was found then return the minimum distance it could be from solved
    if not sol_found:
        yield False