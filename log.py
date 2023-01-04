import numpy as np
import tkinter as tk
from tkinter import filedialog

from twist import Twist

class Log:

    def __init__(self, scramble: list or None = None, solution: list or None = None, scrambling=False) -> None:
        '''
        An object which contains a move history and can be saved or opened from an MC4D log file
        '''
        #list of twist objects representing the scramble moves
        if scramble is None:
            self.scramble = []
        else: self.scramble = scramble
        #list of twist objects representing the solution moves
        if solution is None:
            self.solution = []
        else: 
            self.solution = solution
        
        #initialize the filepath to none
        self.filepath = None

        #scrambling set to false by default
        self.scrambling = scrambling
    
    def append_twist(self, twist: Twist):
        '''
        Appends the scramble twist to the log
        '''
        if self.scrambling:
            self.scramble.append(twist)
        else: self.solution.append(twist)
    
    def scramble_length(self):
        '''
        Gets the length of the scramble
        '''
        return len(self.scramble)
    
    def solution_length(self):
        '''
        Gets the length of the solution
        '''
        return len(self.solution)
    
    def __repr__(self) -> str:
        return repr(self.scramble + self.solution)

    def __str__(self) -> str:
        string = "MagicCube4D 3 0 0 {4,3,3} 2\n0.731762581557179 -0.19593642894153976 0.6527882045858442 0.0\n0.6813606608159284 0.18716613400295473 -0.7076132334650542 0.0\n0.016467365461856454 0.9625890889138652 0.27046454809959974 0.0\n0.0 0.0 0.0 1.0\n*\n"

        #convert the twist objects to a string
        string += " ".join([twist.to_mc4d_string() for twist in self.scramble])

        #if there is a scramble then add the separator
        if len(self.scramble) != 0:
            string += " m| "
        
        #convert the solution twists to a string
        string += " ".join([twist.to_mc4d_string() for twist in self.solution])
        
        #terminating character
        string += "."

        return string
    
    def save(self):
        '''
        Save the log to the file it was loaded from
        '''

        #try to save the file
        try:
            with open(self.filepath, "w") as f:
                f.write(str(self))
        except FileNotFoundError: 
            print("Cannot save log file, invalid filepath.")
            return
    
    def save_as(self):
        '''
        Save the log to a new file
        '''

        #create a gui
        root = tk.Tk()
        root.withdraw()

        #get the file path
        self.filepath = filedialog.asksaveasfilename(defaultextension=".log", filetypes=[("Log files", "*.log")])

        #save the file
        self.save()
    
        
    @classmethod
    def from_file(cls, file_path: str):
        '''
        Opens the MC4D log file from the path and returns a MC4DLog object
        '''

        #try to open the file
        try:
            file = open(file_path, "r")
        except FileNotFoundError: 
            print("Cannot open log file, invalid filepath.")
            return None
      
        
        first_line = file.readline()
        if first_line[:11] != "MagicCube4D" or first_line[-10:-1] != "{4,3,3} 2":
            print("File is not a 2^4 MC4D log file!")
            return None
        
        moves = " ".join(file.readlines()[5:]).strip().rstrip(".")
        
        file.close()

        if "m|" in moves:
            scramble_moves, solution_moves = moves.split("m|")
        else:
            scramble_moves = ""
            solution_moves = moves
        
        scramble_string_list = scramble_moves.strip().split()
        solution_string_list = solution_moves.strip().split()
        
        solution_twists = []
        scramble_twists = []

        for twist_string in scramble_string_list:
            scramble_twists.append(Twist.from_mc4d_string(twist_string))
        
        for twist_string in solution_string_list:
            solution_twists.append(Twist.from_mc4d_string(twist_string))

        #create the log object
        log = cls.__new__(cls)
        log.solution = solution_twists
        log.scramble = scramble_twists
        log.filepath = file_path
        log.scrambling = False

        return log
    
    @classmethod
    def open(cls):
        '''
        Opens a file dialog to open an MC4D log file and returns an MC4DLog object
        '''

        #create a gui
        root = tk.Tk()
        root.withdraw()

        #get the file
        file_path = filedialog.askopenfilename(filetypes=[("Log files", "*.log")])
        
        return cls.from_file(file_path)
    
    @classmethod
    def scramble_n_twists(cls, nTwists: int):
        '''
        Generates a log where the cube has been randomly scrambled by the number of twists. The random scramble is computed in the same way as MC4D
        so these are valid scrambles.
        '''
        #create an empty log
        new_log = cls()

        new_log.scrambling = True

        if nTwists == 0:
            return new_log
       
        #append the first random twist
        new_log.append(Twist.random_mc4d())
        #for the remaining twists
        for i in range(nTwists - 1):
            #get a random twist
            twist = Twist.random_mc4d()
            #get a new twist until the axis does not match the last axis
            while twist.axis == new_log.scramble[-1].axis:
                twist = Twist.random_mc4d()
            #append the new twist
            new_log.append_scramble(twist)
        
        new_log.scrambling = False
        return new_log
    
    @classmethod
    def full_scramble(cls):
        '''
        Generates a log where the cube has been randomly scrambled by 20 twists. The random scramble is computed in the same way as MC4D
        so these are valid scrambles.
        '''

        return cls.scramble_n_twists(20)