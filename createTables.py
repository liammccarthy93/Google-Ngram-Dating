import File, time

#DB_File = File.H5File('C:\Python27\Scripts\downloads\google_ngrams\\2\\2Grams2.hg')		# set the File for the database
#directory = File.Directory('C:\Python27\Scripts\downloads\google_ngrams\\2')					# set the directory in which the files are
DB_File = File.H5File('/Users/Liam/Desktop/2GramsTest2.hg')		# set the File for the database
directory = File.Directory('/Volumes/WP/2/')					# set the directory in which the files are

DB_File.openFile('w', title="2Grams")						# open file - overwrites previous enteries if in 'w' mode
DB_File.closeFile()

for file in directory.getFiles():							# iterate through every file in the directory
	if 'gz' not in file:									# skip over files which aren't .gz files as these are not of interest
		continue
	print("Writting data for file " + str(file))
	fileOBJ = File.GZ_File(directory.getDirectory() + "/" + file)	# create file object for compressed text file
	table = DB_File.createTable(file[-5:-3])						# create table in DB for this set of grams
	start_time = time.time()										# record time before writting beginss
	row_counter=0												
	for record in fileOBJ.Generator():								# for each row in the file (note that there are criterea which the row must meet)
		if row_counter%100000 == 0:									# 	periodically flush changes to disk to avoid buffers filling
			print("Processed " + str(row_counter) + " rows. On word \"" + record[0]+"\" for year "+ str(record[1]) + ".")
			DB_File.writeToDisk(table)
		try:														# 	add the record to the table
			DB_File.setTableProperties(table.row, record[0], record[1], record[2], record[3])
		except TypeError as error:									# 	catch any errors which are caused by adding the record
			print("Failed to input on row " + str(row_counter))
			print(error)			
			print("Record is " + str(record))
		row_counter+=1
	
	print("Processing table took " + str(time.time()-start_time) + " seconds.")
	DB_File.writeToDisk(table)										# flush changes
	DB_File.closeFile()							