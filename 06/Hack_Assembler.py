#Assembler for the Hack Computer and Jack programming language
#Author : Shreesha G Bhat
#         CS18B103
#         CSE Department
#         Indian Institute of Technology, Madras
#Part of CS2300 course based on the Nand2Tetris course
import sys
filename = sys.argv[1]
symbol_table = {}
for i in range(16):
    symbol_table["R"+str(i)] = str(i)
symbol_table["SP"] = "0"
symbol_table["THIS"] = "3"
symbol_table["THAT"] = "4"
symbol_table["LCL"] = "1"
symbol_table["ARG"] = "2"
symbol_table["SCREEN"] = "16384"
symbol_table["KBD"] = "24576"
comp = {
    "0": "0101010",
    "1": "0111111",
    "-1": "0111010",
    "D": "0001100",
    "A": "0110000",
    "!D": "0001101",
    "!A": "0110001",
    "-D": "0001111",
    "-A": "0110011",
    "D+1": "0011111",
    "1+D": "0011111",
    "A+1": "0110111",
    "1+A": "0110111",
    "D-1": "0001110",
    "-1+D": "0001110",
    "A-1": "0110010",
    "-1+A": "0110010",
    "A+D": "0000010",
    "D+A": "0000010",
    "D-A": "0010011",
    "-A+D": "0010011",
    "A-D": "0000111",
    "-D+A": "0000111",
    "D&A": "0000000",
    "A&D": "0000000",
    "D|A": "0010101",
    "A|D": "0010101",
    "M": "1110000",
    "!M": "1110001",
    "-M": "1110011",
    "M+1": "1110111",
    "1+M": "1110111",
    "M-1": "1110010",
    "-1+M": "1110010",
    "D+M": "1000010",
    "M+D": "1000010",
    "D-M": "1010011",
    "-M+D": "1010011",
    "M-D": "1000111",
    "-D+M": "1000111",
    "D&M": "1000000",
    "M&D": "1000000",
    "D|M": "1010101",
    "M|D": "1010101"
}
dest = {
    "null": "000",
    "M": "001",
    "D": "010",
    "A": "100",
    "MD": "011",
    "DM": "011",
    "AM": "101",
    "MA": "101",
    "AD": "110",
    "DA": "110",
    "AMD": "111",
    "ADM": "111",
    "MAD": "111",
    "MDA": "111",
    "DMA": "111",
    "DAM": "111"
}
jump = {
    "null": "000",
    "JGT": "001",
    "JEQ": "010",
    "JGE": "011",
    "JLT": "100",
    "JNE": "101",
    "JLE": "110",
    "JMP": "111"
}
def inititalizer(filename):
    with open(filename,'r') as f:
        code = f.readlines()
        return code
def cleaner(code):
    code = [x.replace(' ','') for x in code]
    code = [x.split('/')[0] for x in code]
    code = [x.replace('\r','') for x in code]
    code = [x.replace('\n','') for x in code]
    code = [x.replace('\t','') for x in code]
    while '' in code: code.remove('')
    return code
def file_creator(code,filename):
    with open(filename,'w') as f:
        for x in code:
            f.write(x)
            f.write("\n")
def A_instruction(string):
    if(string[0]=='@'):
        return True
def L_instruction(string):
    if(string=="("):
        return True
def const_A(string):
    if(A_instruction(string)==1):
        try:
            int(string[1:])
            return True
        except ValueError:
            return False
def build_symbol_table(code):
    counter = -1
    for x in code:
        if(x[0]=='('):
            a = x.replace("(","")
            a = a.replace(")","")
            symbol_table[a] = str(counter+1)
        else:
            counter = counter+1
    i=0
    for x in code:
        if(A_instruction(x)==True and const_A(x) == False and x[1:] not in symbol_table):
            symbol_table[x[1:]] = str(16+i)
            i = i+1
def remove_symbols(code):
    newcode = []
    for x in code:
        if(x[0]!='('):
            newcode.append(x)
    return newcode
def length(code):
    return len(code)
def Pass1(code):
    len = length(code)
    for i in range(len):
        if(A_instruction(code[i])==True and const_A(code[i])==False):
            code[i] = '@' + symbol_table[code[i][1:]]
    return(code)
def C_instruction_manipulation(string):
    if(('=' not in string) and (';' not in string)):
        return -1
    if('=' not in string):
        return "null="+string
    if(';' not in string):
        return string + ";null"
def C_instruction_cleaning(code):
    len = length(code)
    for i in range(len):
        if(not A_instruction(code[i])==True):
            code[i] = C_instruction_manipulation(code[i])
    return code
def split_C_instruction(string):
    a = string.split("=")[0]
    b = string.split("=")[1].split(";")[0]
    c = string.split("=")[1].split(";")[1]
    return comp[b]+dest[a]+jump[c]
def Pass2(code):
    newcode = []
    len = length(code)
    for i in range(len):
        if(A_instruction(code[i])==True):
            newcode.append(str('{0:016b}'.format(int(code[i][1:]))))
        if(not A_instruction(code[i])==True):
            newcode.append(str("111"+split_C_instruction(code[i])))
    return newcode
originalcode = inititalizer(filename)
cleanedcode = cleaner(originalcode)
build_symbol_table(cleanedcode)
cleanedcode = remove_symbols(cleanedcode)
finalpass1 = Pass1(cleanedcode)
file_creator(finalpass1,filename.split('.')[0]+".ir")
code = C_instruction_cleaning(finalpass1)
final = Pass2(code)
file_creator(final,filename.split('.')[0]+".hack")
