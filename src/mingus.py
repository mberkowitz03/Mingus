from posixpath import basename
import music21 as m21
import chord, note as nt
from interface import clear, print, outputFilePath

class Runner:
	CHORD_WEIGHT = [1.2,0.8,1]
	DOWNBEAT_WEIGHT = 0.2
	DISTANCE_WEIGHT = 0
	OFF_KEY_WEIGHT = 0.9 #Higher prefers out of key chords
	JAZZINESS_FACTOR = 1

	def calculateFit(self, measure, chord):
		fit = 0
		for note in measure:
			if note.note in chord.notes:
				fit += (note.beatLength * self.LENGTH_WEIGHT) * (self.CHORD_WEIGHT[chord.notes.index(note.note)] + (int(note.isDownbeat) * self.DOWNBEAT_WEIGHT))
		if len(self.finalChords) != 0:
			#Fitting to be relatively close to the past note in the circle of fifths.
			#MAYBE ALTER THIS TO BE A THEORY BASED APPROACH (I.E. 4 - 5 - 1 AND THINGS LIKE THAT)
			prevChordRootIndex = nt.CIRCLE_OF_FIFTHS.index(self.finalChords[-1].notes[0])
			currChordRootIndex = nt.CIRCLE_OF_FIFTHS.index(chord.notes[0])
			largerIndex = max(prevChordRootIndex, currChordRootIndex)
			smallerIndex = min(prevChordRootIndex, currChordRootIndex)

			#min is needed to find the roll-around distance. (i.e. for [1, 2, 3], 1 and 3 have a dist 1)
			dist = min(largerIndex - smallerIndex, len(nt.CIRCLE_OF_FIFTHS) - largerIndex + smallerIndex)
			#Make algorithm strongly avoid same chords if jazziness is high.
			dist = (dist + 12 - self.JAZZINESS_FACTOR) % 12
			if dist == 0:
				dist = 1
			fit -= dist * self.DISTANCE_WEIGHT
		if chord in self.nonKeyChords: 
			fit *= self.OFF_KEY_WEIGHT
		return fit

	def processMeasure(self, currMeasure):
		#PROCESSING HERE
		fitDict = {}
		for chord in self.keyChords.union(self.nonKeyChords):
			fitDict[chord] = self.calculateFit(currMeasure, chord)
		return keyWithMaxFit(fitDict)
	
	#All Files are converted to musicxml
	def processMusicXML(self):
		self.finalChords = []

		# Get time divisions
		timeSignature = self.m21File.getTimeSignatures()[0].numerator
		self.LENGTH_WEIGHT = 1.0 / timeSignature

		# Finds key name by number of sharps in the scale
		keyScale = nt.getScale(nt.CIRCLE_OF_FIFTHS[self.m21File.parts[0].measure(1).keySignature.sharps])

		# Creates list of chords that are in the scale of the key signature
		self.keyChords = chord.getChords(keyScale)
		# gotta be a better way to do this
		self.nonKeyChords = {c for c in chord.getChords(nt.CHROMATIC_SCALE) if c not in self.keyChords}

		m21FileMeasures = self.m21File.parts[0].getElementsByClass(m21.stream.Measure)

		for measure in m21FileMeasures.getElementsByClass('Measure'):
			currMeasure = []
			downBeat = True

			for note in measure.flatten().notes: #Check to make sure different voices are getting a new downbeat
				if note.isChord:
					for chordNote in note:
						currMeasure.append(nt.Note(chordNote.pitch.midi, chordNote.quarterLength, downBeat))
				else:
					currMeasure.append(nt.Note(note.pitch.midi, note.quarterLength, downBeat))
				downBeat = False

			measureChord = self.processMeasure(currMeasure)
			self.finalChords.append(measureChord)
			#add harmony to measure with resultChord
			measure.insert(m21.harmony.ChordSymbol(str(measureChord)))
			

		return self.finalChords

	def printResults(self, finalChords):
		print("Final chords:")
		measureCount = 1
		for chord in finalChords:
			print("Measure", str(measureCount), str(chord))
			measureCount += 1

	def run(self, filename):
		try:
			self.m21File = m21.converter.parse(filename)
		except:
			clear()
			print("Couldn't parse file - try a different format")
			return
		finalChords = self.processMusicXML()
		self.printResults(finalChords)
		print("Inserting chords into original file...")
		format = filename.split(".")[-1]
		print("Saving file to", outputFilePath(filename))
		self.m21File.write(format, outputFilePath(filename))
		print("Done!")



def keyWithMaxFit(fitDict):
	#by some unfathomable nightmare, this is the fastest way to get the key of the max value in a dictionary
	vals=list(fitDict.values())
	keys=list(fitDict.keys())
	print("performed fit calculation")
	return keys[vals.index(max(vals))]