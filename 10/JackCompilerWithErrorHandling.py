import sys
import re
import os
keyword = ['class','constructor','function','method','field','static','var','int','char','boolean','void','true','false','null','this','let','do','if','else','while','return']
symbol = ['{','}','(',')','[',']','.',',',';','+','-','*','/','&','|','<','>','=','~']
path = sys.argv[1]
nfiles = 0
filenames = []
codes = []
filename = path.split("/")[-1]
for root, dirs, files in os.walk(path):
    for file in files:
        if file.endswith('.jack'):
			code = ""
			filenames.append(file)
			nfiles = nfiles+1
			with open(os.path.join(path,file)) as f:
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
        with open(os.path.join(path,newfilenames[i]),'w') as f:
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
        elif(truth == False and expectedTokenType!=tokenType):
            errfiles[fileno].append("ERROR: Expecting <"+expectedTokenType+"> but "+token)
    return mycode

def compileClass(code,i,n,fileno):
    mycode = []
    mycode = write(checkfor("class","keyword",code[i]),code[i],mycode,n,"class","keyword",fileno)
    i = i+1
    mycode = write(checkfor("className","identifier",code[i]),code[i],mycode,n,"className","identifier",fileno)
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
    mycode = []
    mycode = write(1,code[i],mycode,n,"","",fileno)
    i = i+1
    mycode = write(checkfor("int","keyword",code[i]) or checkfor("char","keyword",code[i]) or checkfor("boolean","keyword",code[i]) or checkfor("className","identifier",code[i]),code[i],mycode,n,"","",fileno)
    i = i+1
    mycode = write(checkfor("varName","identifier",code[i]),code[i],mycode,n,"varName","identifier",fileno)
    i = i+1
    while(checkfor(",","symbol",code[i])):
        mycode = write(1,code[i],mycode,n,"","",fileno)
        i = i+1
        mycode = write(checkfor("varName","identifier",code[i]),code[i],mycode,n,"varName","identifier",fileno)
        i = i+1
    mycode = write(checkfor(";","symbol",code[i]),code[i],mycode,n,";","symbol",fileno)
    i = i+1
    return mycode,i,n

def compileSubroutineDec(code,i,n,fileno):
    mycode = []
    mycode = write(1,code[i],mycode,n,"","",fileno)
    i = i+1
    mycode = write(checkfor("className","identifier",code[i]) or checkfor("void","keyword",code[i]) or checkfor("int","keyword",code[i]) or checkfor("char","keyword",code[i]) or checkfor("boolean","keyword",code[i]),code[i],mycode,n,"","",fileno)
    i = i+1
    mycode = write(checkfor("subroutineName","identifier",code[i]),code[i],mycode,n,"subroutineName","identifier",fileno)
    i = i+1
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
    mycode = []
    mycode = write(1,code[i],mycode,n,"","",fileno)
    i = i+1
    mycode = write(checkfor("className","identifier",code[i]) or checkfor("int","keyword",code[i]) or checkfor("char","keyword",code[i]) or checkfor("boolean","keyword",code[i]),code[i],mycode,n,"","",fileno)
    i = i+1
    mycode = write(checkfor("varName","identifier",code[i]),code[i],mycode,n,"varName","identifier",fileno)
    i = i+1
    while(checkfor(",","symbol",code[i])):
        mycode = write(1,code[i],mycode,n,"","",fileno)
        i = i+1
        mycode = write(checkfor("varName","identifier",code[i]),code[i],mycode,n,"varName","identifier",fileno)
        i = i+1
    mycode = write(checkfor(";","symbol",code[i]),code[i],mycode,n,";","symbol",fileno)
    i = i+1
    return mycode,i,n

def compileParameterList(code,i,n,fileno):
    mycode = []
    if(checkfor(")","symbol",code[i])):
        return mycode,i,n
    mycode = write(checkfor("className","identifier",code[i]) or checkfor("int","keyword",code[i]) or checkfor("char","keyword",code[i]) or checkfor("boolean","keyword",code[i]),code[i],mycode,n,"","",fileno)
    i = i+1
    mycode = write(checkfor("varName","identifier",code[i]),code[i],mycode,n,"varName","identifier",fileno)
    i = i+1
    while(checkfor(",","symbol",code[i])):
        mycode = write(1,code[i],mycode,n,"","",fileno)
        i = i+1
        mycode = write(checkfor("className","identifier",code[i]) or checkfor("int","keyword",code[i]) or checkfor("char","keyword",code[i]) or checkfor("boolean","keyword",code[i]),code[i],mycode,n,"","",fileno)
        i = i+1
        mycode = write(checkfor("varName","identifier",code[i]),code[i],mycode,n,"varName","identifier",fileno)
        i = i+1
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
    mycode = write(1,"<statements>",mycode,n,"","",fileno)
    n = n+1
    temp = []
    temp,i,n = compileStatements(code,i,n,fileno)
    mycode.extend(temp)
    n = n-1
    mycode = write(1,"</statements>",mycode,n,"","",fileno)
    mycode = write(checkfor("}","symbol",code[i]),code[i],mycode,n,"}","symbol",fileno)
    i = i+1
    if(not checkfor("else","keyword",code[i])):
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
    return mycode,i,n

def compileReturnStatement(code,i,n,fileno):
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
    mycode = write(checkfor(";","symbol",code[i]),code[i],mycode,n,";","symbol",fileno)
    i = i+1
    return mycode,i,n

def compileWhileStatement(code,i,n,fileno):
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
    mycode = write(1,"<statements>",mycode,n,"","",fileno)
    n = n+1
    temp = []
    temp,i,n = compileStatements(code,i,n,fileno)
    mycode.extend(temp)
    n = n-1
    mycode = write(1,"</statements>",mycode,n,"","",fileno)
    mycode = write(checkfor("}","symbol",code[i]),code[i],mycode,n,"}","symbol",fileno)
    i = i+1
    return mycode,i,n

def compileDoStatement(code,i,n,fileno):
    mycode = []
    mycode = write(1,code[i],mycode,n,"","",fileno)
    i = i+1
    mycode = write(checkfor("subroutineName","identifier",code[i]),code[i],mycode,n,"","",fileno)
    i = i+1
    if(checkfor("(","symbol",code[i])):
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
    elif(checkfor(".","symbol",code[i])):
        mycode = write(1,code[i],mycode,n,"","",fileno)
        i = i+1
        mycode = write(checkfor("subroutineName","identifier",code[i]),code[i],mycode,n,"subroutineName","identifier",fileno)
        i = i+1
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
    mycode = write(checkfor(";","symbol",code[i]),code[i],mycode,n,";","symbol",fileno)
    i = i+1
    return mycode,i,n

def compileLetStatement(code,i,n,fileno):
    mycode = []
    mycode = write(1,code[i],mycode,n,"","",fileno)
    i = i+1
    mycode = write(checkfor("varName","identifier",code[i]),code[i],mycode,n,"varName","identifier",fileno)
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
        mycode = write(checkfor("=","symbol",code[i]),code[i],mycode,n,"=","symbol",fileno)
        i = i+1
        mycode = write(1,"<expression>",mycode,n,"","",fileno)
        n = n+1
        temp = []
        temp,i,n = compileExpression(code,i,n,fileno)
        n = n-1
        mycode.extend(temp)
        mycode = write(1,"</expression>",mycode,n,"","",fileno)
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
        mycode = write(checkfor(";","symbol",code[i]),code[i],mycode,n,";","symbol",fileno)
        i = i+1
    return mycode,i,n

op = ["+","-","*","&amp;","&gt;","&lt;","/","|","="]

def compileExpression(code,i,n,fileno):
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
        i = i+1
        mycode = write(1,"<term>",mycode,n,"","",fileno)
        temp = []
        n = n+1
        temp,i,n = compileTerm(code,i,n,fileno)
        n = n-1
        mycode.extend(temp)
        mycode = write(1,"</term>",mycode,n,"","",fileno)
    return mycode,i,n

def compileExpressionList(code,i,n,fileno):
    mycode = []
    if(checkfor(")","symbol",code[i])):
        return mycode,i,n
    mycode = write(1,"<expression>",mycode,n,"","",fileno)
    n = n+1
    temp = []
    temp,i,n = compileExpression(code,i,n,fileno)
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
        n = n-1
        mycode.extend(temp)
        mycode = write(1,"</expression>",mycode,n,"","",fileno)
    return mycode,i,n

KeywordConstant = ["true","false","null","this"]
def compileTerm(code,i,n,fileno):
    mycode = []
    if(checkfor("strconst","stringConstant",code[i]) or checkfor("int","integerConstant",code[i])):
        mycode = write(1,code[i],mycode,n,"","",fileno)
        i = i+1
    elif(code[i].split()[1] in KeywordConstant):
        mycode = write(1,code[i],mycode,n,"","",fileno)
        i = i+1
    elif(checkfor("varName","identifier",code[i])):
        mycode = write(1,code[i],mycode,n,"","",fileno)
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
        elif(checkfor("(","symbol",code[i])):
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
        elif(checkfor(".","symbol",code[i])):
            mycode = write(1,code[i],mycode,n,"","",fileno)
            i = i+1
            mycode = write(checkfor("subroutineName","identifier",code[i]),code[i],mycode,n,"subroutineName","identifier",fileno)
            i = i+1
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
        i = i+1
        temp = []
        mycode = write(1,"<term>",mycode,n,"","",fileno)
        n = n+1
        temp,i,n = compileTerm(code,i,n,fileno)
        n = n-1
        mycode.extend(temp)
        mycode = write(1,"</term>",mycode,n,"","",fileno)
    return mycode,i,n

for i in finalcode:
    i[0] = "<tokens> tokenName </tokens>"
    i[-1] = "<tokens> tokenName </tokens>"

finalxml = []
for i in range(nfiles):
    mycode = ["<class>"]
    temp = []
    temp,i,n = compileClass(finalcode[i],1,1,i)
    temp.append("</class>")
    mycode.extend(temp)
    finalxml.append(mycode)

def xmlFileCreator(finalxml,filenames,nfiles):
    newfilenames = []
    for i in range(nfiles):
        newfilenames.append(filenames[i].split(".")[0]+".xml")
    for i in range(nfiles):
        with open(os.path.join(path,newfilenames[i]),'w') as f:
            for j in finalxml[i]:
                f.write(j)
                f.write("\n")

xmlFileCreator(finalxml,filenames,nfiles)
for i in range(nfiles):
    errfiles[i] = errfiles[i][1:2]

def errFileCreator(errfiles,filenames,nfiles):
    newfilenames = []
    for i in range(nfiles):
        newfilenames.append(filenames[i].split(".")[0]+".err")
    for i in range(nfiles):
        with open(os.path.join(path,newfilenames[i]),'w') as f:
            for j in errfiles[i]:
                f.write(j)
                f.write("\n")
errFileCreator(errfiles,filenames,nfiles)
