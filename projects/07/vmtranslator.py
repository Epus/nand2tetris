#vmtranslator for Hack language
#Usage: python vmtranslator.py directory\filename.vm
#Output: directory\filename.asm
DEBUG = 0
import sys
from enum import Enum

NULL = "null"

class CommandType(Enum):
    C_ARITHMETIC = 1
    C_PUSH       = 2
    C_POP        = 3
    C_LABEL      = 4
    C_GOTO       = 5
    C_IF         = 6
    C_FUNCTION   = 7
    C_RETURN     = 8
    C_CALL       = 9

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

    def __init__(self, filepath):    
        self.raw =  open(filepath, 'r') 
        self.__getNextCommand()

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

    def hasMoreCommands(self):
        return (self.nextCommand != "")

    def advance(self):
        if self.hasMoreCommands():
            self.currentCommand = self.nextCommand
            self.__getNextCommand()    

    def commandType(self):
        arithmetic_commands = ["add", "sub", "neg", "eq", "gt", "lt", "and", "or", "not"]
        command_tokens = self.currentCommand.split()
        if (self.currentCommand in arithmetic_commands):        #change to uniform checking?
            return CommandType.C_ARITHMETIC
        elif (command_tokens[0] == "push"):
            return CommandType.C_PUSH 
        elif (command_tokens[0] == "pop"):
            return CommandType.C_POP
        elif (self.currentCommand[0] == "("):
            return CommandType.C_LABEL
        elif (command_tokens[0] == "GOTO"):
            return CommandType.C_GOTO
        elif (command_tokens[0] == "if"):
            return CommandType.C_IF
        elif (command_tokens[0] == "function"):
            return CommandType.C_FUNCTION
        elif (self.currentCommand == "return"):
            return CommandType.C_RETURN
        elif (command_tokens[0] == "call"):
            return CommandType.C_CALL
        else:
            return NULL    #invalid command

    def arg1(self):
        if (self.commandType() == CommandType.C_ARITHMETIC):
            return self.currentCommand
        elif (self.commandType() in [CommandType.C_PUSH, CommandType.C_POP, CommandType.C_LABEL, CommandType.C_GOTO, CommandType.C_IF, CommandType.C_FUNCTION, CommandType.C_CALL]):
            return self.currentCommand.split()[1]
        else:
            return NULL

    def arg2(self):
        if (self.commandType() in [CommandType.C_PUSH, CommandType.C_POP, CommandType.C_FUNCTION, CommandType.C_CALL]):
            return self.currentCommand.split()[2]
        else:
            return NULL
    
    #for debugging
    def printcurrentcommand(self):
        print(self.currentCommand)

class CodeWriter():
    def __init__(self, filepath):
        self.file = open(filepath, "w")
        self.filename = filepath
        self.lines_to_write = []
        self.eq_counter = 0
        self.gt_counter = 0
        self.lt_counter = 0

    def __write(self, string):
        self.lines_to_write.append(string)

    def set_filename(self, filename):
        print("New vm file being translated")

    def write_arithmetic(self, command):
        if command == "add":
            self.__write("@SP\nM=M-1\nA=M\nD=M\nA=A-1\nM=D+M\n")
        elif command == "sub":
            self.__write("@SP\nM=M-1\nA=M\nD=M\nA=A-1\nM=M-D\n")
        elif command == "neg":
            self.__write("@SP\nA=M-1\nM=-M\n")
        elif command == "eq":
            self.__write("@SP\nM=M-1\nA=M\nD=M\nA=A-1\nD=M-D\n@EQ%d\nD;JEQ\n@SP\nA=M-1\nM=0\n@DEQ%d\n0;JMP\n(EQ%d)\n@SP\nA=M-1\nM=-1\n(DEQ%d)\n" % (self.eq_counter, self.eq_counter, self.eq_counter, self.eq_counter))
            self.eq_counter = self.eq_counter + 1
        elif command == "gt":
            self.__write("@SP\nM=M-1\nA=M\nD=M\nA=A-1\nD=M-D\n@GT%d\nD;JGT\n@SP\nA=M-1\nM=0\n@DGT%d\n0;JMP\n(GT%d)\n@SP\nA=M-1\nM=-1\n(DGT%d)\n" % (self.gt_counter, self.gt_counter, self.gt_counter, self.gt_counter))
            self.gt_counter = self.gt_counter + 1
        elif command == "lt":
            self.__write("@SP\nM=M-1\nA=M\nD=M\nA=A-1\nD=M-D\n@LT%d\nD;JLT\n@SP\nA=M-1\nM=0\n@DLT%d\n0;JMP\n(LT%d)\n@SP\nA=M-1\nM=-1\n(DLT%d)\n" % (self.lt_counter, self.lt_counter, self.lt_counter, self.lt_counter))
            self.lt_counter = self.lt_counter + 1            
        elif command == "and":
            self.__write("@SP\nM=M-1\nA=M\nD=M\nA=A-1\nM=D&M\n")
        elif command == "or":
            self.__write("@SP\nM=M-1\nA=M\nD=M\nA=A-1\nM=D|M\n")
        elif command == "not":
            self.__write("@SP\nA=M-1\nM=!M")

    def write_pushpop(self, command, segment, index):
        if (command == CommandType.C_PUSH):
            if (DEBUG):     #REMOVE LATER
                self.__write("//%s %s %s\n" % (command, segment, index))

            if segment == "constant":
                self.__write("@%s\nD=A\n@SP\nA=M\nM=D\n@SP\nM=M+1\n" % (index))
            elif segment == "local":
                self.__write("@%s\nD=A\n@LCL\nA=D+M\nD=M\n@SP\nA=M\nM=D\n@SP\nM=M+1\n" % (index))
            elif segment == "argument":
                self.__write("@%s\nD=A\n@ARG\nA=D+M\nD=M\n@SP\nA=M\nM=D\n@SP\nM=M+1\n" % (index))
            elif segment == "this":
                self.__write("@%s\nD=A\n@THIS\nA=D+M\nD=M\n@SP\nA=M\nM=D\n@SP\nM=M+1\n" % (index))
            elif segment == "that":
                self.__write("@%s\nD=A\n@THAT\nA=D+M\nD=M\n@SP\nA=M\nM=D\n@SP\nM=M+1\n" % (index))
            elif segment == "pointer":
                self.__write("@%s\nD=A\n@3\nA=D+A\nD=M\n@SP\nA=M\nM=D\n@SP\nM=M+1\n" % (index))
            elif segment == "temp":
                self.__write("@%s\nD=A\n@5\nA=D+A\nD=M\n@SP\nA=M\nM=D\n@SP\nM=M+1\n" % (index))
            elif segment == "static":
                self.__write("@%s.%s\nD=M\n@SP\nA=M\nM=D\n@SP\nM=M+1\n" % (self.filename.split(".")[0].split("\\")[-1],index))
            
        elif (command == CommandType.C_POP):
            if (DEBUG):     #REMOVE LATER
                self.__write("//%s %s %s\n" % (command, segment, index))
            if segment == "local":
                self.__write("@%s\nD=A\n@LCL\nD=D+M\n@13\nM=D\n@SP\nM=M-1\nA=M\nD=M\n@13\nA=M\nM=D\n" % (index))
            elif segment == "argument":
                self.__write("@%s\nD=A\n@ARG\nD=D+M\n@13\nM=D\n@SP\nM=M-1\nA=M\nD=M\n@13\nA=M\nM=D\n" % (index))
            elif segment == "this":
                self.__write("@%s\nD=A\n@THIS\nD=D+M\n@13\nM=D\n@SP\nM=M-1\nA=M\nD=M\n@13\nA=M\nM=D\n" % (index))
            elif segment == "that":
                self.__write("@%s\nD=A\n@THAT\nD=D+M\n@13\nM=D\n@SP\nM=M-1\nA=M\nD=M\n@13\nA=M\nM=D\n" % (index))
            elif segment == "pointer":
                self.__write("@%s\nD=A\n@3\nD=D+A\n@13\nM=D\n@SP\nM=M-1\nA=M\nD=M\n@13\nA=M\nM=D\n" % (index))
            elif segment == "temp":
                self.__write("@%s\nD=A\n@5\nD=D+A\n@13\nM=D\n@SP\nM=M-1\nA=M\nD=M\n@13\nA=M\nM=D\n" % (index))
            elif segment == "static":
                self.__write("@SP\nM=M-1\nA=M\nD=M\n@%s.%s\nM=D\n" % (self.filename.split(".")[0].split("\\")[-1], index))
            

    def close(self):
        self.file.writelines(self.lines_to_write)
        self.file.close()



def main():
    filepath = sys.argv[1]      
    parser = Parser(filepath)
    code_writer = CodeWriter(filepath.split(".")[0] + ".asm")
    while(parser.hasMoreCommands()):
        parser.advance() 
        if (parser.commandType() == CommandType.C_ARITHMETIC):
            code_writer.write_arithmetic(parser.arg1())
        elif (parser.commandType() == CommandType.C_PUSH or parser.commandType() == CommandType.C_POP):
            code_writer.write_pushpop(parser.commandType(), parser.arg1(), parser.arg2())
    code_writer.close()
main()