import sys
import re
import os
keyword = ['class','constructor','function','method','field','static','var','int','char','boolean','void','true','false','null','this','let','do','if','else','while','return']
symbol = ['{','}','(',')','[',']','.',',',';','+','-','*','/','&','|','<','>','=','~']
filenames = sys.argv[2:]
nfiles = int(sys.argv[1])
codes = []
for i in range(nfiles):
    code = ""
    with open(filenames[i],'r') as f:
        for i in f.readlines():
			for j in i:
				code = code + j
        codes.append(code)

def tokenType(string):
    if(string in keyword):
        return "keyword"
    elif(string in symbol):
        return "symbol"
    elif(string[0]=='"' and string[-1]=='"' and ('"' not in string[1:-1])):
        return "stringConstant"
    elif(string.isdigit() and int(string)<=32767 and int(string)>=0):
        return "integerConstant"
    elif(not string[0].isdigit()):
        v = False
        for i in string:
            if(i.isdigit() or i.isalpha() or i=="_"):
                v = False
            else:
                v = True
        if(v==False):
            return "identifier"
        elif(v==True):
            return "unidentified"

def token(string):
    if(tokenType(string) == "identifier"):
        return string
    elif(tokenType(string) == "symbol" and string!="<" and string!=">" and string!='"' and string!='&'):
        return string
    elif(tokenType(string) == "stringConstant"):
        return string[1:-1]
    elif(tokenType(string) == "integerConstant"):
        return int(string)
    elif(tokenType(string) == "keyword"):
        return string
    elif(string=="<"):
        return "&lt;"
    elif(string==">"):
        return "&gt;"
    elif(string=='"'):
        return "&quot;"
    elif(string=="&"):
        return "&amp;"

def cleaner(codes):
    new = []
    for code in codes:
        code = code.replace("\r"," ")
        code = code.replace("\t"," ")
        code = re.sub("(?s)/\\*.*?\\*/","",code)
        code = re.sub("//.*","",code)
        code = code.replace("\n"," ")
        new.append(code)
    return new

def tokenizer(codes):
    outmain = []
    for code in codes:
        new = ""
        for chr in code:
            if(chr in symbol):
                new = new + " " + chr + " "
            else:
                new = new + chr
        temp = new.split('"')
        A = []
        for i in range(len(temp)):
            if(i%2==0):
                A.extend(temp[i].split())
            else:
                A.append('"'+temp[i]+'"')
        outmain.append(A)
    return outmain

def output(arr):
    out = []
    for code in arr:
        A = ["<tokens>"]
        for i in code:
            A.append("<"+tokenType(i)+"> "+str(token(i))+" </"+tokenType(i)+">")
        A.append("</tokens>")
        out.append(A)
    return out

cleanedcode = cleaner(codes)
splitcode = tokenizer(cleanedcode)
finalcode = output(splitcode)

nfiles = len(filenames)
def tokenfilecreater(finalcode,filenames,nfiles):
    newfilenames = []
    for i in range(nfiles):
        newfilenames.append(filenames[i].split(".")[0]+"T.xml")
    for i in range(nfiles):
        with open(newfilenames[i],'w') as f:
            for j in finalcode[i]:
                f.write(j)
                f.write("\n")

tokenfilecreater(finalcode,filenames,nfiles)
def printspaces(n):
    mycode = ""
    for i in range(2*n):
        mycode = mycode + " "
    return mycode

errfiles = []
for i in range(nfiles):
    errfiles.append(["Error file"])

def checkfor(token,tokentype,string):
    if(tokentype=="identifier" and string.split()[0]=="<identifier>"):
        return True
    elif(tokentype=="stringConstant" and string.split()[0]=="<stringConstant>"):
        return True
    elif(tokentype=="integerConstant" and string.split()[0]=="<integerConstant>"):
        return True
    if(string == "<"+tokentype+">"+" "+token+" </"+tokentype+">"):
        return True
    else:
        return False

def write(truth,string,mycode,n,expectedToken,expectedTokenType,fileno):
    if(truth == True):
        mycode.append(printspaces(n)+string)
    else:
        tokenType = string.split()[0].split("<")[1].split(">")[0]
        token = string.split()[1]
        if(truth == False and expectedTokenType==tokenType and expectedToken!=token):
            errfiles[fileno].append("ERROR: "+token)
            print("Error occured check error files")
        elif(truth == False and expectedTokenType!=tokenType):
            errfiles[fileno].append("ERROR: Expecting <"+expectedTokenType+"> but "+token)
            print("Error occured check error files")
    return mycode

class_symbol_table = {
}

subroutine_table = {
}
static_count = 0
field_count = 0
total_global_count = 0
local_count = 0
argument_count = 0
total_sub_count = 0
currentClassName = ""
currentSubroutineName = ""
currentSubroutinetype = ""
labelnumber = 0
nP = 0
def compileClass(code,i,n,fileno):
    global vmcode
    global static_count
    global field_count
    global total_global_count
    global labelnumber
    global class_symbol_table
    global currentClassName
    global nP
    nP = 0
    static_count = 0
    field_count = 0
    total_global_count = 0
    labelnumber = 0
    class_symbol_table.clear()
    mycode = []
    mycode = write(checkfor("class","keyword",code[i]),code[i],mycode,n,"class","keyword",fileno)
    i = i+1
    mycode = write(checkfor("className","identifier",code[i]),code[i],mycode,n,"className","identifier",fileno)
    currentClassName = code[i].split()[1]
    i = i+1
    mycode = write(checkfor("{","symbol",code[i]),code[i],mycode,n,"{","symbol",fileno)
    i = i+1
    while(checkfor("static","keyword",code[i]) or checkfor("field","keyword",code[i])):
        mycode = write(1,"<classVarDec>",mycode,n,"","",fileno)
        n = n+1
        temp = []
        temp,i,n = compileClassVarDec(code,i,n,fileno)
        n = n-1
        mycode.extend(temp)
        mycode = write(1,"</classVarDec>",mycode,n,"","",fileno)
    while(checkfor("constructor","keyword",code[i]) or checkfor("function","keyword",code[i]) or checkfor("method","keyword",code[i])):
        mycode = write(1,"<subroutineDec>",mycode,n,"","",fileno)
        n = n+1
        temp = []
        temp,i,n = compileSubroutineDec(code,i,n,fileno)
        n = n-1
        mycode.extend(temp)
        mycode = write(1,"</subroutineDec>",mycode,n,"","",fileno)
    mycode = write(checkfor("}","symbol",code[i]),code[i],mycode,n,"}","symbol",fileno)
    i = i+1
    return mycode,i,n

def compileClassVarDec(code,i,n,fileno):
    global vmcode
    global static_count
    global field_count
    global total_global_count
    global class_symbol_table
    mycode = []
    mycode = write(1,code[i],mycode,n,"","",fileno)
    stat_field = code[i].split()[1]
    i = i+1
    mycode = write(checkfor("int","keyword",code[i]) or checkfor("char","keyword",code[i]) or checkfor("boolean","keyword",code[i]) or checkfor("className","identifier",code[i]),code[i],mycode,n,"type","type",fileno)
    type = code[i].split()[1]
    i = i+1
    mycode = write(checkfor("varName","identifier",code[i]),code[i],mycode,n,"varName","identifier",fileno)
    varName = code[i].split()[1]
    i = i+1
    if(stat_field=="static"):
        count = static_count
        static_count = static_count+1
    else:
        count = field_count
        stat_field = "this"
        field_count = field_count+1
    class_symbol_table[total_global_count] = [stat_field,type,varName,str(count)]
    total_global_count = total_global_count+1
    while(checkfor(",","symbol",code[i])):
        mycode = write(1,code[i],mycode,n,"","",fileno)
        i = i+1
        mycode = write(checkfor("varName","identifier",code[i]),code[i],mycode,n,"varName","identifier",fileno)
        varName = code[i].split()[1]
        i = i+1
        if(stat_field=="static"):
            count = static_count
            static_count = static_count+1
        else:
            count = field_count
            stat_field = "this"
            field_count = field_count+1
        class_symbol_table[total_global_count] = [stat_field,type,varName,str(count)]
        total_global_count = total_global_count+1
    mycode = write(checkfor(";","symbol",code[i]),code[i],mycode,n,";","symbol",fileno)
    i = i+1
    return mycode,i,n

def compileSubroutineDec(code,i,n,fileno):
    global vmcode
    global subroutine_table
    global local_count
    global argument_count
    global field_count
    global total_sub_count
    global currentSubroutineName
    global currentSubroutinetype
    mycode = []
    mycode = write(1,code[i],mycode,n,"","",fileno)
    con_func_met = code[i].split()[1]
    i = i+1
    boolean = checkfor("className","identifier",code[i]) or checkfor("void","keyword",code[i]) or checkfor("int","keyword",code[i]) or checkfor("char","keyword",code[i]) or checkfor("boolean","keyword",code[i])
    mycode = write(boolean,code[i],mycode,n,"type","type",fileno)
    void_type = code[i].split()[1]
    i = i+1
    mycode = write(checkfor("subroutineName","identifier",code[i]),code[i],mycode,n,"subroutineName","identifier",fileno)
    subroutineName = code[i].split()[1]
    i = i+1
    subroutine_table.clear()
    local_count = 0
    argument_count = 0
    total_sub_count = 0
    currentSubroutineName = subroutineName
    currentSubroutinetype = con_func_met
    if(con_func_met=="method"):
        subroutine_table[total_sub_count] = ["argument",currentClassName,"this",str(0)]
        argument_count = argument_count+1
        total_sub_count = total_sub_count+1
    mycode = write(checkfor("(","symbol",code[i]),code[i],mycode,n,"(","symbol",fileno)
    i = i+1
    temp = []
    mycode = write(1,"<parameterList>",mycode,n,"","",fileno)
    n = n+1
    temp,i,n = compileParameterList(code,i,n,fileno)
    n = n-1
    mycode.extend(temp)
    mycode = write(1,"</parameterList>",mycode,n,"","",fileno)
    mycode = write(checkfor(")","symbol",code[i]),code[i],mycode,n,")","symbol",fileno)
    i = i+1
    mycode = write(1,"<subroutineBody>",mycode,n,"","",fileno)
    n = n+1
    mycode = write(checkfor("{","symbol",code[i]),code[i],mycode,n,"{","symbol",fileno)
    i = i+1
    while(checkfor("var","keyword",code[i])):
        mycode = write(1,"<varDec>",mycode,n,"","",fileno)
        n = n+1
        temp = []
        temp,i,n = compileVarDec(code,i,n,fileno)
        mycode.extend(temp)
        n = n-1
        mycode = write(1,"</varDec>",mycode,n,"","",fileno)
    vmcode.append("function "+currentClassName+"."+currentSubroutineName+" "+str(local_count))
    if(currentSubroutinetype=="constructor"):
        vmcode.append("push constant "+str(field_count))
        vmcode.append("call Memory.alloc 1")
        vmcode.append("pop pointer 0")
    elif(currentSubroutinetype=="method"):
        vmcode.append("push argument 0")
        vmcode.append("pop pointer 0")
    temp = []
    mycode = write(1,"<statements>",mycode,n,"","",fileno)
    n = n+1
    temp,i,n = compileStatements(code,i,n,fileno)
    n = n-1
    mycode.extend(temp)
    mycode = write(1,"</statements>",mycode,n,"","",fileno)
    mycode = write(checkfor("}","symbol",code[i]),code[i],mycode,n,"}","symbol",fileno)
    i = i+1
    n = n-1
    mycode = write(1,"</subroutineBody>",mycode,n,"","",fileno)
    return mycode,i,n

def compileVarDec(code,i,n,fileno):
    global vmcode
    global local_count
    global total_sub_count
    global subroutine_table
    mycode = []
    mycode = write(1,code[i],mycode,n,"","",fileno)
    i = i+1
    mycode = write(checkfor("className","identifier",code[i]) or checkfor("int","keyword",code[i]) or checkfor("char","keyword",code[i]) or checkfor("boolean","keyword",code[i]),code[i],mycode,n,"type","type",fileno)
    type = code[i].split()[1]
    i = i+1
    mycode = write(checkfor("varName","identifier",code[i]),code[i],mycode,n,"varName","identifier",fileno)
    varName = code[i].split()[1]
    i = i+1
    subroutine_table[total_sub_count] = ["local",type,varName,str(local_count)]
    local_count = local_count+1
    total_sub_count = total_sub_count+1
    while(checkfor(",","symbol",code[i])):
        mycode = write(1,code[i],mycode,n,"","",fileno)
        i = i+1
        mycode = write(checkfor("varName","identifier",code[i]),code[i],mycode,n,"varName","identifier",fileno)
        varName = code[i].split()[1]
        subroutine_table[total_sub_count] = ["local",type,varName,str(local_count)]
        local_count = local_count+1
        total_sub_count = total_sub_count+1
        i = i+1
    mycode = write(checkfor(";","symbol",code[i]),code[i],mycode,n,";","symbol",fileno)
    i = i+1
    return mycode,i,n

def compileParameterList(code,i,n,fileno):
    global vmcode
    global argument_count
    global total_sub_count
    global subroutine_table
    mycode = []
    if(checkfor(")","symbol",code[i])):
        return mycode,i,n
    mycode = write(checkfor("className","identifier",code[i]) or checkfor("int","keyword",code[i]) or checkfor("char","keyword",code[i]) or checkfor("boolean","keyword",code[i]),code[i],mycode,n,"type","type",fileno)
    type = code[i].split()[1]
    i = i+1
    mycode = write(checkfor("varName","identifier",code[i]),code[i],mycode,n,"varName","identifier",fileno)
    varName = code[i].split()[1]
    i = i+1
    subroutine_table[total_sub_count] = ["argument",type,varName,str(argument_count)]
    argument_count = argument_count+1
    total_sub_count = total_sub_count+1
    while(checkfor(",","symbol",code[i])):
        mycode = write(1,code[i],mycode,n,"","",fileno)
        i = i+1
        mycode = write(checkfor("className","identifier",code[i]) or checkfor("int","keyword",code[i]) or checkfor("char","keyword",code[i]) or checkfor("boolean","keyword",code[i]),code[i],mycode,n,"type","type",fileno)
        type = code[i].split()[1]
        i = i+1
        mycode = write(checkfor("varName","identifier",code[i]),code[i],mycode,n,"varName","identifier",fileno)
        varName = code[i].split()[1]
        i = i+1
        subroutine_table[total_sub_count] = ["argument",type,varName,str(argument_count)]
        argument_count = argument_count+1
        total_sub_count = total_sub_count+1
    return mycode,i,n

def compileStatements(code,i,n,fileno):
    mycode = []
    while(checkfor("let","keyword",code[i]) or checkfor("do","keyword",code[i]) or checkfor("while","keyword",code[i]) or checkfor("if","keyword",code[i]) or checkfor("return","keyword",code[i])):
        if(checkfor("let","keyword",code[i])):
            mycode = write(1,"<letStatement>",mycode,n,"","",fileno)
            n = n+1
            temp = []
            temp,i,n = compileLetStatement(code,i,n,fileno)
            n = n-1
            mycode.extend(temp)
            mycode = write(1,"</letStatement>",mycode,n,"","",fileno)
        elif(checkfor("if","keyword",code[i])):
            mycode = write(1,"<ifStatement>",mycode,n,"","",fileno)
            n = n+1
            temp = []
            temp,i,n = compileIfStatement(code,i,n,fileno)
            n = n-1
            mycode.extend(temp)
            mycode = write(1,"</ifStatement>",mycode,n,"","",fileno)
        elif(checkfor("while","keyword",code[i])):
            mycode = write(1,"<whileStatement>",mycode,n,"","",fileno)
            n = n+1
            temp = []
            temp,i,n = compileWhileStatement(code,i,n,fileno)
            n = n-1
            mycode.extend(temp)
            mycode = write(1,"</whileStatement>",mycode,n,"","",fileno)
        elif(checkfor("do","keyword",code[i])):
            mycode = write(1,"<doStatement>",mycode,n,"","",fileno)
            n = n+1
            temp = []
            temp,i,n = compileDoStatement(code,i,n,fileno)
            n = n-1
            mycode.extend(temp)
            mycode = write(1,"</doStatement>",mycode,n,"","",fileno)
        elif(checkfor("return","keyword",code[i])):
            mycode = write(1,"<returnStatement>",mycode,n,"","",fileno)
            n = n+1
            temp = []
            temp,i,n = compileReturnStatement(code,i,n,fileno)
            n = n-1
            mycode.extend(temp)
            mycode = write(1,"</returnStatement>",mycode,n,"","",fileno)
    return mycode,i,n

def compileIfStatement(code,i,n,fileno):
    global vmcode
    global currentClassName
    global labelnumber
    TlabelNum = labelnumber
    labelnumber = labelnumber+2
    mycode = []
    mycode = write(1,code[i],mycode,n,"","",fileno)
    i = i+1
    mycode = write(checkfor("(","symbol",code[i]),code[i],mycode,n,"(","symbol",fileno)
    i = i+1
    mycode = write(1,"<expression>",mycode,n,"","",fileno)
    temp = []
    n = n+1
    temp,i,n = compileExpression(code,i,n,fileno)
    mycode.extend(temp)
    n = n-1
    mycode = write(1,"</expression>",mycode,n,"","",fileno)
    mycode = write(checkfor(")","symbol",code[i]),code[i],mycode,n,")","symbol",fileno)
    i = i+1
    mycode = write(checkfor("{","symbol",code[i]),code[i],mycode,n,"{","symbol",fileno)
    i = i+1
    vmcode.append("not")
    vmcode.append("if-goto "+currentClassName+"."+str(TlabelNum))
    mycode = write(1,"<statements>",mycode,n,"","",fileno)
    n = n+1
    temp = []
    temp,i,n = compileStatements(code,i,n,fileno)
    mycode.extend(temp)
    n = n-1
    mycode = write(1,"</statements>",mycode,n,"","",fileno)
    mycode = write(checkfor("}","symbol",code[i]),code[i],mycode,n,"}","symbol",fileno)
    i = i+1
    vmcode.append("goto "+currentClassName+"."+str(TlabelNum+1))
    vmcode.append("label "+currentClassName+"."+str(TlabelNum))
    if(not checkfor("else","keyword",code[i])):
        vmcode.append("label "+currentClassName+"."+str(TlabelNum+1))
        return mycode,i,n
    mycode = write(1,code[i],mycode,n,"","",fileno)
    i = i+1
    mycode = write(checkfor("{","symbol",code[i]),code[i],mycode,n,"{","symbol",fileno)
    i = i+1
    mycode = write(1,"<statements>",mycode,n,"","",fileno)
    n = n+1
    temp = []
    temp,i,n = compileStatements(code,i,n,fileno)
    mycode.extend(temp)
    n = n-1
    mycode = write(1,"</statements>",mycode,n,"","",fileno)
    mycode = write(checkfor("}","symbol",code[i]),code[i],mycode,n,"}","symbol",fileno)
    i = i+1
    vmcode.append("label "+currentClassName+"."+str(TlabelNum+1))
    return mycode,i,n

def compileReturnStatement(code,i,n,fileno):
    global vmcode
    mycode = []
    mycode = write(1,code[i],mycode,n,"","",fileno)
    i = i+1
    if(not checkfor(";","symbol",code[i])):
        mycode = write(1,"<expression>",mycode,n,"","",fileno)
        n = n+1
        temp = []
        temp,i,n = compileExpression(code,i,n,fileno)
        mycode.extend(temp)
        n = n-1
        mycode = write(1,"</expression>",mycode,n,"","",fileno)
        vmcode.append("return")
    else:
        vmcode.append("push constant 0")
        vmcode.append("return")
    mycode = write(checkfor(";","symbol",code[i]),code[i],mycode,n,";","symbol",fileno)
    i = i+1
    return mycode,i,n

def compileWhileStatement(code,i,n,fileno):
    global vmcode
    global currentClassName
    global labelnumber
    mycode = []
    TlabelNum = labelnumber
    labelnumber = labelnumber+2
    vmcode.append("label "+currentClassName+"."+str(TlabelNum))
    mycode = write(1,code[i],mycode,n,"","",fileno)
    i = i+1
    mycode = write(checkfor("(","symbol",code[i]),code[i],mycode,n,"(","symbol",fileno)
    i = i+1
    mycode = write(1,"<expression>",mycode,n,"","",fileno)
    temp = []
    n = n+1
    temp,i,n = compileExpression(code,i,n,fileno)
    mycode.extend(temp)
    n = n-1
    mycode = write(1,"</expression>",mycode,n,"","",fileno)
    mycode = write(checkfor(")","symbol",code[i]),code[i],mycode,n,")","symbol",fileno)
    i = i+1
    vmcode.append("not")
    vmcode.append("if-goto "+currentClassName+"."+str(TlabelNum+1))
    mycode = write(checkfor("{","symbol",code[i]),code[i],mycode,n,"{","symbol",fileno)
    i = i+1
    mycode = write(1,"<statements>",mycode,n,"","",fileno)
    n = n+1
    temp = []
    temp,i,n = compileStatements(code,i,n,fileno)
    mycode.extend(temp)
    n = n-1
    mycode = write(1,"</statements>",mycode,n,"","",fileno)
    vmcode.append("goto "+currentClassName+"."+str(TlabelNum))
    vmcode.append("label "+currentClassName+"."+str(TlabelNum+1))
    mycode = write(checkfor("}","symbol",code[i]),code[i],mycode,n,"}","symbol",fileno)
    i = i+1
    return mycode,i,n

def compileDoStatement(code,i,n,fileno):
    global vmcode
    global subroutine_table
    global class_symbol_table
    global nP
    mycode = []
    mycode = write(1,code[i],mycode,n,"","",fileno)
    i = i+1
    mycode = write(checkfor("subroutineName","identifier",code[i]),code[i],mycode,n,"","",fileno)
    id1 = code[i].split()[1]
    i = i+1
    if(checkfor("(","symbol",code[i])):
        vmcode.append("push pointer 0")
        mycode = write(1,code[i],mycode,n,"","",fileno)
        i = i+1
        mycode = write(1,"<expressionList>",mycode,n,"","",fileno)
        n = n+1
        temp = []
        temp,i,n = compileExpressionList(code,i,n,fileno)
        n = n-1
        mycode.extend(temp)
        mycode = write(1,"</expressionList>",mycode,n,"","",fileno)
        mycode = write(checkfor(")","symbol",code[i]),code[i],mycode,n,")","symbol",fileno)
        i = i+1
        vmcode.append("call "+currentClassName+"."+id1+" "+str(nP+1))
        vmcode.append("pop temp 0")
    elif(checkfor(".","symbol",code[i])):
        mycode = write(1,code[i],mycode,n,"","",fileno)
        i = i+1
        mycode = write(checkfor("subroutineName","identifier",code[i]),code[i],mycode,n,"subroutineName","identifier",fileno)
        id2 = code[i].split()[1]
        i = i+1
        a = 0
        for key in subroutine_table:
            if(subroutine_table[key][2]==id1):
                a = 1
                kind = subroutine_table[key][0]
                index = subroutine_table[key][-1]
                type = subroutine_table[key][1]
                vmcode.append("push "+kind+" "+index)
        for key in class_symbol_table:
            if(class_symbol_table[key][2]==id1):
                a = 2
                kind = class_symbol_table[key][0]
                index = class_symbol_table[key][-1]
                type = class_symbol_table[key][1]
                vmcode.append("push "+kind+" "+index)
        mycode = write(checkfor("(","symbol",code[i]),code[i],mycode,n,"(","symbol",fileno)
        i = i+1
        mycode = write(1,"<expressionList>",mycode,n,"","",fileno)
        n = n+1
        temp = []
        temp,i,n = compileExpressionList(code,i,n,fileno)
        n = n-1
        mycode.extend(temp)
        mycode = write(1,"</expressionList>",mycode,n,"","",fileno)
        mycode = write(checkfor(")","symbol",code[i]),code[i],mycode,n,")","symbol",fileno)
        i = i+1
        if(a==0):
            vmcode.append("call "+id1+"."+id2+" "+str(nP))
            vmcode.append("pop temp 0")
        elif((a==1 and kind=="local") or a==2):
            vmcode.append("call "+type+"."+id2+" "+str(nP+1))
            vmcode.append("pop temp 0")
    mycode = write(checkfor(";","symbol",code[i]),code[i],mycode,n,";","symbol",fileno)
    i = i+1
    return mycode,i,n

def compileLetStatement(code,i,n,fileno):
    global vmcode
    mycode = []
    mycode = write(1,code[i],mycode,n,"","",fileno)
    i = i+1
    mycode = write(checkfor("varName","identifier",code[i]),code[i],mycode,n,"varName","identifier",fileno)
    varName = code[i].split()[1]
    a = 0
    for key in class_symbol_table:
        if(class_symbol_table[key][2]==varName):
            a = 1
            kind = class_symbol_table[key][0]
            type = class_symbol_table[key][1]
            index = class_symbol_table[key][-1]
    for key in subroutine_table:
        if(subroutine_table[key][2]==varName):
            a = 1
            kind = subroutine_table[key][0]
            type = subroutine_table[key][1]
            index = subroutine_table[key][-1]
    if(a==0):
        errfiles[fileno].append("Declaration error: "+varName+" undeclared.")
    i = i+1
    if(checkfor("[","symbol",code[i])):
        mycode = write(1,code[i],mycode,n,"","",fileno)
        i = i+1
        mycode = write(1,"<expression>",mycode,n,"","",fileno)
        n = n+1
        temp = []
        temp,i,n = compileExpression(code,i,n,fileno)
        n = n-1
        mycode.extend(temp)
        mycode = write(1,"</expression>",mycode,n,"","",fileno)
        mycode = write(checkfor("]","symbol",code[i]),code[i],mycode,n,"]","symbol",fileno)
        i = i+1
        try:
            vmcode.append("push "+kind+" "+index)
        except UnboundLocalError:
            print("Error occured check error files")
        vmcode.append("add")
        mycode = write(checkfor("=","symbol",code[i]),code[i],mycode,n,"=","symbol",fileno)
        i = i+1
        mycode = write(1,"<expression>",mycode,n,"","",fileno)
        n = n+1
        temp = []
        temp,i,n = compileExpression(code,i,n,fileno)
        n = n-1
        mycode.extend(temp)
        mycode = write(1,"</expression>",mycode,n,"","",fileno)
        vmcode.append("pop temp 0")
        vmcode.append("pop pointer 1")
        vmcode.append("push temp 0")
        vmcode.append("pop that 0")
        mycode = write(checkfor(";","symbol",code[i]),code[i],mycode,n,";","symbol",fileno)
        i = i+1
    else:
        mycode = write(checkfor("=","symbol",code[i]),code[i],mycode,n,"=","symbol",fileno)
        i = i+1
        mycode = write(1,"<expression>",mycode,n,"","",fileno)
        n = n+1
        temp = []
        temp,i,n = compileExpression(code,i,n,fileno)
        n = n-1
        mycode.extend(temp)
        mycode = write(1,"</expression>",mycode,n,"","",fileno)
        try:
            vmcode.append("pop "+kind+" "+index)
        except UnboundLocalError:
            print("Error occured check error files")
        mycode = write(checkfor(";","symbol",code[i]),code[i],mycode,n,";","symbol",fileno)
        i = i+1
    return mycode,i,n

op = ["+","-","*","&amp;","&gt;","&lt;","/","|","="]
oper = {
'+' : 'add',
'-' : 'sub',
'&amp;' : 'and',
'|' : 'or',
'&gt;' : 'gt',
'&lt;' : 'lt',
'=' : 'eq',
'*' : 'call Math.multiply 2',
'/' : 'call Math.divide 2',
}

def compileExpression(code,i,n,fileno):
    global vmcode
    mycode = []
    mycode = write(1,"<term>",mycode,n,"","",fileno)
    temp = []
    n = n+1
    temp,i,n = compileTerm(code,i,n,fileno)
    n = n-1
    mycode.extend(temp)
    mycode = write(1,"</term>",mycode,n,"","",fileno)
    while(code[i].split()[1] in op):
        mycode = write(1,code[i],mycode,n,"","",fileno)
        o = code[i].split()[1]
        i = i+1
        mycode = write(1,"<term>",mycode,n,"","",fileno)
        temp = []
        n = n+1
        temp,i,n = compileTerm(code,i,n,fileno)
        n = n-1
        mycode.extend(temp)
        mycode = write(1,"</term>",mycode,n,"","",fileno)
        vmcode.append(oper[o])
    return mycode,i,n

def compileExpressionList(code,i,n,fileno):
    global vmcode
    global nP
    nP = 0
    mycode = []
    if(checkfor(")","symbol",code[i])):
        return mycode,i,n
    mycode = write(1,"<expression>",mycode,n,"","",fileno)
    n = n+1
    temp = []
    temp,i,n = compileExpression(code,i,n,fileno)
    nP = nP+1
    n = n-1
    mycode.extend(temp)
    mycode = write(1,"</expression>",mycode,n,"","",fileno)
    while(checkfor(",","symbol",code[i])):
        mycode = write(1,code[i],mycode,n,"","",fileno)
        i = i+1
        mycode = write(1,"<expression>",mycode,n,"","",fileno)
        n = n+1
        temp = []
        temp,i,n = compileExpression(code,i,n,fileno)
        nP = nP+1
        n = n-1
        mycode.extend(temp)
        mycode = write(1,"</expression>",mycode,n,"","",fileno)
    return mycode,i,n

KeywordConstant = ["true","false","null","this"]
def compileTerm(code,i,n,fileno):
    global vmcode
    global subroutine_table
    global class_symbol_table
    mycode = []
    if(checkfor("int","integerConstant",code[i])):
        mycode = write(1,code[i],mycode,n,"","",fileno)
        intValue = code[i].split()[1]
        i = i+1
        vmcode.append("push constant "+intValue)
    elif(checkfor("stringConstant","stringConstant",code[i])):
        mycode = write(1,code[i],mycode,n,"","",fileno)
        string = code[i].split(" ",1)[1].split("<")[0][:-1]
        i = i+1
        length = len(string)
        vmcode.append("push constant "+str(length))
        vmcode.append("call String.new 1")
        for j in range(length):
            vmcode.append("push constant "+str(ord(string[j])))
            vmcode.append("call String.appendChar 2")
    elif(code[i].split()[1] in KeywordConstant):
        mycode = write(1,code[i],mycode,n,"","",fileno)
        if(code[i].split()[1]=="true"):
            vmcode.append("push constant 0")
            vmcode.append("not")
        elif(code[i].split()[1]=="false"):
            vmcode.append("push constant 0")
        elif(code[i].split()[1]=="null"):
            vmcode.append("push constant 0")
        elif(code[i].split()[1]=="this"):
            vmcode.append("push pointer 0")
        i = i+1
    elif(checkfor("varName","identifier",code[i])):
        mycode = write(1,code[i],mycode,n,"","",fileno)
        varName = code[i].split()[1]
        i = i+1
        if(checkfor("[","symbol",code[i])):
            mycode = write(1,code[i],mycode,n,"","",fileno)
            i = i+1
            mycode = write(1,"<expression>",mycode,n,"","",fileno)
            n = n+1
            temp = []
            temp,i,n = compileExpression(code,i,n,fileno)
            n = n-1
            mycode.extend(temp)
            mycode = write(1,"</expression>",mycode,n,"","",fileno)
            mycode = write(checkfor("]","symbol",code[i]),code[i],mycode,n,"]","symbol",fileno)
            i = i+1
            a = 0
            for key in subroutine_table:
                if(subroutine_table[key][2]==varName):
                    a = 1
                    kind = subroutine_table[key][0]
                    index = subroutine_table[key][-1]
                    type = subroutine_table[key][1]
            for key in class_symbol_table:
                if(class_symbol_table[key][2]==varName):
                    a = 1
                    kind = class_symbol_table[key][0]
                    type = class_symbol_table[key][1]
                    index = class_symbol_table[key][-1]
            if(a==0):
                errfiles[fileno].append("Declaration error: "+varName+" undeclared.")
            try:
                vmcode.append("push "+kind+" "+index)
            except UnboundLocalError:
                print("Error occured check error files")
            vmcode.append("add")
            vmcode.append("pop pointer 1")
            vmcode.append("push that 0")
        elif(checkfor("(","symbol",code[i])):
            vmcode.append("push pointer 0")
            mycode = write(1,code[i],mycode,n,"","",fileno)
            i = i+1
            mycode = write(1,"<expressionList>",mycode,n,"","",fileno)
            n = n+1
            temp = []
            temp,i,n = compileExpressionList(code,i,n,fileno)
            n = n-1
            mycode.extend(temp)
            mycode = write(1,"</expressionList>",mycode,n,"","",fileno)
            mycode = write(checkfor(")","symbol",code[i]),code[i],mycode,n,")","symbol",fileno)
            i = i+1
            vmcode.append("call "+currentClassName+"."+varName+" "+str(nP+1))
        elif(checkfor(".","symbol",code[i])):
            mycode = write(1,code[i],mycode,n,"","",fileno)
            i = i+1
            mycode = write(checkfor("subroutineName","identifier",code[i]),code[i],mycode,n,"subroutineName","identifier",fileno)
            id2 = code[i].split()[1]
            i = i+1
            a = 0
            for key in subroutine_table:
                if(subroutine_table[key][2]==varName):
                    a = 1
                    kind = subroutine_table[key][0]
                    index = subroutine_table[key][-1]
                    type = subroutine_table[key][1]
                    vmcode.append("push "+kind+" "+index)
            for key in class_symbol_table:
                if(class_symbol_table[key][2]==varName):
                    a = 2
                    kind = class_symbol_table[key][0]
                    index = class_symbol_table[key][-1]
                    type = class_symbol_table[key][1]
                    vmcode.append("push "+kind+" "+index)
            mycode = write(checkfor("(","symbol",code[i]),code[i],mycode,n,"(","symbol",fileno)
            i = i+1
            mycode = write(1,"<expressionList>",mycode,n,"","",fileno)
            n = n+1
            temp = []
            temp,i,n = compileExpressionList(code,i,n,fileno)
            n = n-1
            mycode.extend(temp)
            mycode = write(1,"</expressionList>",mycode,n,"","",fileno)
            mycode = write(checkfor(")","symbol",code[i]),code[i],mycode,n,")","symbol",fileno)
            i = i+1
            if(a==0):
                vmcode.append("call "+varName+"."+id2+" "+str(nP))
            elif((a==1 and kind=="local") or a==2):
                vmcode.append("call "+type+"."+id2+" "+str(nP+1))
        else:
            a = 0
            for key in subroutine_table:
                if(subroutine_table[key][2]==varName):
                    a = 1
                    kind = subroutine_table[key][0]
                    index = subroutine_table[key][-1]
                    type = subroutine_table[key][1]
            for key in class_symbol_table:
                if(class_symbol_table[key][2]==varName):
                    a = 1
                    kind = class_symbol_table[key][0]
                    type = class_symbol_table[key][1]
                    index = class_symbol_table[key][-1]
            if(a==0):
                errfiles[fileno].append("Declaration error: "+varName+" undeclared.")
            try:
                vmcode.append("push "+kind+" "+index)
            except UnboundLocalError:
                print("Error occured check error files")
    elif(checkfor("(","symbol",code[i])):
        mycode = write(1,code[i],mycode,n,"","",fileno)
        i = i+1
        temp = []
        mycode = write(1,"<expression>",mycode,n,"","",fileno)
        n = n+1
        temp,i,n = compileExpression(code,i,n,fileno)
        n = n-1
        mycode.extend(temp)
        mycode = write(1,"</expression>",mycode,n,"","",fileno)
        mycode = write(checkfor(")","symbol",code[i]),code[i],mycode,n,")","symbol",fileno)
        i = i+1
    elif(code[i].split()[1]=="~" or code[i].split()[1]=="-"):
        mycode = write(1,code[i],mycode,n,"","",fileno)
        op = code[i].split()[1]
        i = i+1
        temp = []
        mycode = write(1,"<term>",mycode,n,"","",fileno)
        n = n+1
        temp,i,n = compileTerm(code,i,n,fileno)
        n = n-1
        mycode.extend(temp)
        mycode = write(1,"</term>",mycode,n,"","",fileno)
        if(op == "-"):
            vmcode.append("neg")
        elif(op == "~"):
            vmcode.append("not")
    else:
        print("Error occured check error files")
        errfiles[fileno].append("ERROR: Expecting <term> but "+code[i].split()[1])
    return mycode,i,n

for i in finalcode:
    i[0] = "<tokens> tokenName </tokens>"
    i[-1] = "<tokens> tokenName </tokens>"

finalxml = []
finalvm = []
for j in range(nfiles):
    vmcode = []
    mycode = ["<class>"]
    temp = []
    temp,i,n = compileClass(finalcode[j],1,1,j)
    temp.append("</class>")
    mycode.extend(temp)
    finalxml.append(mycode)
    finalvm.append(vmcode)

def xmlFileCreator(finalxml,filenames,nfiles):
    newfilenames = []
    for i in range(nfiles):
        newfilenames.append(filenames[i].split(".")[0]+".xml")
    for i in range(nfiles):
        with open(newfilenames[i],'w') as f:
            for j in finalxml[i]:
                f.write(j)
                f.write("\n")

xmlFileCreator(finalxml,filenames,nfiles)

def errFileCreator(errfiles,filenames,nfiles):
    newfilenames = []
    for i in range(nfiles):
        newfilenames.append(filenames[i].split(".")[0]+".err")
    for i in range(nfiles):
        with open(newfilenames[i],'w') as f:
            for j in errfiles[i]:
                f.write(j)
                f.write("\n")

for i in range(nfiles):
    errfiles[i] = errfiles[i][1:2]
errFileCreator(errfiles,filenames,nfiles)

def vmFileCreator(finalvm,filenames,nfiles):
    newfilenames = []
    for i in range(nfiles):
        newfilenames.append(filenames[i].split(".")[0]+".vm")
    for i in range(nfiles):
        with open(newfilenames[i],'w') as f:
            for j in finalvm[i]:
                f.write(j)
                f.write("\n")

vmFileCreator(finalvm,filenames,nfiles)
