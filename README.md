Please excuse the mess.

Setup instructions:

1. Install the requirements from `requirements.txt` by running the command `pip install -r requirements.txt` in the Hypersolvepy folder.
2. Upon running `main.py`, Hypersolvepy will generate any missing data files. This may take the better part of a day even on a good computer. Large pruning tables can take a while to save to disk since they must be compressed. The table sizes for `phase1.prun` and `phase2.prun` are flexible. If they take too long to generate for your liking then you can edit the table size in `defs.py`. The variables controlling this are `PHASE1_PRUNE_DEPTH` and `PHASE2_PRUNE_DEPTH`. Decreasing them by 1 should be sufficient. Do not touch any other variables in this folder. If you change the pruning depth then you must delete the corresponding pruning table file so it may be regenerated. Otherwise you will get an error.
3. Run the `main.py` file. It may take up to several minutes to load all the data into memory. It will prompt you to select an MC4D log file. Then it will ask for a termination time. This is the time that Hypersolvepy will continue searching for a better solution after having found one. The timer restarts upon every solution.
4. Happy hypercubing!