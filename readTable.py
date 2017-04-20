import tables
import numpy as np 
import File

file = File.H5File('/Users/Liam/Desktop/1/1Grams.hg')

oneGram = "Liam"

results = file.read(oneGram)
print((results))
#file.openFile('a')
#file.index()