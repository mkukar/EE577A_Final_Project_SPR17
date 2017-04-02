# main.py
# EE577A - Spring 2017
# Final Project



# #
# GLOBAL VARIABLES
# #

# DEBUG VARIABLES
debugModeOn = True # prints out a lot of extra info for debugging. Turn off for cleaner view

# filename variables
configFileName = "config.txt"
codeFileName = "code.txt"
vecFileName = "vec.txt"
goldenResultsFileName = "golden_results.txt"

# vector header info
radix = [1]
io = ['i']
vname = ['CLK', 'OPCODE<4>', 'OPCODE<[3:0]>', 'X<4>', 'X<[3:0]>', 'Y<4>', 'Y<[3:0]>', 'Z<[15:12]>', 'Z<[11:8]>', 'Z<[7:4]>', 'Z<[3:0]>']
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
	# after reading in file, then checks for data dependencies. Corrects them with NO-OPS or rescheduling instructions
	# - current plan is NOPs, then we'll deal with rescheduling later for optimized design
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
			if opcode == instrToOpCode['NOP']: # NOP
				print("NOP DETECTED")
				# does nothing since everything defaults to 0

			elif opcode == instrToOpCode['STOREI']: # STOREI
				# STOREI {bl} xxH #xxxx {#xxxx}
				print("STOREI IN PROGRESS")
				# generates multiple consecutive instructions


				# needs to check if this is a burst instruction first (length > 3)
				if len(wordsInLine) == 7: # BL == 4
					# must be BL == 4
					if int(wordsInLine[1]) == 4:
						zValInt = 0 # not needed for this
						# STOREI 1 xxH #xxxx #xxxx (four instructions, must start at #...00B)
						print("BL == 4 IP")
						# first checks addr
						xValInt = checkIfAddrAndReturn(wordsInLine[2])
						if xValInt == -1:
							opcode = handleBadInputArg(wordsInLine[2])
						# now checks the four values and generates four new instructions
						yValInt = checkIfAddrAndReturn(wordsInLine[3])
						if yValInt == -1:
							opcode = handleBadInputArg(wordsInLine[3])
						elif int(wordsInLine[3][-2]) != 0 or int(wordsInLine[3][-3]) != 0: # must start at 00
							opcode = instrToOpCode['NOP']
							decodedInstr.append([opcode, 0, 0, 0]) # puts in a blank instruction
							print("Error001: Command " + str(line.strip()) + " is not aligned properly.")
						else:
							decodedInstr.append([opcode, xValInt, yValInt, zValInt])
							# now continues to next instruction
							yValInt = checkIfAddrAndReturn(wordsInLine[4])
							if yValInt == -1:
								opcode = checkIfNumAndReturn(wordsInLine[4])
							elif int(wordsInLine[4][-2]) != 0 or int(wordsInLine[4][-3]) != 1:
								opcode = instrToOpCode['NOP']
								decodedInstr.append([opcode, 0, 0, 0]) # puts in a blank instruction
								print("Error001: Command " + str(line.strip()) + " is not aligned properly.")
							else:
								decodedInstr.append([opcode, xValInt, yValInt, zValInt])
								# now to the third instruction
								yValInt = checkIfAddrAndReturn((wordsInLine[5]))
								if yValInt == -1:
									opcode = checkIfAddrAndReturn(wordsInLine[5])
								elif int(wordsInLine[5][-2]) != 1 or int(wordsInLine[5][-3]) != 0:
									opcode = instrToOpCode['NOP']
									decodedInstr.append([opcode, 0, 0, 0])
									print("Error001: Command " + str(line.strip()) + " is not aligned properly.")
								else:
									decodedInstr.append([opcode, xValInt, yValInt, zValInt])
									# final instruction
									yValInt = checkIfAddrAndReturn(wordsInLine[6])
									if yValInt == -1:
										opcode = checkIfAddrAndReturn(wordsInLine[6])
									elif int(wordsInLine[5][-2]) != 1 or int(wordsInLine[5][-3]) != 1:
										opcode = instrToOpCode['NOP']
										print("Error001: Command " + str(line.strip()) + " is not aligned properly.")

					else:
						opcode = instrToOpCode['NOP']
						print("Error000: Command " + str(line.strip()) + " has invalid burst length.")

				elif len(wordsInLine) == 5: # BL == 2
					# STOREI 1 xxH #xxxx #xxxx (two instructions, must start at #...0B)
					if int(wordsInLine[1]) == 2:
						zValInt = 0 # not needed for this
						# first checks addr
						xValInt = checkIfAddrAndReturn(wordsInLine[2])
						if xValInt == -1:
							opcode = handleBadInputArg(wordsInLine[2])
						# now checks the two values and generates two new instructions
						yValInt = checkIfNumAndReturn(wordsInLine[3])
						if yValInt == -1:
							opcode = handleBadInputArg(wordsInLine[3])
						elif int(wordsInLine[3][-2]) != 0:
							opcode = instrToOpCode['NOP']
							decodedInstr.append([opcode, 0, 0, 0]) # puts in a blank instruction
							print("Error001: Command " + str(line.strip()) + " is not aligned properly.")
						else:
							decodedInstr.append([opcode, xValInt, yValInt, zValInt]) # creates first instruction
							yValInt = checkIfNumAndReturn(wordsInLine[4])
							if yValInt == -1:
								opcode = handleBadInputArg(wordsInLine[4])
							elif int(wordsInLine[4][-2]) != 1:
								print(int(wordsInLine[4][-2]))
								opcode = instrToOpCode['NOP']
								decodedInstr.append([opcode, 0, 0, 0]) # puts in a blank instruction
								print("Error001: Command " + str(line.strip()) + " is not aligned properly.")
							# doesnt need to append this time since it'll naturally do the command at the end

					else:
						opcode = instrToOpCode['NOP']
						print("Error000: Command " + str(line.strip()) + " has invalid burst length.")
				elif len(wordsInLine) == 4: # should be BL = 1
					# STOREI 1 xxH #xxxx
					if int(wordsInLine[1]) == 1:
						xValInt = checkIfAddrAndReturn(wordsInLine[2])
						if xValInt == -1:
							opcode = handleBadInputArg(wordsInLine[2])
						yValInt = checkIfNumAndReturn(wordsInLine[3])
						if yValInt == -1:
							opcode = handleBadInputArg(wordsInLine[3])
						zValInt = 0
					else:
						opcode = instrToOpCode['NOP']
						print("Error000: Command " + str(line.strip()) + " has invalid burst length.")
				elif len(wordsInLine) == 3:
					# STOREI xxH #xxxx
					xValInt = checkIfAddrAndReturn(wordsInLine[1])
					if xValInt == -1:
						opcode = handleBadInputArg(wordsInLine[1])
					yValInt = checkIfNumAndReturn(wordsInLine[2])
					if yValInt == -1:
						opcode = handleBadInputArg(wordsInLine[1])
					zValInt = 0
				else:
					opcode = handleBadInputSize(len(wordsInLine))

			elif opcode == instrToOpCode['STORE']: #STORE
				# STORE xxH $R
				print("STORE DETECTED")
				# first checks length to make sure instruction has enough indecies
				if len(wordsInLine) != 3:
					opcode = handleBadInputSize(len(wordsInLine))
				else:
					# checks to make sure storage loc is valid (e.g. xxH is hex or XXXXXb is binary and is between 0 and 31)
					xValInt = checkIfAddrAndReturn(wordsInLine[1])
					if xValInt == -1:
						opcode = handleBadInputArg(wordsInLine[1])

					# checks to make sure register number is valid (0 to 7)
					yValInt = checkIfRegAndReturn(wordsInLine[2])
					if yValInt == -1:
						opcode = handleBadInputArg(wordsInLine[2])

					# does not need a zVal as it only uses the yVal as the register to put data from into memory (xVal)
					zValInt = 0

			elif opcode == instrToOpCode['LOADI']: #LOADI
				# LOADI $R #xxxx
				print("LOADI DETECTED")
				# first check length
				if len(wordsInLine) != 3:
					opcode = handleBadInputSize(len(wordsInLine))
				else:

					# now checks if first one is a register
					xValInt = checkIfRegAndReturn(wordsInLine[1])
					if xValInt == -1:
						opcode = handleBadInputArg(wordsInLine[1])

					# now checks if second one is a 16-bit number
					yValInt = checkIfNumAndReturn(wordsInLine[2])
					if yValInt == -1:
						opcode = handleBadInputArg(wordsInLine[2])

					# does not need z value
					zValInt = 0

			elif opcode == instrToOpCode['LOAD']: # LOAD
				# LOAD $R xxH
				print('LOAD DETECTED')
				if len(wordsInLine) != 3:
					opcode = handleBadInputSize(len(wordsInLine))

				else:
					# checks register
					xValInt = checkIfRegAndReturn(wordsInLine[1])
					if xValInt == -1:
						opcode = handleBadInputArg(wordsInLine[1])

					# checks addr
					yValInt = checkIfAddrAndReturn(wordsInLine[2])
					if yValInt == -1:
						opcode = handleBadInputArg(wordsInLine[2])

					# does not need z value
					zValInt = 0

			elif opcode == instrToOpCode['AND']:
				#AND $x $y $z
				print("AND DETECTED")
				if len(wordsInLine) != 4:
					opcode = handleBadInputSize(len(wordsInLine))
				else:
					# checks 3 registers
					xValInt = checkIfRegAndReturn(wordsInLine[1])
					if xValInt == -1:
						opcode = handleBadInputArg(wordsInLine[1])
					yValInt = checkIfRegAndReturn(wordsInLine[2])
					if yValInt == -1:
						opcode = handleBadInputArg(wordsInLine[2])
					zValInt = checkIfRegAndReturn(wordsInLine[3])
					if zValInt == -1:
						opcode = handleBadInputArg(wordsInLine[3])

			elif opcode == instrToOpCode['ANDI']:
				# ANDI $x $y #xxxx
				print("ANDI DETECTED")
				if len(wordsInLine) != 4:
					opcode = handleBadInputSize(len(wordsInLine))
				else:
					# checks 2 registers then a value
					xValInt = checkIfRegAndReturn(wordsInLine[1])
					if xValInt == -1:
						opcode = handleBadInputArg(wordsInLine[1])
					yValInt = checkIfRegAndReturn(wordsInLine[2])
					if yValInt == -1:
						opcode = handleBadInputArg(wordsInLine[2])
					# value
					zValInt = checkIfNumAndReturn(wordsInLine[3])
					if zValInt == -1:
						opcode = handleBadInputArg(wordsInLine[3])

			elif opcode == instrToOpCode['OR']:
				# OR $x $y $z
				print("OR DETECTED")
				if len(wordsInLine) != 4:
					opcode = handleBadInputSize(len(wordsInLine))
				else:
					# checks 3 registers
					xValInt = checkIfRegAndReturn(wordsInLine[1])
					if xValInt == -1:
						opcode = handleBadInputArg(wordsInLine[1])
					yValInt = checkIfRegAndReturn(wordsInLine[2])
					if yValInt == -1:
						opcode = handleBadInputArg(wordsInLine[2])
					zValInt = checkIfRegAndReturn(wordsInLine[3])
					if zValInt == -1:
						opcode = handleBadInputArg(wordsInLine[3])

			elif opcode == instrToOpCode['ORI']:
				# ORI $x $y #xxxx
				print("ORI DETECTED")
				if len(wordsInLine) != 4:
					opcode = handleBadInputSize(len(wordsInLine))
				else:
					# checks 2 registers then a value
					xValInt = checkIfRegAndReturn(wordsInLine[1])
					if xValInt == -1:
						opcode = handleBadInputArg(wordsInLine[1])
					yValInt = checkIfRegAndReturn(wordsInLine[2])
					if yValInt == -1:
						opcode = handleBadInputArg(wordsInLine[2])
					# value
					zValInt = checkIfNumAndReturn(wordsInLine[3])
					if zValInt == -1:
						opcode = handleBadInputArg(wordsInLine[3])

			elif opcode == instrToOpCode['ADD']:
				# ADD $x $y $z
				print("ADD DETECTED")
				if len(wordsInLine) != 4:
					opcode = handleBadInputSize(len(wordsInLine))
				else:
					# checks 3 registers
					xValInt = checkIfRegAndReturn(wordsInLine[1])
					if xValInt == -1:
						opcode = handleBadInputArg(wordsInLine[1])
					yValInt = checkIfRegAndReturn(wordsInLine[2])
					if yValInt == -1:
						opcode = handleBadInputArg(wordsInLine[2])
					zValInt = checkIfRegAndReturn(wordsInLine[3])
					if zValInt == -1:
						opcode = handleBadInputArg(wordsInLine[3])


			elif opcode == instrToOpCode['ADDI']:
				#ADDI $x $y #xxxx
				print("ADDI DETECTED")
				if len(wordsInLine) != 4:
					opcode = handleBadInputSize(len(wordsInLine))
				else:
					# checks 2 registers then a value
					xValInt = checkIfRegAndReturn(wordsInLine[1])
					if xValInt == -1:
						opcode = handleBadInputArg(wordsInLine[1])
					yValInt = checkIfRegAndReturn(wordsInLine[2])
					if yValInt == -1:
						opcode = handleBadInputArg(wordsInLine[2])
					# value
					zValInt = checkIfNumAndReturn(wordsInLine[3])
					if zValInt == -1:
						opcode = handleBadInputArg(wordsInLine[3])

			elif opcode == instrToOpCode['MUL']:
				# MUL $x $y $z
				print("MUL DETECTED")
				if len(wordsInLine) != 4:
					opcode = handleBadInputSize(len(wordsInLine))
				else:
					# checks 3 registers
					xValInt = checkIfRegAndReturn(wordsInLine[1])
					if xValInt == -1:
						opcode = handleBadInputArg(wordsInLine[1])
					yValInt = checkIfRegAndReturn(wordsInLine[2])
					if yValInt == -1:
						opcode = handleBadInputArg(wordsInLine[2])
					zValInt = checkIfRegAndReturn(wordsInLine[3])
					if zValInt == -1:
						opcode = handleBadInputArg(wordsInLine[3])

			elif opcode == instrToOpCode['MULI']:
				# MULI $x $y #xx
				# SLIGHTLY DIFFERENT IN THAT THE #XX can only be up to 5 bits (0 - 31)
				if len(wordsInLine) != 4:
					opcode = handleBadInputSize(len(wordsInLine))
				else:
					# checks 2 registers then a value
					xValInt = checkIfRegAndReturn(wordsInLine[1])
					if xValInt == -1:
						opcode = handleBadInputArg(wordsInLine[1])
					yValInt = checkIfRegAndReturn(wordsInLine[2])
					if yValInt == -1:
						opcode = handleBadInputArg(wordsInLine[2])
					# value
					zValInt = checkIfNumAndReturn(wordsInLine[3])
					if zValInt == -1 or zValInt < 0 or zValInt > 31: # also checks to make sure it is between 0-31
						opcode = handleBadInputArg(wordsInLine[3])

			elif opcode == instrToOpCode['MIN']:
				# MIN $x $y $z
				print("MIN DETECTED")
				if len(wordsInLine) != 4:
					opcode = handleBadInputSize(len(wordsInLine))
				else:
					# checks 3 registers
					xValInt = checkIfRegAndReturn(wordsInLine[1])
					if xValInt == -1:
						opcode = handleBadInputArg(wordsInLine[1])
					yValInt = checkIfRegAndReturn(wordsInLine[2])
					if yValInt == -1:
						opcode = handleBadInputArg(wordsInLine[2])
					zValInt = checkIfRegAndReturn(wordsInLine[3])
					if zValInt == -1:
						opcode = handleBadInputArg(wordsInLine[3])

			elif opcode == instrToOpCode['MINI']:
				# MINI $x $y #xxxx
				print("MINI DETECTED")
				if len(wordsInLine) != 4:
					opcode = handleBadInputSize(len(wordsInLine))
				else:
					# checks 2 registers then a value
					xValInt = checkIfRegAndReturn(wordsInLine[1])
					if xValInt == -1:
						opcode = handleBadInputArg(wordsInLine[1])
					yValInt = checkIfRegAndReturn(wordsInLine[2])
					if yValInt == -1:
						opcode = handleBadInputArg(wordsInLine[2])
					# value
					zValInt = checkIfNumAndReturn(wordsInLine[3])
					if zValInt == -1:
						opcode = handleBadInputArg(wordsInLine[3])

			elif opcode == instrToOpCode['SFL']:
				# SFL $x $y #xxxx
				print("SFL DETECTED")
				if len(wordsInLine) != 4:
					opcode = handleBadInputSize(len(wordsInLine))
				else:
					# checks 2 registers then a value
					xValInt = checkIfRegAndReturn(wordsInLine[1])
					if xValInt == -1:
						opcode = handleBadInputArg(wordsInLine[1])
					yValInt = checkIfRegAndReturn(wordsInLine[2])
					if yValInt == -1:
						opcode = handleBadInputArg(wordsInLine[2])
					# value
					zValInt = checkIfNumAndReturn(wordsInLine[3])
					if zValInt == -1:
						opcode = handleBadInputArg(wordsInLine[3])

			elif opcode == instrToOpCode['SFR']:
				# SFR $x $y #xxxx
				print("SFR DETECTED")
				if len(wordsInLine) != 4:
					opcode = handleBadInputSize(len(wordsInLine))
				else:
					# checks 2 registers then a value
					xValInt = checkIfRegAndReturn(wordsInLine[1])
					if xValInt == -1:
						opcode = handleBadInputArg(wordsInLine[1])
					yValInt = checkIfRegAndReturn(wordsInLine[2])
					if yValInt == -1:
						opcode = handleBadInputArg(wordsInLine[2])
					# value
					zValInt = checkIfNumAndReturn(wordsInLine[3])
					if zValInt == -1:
						opcode = handleBadInputArg(wordsInLine[3])



		# finally writes the op code states out
		# does a quick NOP check to turn those with opcode == NOP to all 0's (cleans up basically)
		if opcode == instrToOpCode['NOP']:
			xValInt = 0
			yValInt = 0
			zValInt = 0
		print("OUTPUT ARRAY IS: " + str([opcode, xValInt, yValInt, zValInt]))
		decodedInstr.append([opcode, xValInt, yValInt, zValInt])

	codeFile.close()


	# now checks for dependencies
	checkDependenciesAndOptimize()


def generateVectorFile(fileNameIn):
	# now we know that the inputs are valid and in the correct order after being compiled
	# goes through each input and writes it out to the vector file correctly
	# each instruction gets exactly 1 clock (NOTE - NEED TO CHECK ABOUT PRECHARGING TO READ SRAM)
	vecFile = open(fileNameIn, 'w')

	# first writes out header
	vecFile.write("radix\t")
	for rad in radix:
		vecFile.write(str(rad) + '\t')
	vecFile.write("\nio\t")
	for i in io:
		vecFile.write(str(i) + '\t')
	vecFile.write("\nvname\t")
	for name in vname:
		vecFile.write(str(name) + '\t')
	vecFile.write("\nslope\t" + str(slope))
	vecFile.write('\nvih\t' + str(vih))
	vecFile.write('\ntunit\t' + str(tunit))
	vecFile.write('\n\n')

	# now loops through each instruction and writes it out
	counter = 0
	for instr in decodedInstr:
		# writes out time
		vecFile.write(str(counter * clockPeriod) + '\t')
		# now writes out clock
		vecFile.write('0\t')
		# now writes out data

		# op code is 5 bits, 1 binary (should be 0 or 1 in hex too) and 4 bit hex (1 hex digit)
		hexStr = hex(instr[0])[2:]
		# needs to make sure hex string has two bits
		if len(hexStr) == 1:
			hexStr = '0' + hexStr
		vecFile.write(hexStr[0] + "\t" + hexStr[1] + '\t')

		# x value is 5 bits at most (if it is an address)
		hexStr = hex(instr[1])[2:]
		if len(hexStr) == 1:
			hexStr = '0' + hexStr
		vecFile.write(hexStr[0] + '\t' + hexStr[1] + '\t')

		# y value is same as x value
		hexStr = hex(instr[2])[2:]
		if len(hexStr) == 1:
			hexStr = '0' + hexStr
		vecFile.write(hexStr[0] + '\t' + hexStr[1] + '\t')

		# z value can have up to 4 hex digits
		hexStr = hex(instr[3])[2:]
		while len(hexStr) < 4: # must have 4 digits
			hexStr = '0' + hexStr
		vecFile.write(hexStr[0] + '\t' + hexStr[1] + '\t' + hexStr[2] + '\t' + hexStr[3] + '\t')

		vecFile.write('\n')

		# now writes out time and clock again (for clock == 1)
		counter += 1
		vecFile.write(str(counter * clockPeriod) + '\t')
		vecFile.write('1\t')
		# op code is 5 bits, 1 binary (should be 0 or 1 in hex too) and 4 bit hex (1 hex digit)
		hexStr = hex(instr[0])[2:]
		# needs to make sure hex string has two bits
		if len(hexStr) == 1:
			hexStr = '0' + hexStr
		vecFile.write(hexStr[0] + "\t" + hexStr[1] + '\t')

		# x value is 5 bits at most (if it is an address)
		hexStr = hex(instr[1])[2:]
		if len(hexStr) == 1:
			hexStr = '0' + hexStr
		vecFile.write(hexStr[0] + '\t' + hexStr[1] + '\t')

		# y value is same as x value
		hexStr = hex(instr[2])[2:]
		if len(hexStr) == 1:
			hexStr = '0' + hexStr
		vecFile.write(hexStr[0] + '\t' + hexStr[1] + '\t')

		# z value can have up to 4 hex digits
		hexStr = hex(instr[3])[2:]
		while len(hexStr) < 4: # must have 4 digits
			hexStr = '0' + hexStr
		vecFile.write(hexStr[0] + '\t' + hexStr[1] + '\t' + hexStr[2] + '\t' + hexStr[3] + '\t')

		vecFile.write('\n')

		counter += 1

	vecFile.close()

# checks for any code dependencies (multiplier OoO execution, etc.) and solves them
def checkDependenciesAndOptimize():
	global decodedInstr
	# NOW THAT WE HAVE THE VECTOR INPUTS IN ORDER, WE CHECK FOR DATA DEPENDENCIES AND RESCHEDULE ACCORDINGLY
	print("Dependency checking in progress. Do not expect ideal results.")

	# now we'll first check for basic multiplier dependencies (the multiplier gets 2 NOPs after it)
	for x in range(len(decodedInstr)):
		instr = decodedInstr[x]
		if instr[0] == instrToOpCode['MUL'] or instr[0] == instrToOpCode['MULI']:
			# for now we'll insert just a few NOPS before this instruction to prevent any dependencies (mult takes 4 cycles, ex takes 1)
			noOpInstr = [instrToOpCode['NOP'], 0, 0, 0]
			#print("INSERTING NOPS")
			decodedInstr.insert(x, noOpInstr)
			decodedInstr.insert(x, noOpInstr)
			decodedInstr.insert(x, noOpInstr)


# more of a stretch goal to create verifiable output that can be compared to later
def generateGoldenResults(fileNameIn):
	print("Golden Results generation in progress...")
	# goes through each of the vector instructions and calculates its result
	# writes the result to the text file along with the clock it should be generated by (mult takes 4 + normal pipeline time)

	resultsFile = open(fileNameIn, 'w')

	clockCounter = 0

	regArr = [0,0,0,0,0,0,0,0] # 8 register values that start at 0. Assumes memory is similar in that it all is 0

	for instr in decodedInstr:
		# checks each op code and determines what the result should be given what each register value is

		clockCounter += 1 # keeps track of 1 clock per instruction dispatched



	resultsFile.close()


# #
# HELPER FUNCTIONS
# #

# checks if input is a valid address (00H - 1FH hex or 00000B - 11111B binary).
# returns -1 on FALSE
# returns address integer value of 0 - 31 on TRUE
def checkIfAddrAndReturn(inputArgStr):
	res = -1
	try:
		if inputArgStr[-1] == 'H':
			hexInt = int(inputArgStr[:-1], 16)
			if hexInt >= 0 and hexInt < 32:
				res = hexInt
		elif inputArgStr[-1] == 'B':
			binInt = int(inputArgStr[:-1], 2)
			if binInt >= 0 and binInt < 32:
				res = binInt
	except ValueError: # if cannot be converted to binary or hex despite what it says
		res = -1

	return res

# checks if it is a valid register ($X and X is 0 - 7)
# returns -1 on FALSE
# returns register integer value (0 - 7) on TRUE
def checkIfRegAndReturn(inputArgStr):
	res = -1
	if inputArgStr[0] == '$':
		intVal = int(inputArgStr[1:])
		if intVal >= 0 and intVal < 8:
			res = intVal

	return res

# checks if it is a valid operand number #XXXXH (16 bits supported)
def checkIfNumAndReturn(inputArgStr):
	res = -1
	# similar approach as address, except this can be any 16-bit number and the first char should be '#'
	try:
		if inputArgStr[0] == '#':
			if inputArgStr[-1] == 'H':
				hexInt = int(inputArgStr[1:-1], 16)
				if hexInt >= 0 and hexInt < 65536: #2 ^ 16 = 65536
					res = hexInt
			elif inputArgStr[-1] == 'B':
				binInt = int(inputArgStr[1:-1], 2)
				if binInt >= 0 and binInt < 65536:
					res = binInt
	except ValueError:
		res = -1
	return res

# handles if any of the checkXandReturn returns a -1
# prints an error message returns the opcode for NOP
def handleBadInputArg(badInputStr):
	global instrToOpCode
	print("ERROR: Invalid input of form " + str(badInputStr))
	print("Inserting NOP as replacement.")
	return instrToOpCode['NOP']

# handles if any of the sizes are incorrect
# prints an error message returns the opcode for NOP
def handleBadInputSize(badInputSize):
	global instrToOpCode
	print("ERROR: Store instruction of invalid length " + str(badInputSize))
	print("Inserting NOP as a replacement.")
	return instrToOpCode['NOP']
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