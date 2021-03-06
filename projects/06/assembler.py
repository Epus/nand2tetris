#Assembler for Hack language
#Usage: python assembler.py directory\filename.asm
#Output: directory\filename.hack

import sys
from enum import Enum

NULL = "null"

class CommandType(Enum):
    A_COMMAND = 1
    C_COMMAND = 2
    L_COMMAND = 3

class SymbolTable():
    def __init__(self):
        self.dict = {
            "SP"    : 0,
            "LCL"   : 1, 
            "ARG"   : 2,
            "THIS"  : 3,
            "THAT"  : 4,
            "R0"    : 0,
            "R1"    : 1,
            "R2"    : 2,
            "R3"    : 3,
            "R4"    : 4,
            "R5"    : 5,
            "R6"    : 6,
            "R7"    : 7,
            "R8"    : 8,
            "R9"    : 9,
            "R10"   : 10,
            "R11"   : 11,
            "R12"   : 12,
            "R13"   : 13,
            "R14"   : 14,  
            "R15"   : 15,   
            "SCREEN": 16384,
            "KBD"   : 24576,       
        }

    def printdict(self):
        print(self.dict)

    def contains(self, symbol):
        return symbol in self.dict

    def addEntry(self, symbol, value):
        self.dict[symbol] = value

    def GetAddress(self, symbol):
        return self.dict[symbol]

class Parser():

    def __init__(self):
        filepath = sys.argv[1]      
        self.raw =  open(filepath, 'r')
        self.output = open(filepath.split(".")[0] + ".hack", "w")
        self.reset()

    def writeline(self, line):
        self.output.write(line + "\n")    

    def __getNextCommand(self):
        command = ""
        while True:
            line = self.raw.readline()
            if not line:
                break           
            command=line.split("//")[0].strip()
            if command != "":
                break
        self.nextCommand = command

    def reset(self):
        self.raw.seek(0)
        self.currentCommand = ""
        self.nextCommand = ""
        self.__getNextCommand()

    def hasMoreCommands(self):
        return (self.nextCommand != "")

    def advance(self):
        if self.hasMoreCommands():
            self.currentCommand = self.nextCommand
            self.__getNextCommand()    

    def commandType(self):
        if (self.currentCommand[0] == "@"):
            return CommandType.A_COMMAND
        elif (self.currentCommand[0] == "("):
            return CommandType.L_COMMAND 
        else:
            return CommandType.C_COMMAND    

    def symbol(self):
        if (self.commandType() == CommandType.A_COMMAND):
            return self.currentCommand.split("@")[1]
        elif (self.commandType() == CommandType.L_COMMAND):
            return self.currentCommand.split("(")[1].split(")")[0]   

    def dest(self, command):
        if "=" not in command:
            return NULL
        return command.split("=")[0]

    def jump(self, command):
        if ";" not in command:
            return NULL
        return command.split(";")[1]

    def comp(self, command):
        if self.dest(command) != NULL:
            command = command.split("=")[1]
        if self.jump(command) != NULL:
            command = command.split(";")[0]
        return command
    
    #for debugging
    def printcurrentcommand(self):
        print(self.currentCommand)

class Code():
    def __init__(self):
        self.compdict = {
            "0" : "0101010",
            "1" : "0111111",
            "-1": "0111010",
            "D" : "0001100",
            "A" : "0110000", 
            "M" : "1110000",
            "!D": "0001101",
            "!A": "0110001",
            "!M": "1110001", 
            "-D": "0001111",
            "-A": "0110011",
            "-M": "1110011",
            "D+1" : "0011111",
            "A+1" : "0110111",
            "M+1" : "1110111",
            "D-1" : "0001110",
            "A-1" : "0110010",
            "M-1" : "1110010",
            "D+A" : "0000010",
            "D+M" : "1000010",
            "D-A" : "0010011",
            "D-M" : "1010011",
            "A-D" : "0000111",
            "M-D" : "1000111",
            "D&A" : "0000000",
            "D&M" : "1000000",
            "D|A" : "0010101", 
            "D|M" : "1010101", 
        }

        self.destdict = {
            NULL  : "000",
            "M"     : "001",
            "D"     : "010",
            "MD"    : "011",
            "A"     : "100",
            "AM"    : "101",
            "AD"    : "110",
            "AMD"   : "111",
        }

        self.jumpdist = {
            NULL  : "000",
            "JGT"     : "001",
            "JEQ"     : "010",
            "JGE"    : "011",
            "JLT"     : "100",
            "JNE"    : "101",
            "JLE"    : "110",
            "JMP"   : "111",
        }

    def comp(self, command):
        return self.compdict[command]

    def dest(self,command):
        return self.destdict[command]

    def jump(self, command):
        return self.jumpdist[command]

st = SymbolTable()
p = Parser()
c = Code()
pc = 0 #Program counter
ram = 16

def pass1():
    global pc
    while (p.hasMoreCommands()):
        p.advance()
        if (p.commandType() == CommandType.L_COMMAND):
            st.addEntry(p.symbol(), pc)
        elif (p.commandType() == CommandType.A_COMMAND or p.commandType() == CommandType.C_COMMAND):
            pc = pc + 1  

def pass2():
    global ram
    while (p.hasMoreCommands()):
            p.advance()
            translation = ""
            if (p.commandType() == CommandType.A_COMMAND):
                translation = "0"
                if (p.symbol().isdigit() == False):
                    if not st.contains(p.symbol()):
                        st.addEntry(p.symbol(), ram)
                        ram = ram + 1
                    translation = translation + format(int(st.GetAddress(p.symbol())), "015b")
                else:
                    translation = translation + (format(int(p.symbol()), "015b"))    
            elif (p.commandType() == CommandType.C_COMMAND):
                translation = "111" + c.comp(p.comp(p.currentCommand)) + c.dest(p.dest(p.currentCommand)) + c.jump(p.jump(p.currentCommand))
            else:
                continue
            p.writeline(translation)


def main():
    pass1()
    p.reset()
    pass2()    
    
main()