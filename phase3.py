import numpy as np
from tqdm import trange

import defs
import utils

class Node(utils.BaseNode):
    '''
    Contains the data for a phase 3 node and the functionality to generate new nodes by applying moves.
    '''

    __slots__ = ("i", "o")

    def __init__(self, index: int) -> None:
        super().__init__(index)
        self.o, self.i = divmod(index, defs.N_HALF_I_COORD_STATES)
        if self.o >= defs.N_HALF_O_COORD_STATES:
            self.i += defs.N_HALF_I_COORD_STATES
    
    @classmethod
    def from_coords(cls, i_coord: int, o_coord: int):
        node = cls.__new__(cls)
        node.i = i_coord
        node.o = o_coord
        node.index = int(o_coord) * defs.N_HALF_I_COORD_STATES + int(i_coord) % defs.N_HALF_I_COORD_STATES
        return node
       
    def apply_move(self, move: int):
        new_node = Node.__new__(Node)

        new_node.i, new_node.o = defs.I_MOVE_TABLE[move, self.i], defs.O_MOVE_TABLE[move, self.o]
        new_node.index = int(new_node.o) * defs.N_HALF_I_COORD_STATES + int(new_node.i) % defs.N_HALF_I_COORD_STATES
        
        return new_node

def prune():
    '''
    Calculates and saves the pruning table
    '''
    print("Generating Phase 3 Pruning Table...")

    #initialize the distance array with all entries as max_depth + 1
    distance = np.full(defs.N_PHASE3_STATES, defs.PHASE3_PRUNE_DEPTH+1, dtype=np.uint8)

    #queue contains a tuple of (I_coord, O_coord, last_move_axis)
    #initialize 2 queues with the first one having the solved state in it
    queues = [[(np.uint16(0), np.uint16(0), np.uint8(-1))],[]]

    #set the solved state
    distance[0] = 0

    #defines which queue we are currently working out of
    current_queue = 0

    #current distance from solved
    current_depth = 0

    #while any of the queues are full and we are below the max depth
    while (queues) and (current_depth < defs.PHASE3_PRUNE_DEPTH):

        #for every node in the queue
        for j in trange(len(queues[current_queue]), leave=False, desc="Exploring Depth " + str(current_depth+1)):
            
            #dequeue a node
            node_I, node_O, axis = queues[current_queue].pop()

            #for every move in PHASE 2
            for i in defs.PHASE3_MOVES[(axis + 1) % 4]:

                #check if the move is redundant given the last move
                if axis == defs.TWIST_AXES[i]:
                    break
                
                #get the new node list
                new_node_I, new_node_O = defs.I_MOVE_TABLE[i, node_I], defs.O_MOVE_TABLE[i, node_O]

                #get the index of this new node
                new_node = int(new_node_O) * defs.N_HALF_I_COORD_STATES + int(new_node_I) % defs.N_HALF_I_COORD_STATES
               
                #if the node has not been visited
                if distance[new_node] == defs.PHASE3_PRUNE_DEPTH + 1:
                    #update the distance
                    distance[new_node] = current_depth + 1
                    
                    #add the move to a queue if it will be within the maximum depth
                    if current_depth + 1 < defs.PHASE3_PRUNE_DEPTH:
                        queues[np.mod(current_queue + 1, 2)].append((new_node_I, new_node_O, defs.TWIST_AXES[i]))
    
        #cycle which queue we are working out of
        current_queue = np.mod(current_queue + 1, 2)

        #add 1 to the current distance
        current_depth += 1

    #write the data
    defs.PHASE3_PRUNING_TABLE = distance
    utils.write_data(distance, defs.PHASE3_PRUNING_TABLE_NAME)

    return

def can_solve(node: Node, moves: int, last_move: int or None = None) -> bool:
    '''
    Returns whether or not the node can be solved in the given number of moves.

    node: the node to be solved
    moves: the number of moves available
    '''

    pruneVal = defs.PHASE3_PRUNING_TABLE[node.index]

    #if the last axis is none or if the prune value + 1 is not equal to the number of moves then we don't need to check if first move cancellation is possible
    if last_move is None or pruneVal + 1 != moves:
        return pruneVal <= moves
    else: 
        #condition with move cancellation
        return defs.PHASE3_PRUNING_TABLE[node.index] - int(match_axis_first_move(node, defs.TWIST_AXES[last_move])) <= moves

def match_axis_first_move(node: Node, last_axis: int) -> bool:
    '''
    Returns True if an optimal solution begins with a move whose axis matches move, False otherwise

    node: the node to be solved
    last_axis: the axis of the last move performed
    '''
    #get the distance to solved
    dist = defs.PHASE3_PRUNING_TABLE[node.index]

    #for every move
    for i in defs.PHASE3_MOVES[last_axis]:
        #break when we hit redundant moves
        if defs.TWIST_AXES[i] != last_axis:
            break

        #get a new node
        new_node = node.apply_move(i)

        #if the pruning value decreased then this is an optimal first move
        if defs.PHASE3_PRUNING_TABLE[new_node.index] < dist:
            return True

    return False


def solution_generator(node: Node, last_axis: int = 0):
    '''
    A generator which returns all shortest solutions for the node

    node: the node to be solved
    last_move: the last move performed (prioritizes finding sequences that begin with the same axis to cancel a move)
    '''

    #initialize the maximum search depth to the lower bound from the pruning table
    depth = defs.PHASE3_PRUNING_TABLE[node.index]

    #initialize an empty sequence
    sequence = []

    #yield each solution
    while True:
        #create a solution generator
        solutions = search_generator(node, sequence, depth, (last_axis - 1) % 4)

        #for every solution yield the sequence
        for _ in solutions:
            yield sequence
        
        #increase the depth and start again
        depth += 1


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

    #get the the number of moves required to solve the original node
    dist = seqLen + defs.PHASE3_PRUNING_TABLE[node.index]

    #if the minimum distance is more than the bound then then stop the generator
    if dist > depth: 
        return
    
    #if the node is the solution and we are at the full depth then yield true
    if node.index == 0 and seqLen == depth: 
        yield True
        return

    #for every move
    for i in defs.PHASE3_MOVES[(last_axis + 1) % 4]:

        #don't try redundant moves (the moves are iterated in sorted order so if we reach the axis of the last move then we can break the loop)
        if (not seqLen == 0) and (defs.TWIST_AXES[i] == last_axis):
            break
        
        #get the new node
        new_node = node.apply_move(i)

        #append the move to the path
        sequence.append(i)

        #recursively continue searching, setting the last axis such that the redundant moves are searched last
        for sol in search_generator(new_node, sequence, depth, defs.TWIST_AXES[i]):

            #if a solution was found then yield true otherwise we can stop searching this node
            yield True

        #remove the last move from the sequence since no solution was found
        del sequence[-1]

