import numpy as np

import utils

#total number of 2^4 states
N_STATES = 3357894533384932272635904000

#number of different states for each coordinate
N_C3_COORD_STATES = 4782969
N_IO_COORD_STATES = 6435
N_I_COORD_STATES = 40320
N_HALF_I_COORD_STATES = 20160
N_O_COORD_STATES = 5040
N_HALF_O_COORD_STATES = 2520

#number of states in each phase
N_PHASE1_STATES = 1073741824
N_PHASE2_STATES = 30778405515
N_PHASE3_STATES = 101606400

#number of moves
N_PHASE1_MOVES = 92
N_PHASE2_MOVES = 44
N_PHASE3_MOVES = 12

#pruning table depths
PHASE1_PRUNE_DEPTH = 6 #default 6
PHASE2_PRUNE_DEPTH = 7 #default 7
PHASE3_PRUNE_DEPTH = 21 #full depth

#file names
PERMUTATION_LIST_MOVE_TABLE_FILENAME = "perm_list.move"
A4_LIST_MOVE_TABLE_FILENAME = "A4_list.move"
C3_MOVE_TABLE_FILENAME = "C3.move"
I_MOVE_TABLE_FILENAME = "I.move"
O_MOVE_TABLE_FILENAME = "O.move"
IO_MOVE_TABLE_FILENAME = "IO.move"

PHASE1_PRUNING_TABLE_NAME = "phase1.prun"
PHASE2_PRUNING_TABLE_NAME = "phase2.prun"
PHASE3_PRUNING_TABLE_NAME = "phase3.prun"

#twist data
TWIST_AXES = (0, 1, 2, 2, 2, 3, 3, 3, 3, 3, 3, 3, 0, 0, 0, 0, 0, 0, 1, 1, 1, 1, 1, 1, 2, 2, 2, 2, 3, 3, 3, 3, 3, 3, 3, 3, 3, 3, 3, 3, 3, 3, 3, 3, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2)
TWIST_MC4D_NAMES = ('128,1,1 128,1,1', '79,1,1 79,1,1', '182,1,1', '182,1,1 182,1,1', '182,-1,1', '20,1,1', '20,1,1 20,1,1', '20,-1,1', '24,1,1 24,1,1', '12,1,1', '22,1,1 22,1,1', '14,1,1', '128,1,1', '128,-1,1', '132,1,1 132,1,1', '120,1,1', '130,1,1 130,1,1', '122,1,1', '79,1,1', '79,-1,1', '75,1,1 75,1,1', '68,1,1', '76,1,1 76,1,1', '66,1,1', '183,1,1 183,1,1', '177,1,1', '185,1,1 185,1,1', '175,1,1', '19,1,1', '24,1,1', '24,-1,1', '11,1,1', '3,-1,1', '3,1,1', '0,1,1', '0,-1,1', '17,1,1', '22,1,1', '22,-1,1', '9,1,1', '6,1,1', '6,-1,1', '2,1,1', '2,-1,1', '127,1,1', '132,1,1', '132,-1,1', '119,1,1', '111,-1,1', '111,1,1', '108,1,1', '108,-1,1', '125,1,1', '130,1,1', '130,-1,1', '117,1,1', '114,1,1', '114,-1,1', '110,1,1', '110,-1,1', '62,1,1', '75,1,1', '75,-1,1', '70,1,1', '59,-1,1', '59,1,1', '60,1,1', '60,-1,1', '63,1,1', '76,1,1', '76,-1,1', '71,1,1', '54,1,1', '54,-1,1', '58,1,1', '58,-1,1', '178,1,1', '183,1,1', '183,-1,1', '170,1,1', '162,-1,1', '162,1,1', '165,1,1', '165,-1,1', '180,1,1', '185,1,1', '185,-1,1', '172,1,1', '167,1,1', '167,-1,1', '163,1,1', '163,-1,1')
TWIST_NAMES = ('RI2', 'FI2', 'UI', 'UI2', "UI'", 'IU', 'IU2', "IU'", 'IF2', 'IRB', 'IR2', 'IRF', 'RI', "RI'", 'RU2', 'RFD', 'RF2', 'RFU', 'FI', "FI'", 'FU2', 'FRD', 'FR2', 'FRU', 'UF2', 'URB', 'UR2', 'URF', 'IFD', 'IF', "IF'", 'IFU', "ILFU'", 'ILFU', 'IRBU', "IRBU'", 'IRD', 'IR', "IR'", 'IRU', 'IRFD', "IRFD'", 'IRFU', "IRFU'", 'RUO', 'RU', "RU'", 'RUI', "RBUI'", 'RBUI', 'RFDI', "RFDI'", 'RFO', 'RF', "RF'", 'RFI', 'RFUO', "RFUO'", 'RFUI', "RFUI'", 'FUO', 'FU', "FU'", 'FUI', "FLUI'", 'FLUI', 'FRDI', "FRDI'", 'FRO', 'FR', "FR'", 'FRI', 'FRUO', "FRUO'", 'FRUI', "FRUI'", 'UFO', 'UF', "UF'", 'UFI', "ULFI'", 'ULFI', 'URBI', "URBI'", 'URO', 'UR', "UR'", 'URI', 'URFO', "URFO'", 'URFI', "URFI'")

#Moves for each phase ordered by which twist axis comes first
PHASE1_MOVES = ((0, 12, 13, 14, 15, 16, 17, 44, 45, 46, 47, 48, 49, 50, 51, 52, 53, 54, 55, 56, 57, 58, 59, 1, 18, 19, 20, 21, 22, 23, 60, 61, 62, 63, 64, 65, 66, 67, 68, 69, 70, 71, 72, 73, 74, 75, 2, 3, 4, 24, 25, 26, 27, 76, 77, 78, 79, 80, 81, 82, 83, 84, 85, 86, 87, 88, 89, 90, 91, 5, 6, 7, 8, 9, 10, 11, 28, 29, 30, 31, 32, 33, 34, 35, 36, 37, 38, 39, 40, 41, 42, 43), (1, 18, 19, 20, 21, 22, 23, 60, 61, 62, 63, 64, 65, 66, 67, 68, 69, 70, 71, 72, 73, 74, 75, 2, 3, 4, 24, 25, 26, 27, 76, 77, 78, 79, 80, 81, 82, 83, 84, 85, 86, 87, 88, 89, 90, 91, 5, 6, 7, 8, 9, 10, 11, 28, 29, 30, 31, 32, 33, 34, 35, 36, 37, 38, 39, 40, 41, 42, 43, 0, 12, 13, 14, 15, 16, 17, 44, 45, 46, 47, 48, 49, 50, 51, 52, 53, 54, 55, 56, 57, 58, 59), (2, 3, 4, 24, 25, 26, 27, 76, 77, 78, 79, 80, 81, 82, 83, 84, 85, 86, 87, 88, 89, 90, 91, 5, 6, 7, 8, 9, 10, 11, 28, 29, 30, 31, 32, 33, 34, 35, 36, 37, 38, 39, 40, 41, 42, 43, 0, 12, 13, 14, 15, 16, 17, 44, 45, 46, 47, 48, 49, 50, 51, 52, 53, 54, 55, 56, 57, 58, 59, 1, 18, 19, 20, 21, 22, 23, 60, 61, 62, 63, 64, 65, 66, 67, 68, 69, 70, 71, 72, 73, 74, 75), (5, 6, 7, 8, 9, 10, 11, 28, 29, 30, 31, 32, 33, 34, 35, 36, 37, 38, 39, 40, 41, 42, 43, 0, 12, 13, 14, 15, 16, 17, 44, 45, 46, 47, 48, 49, 50, 51, 52, 53, 54, 55, 56, 57, 58, 59, 1, 18, 19, 20, 21, 22, 23, 60, 61, 62, 63, 64, 65, 66, 67, 68, 69, 70, 71, 72, 73, 74, 75, 2, 3, 4, 24, 25, 26, 27, 76, 77, 78, 79, 80, 81, 82, 83, 84, 85, 86, 87, 88, 89, 90, 91))
PHASE2_MOVES = ((0, 12, 13, 14, 15, 16, 17, 1, 18, 19, 20, 21, 22, 23, 2, 3, 4, 24, 25, 26, 27, 5, 6, 7, 8, 9, 10, 11, 28, 29, 30, 31, 32, 33, 34, 35, 36, 37, 38, 39, 40, 41, 42, 43), (1, 18, 19, 20, 21, 22, 23, 2, 3, 4, 24, 25, 26, 27, 5, 6, 7, 8, 9, 10, 11, 28, 29, 30, 31, 32, 33, 34, 35, 36, 37, 38, 39, 40, 41, 42, 43, 0, 12, 13, 14, 15, 16, 17), (2, 3, 4, 24, 25, 26, 27, 5, 6, 7, 8, 9, 10, 11, 28, 29, 30, 31, 32, 33, 34, 35, 36, 37, 38, 39, 40, 41, 42, 43, 0, 12, 13, 14, 15, 16, 17, 1, 18, 19, 20, 21, 22, 23), (5, 6, 7, 8, 9, 10, 11, 28, 29, 30, 31, 32, 33, 34, 35, 36, 37, 38, 39, 40, 41, 42, 43, 0, 12, 13, 14, 15, 16, 17, 1, 18, 19, 20, 21, 22, 23, 2, 3, 4, 24, 25, 26, 27))
PHASE3_MOVES = ((0, 1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11), (1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 0), (2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 0, 1), (5, 6, 7, 8, 9, 10, 11, 0, 1, 2, 3, 4))

#tables
print("Loading tables...")
try: PHASE1_PRUNING_TABLE = utils.import_data(PHASE1_PRUNING_TABLE_NAME)
except FileNotFoundError: PHASE1_PRUNING_TABLE = None
try: PHASE2_PRUNING_TABLE = utils.import_data(PHASE2_PRUNING_TABLE_NAME)
except FileNotFoundError: PHASE2_PRUNING_TABLE = None
try: PHASE3_PRUNING_TABLE = utils.import_data(PHASE3_PRUNING_TABLE_NAME)
except FileNotFoundError: PHASE3_PRUNING_TABLE = None
try: PERMUTATION_LIST_MOVE_TABLE = utils.import_data(PERMUTATION_LIST_MOVE_TABLE_FILENAME)
except FileNotFoundError: PERMUTATION_LIST_MOVE_TABLE = np.empty((1, 15), dtype=np.uint8)
try: A4_LIST_MOVE_TABLE = utils.import_data(A4_LIST_MOVE_TABLE_FILENAME)
except FileNotFoundError: A4_LIST_MOVE_TABLE = np.empty((1, 15), dtype=np.uint8)
try: C3_MOVE_TABLE = utils.import_data(C3_MOVE_TABLE_FILENAME)
except FileNotFoundError: C3_MOVE_TABLE = None
try: I_MOVE_TABLE = utils.import_data(I_MOVE_TABLE_FILENAME)
except FileNotFoundError: I_MOVE_TABLE = None
try: O_MOVE_TABLE = utils.import_data(O_MOVE_TABLE_FILENAME)
except FileNotFoundError: O_MOVE_TABLE = None
try: IO_MOVE_TABLE = utils.import_data(IO_MOVE_TABLE_FILENAME)
except FileNotFoundError: IO_MOVE_TABLE = None
print("Done")