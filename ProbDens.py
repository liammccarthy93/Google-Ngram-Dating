import matplotlib.pyplot as plt
import pyqtgraph as pg
import numpy as np
from scipy.optimize import curve_fit
import scipy.stats, sys, scipy.ndimage.measurements
import matplotlib.cm as cm
import sys, copy
import warnings
import scipy.stats as st
import  math

class ProbabilityDensity:
	def __init__(self):
		self.ax, self.axes, self.fig = self.createFigure()					# create the axes object on which the probability density will be plotted
		self.ProbabilityDensity = self.initialise()

	def createFigure(self):
		#max_line = 0.05
		fig = plt.figure()
		axes = fig.gca()
		#axes.set_ylim([0.39,0.4])
		axes.set_xlim(1800,2001)
		ax = fig.add_subplot(111)
		ax.set_xlabel('Year')
		ax.set_ylabel('P(Year|words)')		
		return  ax, axes, ax.get_figure()

	def Smooth(self, window_size=10):
		self.ProbabilityDensity = np.convolve(self.ProbabilityDensity, np.ones((window_size,))/window_size)[(window_size-1):]
		return self.ProbabilityDensity

	def initialise(self):
		self.ProbabilityDensity = np.array([1.0/201.0 for x in range(201)])
		self.closePlot()
		self.axes = self.createFigure()
		return self.ProbabilityDensity

	def ML(self, NGramObj):
		return self.Normalise(np.multiply(NGramObj.getValues(),self.ProbabilityDensity))

	def summation(self, NGramObj):
		self.ProbabilityDensity = np.add(self.Normalise(NGramObj.getValues()),self.ProbabilityDensity)
		return (np.add((NGramObj.getValues()),self.ProbabilityDensity))

	def getProbabilityDensity(self):
		return self.ProbabilityDensity

	def getMaxProbValue(self):
		return np.amax(self.ProbabilityDensity)

	def getMaxYear(self):
		return np.argmax(self.ProbabilityDensity)+1800

	def getValues(self):
		return self.ProbabilityDensity

	def uncertainty(self, k=3):	

		cdf = self.cdf()
		confidence_level = 0.9
		lower, upper = self.find_nearest(cdf, 0.05), self.find_nearest(cdf, 0.95)
		region = 1800+np.array(range(np.where(cdf==lower)[0][0], np.where(cdf==upper)[0][0]))
		return region

	def find_nearest(self,array,value):   # http://stackoverflow.com/questions/2566412/find-nearest-value-in-numpy-array
	    idx = np.searchsorted(array, value, side="left")
	    if idx > 0 and (idx == len(array) or math.fabs(value - array[idx-1]) < math.fabs(value - array[idx])):
	        return array[idx-1]
	    else:
	        return array[idx]	


	def getMostLikelyYear(self):
		cdf = self.cdf()
		center = self.find_nearest(cdf, 0.5)
		value = 1800+np.where(cdf==center)[0][0]
		return value#1800+np.round(scipy.ndimage.measurements.center_of_mass(probDensWithoutSmallValues, labels=np.array(range(201)))[0])

	def closestYear(self, num):
		diff = 100			# initialise it with a big number
		closestIdx = 0
		i = -1
		for n in self.ProbabilityDensity:
			i+=1
			diffTemp = abs(n-num)
			if diffTemp < diff:
				diff = diffTemp 
				closestIdx = i
		return closestIdx

	def Bayes(self, NGramObj):
		#self.ProbabilityDensity = 
		return self.Normalise((np.true_divide(np.multiply(NGramObj.getValues(),self.ProbabilityDensity),(np.sum(NGramObj.getValues())))))


	def Normalise(self, posterior):
		self.ProbabilityDensity = np.true_divide(posterior,(np.sum(posterior)))
		return self.ProbabilityDensity

	def kurtosis(self):
		return scipy.stats.kurtosis(np.round(self.ProbabilityDensity, 6), fisher=False)	# rounding avoids scenarios where floating point differences in what should be a uniform distribution cause very high kurtosis

	def plot(self, plotname, x=np.array(range(1800, 2001)), y=None):
		if y is None:
			y=self.ProbabilityDensity
		lines = self.ax.step(x, y, 'b')
		self.fig.savefig(plotname.replace(' ', '_'))
		self.ax.lines.remove(lines[0])

	def closePlot(self):
		plt.close('all')
		
	def cdf(self):
		cdf = np.cumsum(self.Normalise(self.ProbabilityDensity))
		return cdf

class ProbabilityDensityList():
	def __init__(self):
		self.probDensList = np.array([])

	def append(self, obj):
		self.probDensList = np.append(self.probDensList, copy.copy(obj))
		return self.probDensList

	def getList(self):
		return self.probDensList

	def getElementValues(self, idx):
		return self.probDensList[idx].getProbabilityDensity()

	def plot(self, plotname):
		bounds = np.array([[0 for x in range(2)] for y in range(len(self.probDensList))])
		i=0
		plt.close()
		for pd in self.probDensList:
			bounds[i,:] = [pd.uncertainty()[0], pd.uncertainty()[-1]]
			i+=1
		
		plt.plot(range(i), bounds[:,0], 'r')
		plt.plot(range(i), bounds[:,1], 'r')
		plt.yticks([1800, 1850, 1950, 2000])	
		x, y = np.meshgrid(range(len(self.probDensList)), range(1800,2001))

		axes = plt.gca()
		axes.set_xlabel("Ngrams considered", fontsize=12)
		axes.set_ylabel('Year', fontsize=12)
		axes.tick_params(labelsize=12)

		fig0 = plt.pcolormesh(x, y, self.getHeatmapValues(), cmap=cm.get_cmap('binary'))
		plt.savefig(plotname, bbox_inches='tight')

	def getHeatmapValues(self):
		values = np.array([[0.0 for x in range(len(self.probDensList))] for y in range(1800,2001)])
		for i in range(len(self.probDensList)):
			values[:,i] = self.getElementValues(i)
		#print(values)
		return values

	def Normalise(self,data):
		return data/(np.sum(data))

	def Bayes(self, indexes):
		B = np.array([1.0/201.0 for x in range(201)])
		print(indexes)
		print(self.getList()[indexes])
		k=0.25
		for pDens in self.getList()[indexes]:
			values = pDens.getValues()
			dist = np.mean(values) - values		# get distance from mean. Negative if value is above mean, and vica versa

			values += k*dist 															# bring value closer to mean.
			B = self.Normalise((np.true_divide(np.multiply(values,B),(np.sum(values)))))

		return [B, self.uncertainty(B)]

	def uncertainty(self, B):	

		cdf = np.cumsum(self.Normalise(B))
		confidence_level = 0.9
		lower, upper = self.find_nearest(cdf, 0.05), self.find_nearest(cdf, 0.95)
		region = 1800+np.array(range(np.where(cdf==lower)[0][0], np.where(cdf==upper)[0][0]))
		return region

	def find_nearest(self,array,value):   # http://stackoverflow.com/questions/2566412/find-nearest-value-in-numpy-array
	    idx = np.searchsorted(array, value, side="left")
	    if idx > 0 and (idx == len(array) or math.fabs(value - array[idx-1]) < math.fabs(value - array[idx])):
	        return array[idx-1]
	    else:
	        return array[idx]


