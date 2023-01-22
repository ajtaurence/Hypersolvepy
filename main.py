from cube import Cube
from gen_all_data import gen_data_if_missing

#generate any data if it is missing
gen_data_if_missing()

while True:
    #get the cube from a log file
    while True:
        input("\nPress Enter to select a log file...")
        cube = Cube.from_log()

        if cube is not None:
            break

    #set the save location for the log
    print("Save solution file as...")
    if not cube.log.set_filepath():
        continue

    #fast algorithm or optimal?
    while True:
        response = input("Mode: fast or optimal (f/o): ").rstrip().lower()
        
        if response == 'o':
            optimal = True
            break
        elif response == 'f':
            optimal = False
            break
        else:
            print("unkown input")

    #optimal solution
    if optimal:
        print("Finding optimal solution... press ctrl+c to stop")
        cube.optimal_solve()

    #normal solution
    else:
        max_length = input("Maximum solution length (press enter to find any solution): ")

        try:
            max_length = int(max_length)
        except ValueError:
            max_length = None

        if max_length is not None:
            print("Finding solutions shorter than {}... press ctrl+c to stop".format(max_length+1))
        else: 
            print("Solving... press ctrl+c to stop")
        
        cube.solve(max_length)