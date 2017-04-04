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
vecFileName = "vector_file.vec"
goldenResultsFileName = "golden_results.txt"

# vector header info
radix = [1, 1, 1, 4, 1, 4, 1, 1, 1, 4, 4, 4, 4, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1]
io = ['i'] * 23 # all inputs
vname = ['CLK', 'CLK_B', 'NO_OP_IN', 'OP_IN<[3:0]>', 'ADDR_IN<4>', 'ADDR_IN<[3:0]>',
		 'DEST_REG_ADDR_IN<2>', 'DEST_REG_ADDR_IN<1>', 'DEST_REG_ADDR_IN<0>',
		 'IMMEDIATE_DATA<[15:12]>', 'IMMEDIATE_DATA<[11:8]>', 'IMMEDIATE_DATA<[7:4]>', 'IMMEDIATE_DATA<[3:0]>',
		 'PRECHARGE', 'READ_EN', 'WRITE_EN', 'RESET', 'REGID_IF2<2>', 'REGID_IF2<1>', 'REGID_IF2<0>',
		 'REGID_IF1<2>', 'REGID_IF1<1>', 'REGID_IF1<0>']
slope = 0.01
vih = 1.8
tunit = "ns"
clockPeriod = 10 # given in tunit, default is this

# op codes map to their instruction
instrToOpCode = {
	'NOP': 16,
	'STOREI': 14,
	'STORE': 15,
	'LOADI': 0,
	'LOAD': 1,
	'AND': 3,
	'ANDI': 2,
	'OR': 5,
	'ORI': 4,
	'ADD': 7,
	'ADDI': 6,
	'MUL': 13,
	'MULI': 12,
	'MIN': 11,
	'MINI': 10,
	'SFL': 8,
	'SFR': 9
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
				#print("NOP DETECTED")
				# does nothing since everything defaults to 0
				pass

			elif opcode == instrToOpCode['STOREI']: # STOREI
				# STOREI {bl} xxH #xxxx {#xxxx}
				#print("STOREI IN PROGRESS")
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
				#print("STORE DETECTED")
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
				#print("LOADI DETECTED")
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
				#print('LOAD DETECTED')
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
				#print("AND DETECTED")
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
				#print("ANDI DETECTED")
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
				#print("OR DETECTED")
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
				#print("ORI DETECTED")
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
				#print("ADD DETECTED")
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
				#print("ADDI DETECTED")
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
				#print("MUL DETECTED")
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
				#print("MIN DETECTED")
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
				#print("MINI DETECTED")
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
				#print("SFL DETECTED")
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
				#print("SFR DETECTED")
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
	# now we have the instruction, the destination, and the operands. This allows us to generate the correct inputs
	# for every given situation


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
	counter = 0.0
	# first instruction is RESET for the registers
	writeSingleInstruction([instrToOpCode['NOP'],0,0,0], vecFile, counter, 0, 0, 0, 0, 0) # assumes reset is active LOW
	counter += 1.0
	writeSingleInstruction([instrToOpCode['NOP'],0,0,0], vecFile, counter, 1, 0, 0, 0, 0)
	counter += 1.0
	for instr in decodedInstr:

		writeSingleInstruction(instr, vecFile, counter, 0, 1, 0, 0, 1) # precharge state for half of clock LOW
		counter += 0.5

		# if instruction is STORE or STOREI, we write to SRAM.
		if instr[0] == instrToOpCode['STORE'] or instr[0] == instrToOpCode['STOREI']:
			writeSingleInstruction(instr, vecFile, counter, 0, 0, 0, 1, 1)
		# if instruction is LOAD, we read from SRAM
		elif instr[0] == instrToOpCode['LOAD']:
			writeSingleInstruction(instr, vecFile, counter, 0, 0, 1, 0, 1)
		# otherwise no read or write
		else:
			writeSingleInstruction(instr, vecFile, counter, 0, 0, 0, 0, 1)

		counter += 0.5

		# now writes a full clock HIGH
		# if instruction is STORE or STOREI, we write to SRAM.
		if instr[0] == instrToOpCode['STORE'] or instr[0] == instrToOpCode['STOREI']:
			writeSingleInstruction(instr, vecFile, counter, 1, 0, 0, 1, 1)
		# if instruction is LOAD, we read from SRAM
		elif instr[0] == instrToOpCode['LOAD']:
			writeSingleInstruction(instr, vecFile, counter, 1, 0, 1, 0, 1)
		# otherwise no read or write
		else:
			writeSingleInstruction(instr, vecFile, counter, 1, 0, 0, 0, 1)

		counter += 1.0 # no half-clocking here

	# adds a 5 dummy clocks to finish out the simulation
	for x in range(5):
		writeSingleInstruction([instrToOpCode['NOP'], 0, 0, 0], vecFile, counter, 0, 0, 0, 0, 1)
		counter += 1.0
		writeSingleInstruction([instrToOpCode['NOP'], 0, 0, 0], vecFile, counter, 1, 0, 0, 0, 1)
		counter += 1.0

	vecFile.close()

# writes out a single instruction code to the file input (handles clocks, etc.)
def writeSingleInstruction(instr, vecFile, counter, clock, precharge, sram_read, sram_write, reset):
	# counter first to keep track of time
	vecFile.write(str(counter * clockPeriod) + '\t')

	# now clock and clock bar
	if clock == 0:
		vecFile.write('0\t1\t')
	else:
		vecFile.write('1\t0\t')

	# first is if this is a no-op
	if instr[0] == instrToOpCode['NOP']:
		vecFile.write('1\t0\t')
	else:
		vecFile.write('0\t')
		# now writes proper op code out since it is something else
		vecFile.write(hex(instr[0])[2:].upper())
		vecFile.write('\t')

	# now writes address (if it exists, otherwise write 0 to it)
	firstBit = 0
	nextFour = 0
	if instr[0] == instrToOpCode['STORE'] or instr[0] == instrToOpCode['STOREI']:
		firstBit = (instr[1] & 16) >> 4
		nextFour = instr[1] & 15
	elif instr[0] == instrToOpCode['LOAD']:
		firstBit = (instr[2] & 16) >> 4
		nextFour = instr[2] & 15
	vecFile.write(str(firstBit) + '\t' + hex(nextFour)[2:].upper() + '\t')

	# now destination register in (if it exists)
	firstBit = 0
	secondBit = 0
	thirdBit = 0
	if instr[0] != instrToOpCode['STORE'] and instr[0] != instrToOpCode['STOREI']:
		firstBit = (instr[1] & 4) >> 2
		secondBit = (instr[1] & 2) >> 1
		thirdBit = instr[1] & 1
	vecFile.write(str(firstBit) + '\t' + str(secondBit) + '\t' + str(thirdBit) + '\t')

	# now writes immediate data (if exists)
	hexRep = '0000'
	if (instr[0] % 2 == 0 and instr[0] != instrToOpCode['NOP']) or instr[0] == instrToOpCode['SFL'] or instr[0] == instrToOpCode['SFR']:
		if instr[0] != instrToOpCode['LOADI'] and instr[0] != instrToOpCode['STOREI']:
			# always is the 'z' value except for LOADI and STOREI in which it is the 'y' value
			hexRep = hex(instr[3])[2:].upper()
		else:
			hexRep = hex(instr[2])[2:].upper()
	while len(hexRep) < 4:
		hexRep = '0' + hexRep
	for x in range(4):
		#print("HEX REP IS " + str(hexRep))
		vecFile.write(hexRep[x] + '\t')

	# now writes out SRAM values
	# precharge
	vecFile.write(str(precharge) + '\t')
	# read
	vecFile.write(str(sram_read) + '\t')
	# write
	vecFile.write(str(sram_write) + '\t')

	# reset command (resets registers)
	vecFile.write(str(reset) + '\t')

	# now writes out register Y (IF2)

	# exists on all operations that arent load or store or NOP
	firstBit = 0
	secondBit = 0
	thirdBit = 0
	if instr[0] != instrToOpCode['LOAD'] and instr[0] != instrToOpCode['LOADI'] and instr[0] != instrToOpCode['STORE'] and instr[0] != instrToOpCode['STOREI'] and instr[0] != instrToOpCode['NOP']:
		firstBit = (instr[2] & 4) >> 2
		secondBit = (instr[2] & 2) >> 1
		thirdBit = (instr[2] & 1)
	vecFile.write(str(firstBit) + '\t' + str(secondBit) + '\t' + str(thirdBit) + '\t')

	# now writes out register Z (IF1) if it exists (only exists if not an immediate command)
	firstBit = 0
	secondBit = 0
	thirdBit = 0
	if instr[0] % 2 == 1 and instr[0] != instrToOpCode['LOAD'] and instr[0] != instrToOpCode['SFL'] and instr[0] != instrToOpCode['SFR']:
		# uses the z value by default
		if instr[0] != instrToOpCode['STORE']:
			firstBit = (instr[3] & 4) >> 2
			secondBit = (instr[3] & 2) >> 1
			thirdBit = (instr[3] & 1)
		# store uses the 'y' value
		else:
			firstBit = (instr[2] & 4) >> 2
			secondBit = (instr[2] & 2) >> 1
			thirdBit = (instr[2] & 1)
	vecFile.write(str(firstBit) + '\t' + str(secondBit) + '\t' + str(thirdBit) + '\t')


	# writes new line
	vecFile.write('\n')




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
	# goes through entire code, keeping track of values stored in memory
	# at end of execution, prints out all the register values along with a dump of the memory

	# initializes all values to 0
	regVals = [0,0,0,0,0,0,0,0] # 0 - 7
	memVals = [0] * 32 # 0 - 31


	# goes through each instruction and calculates what it does on the memory
	'''
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
	'''
	for instr in decodedInstr:
		# checks what type of instruction this is and each instruction is handled correctly
		if instr[0] == instrToOpCode['NOP']:
			# does nothing
			pass
		elif instr[0] == instrToOpCode['STOREI']:
			# stores val y into address x
			memVals[instr[1]] = instr[2]
		elif instr[0] == instrToOpCode['STORE']:
			# stores reg y into address x
			memVals[instr[1]] = regVals[instr[2]]
		elif instr[0] == instrToOpCode['LOADI']:
			# loads val y into reg x
			regVals[instr[1]] = instr[2]
		elif instr[0] == instrToOpCode['LOAD']:
			# loads addr y into reg x
			regVals[instr[1]] = memVals[instr[2]]
		elif instr[0] == instrToOpCode['AND']:
			# bitwise AND of y and z, stored in x
			regVals[instr[1]] = regVals[instr[2]] & regVals[instr[3]]
		elif instr[0] == instrToOpCode['ANDI']:
			# bitwise AND of reg y and val z
			regVals[instr[1]] = regVals[instr[2]] & instr[3]
		elif instr[0] == instrToOpCode['OR']:
			# bitwise OR of y and z, stored in x
			regVals[instr[1]] = regVals[instr[2]] | regVals[instr[3]]
		elif instr[0] == instrToOpCode['ORI']:
			# bitwise OR of reg y and val z
			regVals[instr[1]] = regVals[instr[2]] | instr[3]
		elif instr[0] == instrToOpCode['ADD']:
			#  ADD of y and z, stored in x
			regVals[instr[1]] = regVals[instr[2]] + regVals[instr[3]]
		elif instr[0] == instrToOpCode['ADDI']:
			# ADD of reg y and val z
			regVals[instr[1]] = regVals[instr[2]] + instr[3]
		elif instr[0] == instrToOpCode['MUL']:
			# 5-bit multiplication of y and z, stored in x
			regVals[instr[1]] = (regVals[instr[2]] & 31) * (regVals[instr[3]] & 31) # only uses lower five bits (11111B = 31)
		elif instr[0] == instrToOpCode['MULI']:
			# 5-bit multiplication of reg y and val z
			regVals[instr[1]] = (regVals[instr[2]] & 31) * instr[3]
		elif instr[0] == instrToOpCode['MIN']:
			# MIN of y and z, stored in x
			regVals[instr[1]] = min(regVals[instr[2]],regVals[instr[3]])
		elif instr[0] == instrToOpCode['MINI']:
			# MIN of reg y and val z
			regVals[instr[1]] = min(regVals[instr[2]],instr[3])
		elif instr[0] == instrToOpCode['SFL']:
			# shift of y left z, stored in x
			regVals[instr[1]] = regVals[instr[2]] << instr[3]
		elif instr[0] == instrToOpCode['SFR']:
			# shift of y right z, stored in x
			regVals[instr[1]] = regVals[instr[2]] >> instr[3]

	# writes out the results to the file
	resultsFile = open(fileNameIn, 'w')
	resultsFile.write("REGISTER VALUES\n")
	resultsFile.write("$0\t$1\t$2\t$3\t$4\t$5\t$6\t$7\n")
	for reg in regVals:
		resultsFile.write(str(reg) + '\t')
	resultsFile.write('\n\n')

	resultsFile.write("MEMORY VALUES\n")
	for x in range(16):
		resultsFile.write(str(x) + "\t")
	resultsFile.write('\n')
	for x in range(16):
		resultsFile.write(str(memVals[x]) + '\t')
	resultsFile.write('\n\n')
	for x in range(16):
		resultsFile.write(str(x+16) + '\t')
	resultsFile.write('\n')
	for x in range(16):
		resultsFile.write(str(memVals[x + 16]) + '\t')
	resultsFile.write('\n')

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