import sys
file = sys.argv[1]
filename = file.split(".")[0]
arithmetic_logic = ["add","sub","neg","eq","lt","gt","and","or","not"]
def inititalizer(file):
    with open(file,'r') as f:
        code = f.readlines()
    return code

def cleaner(code):
    code = [x.split('/')[0] for x in code]
    code = [x.replace('\r','') for x in code]
    code = [x.replace('\t','') for x in code]
    code = [x.replace('\n','') for x in code]
    while '' in code: code.remove('')
    return code

def commandType(string):
    if(string in arithmetic_logic):
        return "al"
    elif(string.split()[0]=="push"):
        return "pu"
    elif(string.split()[0]=="pop"):
        return "po"

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

finalcode = []
def codewriter(string,i,filename):
    if(commandType(string)=="al"):
        finalcode.append("//"+string)
        finalcode.extend(codedictal[string])
        if(string == "gt" or string == "lt" or string == "eq"):
            finalcode.append("@IFEQ"+str(i)+filename)
            finalcode.extend(codedictal[string+"end"])
            finalcode.append("(IFEQ"+str(i)+filename+")")
    elif(commandType(string)=="pu"):
        finalcode.append("//"+string)
        segment,index = pushpoptype(string)
        finalcode.extend(pushhandling(segment,index))
    elif(commandType(string)=="po"):
        finalcode.append("//"+string)
        segment,index = pushpoptype(string)
        finalcode.extend(pophandling(segment,index))


code = inititalizer(file)
cleanedcode = cleaner(code)
length = len(cleanedcode)
for i in range(length):
    codewriter(cleanedcode[i],i,filename)
finalcode.extend(["(END)","@END","0;JMP"])
def file_creator(code,filename):
    with open(filename,'w') as f:
        for x in code:
            f.write(x)
            f.write("\n")
file_creator(finalcode,filename.split(".")[0]+".asm")
