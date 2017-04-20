from scipy.signal import butter, lfilter
import numpy as np

class LP_Filter():
	def __init__(self, preFilteredValues):
		self.preFilteredValues = preFilteredValues
		self.period = 365*24*60*60
		self.cutoffFreq = self.setCutoffFreq()
		self.FilteredValues = self.Filter()

	def setCutoffFreq(self):
		cutoffHarmonic = 1
		VALUES = np.fft.fft(self.preFilteredValues[-50:])
		freqs = np.fft.fftfreq(len(VALUES), self.period)	
		return freqs[cutoffHarmonic]

	def Filter(self):
		nyq = 0.5/self.period
		normalCutoff = self.cutoffFreq/nyq
		b, a = butter(1, normalCutoff, btype = 'low', analog=False)
		return lfilter(b, a, self.preFilteredValues)

	def getFilteredValues(self):
		return self.FilteredValues