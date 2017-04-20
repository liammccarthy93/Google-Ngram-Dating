import File, RegEx, datetime, sys
import numpy as np
from stop_words import get_stop_words

class Text:
	def __init__(self, File):	
		self.file = File
		self.text = self.setText()
		self.sentences = self.setSentences()
		self.N_start = 1
		self.N_end = 2
		print("Parsing Text...")
		self.NGrams = self.setNGrams()
		
		print("Text parsed.")
	def setText(self):
		return self.file.readContents()

	def getWords(self, text):
		return text.split()

	def setSentences(self):
		SentencesRegEx = RegEx.RegEx(".*?[\\.|?|!]", self.text)
		return SentencesRegEx.getResults()

	def getNGrams(self, N):				# N should be a list of N grams required eg. [1, 2] or [3]
		ngrams = []
		for n in N:
			ngrams.append(self.NGrams[n-1])
		return np.asarray(ngrams)

	def setNGrams(self):
		ngrams = self.set1Grams()									# get 1 grams first to set dimensions of matrix
		ngramsTemp = self.set_2to5_Grams()
		for row in range(len(ngramsTemp)):
			ngrams[row+1, 0:len(ngramsTemp[row])] = ngramsTemp[row]
		#print(ngrams)
		i=0
		for row in ngrams:
			ngrams[i] = self.removePeriods(self.removeNGramswithPunctuation(row))	# remove grams which cross commas, inverted commas, etc. then remove commas, full stops or question marks at end of sentences.
			i+=1

		for i in range(len(ngrams[:,0])):
			ngrams[i,:] = self.removeStopwords(ngrams[i,:])

		return ngrams

	def removeStopwords(self, row):
		stopwords = set(get_stop_words('english'))
		delete_indexes = []
	
		for i in range(len(row)):
			if row[i] is None:
				break
			splitted_ngram = row[i].split()
	
			if row[i] == splitted_ngram[0]:      # if its just a 1-gram then .split wouldn't have changed it
				if row[i].lower() in stopwords:       # can just check if that ngram is in the stop
					delete_indexes.append(i)
			elif len(splitted_ngram) == 2:
				if splitted_ngram[0].lower() in stopwords and splitted_ngram[1].lower() in stopwords:
					delete_indexes.append(i)
			else:
				print(row[i], splitted_ngram)

#		for i in range(len(row)):
#			if row[i] is None:
#				break
#			for stopword in stopwords:
#				if stopword == row[i].lower() or (((' '+stopword) in row[i].lower()) and ((stopword+' ') in row[i].lower())):
#					print(stopword,row[i].lower())
					
		row = np.delete(row, delete_indexes)
		
		row = np.append(row, [None for x in range(len(delete_indexes))])

		return row

	def set1Grams(self):				
		One_Grams = self.getWords(self.text)				
		ngrams = np.array([[None for x in range(len(One_Grams))] for y in range(self.N_end)])
		ngrams[0] = One_Grams
		return ngrams

	def set_2to5_Grams(self):
		N = range(2, self.N_end+1)
		ngrams = [[] for x in range(N[-1])]
		for n in N:
			for sentenceNum in range(len(self.sentences)):
				words = self.getWords((self.sentences[sentenceNum]))
				for word in range(len(words)-(n-1)):
					ngram = words[word]
					for i in range(1,n):
						ngram += (' ' + words[word+i])
					ngrams[n-1].append(ngram)
		
				ngrams[n-1][-1] = ngrams[n-1][-1]

		del(ngrams[0])
		return np.asarray(ngrams)	

	def doesNGramContainPunctuation(self, ngram):
		regEx = RegEx.RegEx('[\\w| ]+', ngram)		# check if there's anything breaking up the series of letters and spaces
		try:
			if len(regEx.getResults()) > 1:				# if there's anything other than a space or a letter then the regex will return more than 1 result
				return True
			else:
				return False
		except:										# some punctuation may have been classified as a 1 gram (eg. " - "), which won't be caught by RegEx, so need to delete this.
			return True
	def removeNGramswithPunctuation(self, ngrams):
		i = 0
		for ngram in ngrams:
			if self.doesNGramContainPunctuation(ngram):
				ngrams = np.append(np.delete(ngrams, i), None)	# delete ngrams with punctuation and append an extra zero to maintain the correct size
			else:
				i+=1
		return ngrams

	def removePeriods(self, Grams):
		originalLength = len(Grams)
		i=0

		for gram in Grams:
			if gram is None:
				continue
			gram = gram.replace('.', '').replace('?', '').replace('!', '').replace(':', '').replace(';', '')				# remove trailing punctuation
			gram = gram.replace("'", '')
			gram = gram.replace(',', '')
			gram = gram.replace('"', '')
			gram = gram.replace('(', '')
			gram = gram.replace(')', '').replace(':', '').replace(';', '')
			Grams[i] = gram
			i+=1

		return np.append(Grams, [None for x in range(len(Grams), originalLength)])


