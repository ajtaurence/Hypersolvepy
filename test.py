import numpy as np


index = 0

solvedpos = np.array([-1,2,3,4])

position = np.array([-4, -1, -2, -3])


def get_action(initialPos, finalPos):
    return initialPos[np.abs(finalPos) - 1] * np.sign(finalPos)

def apply_action(state, action):
    return state[np.abs(action) - 1] * np.sign(action)

def inverse_action(action):
    inverse = np.empty_like(action)
    inverse[np.abs(action) - 1] = (np.arange(4) + 1) * np.sign(action)
    return inverse

action = get_action(-np.arange(4) - 1, position)
inv_action = inverse_action(action)
print(inv_action)
#inv_action = get_action(position, solvedpos)
#print(inv_action)

print(apply_action(apply_action(solvedpos, inv_action), action))




#get the action and inverse action applied to the reference sticker
ref_action = get_action(Stickercube.solved[index], self.position[index])
inv_ref_action = inverse_action(ref_action)

#apply the inverse action to the entire solved state
new_solved = np.empty_like(Stickercube.solved)
for i in range(16):
    new_solved[i] = apply_action(Stickercube.solved[i], inv_ref_action)

#apply the original action for every piece to the new solved state
new_pos = np.empty_like(self.position)
for i in range(16):
    action = get_action(Stickercube.solved[i], self.position[i])
    new_pos[i] = apply_action(new_solved[i], action)

#find the permutation going from the old solved position to the new position
permutation = np.empty(16, dtype=np.uint8)
for i, piece in enumerate(np.sign(Stickercube.solved)):
        permutation[i] = [np.all(np.sign(new_pos)[j,:]==piece) for j in range(16)].index(True)

#apply the permutation
new_pos = new_pos[permutation, :]