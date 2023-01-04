import numpy as np
import numba as nb
from tqdm import trange

import defs
import utils

class Node(utils.BaseNode):
    '''
    Contains the data for a phase 1 node and the functionality to generate new nodes by applying moves.
    '''

    __slots__ = ("list",)

    def __init__(self, index: int) -> None:
        super().__init__(index)
        self.list = utils.int_to_base(self.index, 4, 15)
    
    @classmethod
    def from_list(cls, list):
        node = cls.__new__(cls)
        node.list = list
        node.index = utils.base_to_int(list, 4)
        return node
       
    def apply_move(self, move: int):
        new_list = apply_move(move, self.list)
        new_index = utils.base_to_int(new_list, 4)
        
        new_node = Node.__new__(Node)
        new_node.index = new_index
        new_node.list = new_list
        return new_node

@nb.njit(nb.uint8[:](nb.uint8, nb.uint8[:]))
def apply_move(move: int, k4_state: np.ndarray) -> int:
    '''
    Calculates the K4 list state resulting from applying the given move on the K4 list state
    '''
    #apply the permutation
    new_k4_state = k4_state[defs.PERMUTATION_LIST_MOVE_TABLE[move]]

    #apply the group multiplication
    #utils.k4_table[new_k4_state, move_tables.a4_list[move]]

    result = np.empty(15, dtype=np.uint8)
    for i in range(15):
        result[i] = utils.k4_table[new_k4_state[i], defs.A4_LIST_MOVE_TABLE[move, i]]

    return result

def prune():
    '''
    Calculates and saves the pruning table
    '''
    print("Generating Phase 1 Pruning Table...")

    #initialize the distance array with all entries as max_depth + 1
    distance = np.full(defs.N_PHASE1_STATES, defs.PHASE1_PRUNE_DEPTH+1, dtype=np.uint8)

    #queue contains a tuple of (k4_state_index, last_move_axis)
    #initialize 2 queues with the first one having the solved state in it
    queues = [[(np.uint32(0), np.uint8(-1))],[]]

    #set the solved state
    distance[0] = 0

    #defines which queue we are currently working out of
    current_queue = 0

    #current distance from solved
    current_depth = 0

    #while any of the queues are full and we are below the max depth
    while (queues) and (current_depth < defs.PHASE1_PRUNE_DEPTH):

        #for every node in the queue
        for j in trange(len(queues[current_queue]), leave=False, desc="Exploring Depth " + str(current_depth+1)):
            
            #dequeue a node
            node, axis = queues[current_queue].pop()

            #compute the list representation of the node
            node_list = utils.int_to_base(node, 4, 15)

            #for every move in PHASE 1
            for i in defs.PHASE1_MOVES[(axis + 1) % 4]:

                #check if the move is redundant given the last move
                if axis == defs.TWIST_AXES[i]:
                    break
                
                #get the new node list
                new_node_list = apply_move(i, node_list)

                #get the index of this new node
                new_node = utils.base_to_int(new_node_list, 4)
               
                #if the node has not been visited
                if distance[new_node] == defs.PHASE1_PRUNE_DEPTH + 1:
                    #update the distance
                    distance[new_node] = current_depth + 1
                    
                    #add the move to a queue if it will be within the maximum depth
                    if current_depth + 1 < defs.PHASE1_PRUNE_DEPTH:
                        queues[np.mod(current_queue + 1, 2)].append((new_node, defs.TWIST_AXES[i]))
    
        #cycle which queue we are working out of
        current_queue = np.mod(current_queue + 1, 2)

        #add 1 to the current distance
        current_depth += 1

    #write the data
    defs.PHASE1_PRUNING_TABLE = distance
    utils.write_data(distance, defs.PHASE1_PRUNING_TABLE_NAME)

    return

def can_solve(node: Node, moves: int) -> bool:
    '''
    Returns whether or not the node can be solved in the given number of moves.
    Search is performed using depth first algorithm so 'moves' should be reasonable.

    node: the node to be solved
    moves: the number of moves available
    '''

    #if negative moves must be done then return false
    if moves < 0:
        return False

    #get the value from the pruning table
    pruneVal = defs.PHASE1_PRUNING_TABLE[node.index]

    #the number of moves is less than the lower bound then return false
    if moves < pruneVal:
        return False

    #if the pruning table value is less than or equal to the pruning depth then we can find out easily
    if pruneVal <= defs.PHASE1_PRUNE_DEPTH:
        return pruneVal <= moves
    
    #for every move
    for i in range(defs.N_PHASE1_MOVES):
        #get the new node list
        new_node = node.apply_move(i)

        #if this state is solveable in 1 less move then return true
        if can_solve(new_node, moves - 1):
            return True
    
    #if no new states are solvable in the required number of moves then return false
    return False

def solution_generator(node: Node):
    '''
    A generator which returns all solutions for the node in order of increasing length

    node: the node to be solved
    '''

    #initialize the maximum search depth to the lower bound from the pruning table
    depth = defs.PHASE1_PRUNING_TABLE[node.index]

    #initialize an empty sequence
    sequence = []

    #create a solution generator
    solutions = search_generator(node, sequence, depth)

    #while there is no solution
    while not next(solutions):
        #increase the depth of the solution generator
        depth += 1
        solutions = search_generator(node, sequence, depth)
    
    #yield the first solution found
    yield sequence
    
    #yield all subsequent solutions
    while True:
        #yield each solution
        for _ in solutions:
            yield sequence

        #increase the depth of the generator
        depth += 1
        solutions = search_generator(node, sequence, depth)


def search_generator(node: Node, sequence: list, depth: int):
    '''
    A generator which returns false if no solution was found and true if solutions were found. The solution sequence is stored in sequence.

    node: the node which is being searched
    sequence: the sequence of moves which was applied to get to node
    depth: the maximum depth of the search
    '''

    #save the sequence length
    seqLen = len(sequence)

    #get the lower bound for the number of moves required to solve the original node
    distGuess = seqLen + defs.PHASE1_PRUNING_TABLE[node.index]

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
    for i in range(defs.N_PHASE1_MOVES):

        #don't try redundant moves
        if (not seqLen == 0) and (defs.TWIST_AXES[i] == defs.TWIST_AXES[sequence[-1]]):
            continue
        
        #get the new node
        new_node = node.apply_move(i)

        #append the move to the path
        sequence.append(i)

        #recursively continue searching
        for sol in search_generator(new_node, sequence, depth):

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