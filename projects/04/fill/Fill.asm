// This file is part of www.nand2tetris.org
// and the book "The Elements of Computing Systems"
// by Nisan and Schocken, MIT Press.
// File name: projects/04/Fill.asm

// Runs an infinite loop that listens to the keyboard input.
// When a key is pressed (any key), the program blackens the screen,
// i.e. writes "black" in every pixel;
// the screen should remain fully black as long as the key is pressed. 
// When no key is pressed, the program clears the screen, i.e. writes
// "white" in every pixel;
// the screen should remain fully clear as long as no key is pressed.

// Put your code here.
(LOOP)
    @KBD
    D=M
    @CLEAR
    D;JEQ

    @color
    M=-1
    @FILL
    0;JMP

(CLEAR)    
    @color
    M=0

(FILL)
    @SCREEN
    D=A
    @current
    M=D

(LOOPFILL)
    @color
    D=M
    @current
    A=M
    M=D
    @current
    M=M+1
    D=M
    @KBD
    D=A-D
    @LOOPFILL
    D;JGT

    @LOOP
    0;JMP