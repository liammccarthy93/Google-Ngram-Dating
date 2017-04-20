import numpy as np
from sklearn.cluster import DBSCAN
import matplotlib.pyplot as plt
import warnings, sys
warnings.filterwarnings("error")		# allows warnings to be caught as errors

class Cluster:
	def __init__(self, points):
		self.points = np.array(points)
		self.samples_threshold = 5#int(0.4*len(points))		# minimum number of points required for a cluster
		self.eps = 7		
		self.model = self.create(self.samples_threshold)	# create object for the cluster

	def create(self, samples_threshold):

		return self.makeCluster(self.eps, samples_threshold)# make the cluster and return the object

	def makeCluster(self, eps, samples_threshold):
		try:	# call constructor from sklearn.cluster library to create cluster object
			return DBSCAN(eps=eps, min_samples=samples_threshold).fit(self.points.reshape(-1,1))
		except:
			return None

	def getNumPoints(self):
		return len(self.points)

	def findAggregateOfStrongestCluster(self, pDensList):
		end, step = 1, -1
		for threshold in range(len(self.points), end, step):
			cluster = self.makeCluster(self.eps, threshold)
			clusterPoints = self.getModelComponents(model=cluster)
			if len(clusterPoints) != 0 and clusterPoints is not None:
				print("Found cluster of " + str(threshold) + " points.")
				return self.getAggregateYear(pDensList, components=clusterPoints, labels=self.getLabels(model=cluster))
		return None


	def getLabels(self, model=None):
		if model is None:
			model = self.model
		return model.labels_

	def getModelComponents(self, model=None):
		if model is None:
			model=self.model.components_
		return model.components_

	def getAggregateYear(self, pDensList, components = None, labels=None):
		if components is None:
			components = self.model.components_
		if labels is None:
			labels = self.model.labels_
		try:
			print(labels)

			if(len(np.where(labels>=0)[0]))<1:
				return None

			return [1800+np.argmax(pDensList.Bayes(np.where(labels>=0)[0])[0]), pDensList.Bayes(np.where(labels>=0)[0])[1]]
		except RuntimeWarning:
			return None

	def plot(self, plotname, correctYear, points = None, model = None):
		if points is None:
			points = self.points
		if model is None:
			model = self.model
		markers = self.setMarkers(points, model)
		plt.close()
		plt.figure()
		for x in range(len(points)):
			plt.plot(points[x], np.array(x+1), markers[x])
		axes = plt.gca()
		axes.set_xlim([1800,2000])	
		lim=15
		if x+3 < lim:
			axes.set_ylim([0,lim])
		else:
			axes.set_ylim([0,x+3])
		plt.xlabel('Year')
		plt.ylabel('Cluster Number')
		axes.set_xticks([1800, correctYear, 2000])	
		plt.savefig(plotname+str(x) + '.png')
		plt.close()		

	def setMarkers(self, points, model):
		noiseMarker = 'r.'
		pointMarker = 'b.'
		if len(model.components_) is 0:
			markers = [noiseMarker for x in range(len(points))]
		else:
			markers = []
			for x in range(len(points)):
				if model.labels_[x] == -1:
					markers.append(noiseMarker)
				else:
					markers.append(pointMarker)
		return markers