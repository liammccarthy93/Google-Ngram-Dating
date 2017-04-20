
import numpy as np
import matplotlib as mpl
import matplotlib.pyplot as plt


class Inferences:
	# Constructor
	def __init__(self, correctYears):
		self.correctYears = correctYears
		self.estimatedYears = self.correctYears.fromkeys([key for key in self.correctYears])
		self.withinBounds = 0
		self.stress_scores = []
		self.green = [[]]
		self.orange = [[]]
		self.red = [[]]
		self.boundSizeSum = 0
		#self.diff = pd.DataFrame(index = [x for x in range(200)])#,columns=[key for key in self.correctYears])
		#self.occurances = pd.DataFrame(index = [x for x in range(200)])

	def setEstimates(self, estimate, key):
		self.estimatedYears[key] = estimate[0]
		self.green.append(estimate[1])
		self.stress_scores.append(estimate[-2])
		if self.correctYears[key] in self.green[-1]:
			self.withinBounds+=1

		#toConcatOcc = pd.DataFrame({key:np.array(estimate[-2])})
		#self.occurances = pd.concat([self.occurances, toConcat], ignore_index=True, axis=1).dropna()
		#plt.close()
		#plt.plot(self.occurances)
		
		print('Number of estimates within bounds is '+str(self.withinBounds) + ' out of ' + str(len(self.green)-1)+'; '+str(100*self.withinBounds/(len(self.green)-1))[0:4]+'%.')
		self.boundSizeSum += self.green[-1][-1] - self.green[-1][0] 
		print('Average bound size is ', self.boundSizeSum/(len(self.green)-1))
		return self.getEstimates()

	def getEstimate(self, key):
		return self.estimatedYears[key]

	def getEstimates(self):
		return self.estimatedYears

	def getCorrectYears(self):
		return self.correctYears

	def print(self):
		return print(self.getEstimates())

	def plot(self):
		plt.close()
		fig = plt.figure(figsize=(50,50))
		size=15
		mpl.rcParams['xtick.labelsize'] = size-6
		mpl.rcParams['ytick.labelsize'] = size-6	
		fig0 = plt.figure()
		fig = fig0.add_subplot(111)
		colours = ['-g', 'b.', 'r.']

		minYear, maxYear = 1795, 2005
		plt.plot(np.array(range(minYear,2000)), np.array(range(minYear,2000)), '#dcdcdc', lw=1)

		j=1
		for key in self.correctYears:
			if self.estimatedYears[key] is None:
				continue
			i=0
			for points_set in [self.green[j]]:#, self.orange[j], self.red[j]]:
				if self.correctYears[key] in range(points_set[0], points_set[-1]+1):
					plt.plot(np.array([key for x in range(2) if key is not None]), [points_set[0], points_set[-1]], '-g', markersize=1, lw=1, alpha=0.6)
				else:
					plt.plot(np.array([key for x in range(2) if key is not None]), [points_set[0], points_set[-1]], '-r', markersize=1, lw=1, alpha=0.6)
				i+=1
			j+=1
		plt.plot(np.array(list(self.correctYears.values())), np.array(list(self.estimatedYears.values())), 'k.', markersize=1, alpha=0.8)


		ax = plt.gca()
		ax.set_frame_on(False)
		ax.axes.get_xaxis().tick_bottom()
		ax.axes.get_yaxis().tick_left()
		plt.plot([minYear, minYear], [minYear, 2000], '-k', lw=1)			# put back in the desired axes
		plt.plot([minYear, 2000], [minYear, minYear], '-k', lw=2)	
		ax.set_xlim([minYear,maxYear])
		ax.set_ylim([minYear,maxYear])
		plt.gca().set_aspect('equal', adjustable='box')	
		plt.xlabel('Correct Year', fontsize=size)
		plt.ylabel('Estimated Year', fontsize=size)
		plt.savefig('Plots/ActualVsEstimate.pdf', format='pdf', bbox_inches='tight')
		plt.close()
		"""
		plt.figure()
		ax = plt.gca()
		ax.set_ylim([0,np.max(self.stress_scores)*1.3])		
		ax.set_xlim([0,len(self.stress_scores)+1])	
		plt.xlabel('Text Number', fontsize=size-3)
		plt.ylabel('Stress Score', fontsize=size-3)
		plt.scatter(np.array(range(len(self.stress_scores)))+1, np.array(self.stress_scores))
		plt.plot([0, len(self.stress_scores)+1],[np.mean(self.stress_scores), np.mean(self.stress_scores)], '#dcdcdc', lw=1, label='Mean Stress Score')
		plt.legend()
		plt.savefig('Plots/stress.pdf', format='pdf')
		plt.close()
		"""