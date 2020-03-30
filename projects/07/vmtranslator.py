#vmtranslator for Hack language
#Usage: python vmtranslator.py [directory|filename]
#Output: directory\[directory|filename].asm 
DEBUG = 1
import sys
import os
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
        elif (command_tokens[0] == "label"):
            return CommandType.C_LABEL
        elif (command_tokens[0] == "goto"):
            return CommandType.C_GOTO
        elif (command_tokens[0] == "if-goto"):
            return CommandType.C_IF
        elif (command_tokens[0] == "function"):
            return CommandType.C_FUNCTION
        elif (command_tokens[0] == "return"):
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
        self.lines_to_write = []
        self.ret_add_counter = 0
        self.current_f = ""
        self.eq_counter = 0
        self.gt_counter = 0
        self.lt_counter = 0

    def __write(self, string):
        self.lines_to_write.append(string)

    def set_filename(self, filepath):
        self.filename = filepath

    def __set_current_f(self, functionName):
        self.current_f = functionName

    def write_arithmetic(self, command):
        if (DEBUG):     #REMOVE LATER
            self.__write("//%s \n" % (command))

        if command == "add":
            self.__write("@SP\nAM=M-1\nD=M\nA=A-1\nM=D+M\n")
        elif command == "sub":
            self.__write("@SP\nAM=M-1\nD=M\nA=A-1\nM=M-D\n")
        elif command == "neg":
            self.__write("@SP\nA=M-1\nM=-M\n")
        elif command == "eq":
            self.__write("@SP\nAM=M-1\nD=M\nA=A-1\nD=M-D\n@EQ%d\nD;JEQ\n@SP\nA=M-1\nM=0\n@DEQ%d\n0;JMP\n(EQ%d)\n@SP\nA=M-1\nM=-1\n(DEQ%d)\n" % (self.eq_counter, self.eq_counter, self.eq_counter, self.eq_counter))
            self.eq_counter = self.eq_counter + 1
        elif command == "gt":
            self.__write("@SP\nAM=M-1\nD=M\nA=A-1\nD=M-D\n@GT%d\nD;JGT\n@SP\nA=M-1\nM=0\n@DGT%d\n0;JMP\n(GT%d)\n@SP\nA=M-1\nM=-1\n(DGT%d)\n" % (self.gt_counter, self.gt_counter, self.gt_counter, self.gt_counter))
            self.gt_counter = self.gt_counter + 1
        elif command == "lt":
            self.__write("@SP\nAM=M-1\nD=M\nA=A-1\nD=M-D\n@LT%d\nD;JLT\n@SP\nA=M-1\nM=0\n@DLT%d\n0;JMP\n(LT%d)\n@SP\nA=M-1\nM=-1\n(DLT%d)\n" % (self.lt_counter, self.lt_counter, self.lt_counter, self.lt_counter))
            self.lt_counter = self.lt_counter + 1            
        elif command == "and":
            self.__write("@SP\nAM=M-1\nD=M\nA=A-1\nM=D&M\n")
        elif command == "or":
            self.__write("@SP\nAM=M-1\nD=M\nA=A-1\nM=D|M\n")
        elif command == "not":
            self.__write("@SP\nA=M-1\nM=!M")

    def write_pushpop(self, command, segment, index):
        if (command == CommandType.C_PUSH):
            if (DEBUG):     #REMOVE LATER
                self.__write("//%s %s %s\n" % (command, segment, index))

            if segment == "constant":
                self.__write("@%s\nD=A\n@SP\nAM=M+1\nA=A-1\nM=D\n" % (index))
            elif segment == "local":
                self.__write("@%s\nD=A\n@LCL\nA=D+M\nD=M\n@SP\nAM=M+1\nA=A-1\nM=D\n" % (index))
            elif segment == "argument":
                self.__write("@%s\nD=A\n@ARG\nA=D+M\nD=M\n@SP\nAM=M+1\nA=A-1\nM=D\n" % (index))
            elif segment == "this":
                self.__write("@%s\nD=A\n@THIS\nA=D+M\nD=M\n@SP\nAM=M+1\nA=A-1\nM=D\n" % (index))
            elif segment == "that":
                self.__write("@%s\nD=A\n@THAT\nA=D+M\nD=M\n@SP\nAM=M+1\nA=A-1\nM=D\n" % (index))
            elif segment == "pointer":
                self.__write("@%s\nD=A\n@3\nA=D+A\nD=M\n@SP\nAM=M+1\nA=A-1\nM=D\n" % (index))
            elif segment == "temp":
                self.__write("@%s\nD=A\n@5\nA=D+A\nD=M\n@SP\nAM=M+1\nA=A-1\nM=D\n" % (index))
            elif segment == "static":
                self.__write("@%s.%s\nD=M\n@SP\nAM=M+1\nA=A-1\nM=D\n" % (self.filename.split(".")[0].split("\\")[-1],index))
            
        elif (command == CommandType.C_POP):
            if (DEBUG):     #REMOVE LATER
                self.__write("//%s %s %s\n" % (command, segment, index))
            if segment == "local":
                self.__write("@%s\nD=A\n@LCL\nD=D+M\n@R13\nM=D\n@SP\nAM=M-1\nD=M\n@R13\nA=M\nM=D\n" % (index))
            elif segment == "argument":
                self.__write("@%s\nD=A\n@ARG\nD=D+M\n@R13\nM=D\n@SP\nAM=M-1\nD=M\n@R13\nA=M\nM=D\n" % (index))
            elif segment == "this":
                self.__write("@%s\nD=A\n@THIS\nD=D+M\n@R13\nM=D\n@SP\nAM=M-1\nD=M\n@R13\nA=M\nM=D\n" % (index))
            elif segment == "that":
                self.__write("@%s\nD=A\n@THAT\nD=D+M\n@R13\nM=D\n@SP\nAM=M-1\nD=M\n@R13\nA=M\nM=D\n" % (index))
            elif segment == "pointer":
                self.__write("@%s\nD=A\n@3\nD=D+A\n@R13\nM=D\n@SP\nAM=M-1\nD=M\n@R13\nA=M\nM=D\n" % (index))
            elif segment == "temp":
                self.__write("@%s\nD=A\n@5\nD=D+A\n@R13\nM=D\n@SP\nAM=M-1\nD=M\n@R13\nA=M\nM=D\n" % (index))
            elif segment == "static":
                self.__write("@SP\nAM=M-1\nD=M\n@%s.%s\nM=D\n" % (self.filename.split(".")[0].split("\\")[-1], index))
            
    def writeInit(self):
        self.__write("@256\nD=A\n@SP\nM=D\n")
        self.writeCall("Sys.init", 0)

    def writeLabel(self, label):
        if (DEBUG):     #REMOVE LATER
            self.__write("//label %s \n" % (label))
        if (self.current_f != ""):
            self.__write("(%s$%s)\n" % (self.current_f,label))
        else:
            self.__write("(%s)\n" % (label))

    def writeGoto(self, label):
        if (DEBUG):     #REMOVE LATER
            self.__write("//goto %s \n" % (label))
        if (self.current_f != ""):
            self.__write("@%s$%s\n0;JMP\n" % (self.current_f, label))
        else:
            self.__write("@%s\n0;JMP\n" % (label))

    def writeIf(self, label):
        if (DEBUG):     #REMOVE LATER
            self.__write("//if-goto %s \n" % (label))
        if(self.current_f != ""):
            self.__write("@SP\nAM=M-1\nD=M\n@%s$%s\nD;JNE\n" % (self.current_f,label))
        else:
            self.__write("@SP\nAM=M-1\nD=M\n@%s\nD;JNE\n" % (label))

    def writeCall(self, functionName, numArgs):
        if (DEBUG):     #REMOVE LATER
            self.__write("//call %s %s \n" % (functionName, numArgs))
        
        self.__write("@RETADD%d\nD=A\n@SP\nAM=M+1\nA=A-1\nM=D\n" % (self.ret_add_counter))    #push return address
        self.__write("@LCL\nD=M\n@SP\nAM=M+1\nA=A-1\nM=D\n")                            #push LCL
        self.__write("@ARG\nD=M\n@SP\nAM=M+1\nA=A-1\nM=D\n")                            #push ARG
        self.__write("@THIS\nD=M\n@SP\nAM=M+1\nA=A-1\nM=D\n")                            #push THIS
        self.__write("@THAT\nD=M\n@SP\nAM=M+1\nA=A-1\nM=D\n")                            #push THAT
        self.__write("@SP\nD=M\n@5\nD=D-A\n@%s\nD=D-A\n@ARG\nM=D\n" % (numArgs))          #Reposition ARG
        self.__write("@SP\nD=M\n@LCL\nM=D\n")                                              #Reposition LCL
        self.__write("@%s\n0;JMP\n" % (functionName))                                       #goto function
        self.__write("(RETADD%d)\n" %(self.ret_add_counter))                                   #label for return-address
        self.ret_add_counter = self.ret_add_counter + 1


    def writeReturn(self):
        if (DEBUG):     #REMOVE LATER
            self.__write("//return\n")

        self.__write("@LCL\nD=M\n@R13\nM=D\n@5\nA=D-A\nD=M\n@R14\nM=D\n")   #put the return address in R14
        self.__write("@SP\nAM=M-1\nD=M\n@ARG\nA=M\nM=D\n")                   #reposition the return value
        self.__write("D=A+1\n@SP\nM=D\n")                                   #restore the SP
        self.__write("@R13\nAM=M-1\nD=M\n@THAT\nM=D\n")                      #restore THAT
        self.__write("@R13\nAM=M-1\nD=M\n@THIS\nM=D\n")                      #restore THIS
        self.__write("@R13\nAM=M-1\nD=M\n@ARG\nM=D\n")                       #restore ARG
        self.__write("@R13\nA=M-1\nD=M\n@LCL\nM=D\n")                       #restore LCL
        self.__write("@R14\nA=M\n0;JMP\n")                                       #goto return address           

    def writeFunction(self, functionName, numLocals):
        if (DEBUG):     #REMOVE LATER
            self.__write("//function %s %s \n" % (functionName, numLocals))

            self.__write("(%s)\n" % (functionName))
        if (int(numLocals) !=0):
            self.__write("@%s\nD=A\n(%sAddLocal)\n" % (numLocals, functionName)) 
            self.__write("@SP\nAM=M+1\nA=A-1\nM=0\n")
            self.__write("@%sAddLocal\n" % (functionName))
            self.__write("D=D-1;JGT\n")
        self.__set_current_f(functionName)

    def close(self):
        self.file.writelines(self.lines_to_write)
        self.file.close()



def main():
    if len(sys.argv) < 2:
        filepath = os.getcwd()
    else:
        filepath = sys.argv[1]
    files_to_translate = []
    outputfile = ""   
    if os.path.isfile(filepath):
        if(filepath[-3:] != ".vm"):
            print("File is not .vm file")
        else:
            files_to_translate.append(filepath)
            outputfile = ("%s.%s" % (filepath.split(".")[0], "asm"))
    elif os.path.isdir(filepath):
        outputfile = ("%s\\%s.%s" % (filepath, filepath.split("\\")[-1], "asm"))
        for filename in os.listdir(filepath):
            if(".vm" in filename):
                files_to_translate.append("%s\\%s" % (filepath, filename))                
    code_writer = CodeWriter(outputfile)
    code_writer.writeInit()
    for filename in files_to_translate:
        parser = Parser(filename)
        code_writer.set_filename(filename.split(".")[0])
        while(parser.hasMoreCommands()):
            parser.advance() 
            if (parser.commandType() == CommandType.C_ARITHMETIC):
                code_writer.write_arithmetic(parser.arg1())
            elif (parser.commandType() == CommandType.C_PUSH or parser.commandType() == CommandType.C_POP):
                code_writer.write_pushpop(parser.commandType(), parser.arg1(), parser.arg2())
            elif (parser.commandType() == CommandType.C_LABEL):
                code_writer.writeLabel(parser.arg1())
            elif (parser.commandType() == CommandType.C_GOTO):
                code_writer.writeGoto(parser.arg1())
            elif (parser.commandType() == CommandType.C_IF):
                code_writer.writeIf(parser.arg1())
            elif (parser.commandType() == CommandType.C_CALL):
                code_writer.writeCall(parser.arg1(), parser.arg2())
            elif (parser.commandType() == CommandType.C_RETURN):
                code_writer.writeReturn()
            elif (parser.commandType() == CommandType.C_FUNCTION):
                code_writer.writeFunction(parser.arg1(), parser.arg2())
    code_writer.close()
main()