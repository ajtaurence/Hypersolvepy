import numpy as np

from cube_internal import Stickercube
from cube import Cube
import utils


flipped = utils.permutation_list_to_a4[3, 2]

superflip = Cube.from_stickercube(Stickercube.from_a4_list(np.array([0, flipped, flipped, 0,
                                                                    flipped, 0, 0, flipped,
                                                                    flipped, 0, 0, flipped,
                                                                    0, flipped, flipped])))


superflip.solve(10)

superflip.log.save_as()

