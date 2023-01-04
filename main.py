from cube import Cube
from gen_all_data import gen_data_if_missing

#generate any data if it is missing
gen_data_if_missing()

while True:
    input("\nPress Enter to select a log file...")

    cube = None
    while cube is None:
        cube = Cube.from_log()

    success = False
    while not success:
        input_text = input("Enter time (s) after last solution was found to terminate the search. Enter 'optimal' to return an optimal solution: ")
        if input_text.strip() == 'optimal':
            terminate_time = None
            success = True
        else:
            try:
                terminate_time = float(input_text)
            except ValueError:
                print("Uknown input, please try again")
            else:
                success = True

    cube.solve(terminate_time)

    print("Save log file as...")
    cube.log.save_as()