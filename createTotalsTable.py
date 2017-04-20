import File

DB_File = File.TotalCountsDB('/Users/Liam/Desktop/1/Totals.hg')		# set the File for the database

#DB_File.openFile('w', title='Totals')
#DB_File.closeFile()
print(DB_File.read())
#table = DB_File.createTable()
#DB_File.write(File.File("/Users/Liam/Dropbox/College/Project/PythonCode/RefactoredCode/googlebooks-eng-all-totalcounts-20120701.txt"), table)
