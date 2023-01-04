import gen_move_tables
import phase1
import phase2
import phase3
import defs

def gen_data_if_missing():
    #generate any data that is missing

    #must be done first
    if defs.PERMUTATION_LIST_MOVE_TABLE.shape == (1, 15) or defs.A4_LIST_MOVE_TABLE.shape == (1, 15):
        gen_move_tables.gen_k4_and_permutation_move_table()

    #then these can be generated
    if defs.C3_MOVE_TABLE is None:
        gen_move_tables.gen_c3_move_table()
    if defs.IO_MOVE_TABLE is None:
        gen_move_tables.gen_IO_move_table()
    if defs.I_MOVE_TABLE is None:
        gen_move_tables.gen_I_move_table()
    if defs.O_MOVE_TABLE is None:
        gen_move_tables.gen_O_move_table()

    #then we can generate the pruning tables
    if defs.PHASE1_PRUNING_TABLE is None:
        phase1.prune()
    if defs.PHASE2_PRUNING_TABLE is None:
        phase2.prune()
    if defs.PHASE3_PRUNING_TABLE is None:
        phase3.prune()