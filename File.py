import RegEx, os
import numpy as np
import gzip, subprocess, tables,sys, shutil

class File:
	# Constructor
	def __init__(self, filename):
		self.filename = filename

	def getFilename(self):
		return self.filename

	# opens the file in a given mode, with error checking
	def openFile(self, mode):
		self.checkMode(mode)			# ensure that the opening mode is valid
		try:    												
			fPtr = open(self.filename, mode)
		except IOError as e:
			raise RuntimeError('Could not open file ' + self.filename + ' in mode \'' + mode + '\'')
		return fPtr

	def checkMode(self, mode):
		correct_modes = ['w', 'r', 'a']
		if mode != correct_modes[0] and mode != correct_modes[1] and mode != correct_modes[2]:
			raise RuntimeError(str(mode) + " is not a valid mode to open a file in. Please use \'w\' for writing or \'r\' for reading or \'a\' for appending.")

	def closeFile(self, fPtr):
		return fPtr.close()			# returns true if file closes successfully, as is convention from built in close() method. Else raises error

	def readContents(self):			
		fPtr = self.openFile('r')
		text = fPtr.read()
		self.closeFile(fPtr)
		return text

	def writeContents(self, content):	
		self.convertToString(content)
		fPtr = self.openFile('a')
		self.writeToFile(content, fPtr)
		return self.closeFile(fPtr)

	def convertToString(self, content):
		try:
			return str(content)
		except:
			raise RuntimeError('Cannot write object of type ' + type(content) + ' to file.')	

	def writeToFile(self, content, fPtr):
		try:
			fPtr.write(content)
		except:
			raise RuntimeError('Failed while attempting to write to the file.')

	def clear(self):
		fPtr = self.openFile('w')	# opening for writting clears the file
		return self.closeFile(fPtr)

class GZ_File(File):
	def openFile(self, mode):
		self.checkMode(mode)
		try:
			fPtr = gzip.open(self.filename, mode)
		except IOError as e:
			raise RuntimeError('Could not open file ' + self.filename + ' in mode \'' + mode + '\'')
		return fPtr

	def Generator(self):
		fPtr = self.openFile('r')
		records = self.EmptyArray()
		for line in fPtr:
			line = line.decode('utf-8')
			#regEx = RegEx.RegEx("[^\t]+", line)
			#line = 
			#[word, year, occurances, books] = regEx.getResults()
			[word, year, occurances, books] = line.split('\t')		# split way faster than regex - uncomment above to do speed tests.
			if('_' not in (word)):
				# if we're still on the same word
				if records[0,0] == word:
					records = np.vstack((records, [word, int(year), int(occurances), int(books)]))				
				# if there's no real records in the array yet
				elif records[0,0] == '':
					records = np.vstack(([word, int(year), int(occurances), int(books.replace('\\n', ''))], records))
				# otherwise we've reached a new word, so need to deal with the last word
				else:
					# check if the number of occurances reached the threshold
					if(np.sum(records[:,2].astype(np.int)) > 2000):
						# if if did then write those records to the database
						for record in records:	
							if record[0]!='':
								yield record
					# stack the new record onto an empty array (need the empty array so that the first if condition has a 2D array)			
					records = np.vstack(([word, year, occurances, books],self.EmptyArray()))
		fPtr.close()

	# create empty 2x4 array - Needs to be 2 rows to allow row access in general case. empty rows not passed outside of function
	def EmptyArray(self):
		return np.vstack((['',0,0,0], ['',0,0,0]))

class Directory():
	def __init__(self, path):
		self.path = path

	def getDirectory(self):
		return self.path

	def setPath(self, path):
		if path is None:
			return self.path
		else:
			return path

	def getFiles(self, path=None): # self arguments cannot be assigned here http://stackoverflow.com/questions/1802971/nameerror-name-self-is-not-defined
		path = self.setPath(path)
		#print(subprocess.check_output(['ls', path]))
		filesText = str(subprocess.check_output(['ls', path]), 'ascii')
		for file in filesText.split():
			yield file

	def clear(self, path=None):
		path = self.setPath(path)
		for file in self.getFiles(path=path):
			if '/' not in file:
				file = '/' + file
			if self.isDir(path+file):	
				self.clear(path=path+file)
			else:
				os.remove(path+file)
	def isDir(self, name):
		if '.' in name:
			return False
		else:
			return True

class gramData(tables.IsDescription):
	word	    = tables.StringCol(100)
	year 		= tables.UInt16Col()
	occurances  = tables.UInt32Col()
	books 		= tables.UInt32Col() 	

class H5File(File):
	# Constructor
	def __init__(self, filename):
		self.filename = filename
		self.h5filePtr = None

	def openFile(self, mode, *args, **kwargs):
		self.checkMode(mode)
		if 'w' in mode:
			self.h5filePtr = tables.open_file(self.filename, mode = mode, title = kwargs['title'])
		else:
			self.h5filePtr = tables.open_file(self.filename, mode = mode)
		return self.h5filePtr

	def createTable(self, table):
		table = table + "_"	# add underscore to avoid issues with keywords like "as"
		if '-' in table:			# replace a dash with underscore to go with convention naming schemes
			table = '_' + table[1:]
		self.openFile('a')
		filters = tables.Filters(complevel=1, complib="blosc", fletcher32=False)	
		return self.h5filePtr.create_table("/", str(table), gramData, str(table), filters=filters)
		
	def createGroup(self, directory, GroupName):
		return self.h5filePtr.create_group("/", GroupName, 'Data for Ngrams starting with '+GroupName)		

	def getH5FileInfo(self):
		return self.h5filePtr

	def setTableProperties(self, rowPtr, word, year, occurances, books):
		rowPtr['word'] 		 = word
		rowPtr['occurances'] = int(occurances)
		rowPtr['books']		 = int(books)
		rowPtr['year']		 = int(year)
		rowPtr.append()

	def writeToDisk(self, table):
		table.flush()

	def closeFile(self):
		self.h5filePtr.close()

	def read(self, string, N):
		self.openFile('r')
		condition = '((word == b\"{0}\") & (year >= 1770))'.format(string)
		desiredTableName = self.setDesiredTableName(string, N)
		for table in self.tablesGenerator():
			if (desiredTableName in table.name):
				try:
					result = np.array([[(row["word"]), int((row["year"])), int((row["occurances"])), int((row["books"]))] for row in table.where(condition)])	
				except:
					print("Corrputed table: " + str(table.name))
					result = []
				finally:
					self.closeFile()
					return result

		
	def setDesiredTableName(self, string, N):
		string = string.lower()
		if int(N) == 1:
			return string[0]
		elif int(N) == 2:
			desiredTableName = string[0]+string[1] + '_'
			if ' ' in desiredTableName:
				desiredTableName = desiredTableName.replace(' ', '_')
			return desiredTableName
		else:
			ValueError('Cannot read N grams of value ' + str(N))

	def index(self):
		for table in self.tablesGenerator():
			print("Creating Index for table: " + table.name)
			table.cols.word.create_index()

	def tablesGenerator(self):
		for group in self.h5filePtr.walk_groups("/"):
			for table in self.h5filePtr.list_nodes(group):	
				yield table	

class totalData(tables.IsDescription):
	year	     = tables.UInt16Col()
	match_count  = tables.UInt64Col()
	volume_count = tables.UInt64Col()
	page_count 	 = tables.UInt32Col() 

class TotalCountsDB(H5File):
	def setTableProperties(self, rowPtr, data):
		rowPtr['year']		  =	data[0]		
		rowPtr['match_count'] =	data[1]
		rowPtr['page_count']  =	data[2]
		rowPtr['volume_count']= data[3]
		rowPtr.append()

	def read(self):
		self.openFile('r')
		condition = '(((year)>=1650) & ((year)<2003))'
		for table in self.tablesGenerator():		
			results = np.array([[(row["year"]), (row["match_count"]), (row["volume_count"])] for row in table.where(condition)])
		self.closeFile()
		return results

	def totalGrams(self):
		return np.sum(self.read()[:,1])

	def createGroup(self):
		return self.h5filePtr.create_group("/", TotalCounts, 'Total counts for all data.')		

	def getData(self, TotalFileObj):
		regExYearRecords = RegEx.RegEx("[^\t|,]+", TotalFileObj.readContents())
		return self.convertToMatrix(regExYearRecords.getResults())

	def convertToMatrix(self, results):
		totalCounts = np.array([[0 for x in range(4)] for y in range(425)])
		j,i=0,0
		for x in range(1700):
			totalCounts[i][j] = results[x]
			j+=1
			if j == 4:
				j=0
				i+=1
		return totalCounts

	def createTable(self):
		self.openFile('a')
		filters = tables.Filters(complevel=9, complib="blosc", fletcher32=False)	
		return self.h5filePtr.create_table("/", "TotalCountsTable", totalData, "TotalCountsTable", filters=filters)	

	def write(self, TotalFileObj, table):
		data = self.getData(TotalFileObj)
		for i in range(len(data)):
			self.setTableProperties(table.row, data[i])





