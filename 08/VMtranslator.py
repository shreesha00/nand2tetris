import sys
import os
arithmetic_logic = ["add","sub","neg","eq","lt","gt","and","or","not"]
path = sys.argv[1]
code = []
nfiles = 0
filenames = []
filename = path.split("/")[-1]
for root, dirs, files in os.walk(path):
    for file in files:
        if file.endswith('.vm'):
            filenames.append(file)
            nfiles=nfiles+1
            with open(os.path.join(path,file)) as f:
                code.extend(f.readlines())
                code.append("Next file coming up")

code.pop()
def cleaner(code):
    code = [x.split('/')[0] for x in code]
    code = [x.replace('\r','') for x in code]
    code = [x.replace('\t','') for x in code]
    code = [x.replace('\n','') for x in code]
    code = [x.strip() for x in code]
    while '' in code: code.remove('')
    return code

codedictal = {
 "add" : ["@SP","AM=M-1","D=M","A=A-1","M=D+M"],
 "sub" : ["@SP","AM=M-1","D=M","A=A-1","M=M-D"],
 "or" : ["@SP","AM=M-1","D=M","A=A-1","M=D|M"],
 "and" : ["@SP","AM=M-1","D=M","A=A-1","M=D&M"],
 "neg" : ["@SP","A=M-1","M=-M"],
 "not" : ["@SP","A=M-1","M=!M"],
 "eq" : ["@SP","AM=M-1","D=M","A=A-1","D=M-D","M=-1"],
 "eqend" : ["D;JEQ","@SP","A=M-1","M=0"],
 "gt" : ["@SP","AM=M-1","D=M","A=A-1","D=M-D","M=-1"],
 "gtend" : ["D;JGT","@SP","A=M-1","M=0"],
 "lt" : ["@SP","AM=M-1","D=M","A=A-1","D=M-D","M=-1"],
 "ltend" : ["D;JLT","@SP","A=M-1","M=0"]
 }

def commandType(string):
    if(string.split()[0] in arithmetic_logic):
        return "al"
    elif(string.split()[0]=="push"):
        return "pu"
    elif(string.split()[0]=="pop"):
        return "po"
    elif(string.split()[0]=="label"):
        return "lab"
    elif(string.split()[0]=="goto"):
        return "got"
    elif(string.split()[0]=="if-goto"):
        return "ifgot"
    elif(string.split()[0]=="function"):
        return "fundef"
    elif(string.split()[0]=="call"):
        return "funcall"
    elif(string.split()[0]=="return"):
        return "funret"

def pushpoptype(string):
    if(commandType(string)=="pu" or commandType(string)=="po"):
        return (string.split()[1],string.split()[2])

pushend = ["@SP","A=M","M=D","@SP","M=M+1"]
def pushhandling(segment,index):
    code = []
    code.append("@"+index)
    code.append("D=A")
    if(segment == "constant"):
        code.extend(pushend)
    elif(segment == "local"):
        code.extend(["@LCL","A=D+M","D=M"])
        code.extend(pushend)
    elif(segment == "this"):
        code.extend(["@THIS","A=D+M","D=M"])
        code.extend(pushend)
    elif(segment == "that"):
        code.extend(["@THAT","A=D+M","D=M"])
        code.extend(pushend)
    elif(segment == "argument"):
        code.extend(["@ARG","A=D+M","D=M"])
        code.extend(pushend)
    elif(segment == "pointer"):
        code.extend(["@3","A=D+A","D=M"])
        code.extend(pushend)
    elif(segment == "temp"):
        code.extend(["@5","A=D+A","D=M"])
        code.extend(pushend)
    elif(segment == "static"):
        code.extend(["@"+filename+"."+index,"D=M"])
        code.extend(pushend)
    return code

poppart = ["@SP","AM=M-1","D=M","M=0"]
def pophandling(segment,index):
    code = []
    code.append("@"+index)
    code.append("D=A")
    if(segment == "local"):
        code.extend(["@LCL","A=D+M","D=A","@R13","M=D"])
        code.extend(poppart)
        code.extend(["@R13","A=M","M=D","@R13","M=0"])
    elif(segment == "argument"):
        code.extend(["@ARG","A=D+M","D=A","@R13","M=D"])
        code.extend(poppart)
        code.extend(["@R13","A=M","M=D","@R13","M=0"])
    elif(segment == "this"):
        code.extend(["@THIS","A=D+M","D=A","@R13","M=D"])
        code.extend(poppart)
        code.extend(["@R13","A=M","M=D","@R13","M=0"])
    elif(segment == "that"):
        code.extend(["@THAT","A=D+M","D=A","@R13","M=D"])
        code.extend(poppart)
        code.extend(["@R13","A=M","M=D","@R13","M=0"])
    elif(segment == "temp"):
        code.extend(["@5","A=D+A","D=A","@R13","M=D"])
        code.extend(poppart)
        code.extend(["@R13","A=M","M=D","@R13","M=0"])
    elif(segment == "pointer"):
        code.extend(["@3","A=D+A","D=A","@R13","M=D"])
        code.extend(poppart)
        code.extend(["@R13","A=M","M=D","@R13","M=0"])
    elif(segment == "static"):
        code.extend(["@"+filename+"."+index,"D=A","@R13","M=D"])
        code.extend(poppart)
        code.extend(["@R13","A=M","M=D","@R13","M=0"])
    return code

def controlparts(string):
    return string.split()[1]

def controlhandling(string,currentfunction):
    code = []
    if(commandType(string)=="lab"):
        code.append("("+currentfunction+"$"+controlparts(string)+")")
    elif(commandType(string)=="got"):
        code.append("@"+currentfunction+"$"+controlparts(string))
        code.append("0;JMP")
    elif(commandType(string)=="ifgot"):
        code.extend(["@SP","AM=M-1","D=M","@"+currentfunction+"$"+controlparts(string),"D;JNE"])
    return code

def functionparts(string):
    if(commandType(string)=="fundef"):
        return (string.split()[1],string.split()[2])
    elif(commandType(string)=="funcall"):
        return (string.split()[1],string.split()[2])

def functionhandling(string,i,filename):
    code = []
    if(commandType(string)=="fundef"):
        fname,lcl = functionparts(string)
        code.append("("+fname+")")
        code.extend(["@"+lcl,"D=A","("+str(i)+fname+"2"+")","@"+str(i)+fname+"1","D;JLE","@SP","AM=M+1"])
        code.extend(["A=A-1","M=0","D=D-1","@"+str(i)+fname+"2","0;JMP","("+str(i)+fname+"1"+")"])
    elif(commandType(string)=="funcall"):
        fname,args = functionparts(string)
        code.extend(["@fret"+filename+str(i),"D=A","@SP","AM=M+1","A=A-1","M=D"])
        code.extend(["@LCL","D=M","@SP","AM=M+1","A=A-1","M=D"])
        code.extend(["@ARG","D=M","@SP","AM=M+1","A=A-1","M=D"])
        code.extend(["@THIS","D=M","@SP","AM=M+1","A=A-1","M=D"])
        code.extend(["@THAT","D=M","@SP","AM=M+1","A=A-1","M=D"])
        code.extend(["@SP","D=M","@"+args,"D=D-A","@5","D=D-A","@ARG","M=D"])
        code.extend(["@SP","D=M","@LCL","M=D"])
        code.extend(["@"+fname,"0;JMP"])
        code.extend(["(fret"+filename+str(i)+")"])
    elif(commandType(string)=="funret"):
        code.extend(["@LCL","D=M","@R14","M=D","@5","D=A"])
        code.extend(["@R14","A=M-D","D=M","@R15","M=D"])
        code.extend(["@SP","AM=M-1","D=M","@ARG","A=M","M=D"])
        code.extend(["@ARG","D=M","@SP","M=D+1"])
        code.extend(["@R14","A=M-1","D=M","@THAT","M=D"])
        code.extend(["@R14","A=M-1","A=A-1","D=M","@THIS","M=D"])
        code.extend(["@R14","A=M-1","A=A-1","A=A-1","D=M","@ARG","M=D"])
        code.extend(["@R14","A=M-1","A=A-1","A=A-1","A=A-1","D=M","@LCL","M=D"])
        code.extend(["@R15","A=M","0;JMP"])
    return code

finalcode = []
if(nfiles!=1):
    finalcode.extend(["@256","D=A","@SP","M=D"])
    finalcode.extend(["@fret"+filename+"1","D=A","@SP","AM=M+1","A=A-1","M=D"])
    finalcode.extend(["@LCL","D=M","@SP","AM=M+1","A=A-1","M=D"])
    finalcode.extend(["@ARG","D=M","@SP","AM=M+1","A=A-1","M=D"])
    finalcode.extend(["@THIS","D=M","@SP","AM=M+1","A=A-1","M=D"])
    finalcode.extend(["@THAT","D=M","@SP","AM=M+1","A=A-1","M=D"])
    finalcode.extend(["@SP","D=M","@0","D=D-A","@5","D=D-A","@ARG","M=D"])
    finalcode.extend(["@SP","D=M","@LCL","M=D"])
    finalcode.extend(["@"+"Sys.init","0;JMP"])
    finalcode.extend(["(fret"+filename+"1"+")"])

def codewriter(string,i,filename,currentfunction):
    finalcode.append("//"+string)
    if(commandType(string)=="al"):
        finalcode.extend(codedictal[string.split()[0]])
        if(string.split()[0] == "gt" or string.split()[0] == "lt" or string.split()[0] == "eq"):
            finalcode.append("@IFEQ"+str(i)+filename)
            finalcode.extend(codedictal[string.split()[0]+"end"])
            finalcode.append("(IFEQ"+str(i)+filename+")")
    elif(commandType(string)=="funret" or commandType(string)=="funcall" or commandType(string)=="fundef"):
        if(commandType(string)=="fundef"):
            currentfunction = functionparts(string)[0]
        elif(commandType(string)=="funcall"):
            currentfunction = functionparts(string)[0]
        finalcode.extend(functionhandling(string,i,filename))
    elif(commandType(string)=="pu"):
        segment,index = pushpoptype(string)
        finalcode.extend(pushhandling(segment,index))
    elif(commandType(string)=="po"):
        segment,index = pushpoptype(string)
        finalcode.extend(pophandling(segment,index))
    elif(commandType(string)=="lab" or commandType(string)=="got" or commandType(string)=="ifgot"):
        finalcode.extend(controlhandling(string,currentfunction))
    return currentfunction

cleanedcode = cleaner(code)
length = len(cleanedcode)
currentfunction = ""
j=0
for i in range(length):
    if(cleanedcode[i]=="Next file coming up" and j<len(filenames)):
        filename = filenames[j+1]
        j = j+1
    currentfunction = codewriter(cleanedcode[i],i,filename,currentfunction)

def file_creator(code,filename):
    with open(filename,'w') as f:
        for x in code:
            f.write(x)
            f.write("\n")

filename = path.split("/")[-1]
file_creator(finalcode,filename.split(".")[0]+".asm")
