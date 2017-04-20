import File, Filter, time
import numpy as np
import scipy.stats

class NGram():	

	def __init__(self, words, totalsFile):
		self.words = words
		self.totalsFile = totalsFile
		self.N = str(len(self.words.split()))							# find the N value for the ngram
		self.books = None
		self.occurances = self.setValues()

	def getNGram(self):
		return self.words

	# return ngram frequency values for the years 1800-2000
	def getValues(self):
		return self.occurances[-203:-2]

	def normalise(self):
		return np.true_divide(self.getValues(),np.sum(self.getValues()))

	def getMaxYear(self):
		return 1800+np.argmax(self.getValues())

	# return the number of volumn occurences for the years 1800-2000
	def getBooks(self):
		#tp = [self.books[i,1] for i in range(len(self.books)) if self.books[i,0]>=1800 and self.books[i,0]<=2000]
		#plt.plot(tp)
		#plt.show()
		F = Filter.LP_Filter([self.books[i,1] for i in range(len(self.books)) if self.books[i,0]>=1800 and self.books[i,0]<=2000], cutoffHarmonic=10)
		#plt.plot(F.getFilteredValues())
		#plt.show()
		#return F.getFilteredValues()
		return np.array([self.books[i,1] for i in range(len(self.books)) if self.books[i,0]>=1800 and self.books[i,0]<=2000])

	def getTotalBooks(self):
		return np.sum(self.getBooks())

	def plot(self):
		plt.close()
		plt.plot(np.array(range(1800,2001)), self.getValues())
		plt.savefig("Plots/"+self.words+".png")


	def getNormalisedValues(self):
		return np.true_divide(self.getValues(),(np.sum(self.getValues())))

	def Smooth(self):
		self.occurances = self.Filtering(self.occurances[:])				# apply Low Pass Filter
		self.occurances = self.Squish()					# Move all values closer to the mean by k
		"""
		plt.close()
		plt.plot(range(1800,2001),self.getNormalisedValues())
		ax = plt.gca()
		ax.set_ylim([0, 0.015])
		ax.set_xlim([1800, 2000])
		plt.xticks([1800, 1850,1900, 1950, 2000])
		plt.yticks([0, 0.015])	
		ax.tick_params(labelsize=17)

		plt.xlabel('Year', fontsize=17)
		plt.ylabel('P(year|ngram)', fontsize=17)
		plt.savefig('post_filt.png', dpi=500, bbox_inches='tight')
		sys.exit()
		"""
		return self						# return relevant values

	def Squish(self):
		#k=0.95

		k=0.05
		dist = np.mean(self.occurances) - self.occurances		# get distance from mean. Negative if value is above mean, and vica versa

		self.occurances += k*dist 															# bring value closer to mean.

		return self.occurances

	def Filtering(self, data):
		LPfilter = Filter.LP_Filter(data)	# create low-pass filter object
		data = LPfilter.getFilteredValues()	# apply filter to the values
		return data

	def kurtosis(self):
		return scipy.stats.kurtosis(np.round(self.normalise(), 6), fisher=False)	# rounding avoids scenarios where floating point differences in what should be a uniform distribution cause very high kurtosis

	def StdDev(self):
		return np.std(self.normalise())

	def IQR(self):
		return np.subtract(*np.percentile(self.getValues(), [75, 25]))

	# retrieve values for the number of occurences of the ngram
	def setOccurances(self, downloadFlag):		
		# try to open the CSV file corresponding to this ngram. If it doesn't exist then this will fail so program will go to 'except'
		try:
			# read the CSV file
			self.totalOccurances = pd.read_csv('CSVs/'+self.getNGram()+'.csv', usecols=['Year', 'Occurances', 'Books'])
			# try to remove extra 'b' and inverted-commas from either side of the string.
			try:
				self.totalOccurances['Year'] = self.totalOccurances['Year'].map(lambda x: x.lstrip('b\'').rstrip('\''))
				self.totalOccurances['Occurances'] = self.totalOccurances['Occurances'].map(lambda x: x.lstrip('b\'').rstrip('\''))
				self.totalOccurances['Books'] = self.totalOccurances['Books'].map(lambda x: x.lstrip('b\'').rstrip('\''))
			# if above fails then just continue with the program
			except:
				pass
			finally:
				# convert pandas dataframe into matrix
				self.totalOccurances = self.totalOccurances.as_matrix()
				ngram = (np.array([self.getNGram() for x in range(len(self.totalOccurances[:,0]))]))
				self.totalOccurances = np.column_stack((ngram, self.totalOccurances.astype(int)))

		# if opening the CSV file failed then read values from the DB and write a new CSV file for next time
		except:
			self.totalOccurances = File.H5File('/Users/Liam/Desktop/'+str(self.N)+'/'+str(self.N)+'Grams.hg').read(self.words, self.N)
			self.writeToCSV(self.totalOccurances)
		finally:
			return self.totalOccurances

    # return the raw occurences of the ngram
	def getOccurances(self):
		try:
			toReturn = [int(x[2]) for x in self.totalOccurances]
			return toReturn
		except:
			return 0

    # return the sum of all occurences of the ngram
	def getTotalOccurances(self):
		return np.sum(self.getOccurances())

	def setValues(self):
		NGram_DB = File.H5File('/Users/Liam/Desktop/'+str(self.N)+'/'+str(self.N)+'Grams.hg')
		#print("Retrieving data for \'" + self.words + "\'.")
		start_time = time.time()
		occ = self.setOccurances(True)

		if occ is None:
			occ = np.column_stack((self.words,1800,0,0))
		elif len(occ) == 0:
			occ = np.column_stack((self.words,1800,0,0))
		occurances = self.LimitToYearsOfInterest(np.column_stack((occ[:,0], occ[:,1], occ[:,2]))) # read in ngram frequency values for 1770-2003

		#print("Data retrieved in a time of " + str((time.time() - start_time))[0:4] + " seconds.")
		# read total values for 1770-2003
		totals = self.LimitToYearsOfInterest(np.insert(self.totalsFile.read(), 0, [0 for x in range((2003-1650))], axis=1))

		self.books = self.LimitToYearsOfInterest(np.column_stack((occ[:,0], occ[:,1], occ[:,3])))
		return (np.true_divide(occurances[:,1],totals[:,1]))	# return float division of value and total for each year



	# remove early/late years which are outside range of interest. Fill in empty years with 0. Fill in early empty years with the value for 1800
	# this reduces the effects of the low pass filter on the early and later data.
	def LimitToYearsOfInterest(self, occurances):
		firstYear, lastYear = 1650, 2003						# set years of interest
		newOccurances = np.array([[0 for x in range(2)] for y in range(lastYear-firstYear)])	# create empty array for values for each year
		newOccurances[:, 0] = np.array(range(firstYear, lastYear))	# put the years in the first column
		if len(occurances[:,0]) <= 0:									# if no data found for ngram in DB:
			newOccurances[:,1] = self.getTotals()						#	this ensures frequency values are the same for each year (ie. sample has no affect on overall probability distribution)
		else:
			try:
				yearsContained = np.in1d(newOccurances[:,0], occurances[:,1])	# create array showing which years are not accounted for in the DB (ie. no occurance of ngram in that year)
			except:
				yearsContained = np.array([0 for x in range(len(newOccurances))])
			j=0														# keep track of position in original array
			for i in range(len(newOccurances)):						# for each year of interest		
				if yearsContained[i]:								# if there's ngram data then copy that into the new array
					newOccurances[i, 1] = occurances[j, 2]	
					j+=1
																	# else keep the occurances value at zeros
		return newOccurances										# return the new array with all values filled in

	def getTotals(self):
		return self.totalsFile.read()[:,1]

	def writeToCSV(self, occurances):
		# placeholder to avoid writting an empty CSV
		if len(occurances) <= 1:
			occurances = np.column_stack(([self.getNGram()],[b'1800'], [b'0'], [b'0']))
		df = pd.DataFrame(occurances, columns = ['NGram', 'Year', 'Occurances', 'Books']).set_index('Year')
		df.to_csv('CSVs/'+self.getNGram()+'.csv')
	
	