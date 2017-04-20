from File import Directory
from main import runner
import numpy as np
import Inferences, sys, math

testDir = Directory('TestFiles/')															# set the directory where the text files are
plotsDir = Directory('Plots')																# set the directory where plots are stored
plotsDir.clear()																			# clear out plots from previous runs
correctYears = {'1802':1802,'1803':1803, '1804':1804,'1806':1806, '1807':1807, 
               '1810':1810, '1813':1813, '1815':1815, '1816': 1816, '1817':1817, '1818':1818, '1819':1819,
                '1820': 1820, '1822':1822, '1823':1823, '1825':1825, '1827': 1827, 
               '1830':1830,
               '1831':1831, '1832':1832, '1837':1837, '1838':1838,
               '1842':1842, '1843':1843,
				'1844':1844, '1845':1845, '1847':1847,
               '1850':1850, '1851': 1851, '1854':1854, '1859':1859, '1860':1860, '1861':1861, '1864':1864, '1865':1865, '1867':1867,
				'1869':1869, '1870':1870, '1872':1872, '1877':1877,
				'1882':1882, '1884':1884, '1887':1887, '1890':1890, '1892':1892, '1895':1895, '1898':1898,
				'1899':1899, '1900':1900, '1902':1902, '1909':1909, '1910':1910, '1911':1911, '1912':1912, '1915':1915, '1916':1916, '1917':1917, '1920':1920, '1921':1921, '1922':1922,
				'1925':1925,  '1928':1928, '1929':1929, '1930':1930, '1934':1934,
				'1935':1935, '1936':1936, '1937':1937,'1939':1939, '1940':1940, '1942':1942,  '1945':1945, '1946':1946, '1949':1949,
				 '1950':1950, '1952':1952, '1953':1953, '1954':1954,
				'1955':1955, '1957':1957, '1958':1958, '1960':1960, '1961':1961,  '1962':1962,'1965':1965, '1967':1967, '1969':1969, '1971':1971, '1977':1977, 
				'1979':1979, '1982':1982, '1984':1984, '1985':1985, '1986':1986, '1987':1987, '1989':1989,
				'1995':1995, '1996':1996,
				'1997':1997}														# set correct years of the different texts
inferences = Inferences.Inferences(correctYears)											# create inferences object					

for testFile in testDir.getFiles():															# for each test file	
	if '.txt' not in testFile:
		continue																						#	set the estimates attribute in the inferences object for the inference returned from each of the runs of the runner function
	inferences.setEstimates(
							runner(testDir.getDirectory()+testFile, inferences.getCorrectYears()[testFile.replace('.txt', '')], N=[1]), 
							testFile.replace('.txt', '')
							)
	print("Current list of estimates:")														#	print information related to the program progress
	inferences.plot()
	print('===================================================\n\n\n')

diff, diff_squared,num = 0, 0, 0												# initialise performance measures
for key in correctYears:												# for each text under test
	if inferences.getEstimate(key) is None:
		continue
	diff += abs(correctYears[key] - inferences.getEstimate(key))		# 	calculate difference between estimated year and actual year
	diff_squared += diff*diff 											# 	get square of the difference
	num+=1

MAE = (diff)/num											# get mean absolute error
RMSE = math.sqrt((diff_squared)/num)						# get root mean squared error
print("MAE =  " + str(MAE) + "\nRMSE = " + str(RMSE)[:5])				# print the measures
inferences.plot()														# plot actual years vs. estimated years