# check_results.py
# EE577A Final Project
# Spring - 2017

import csv

# reads in the out.csv file which should be the values data_in[0-15] and en[0-7]
# when en[0-7] == 0 (or 00000000B), we look at the data_in values to see what is being loaded
# and report that along with the clock timestamp in the actual_results.txt file

# #
# GLOBAL VARIABLES
# #

csvFileName = 'out1.csv'
resultsFileName = 'actual_results.txt'
clockPeriod = 1.0e-9 # in seconds

resultsArr = [[0,0]] # pairs matching clock # to the value seen (start with 0,0)

# #
# FUNCTIONS
# #

def readCSV(filenameIn):
	global resultsArr
	csvFile = open(filenameIn)
	reader = csv.DictReader(csvFile)
	clockCounter = 0
	for row in reader:
		# checks value right after the clock (e.g. if its 1ns clock, looks at value at >1ns, >2ns, etc.)
		if str(row['/en[0] Y']).strip() != '':
			if float(row['/en[0] Y']) > clockCounter * clockPeriod:
				# now we check if we're writing to $0 (en[7:0] == 0)
				allZeros = True
				for x in range(8):
					if float(row['/en[' + str(x) + '] X']) > 1.0:
						allZeros = False
				if allZeros == True: # if the right index, then we save the value on data_in[15:0]
					result = 0
					for x in range(16):
						if float(row['/data_in[' + str(x) + '] X']) > 1.0:
							result += 1 * pow(2, x)
					resultsArr.append([clockCounter, result])

				# increment clock counter for next variable to read
				clockCounter += 1

	csvFile.close()

def writeResults(filenameIn):
	resultsFile = open(filenameIn, 'w')

	resultsFile.write("CLOCK #\t$0 VALUE\n")

	for res in resultsArr:
		resultsFile.write(str(res[0]) + '\t\t' + str(res[1]) + '\n')

	resultsFile.close()
# #
# MAIN
# #

def main():
	print("Reading in out.csv . . . ")
	readCSV(csvFileName)
	print('done.')

	print("Writing actual_results.txt . . . ")
	writeResults(resultsFileName)
	print('done.')

if __name__ == "__main__":
	main()