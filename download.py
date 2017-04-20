import File, Values, Text,sys, ProbDens, sys

inputfilename = "textCopy.txt"
outputfilename = 'testOutput.txt'
N_start = 1
N_end = 2
desiredNGrams = range(N_start, N_end+1)

# create file objects
inputFile = File.File(inputfilename)
outputFile = File.File(outputfilename)

# create text object for the text in the inputfile.
text = Text.Text(inputFile)

# get the list ngrams in text form from the text
ngrams = text.getNGrams(desiredNGrams)
text.estimateDownloadTime(desiredNGrams)

outputFile.clear()

# download the values for each ngram
for row in ngrams:
	for ngram in row:
		if ngram is None:
			break
		ngramOBJ = Values.undownloadedNGram(ngram, outputFile)		# create ngram object for each piece of ngram text.
		ngramOBJ.writeValuesToFile()
