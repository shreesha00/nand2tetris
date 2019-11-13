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
    temp = []
    temp,i,n = compileTerm(code,i,n,fileno)
    mycode.extend(temp)
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

for code in finalxml:
    for i in range(len(code)):
        code[i] = "<"+code[i].split("<",1)[1]
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
def CompileClass(finalxml,i,fileno):
    global vmcode
    global static_count
    global field_count
    global total_global_count
    global labelnumber
    global class_symbol_table
    global currentClassName
    static_count = 0
    field_count = 0
    total_global_count = 0
    labelnumber = 0
    class_symbol_table.clear()
    #class
    i = i+1
    #className
    currentClassName = finalxml[i].split()[1]
    i = i+1
    #{
    i = i+1
    while(finalxml[i]=="<classVarDec>"):
        #<classVarDec>
        i = i+1
        i = CompileClassVarDec(finalxml,i,fileno)
        #</classVarDec>
        i = i+1
    while(finalxml[i]=="<subroutineDec>"):
        #<subroutineDec>
        i = i+1
        i = CompileSubroutineDec(finalxml,i,fileno)
        #</subroutineDec>
        i = i+1
    #}
    i = i+1
    return i

def CompileClassVarDec(finalxml,i,fileno):
    global vmcode
    global static_count
    global field_count
    global total_global_count
    global class_symbol_table
    stat_field = finalxml[i].split()[1]
    i = i+1
    type = finalxml[i].split()[1]
    i = i+1
    varName = finalxml[i].split()[1]
    i = i+1
    if(stat_field=="static"):
        count = static_count
        static_count = static_count+1
    else:
        count = field_count
        field_count = field_count+1
    class_symbol_table[total_global_count] = [stat_field,type,varName,str(count)]
    total_global_count = total_global_count+1
    while(finalxml[i].split()[1]==","):
        #,
        i = i+1
        varName = finalxml[i].split()[1]
        i = i+1
        if(stat_field=="static"):
            count = static_count
            static_count = static_count+1
        else:
            count = field_count
            field_count = field_count+1
        class_symbol_table[total_global_count] = [stat_field,type,varName,str(count)]
        total_global_count = total_global_count+1
    #;
    i = i+1
    return i

def CompileSubroutineDec(finalxml,i,fileno):
    global vmcode
    global subroutine_table
    global local_count
    global argument_count
    global total_sub_count
    global currentSubroutineName
    global currentSubroutinetype
    con_func_met = finalxml[i].split()[1]
    i = i+1
    void_type = finalxml[i].split()[1]
    i = i+1
    subroutineName = finalxml[i].split()[1]
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
    #(
    i = i+1
    #<parameterList>
    i = i+1
    i = CompileParameterList(finalxml,i,fileno)
    #</parameterList>
    i = i+1
    #)
    i = i+1
    #<subroutineBody>
    i = i+1
    i = CompileSubroutineBody(finalxml,i,fileno)
    #</subroutineBody>
    i = i+1
    return i

def CompileParameterList(finalxml,i,fileno):
    global vmcode
    global argument_count
    global total_sub_count
    global subroutine_table
    if(finalxml[i]=="</parameterList>"):
        return i
    type = finalxml[i].split()[1]
    i = i+1
    varName = finalxml[i].split()[1]
    i = i+1
    subroutine_table[total_sub_count] = ["argument",type,varName,str(argument_count)]
    argument_count = argument_count+1
    total_sub_count = total_sub_count+1
    while("," in finalxml[i]):
        #,
        i = i+1
        type = finalxml[i].split()[1]
        i = i+1
        varName = finalxml[i].split()[1]
        i = i+1
        subroutine_table[total_sub_count] = ["argument",type,varName,str(argument_count)]
        argument_count = argument_count+1
        total_sub_count = total_sub_count+1
    return i

def CompileSubroutineBody(finalxml,i,fileno):
    global vmcode
    global currentClassName
    global currentSubroutineName
    global local_count
    global field_count
    #{
    i = i+1
    while(finalxml[i]=="<varDec>"):
        #<varDec>
        i = i+1
        i = CompileVarDec(finalxml,i,fileno)
        #</varDec>
        i = i+1
    vmcode.append("function "+currentClassName+"."+currentSubroutineName+" "+str(local_count))
    if(currentSubroutinetype=="constructor"):
        vmcode.append("push constant "+str(field_count))
        vmcode.append("call Memory.alloc 1")
        vmcode.append("pop pointer 0")
    elif(currentSubroutinetype=="method"):
        vmcode.append("push argument 0")
        vmcode.append("pop pointer 0")
    #<statements>
    i = i+1
    i = CompileStatements(finalxml,i,fileno)
    #</statements>
    i = i+1
    #}
    i = i+1
    return i

def CompileVarDec(finalxml,i,fileno):
    global vmcode
    global local_count
    global total_sub_count
    global subroutine_table
    #var
    i = i+1
    type = finalxml[i].split()[1]
    i = i+1
    varName = finalxml[i].split()[1]
    i = i+1
    subroutine_table[total_sub_count] = ["local",type,varName,str(local_count)]
    local_count = local_count+1
    total_sub_count = total_sub_count+1
    while("," in finalxml[i]):
        #,
        i = i+1
        varName = finalxml[i].split()[1]
        subroutine_table[total_sub_count] = ["local",type,varName,str(local_count)]
        local_count = local_count+1
        total_sub_count = total_sub_count+1
        i = i+1
    #;
    i = i+1
    return i

statementlist = ["<ifStatement>","<whileStatement>","<doStatement>","<letStatement>","<returnStatement>"]
def CompileStatements(finalxml,i,fileno):
    global vmcode
    while(finalxml[i] in statementlist):
        if(finalxml[i]=="<letStatement>"):
            #<letStatement>
            i = i+1
            i = CompileLetStatement(finalxml,i,fileno)
            #</letStatment>
            i = i+1
        elif(finalxml[i]=="<whileStatement>"):
            #<whileStatement>
            i = i+1
            i = CompileWhileStatement(finalxml,i,fileno)
            #</whileStatement>
            i = i+1
        elif(finalxml[i]=="<doStatement>"):
            #<doStatement>
            i = i+1
            i = CompileDoStatement(finalxml,i,fileno)
            #</doStatement>
            i = i+1
        elif(finalxml[i]=="<ifStatement>"):
            #<ifStatement>
            i = i+1
            i = CompileIfStatement(finalxml,i,fileno)
            #</ifStatement>
            i = i+1
        elif(finalxml[i]=="<returnStatement>"):
            #<returnStatement>
            i = i+1
            i = CompileReturnStatement(finalxml,i,fileno)
            #</returnStatement>
            i = i+1
    return i

def CompileIfStatement(finalxml,i,fileno):
    global vmcode
    global currentClassName
    TlabelNum = labelnumber
    labelnumber = labelnumber+2
    #if
    i = i+1
    #(
    i = i+1
    #<expression>
    i = i+1
    i = CompileExpression(finalxml,i,fileno)
    #</expression>
    i = i+1
    #)
    i = i+1
    #{
    i = i+1
    vmcode.append("not")
    vmcode.append("if-goto "+currentClassName+"."+str(TlabelNum))
    #<statements>
    i = i+1
    i = CompileStatements(finalxml,i,fileno)
    #</statements>
    i = i+1
    #}
    i = i+1
    vmcode.append("goto "+currentClassName+"."+str(TlabelNum+1))
    vmcode.append("label "+currentClassName+"."+str(TlabelNum))
    if("else" in finalxml[i]):
        #else
        i = i+1
        #{
        i = i+1
        #<statements>
        i = i+1
        i = CompileStatements(finalxml,i,fileno)
        #</statements>
        i = i+1
        #}
        i = i+1
        vmcode.append("label "+currentClassName+"."+str(TlabelNum+1))
    return i

def CompileWhileStatement(finalxml,i,fileno):
    global vmcode
    global currentClassName
    global labelnumber
    #while
    i = i+1
    #{
    i = i+1
    #<expression>
    i = i+1
    TlabelNum = labelnumber
    labelnumber = labelnumber+2
    vmcode.append("label "+currentClassName+"."+str(TlabelNum))
    i = CompileExpression(finalxml,i,fileno)
    #</expression>
    i = i+1
    #}
    i = i+1
    vmcode.append("not")
    vmcode.append("if-goto "+currentClassName+"."+str(TlabelNum+1))
    #{
    i = i+1
    #<statements>
    i = i+1
    i = CompileStatements(finalxml,i,fileno)
    #</statements>
    i = i+1
    #}
    i = i+1
    vmcode.append("goto "+currentClassName+"."+str(TlabelNum))
    vmcode.append("label "+currentClassName+"."+str(TlabelNum+1))
    return i

def CompileDoStatement(finalxml,i,fileno):
    global vmcode
    global subroutine_table
    global class_symbol_table
    #do
    i = i+1
    id1 = finalxml[i].split()[1]
    i = i+1
    if(finalxml[i].split()[1]=="."):
        #.
        i = i+1
        id2 = finalxml[i].split()[1]
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
            if(class_symbol_table[key][2]==id2):
                a = 2
                kind = class_symbol_table[key][0]
                index = class_symbol_table[key][-1]
                type = class_symbol_table[key][1]
                vmcode.append("push "+kind+" "+index)
        #(
        i = i+1
        #<expressionList>
        i = i+1
        i,nP = CompileExpressionList(finalxml,i,fileno)
        #</expressionList>
        i = i+1
        #)
        i = i+1
        #;
        i = i+1
        if(a==0):
            vmcode.append("call "+id1+"."+id2+" "+str(nP))
            vmcode.append("pop temp 0")
        elif((a==1 and kind=="local") or a==2):
            vmcode.append("call "+type+"."+id2+" "+str(nP+1))
            vmcode.append("pop temp 0")
    else:
        vmcode.append("push pointer 0")
        #(
        i = i+1
        #<expressionList>
        i = i+1
        i,nP = CompileExpressionList(finalxml,i,fileno)
        #</expressionList>
        i = i+1
        #)
        i = i+1
        #;
        i = i+1
        vmcode.append("call "+currentClassName+"."+id1+" "+str(nP+1))
        vmcode.append("pop temp 0")
    return i

def CompileExpressionList(finalxml,i,fileno):
    global vmcode
    nP = 0
    if(finalxml[i]!="<expression>"):
        return i,nP
    #<expression>
    i = i+1
    i = CompileExpression(finalxml,i,fileno)
    nP = nP+1
    #</expression>
    i = i+1
    while("," in finalxml[i]):
        #,
        i = i+1
        #<expression>
        i = i+1
        i = CompileExpression(finalxml,i,fileno)
        nP = nP+1
        #</expression>
        i = i+1
    return i,nP

oper = {
'+' : 'add',
'-' : 'sub',
'&amp;' : 'and',
'|' : 'or',
'&gt;' : '>',
'&lt;' : '<',
'=' : 'eq',
'*' : 'call Math.multiply 2',
'/' : 'call Math.divide 2',
}

def CompileExpression(finalxml,i,fileno):
    global vmcode
    if(finalxml[i]!="<term>"):
        return i
    #<term>
    i = i+1
    i = CompileTerm(finalxml,i,fileno)
    #</term>
    i = i+1
    while(finalxml[i] in op):
        #op
        o = finalxml[i].split()[1]
        i = i+1
        #<term>
        i = i+1
        i = CompileTerm(finalxml,i,fileno)
        #</term>
        i = i+1
        vmcode.append(oper[o])
    return i

def CompileTerm(finalxml,i,fileno):
    global vmcode
    global subroutine_table
    global class_symbol_table
    if('-' in finalxml[i] or '~' in finalxml[i]):
        op = finalxml[i].split()[1]
        i = i+1
        #<term>
        i = i+1
        i = CompileTerm(finalxml,i,fileno)
        #</term>
        i = i+1
        if(op == "-"):
            vmcode.append("neg")
        elif(op == "~"):
            vmcode.append("not")
        return i
    elif('(' in finalxml[i] and finalxml[i+1]=='<expression>'):
        #(
        i = i+1
        #<expression>
        i = i+1
        i = CompileExpression(finalxml,i,fileno)
        #</expression>
        i = i+1
        #)
        i = i+1
        print(finalxml[i])
        return i
    elif("<integerConstant>" in finalxml[i]):
        intvalue = finalxml[i].split()[1]
        i = i+1
        vmcode.append("push constant "+intvalue)
        return i
    elif("this" in finalxml[i] or "null" in finalxml[i] or "true" in finalxml[i] or "false" in finalxml[i]):
        if(finalxml[i].split()[1]=="true"):
            #true
            i = i+1
            vmcode.append("push constant 0")
            vmcode.append("not")
        elif(finalxml[i].split()[1]=="false"):
            #false
            i = i+1
            vmcode.append("push constant 0")
        elif(finalxml[i].split()[1]=="null"):
            #null
            i = i+1
            vmcode.append("push constant 0")
        elif(finalxml[i].split()[1]=="this"):
            #this
            i = i+1
            vmcode.append("push pointer 0")
        return i
    elif("<identifier>" in finalxml[i] and not ("(" in finalxml[i+1] or "[" in finalxml[i+1] or "." in finalxml[i+1])):
        a = 0
        varName = finalxml[i].split()[1]
        i = i+1
        for key in subroutine_table:
            if(subroutine_table[key][2]==varName):
                a = 1
                kind = subroutine_table[key][0]
                index = subroutine_table[key][-1]
                type = subroutine_table[key][1]
                vmcode.append("push "+kind+" "+index)
        for key in class_symbol_table:
            if(class_symbol_table[key][2]==varName):
                a = 1
                kind = class_symbol_table[key][0]
                type = class_symbol_table[key][1]
                index = class_symbol_table[key][-1]
                vmcode.append("push "+kind+" "+index)
        #if(a==0) #Error handling
        return i
    elif("<identifier>" in finalxml[i] and "[" in finalxml[i+1]):
        varName = finalxml[i].split()[1]
        i = i+1
        #[
        i = i+1
        #<expression>
        i = i+1
        i = CompileExpression(finalxml,i,fileno)
        #</expression>
        i = i+1
        #]
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
                a = 1
                kind = class_symbol_table[key][0]
                type = class_symbol_table[key][1]
                index = class_symbol_table[key][-1]
                vmcode.append("push "+kind+" "+index)
        #if(a==0) #Error handling
        vmcode.append("add")
        vmcode.append("pop pointer 1")
        vmcode.append("push that 0")
        return i
    elif(finalxml[i].split()[0]=="<stringConstant>"):
        string = finalxml[i].split(" ",1)[1].split("<")[0][:-1]
        i = i+1
        length = len(string)
        vmcode.append("push constant "+str(length))
        vmcode.append("call String.new 1")
        for j in range(length):
            vmcode.append("push constant "+str(ord(string[j])))
            vmcode.append("call String.appendChar 2")
        return i
    elif(finalxml[i].split()[0]=="<identifier>" and ("(" in finalxml[i+1] or "." in finalxml[i+1])):
        id1 = finalxml[i].split()[1]
        i = i+1
        if("." in finalxml[i]):
            #.
            i = i+1
            id2 = finalxml[i].split()[1]
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
                if(class_symbol_table[key][2]==id2):
                    a = 2
                    kind = class_symbol_table[key][0]
                    index = class_symbol_table[key][-1]
                    type = class_symbol_table[key][1]
                    vmcode.append("push "+kind+" "+index)
            #(
            i = i+1
            #<expressionList>
            i = i+1
            i,nP = CompileExpressionList(finalxml,i,fileno)
            #</expressionList>
            i = i+1
            #)
            i = i+1
            if(a==0):
                vmcode.append("call "+id1+"."+id2+" "+str(nP))
            elif((a==1 and kind=="local") or a==2):
                vmcode.append("call "+type+"."+id2+" "+str(nP+1))
        elif(finalxml[i].split()[1]=="("):
            vmcode.append("push pointer 0")
            #(
            i = i+1
            #<expressionList>
            i = i+1
            i,nP = CompileExpressionList(finalxml,i,fileno)
            #</expressionList>
            i = i+1
            #)
            i = i+1
            vmcode.append("call "+currentClassName+"."+id1+" "+str(nP+1))
        return i

def CompileLetStatement(finalxml,i,fileno):
    global vmcode
    #<let>
    i = i+1
    varName = finalxml[i].split()[1]
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
    #if(a==0) #Error handling
    i = i+1
    if("[" not in finalxml[i]):
        #=
        i = i+1
        #<expression>
        i = i+1
        i = CompileExpression(finalxml,i,fileno)
        #</expression>
        i = i+1
        a = 0
        vmcode.append("pop "+kind+" "+index)
        #;
        i = i+1
    elif("[" in finalxml[i]):
        #[
        i = i+1
        #<expression>
        i = i+1
        i = CompileExpression(finalxml,i,fileno)
        #</expression>
        i = i+1
        #]
        i = i+1
        vmcode.append("push "+kind+" "+index)
        vmcode.append("add")
        #=
        i = i+1
        #<expression>
        i = i+1
        i = CompileExpression(finalxml,i,fileno)
        #</expression>
        i = i+1
        vmcode.append("pop temp 0")
        vmcode.append("pop pointer 1")
        vmcode.append("push temp 0")
        vmcode.append("pop that 0")
        #;
        i = i+1
    return i

def CompileReturn(finalxml,i,fileno):
    global vmcode
    #return
    i = i+1
    if(finalxml[i]=="<expression>"):
        #<expression>
        i = i+1
        i = CompileExpression(finalxml,i,fileno)
        #</expression>
        i = i+1
        vmcode.append("return")
    else:
        vmcode.append("push constant 0")
        vmcode.append("return")
    return i

vmcode = []
for fileno in range(nfiles):
    vmcode = []
    i = 0
    #<class>
    i = i+1
    i = CompileClass(finalxml[fileno],i,fileno)
    for j in vmcode:
        print(j)
