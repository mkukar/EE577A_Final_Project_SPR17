# main.py
# EE577A - Spring 2017
# Final Project



# #
# GLOBAL VARIABLES
# #

# filename variables
configFileName = "config.txt"
codeFileName = "code.txt"
vecFileName = "vec.txt"
goldenResultsFileName = "golden_results.txt"


# vector header info
radix = [1, 4, 1, 4, 1]
io = ['i', 'i', 'i', 'i', 'i']
vname = ['A<4>', 'A<[3:0]>', 'B<4>', 'B<[3:0]>', 'CLK']
slope = 0.01
vih = 1.8
tunit = "ns"
clockPeriod = 1 # given in tunit, default is this

# op codes map to their instruction
instrToOpCode = {
	'NOP': 0,
	'STOREI': 1,
	'STORE': 2,
	'LOADI': 3,
	'LOAD': 4,
	'AND': 5,
	'ANDI': 6,
	'OR': 7,
	'ORI': 8,
	'ADD': 9,
	'ADDI': 10,
	'MUL': 11,
	'MULI': 12,
	'MIN': 13,
	'MINI': 14,
	'SFL': 15,
	'SFR': 16
}


# decoded instruction vector
# holds the instruction in the form [OPCODE(int), X(int), Y(int), Z(int)]
decodedInstr = [
	[0,0,0,0] # starts filled with a NO-OP to initialize everything
]


# #
# GLOBAL FUNCTIONS
# #



def parseConfigFile():
	print("IN PROGRESS - TO BE ADDED")


def compileCode(fileNameIn):
	global decodedInstr
	# ALGORITHM DESCRIPTION
	# reads in the compiled code line by line
	# for each line, looks up opcode and then generates correct line
	codeFile = open(fileNameIn, 'r')
	for line in codeFile:
		print("PARSING INSTRUCTION \"" + str(line.strip()) + "\"")
		# default state for everything is NO OP
		opcode = 0
		xValInt = 0
		yValInt = 0
		zValInt = 0

		wordsInLine = line.strip().split() # splits each line into a list of words seperated by spaces
		# now finds the op code equivalent based on the first word
		if wordsInLine[0] in instrToOpCode:
			opcode = instrToOpCode[wordsInLine[0]]
			# now handles each special case for the op codes
			if opcode == 0: # NOP
				print("NOP DETECTED")
				print("FILLING STATES WITH 0")
				# does nothing since everything defaults to 0
			elif opcode == 1: # STOREI
				# STOREI {bl} xxH #xxxx {#xxxx}
				print("STOREI IN PROGRESS")
			elif opcode == 2: #STORE
				# STORE xxH $R
				print("STORE DETECTED")
				# checks to make sure storage loc is valid (e.g. xxH is hex or XXXXXb is binary and is between 0 and 31)

				# checks to make sure register number is valid (0 to 7)


		# finally writes the op code states out
		print("OUTPUT ARRAY IS: " + str([opcode, xValInt, yValInt, zValInt]))
		decodedInstr.append([opcode, xValInt, yValInt, zValInt])


	codeFile.close()

def generateVectorFile(fileNameIn):
	print("IN PROGRESS")

def generateGoldenResults(fileNameIn):
	print("IN PROGRESS")

# checks if input is valid. If yes, returns its INT value. If no, returns - (out of range of our 16 bit numbers)
def checkIfValidAndReturn(inputArg):



# #
# HELPER FUNCTIONS
# #

# #
# MAIN
# #

def main():
	print("EE577A Final Project")
	print("Front-End Python Code (IF & ID)")
	print("Compiling source code " + str(codeFileName) +  " into vector file format . . . ")
	compileCode('code.txt')
	print("Done.")
	print("Writing vector file to " + str(vecFileName) + " . . . ")
	generateVectorFile(vecFileName)
	print("Done.")
	print("Generating " + str(goldenResultsFileName) + " . . . ")
	generateGoldenResults(goldenResultsFileName)
	print("Done.")
	print("To run code, use " + str(vecFileName) + " in cadence.")
	print("To verify code, save cadence output file named 'out.csv' to this directory and run 'verify.py'.")


if __name__ == "__main__":
	main()