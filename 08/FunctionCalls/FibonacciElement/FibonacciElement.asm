@256
D=A
@SP
M=D
@fretFibonacciElement1
D=A
@SP
AM=M+1
A=A-1
M=D
@LCL
D=M
@SP
AM=M+1
A=A-1
M=D
@ARG
D=M
@SP
AM=M+1
A=A-1
M=D
@THIS
D=M
@SP
AM=M+1
A=A-1
M=D
@THAT
D=M
@SP
AM=M+1
A=A-1
M=D
@SP
D=M
@0
D=D-A
@5
D=D-A
@ARG
M=D
@SP
D=M
@LCL
M=D
@Sys.init
0;JMP
(fretFibonacciElement1)
//function Main.fibonacci 0
(Main.fibonacci)
@0
D=A
(0Main.fibonacci2)
@0Main.fibonacci1
D;JLE
@SP
AM=M+1
A=A-1
M=0
D=D-1
@0Main.fibonacci2
0;JMP
(0Main.fibonacci1)
//push argument 0
@0
D=A
@ARG
A=D+M
D=M
@SP
A=M
M=D
@SP
M=M+1
//push constant 2
@2
D=A
@SP
A=M
M=D
@SP
M=M+1
//lt
@SP
AM=M-1
D=M
A=A-1
D=M-D
M=-1
@IFEQ3FibonacciElement
D;JLT
@SP
A=M-1
M=0
(IFEQ3FibonacciElement)
//if-goto IF_TRUE
@SP
AM=M-1
D=M
@Main.fibonacci$IF_TRUE
D;JNE
//goto IF_FALSE
@Main.fibonacci$IF_FALSE
0;JMP
//label IF_TRUE
(Main.fibonacci$IF_TRUE)
//push argument 0
@0
D=A
@ARG
A=D+M
D=M
@SP
A=M
M=D
@SP
M=M+1
//return
@LCL
D=M
@R14
M=D
@5
D=A
@R14
A=M-D
D=M
@R15
M=D
@SP
AM=M-1
D=M
@ARG
A=M
M=D
@ARG
D=M
@SP
M=D+1
@R14
A=M-1
D=M
@THAT
M=D
@R14
A=M-1
A=A-1
D=M
@THIS
M=D
@R14
A=M-1
A=A-1
A=A-1
D=M
@ARG
M=D
@R14
A=M-1
A=A-1
A=A-1
A=A-1
D=M
@LCL
M=D
@R15
A=M
0;JMP
//label IF_FALSE
(Main.fibonacci$IF_FALSE)
//push argument 0
@0
D=A
@ARG
A=D+M
D=M
@SP
A=M
M=D
@SP
M=M+1
//push constant 2
@2
D=A
@SP
A=M
M=D
@SP
M=M+1
//sub
@SP
AM=M-1
D=M
A=A-1
M=M-D
//call Main.fibonacci 1
@fretFibonacciElement13
D=A
@SP
AM=M+1
A=A-1
M=D
@LCL
D=M
@SP
AM=M+1
A=A-1
M=D
@ARG
D=M
@SP
AM=M+1
A=A-1
M=D
@THIS
D=M
@SP
AM=M+1
A=A-1
M=D
@THAT
D=M
@SP
AM=M+1
A=A-1
M=D
@SP
D=M
@1
D=D-A
@5
D=D-A
@ARG
M=D
@SP
D=M
@LCL
M=D
@Main.fibonacci
0;JMP
(fretFibonacciElement13)
//push argument 0
@0
D=A
@ARG
A=D+M
D=M
@SP
A=M
M=D
@SP
M=M+1
//push constant 1
@1
D=A
@SP
A=M
M=D
@SP
M=M+1
//sub
@SP
AM=M-1
D=M
A=A-1
M=M-D
//call Main.fibonacci 1
@fretFibonacciElement17
D=A
@SP
AM=M+1
A=A-1
M=D
@LCL
D=M
@SP
AM=M+1
A=A-1
M=D
@ARG
D=M
@SP
AM=M+1
A=A-1
M=D
@THIS
D=M
@SP
AM=M+1
A=A-1
M=D
@THAT
D=M
@SP
AM=M+1
A=A-1
M=D
@SP
D=M
@1
D=D-A
@5
D=D-A
@ARG
M=D
@SP
D=M
@LCL
M=D
@Main.fibonacci
0;JMP
(fretFibonacciElement17)
//add
@SP
AM=M-1
D=M
A=A-1
M=D+M
//return
@LCL
D=M
@R14
M=D
@5
D=A
@R14
A=M-D
D=M
@R15
M=D
@SP
AM=M-1
D=M
@ARG
A=M
M=D
@ARG
D=M
@SP
M=D+1
@R14
A=M-1
D=M
@THAT
M=D
@R14
A=M-1
A=A-1
D=M
@THIS
M=D
@R14
A=M-1
A=A-1
A=A-1
D=M
@ARG
M=D
@R14
A=M-1
A=A-1
A=A-1
A=A-1
D=M
@LCL
M=D
@R15
A=M
0;JMP
//Next file coming up
//function Sys.init 0
(Sys.init)
@0
D=A
(21Sys.init2)
@21Sys.init1
D;JLE
@SP
AM=M+1
A=A-1
M=0
D=D-1
@21Sys.init2
0;JMP
(21Sys.init1)
//push constant 4
@4
D=A
@SP
A=M
M=D
@SP
M=M+1
//call Main.fibonacci 1
@fretSys.vm23
D=A
@SP
AM=M+1
A=A-1
M=D
@LCL
D=M
@SP
AM=M+1
A=A-1
M=D
@ARG
D=M
@SP
AM=M+1
A=A-1
M=D
@THIS
D=M
@SP
AM=M+1
A=A-1
M=D
@THAT
D=M
@SP
AM=M+1
A=A-1
M=D
@SP
D=M
@1
D=D-A
@5
D=D-A
@ARG
M=D
@SP
D=M
@LCL
M=D
@Main.fibonacci
0;JMP
(fretSys.vm23)
//label WHILE
(Main.fibonacci$WHILE)
//goto WHILE
@Main.fibonacci$WHILE
0;JMP