from posixpath import basename
import music21 as m21
import PySimpleGUI as psg
import chord, note as nt
import os
global CHROMATIC_SCALE, CIRCLE_OF_FIFTHS
CHROMATIC_SCALE = ['C', 'C#', 'D', 'D#', 'E', 'F', 'F#', 'G', 'G#', 'A', 'A#', 'B']
CIRCLE_OF_FIFTHS = ['C', 'G', 'D', 'A', 'E', 'B', 'F#', 'C#', 'G#', 'D#', 'A#', 'F']

class MingusRunner:
	CHORD_WEIGHT = [1.2,0.8,1]
	DOWNBEAT_WEIGHT = 0.2
	DISTANCE_WEIGHT = 0
	OFF_KEY_WEIGHT = 0.9 #Higher prefers out of key chords
	JAZZINESS_FACTOR = 1
	m21File = None

	def processMeasure(self, currMeasure, finalChords):
		#PROCESSING HERE
		fitDict = {}
		for chord in keyChords + nonKeyChords:
			fit = 0
			for note in currMeasure:
				if note.note in chord.notes:
					fit += (note.beatLength * LENGTH_WEIGHT) * (self.CHORD_WEIGHT[chord.notes.index(note.note)] + (int(note.isDownbeat) * self.DOWNBEAT_WEIGHT))
			if len(finalChords) != 0:
				#Fitting to be relatively close to the past note in the circle of fifths.
				#MAYBE ALTER THIS TO BE A THEORY BASED APPROACH (I.E. 4 - 5 - 1 AND THINGS LIKE THAT)
				prevChordRootIndex = CIRCLE_OF_FIFTHS.index(finalChords[-1].notes[0])
				currChordRootIndex = CIRCLE_OF_FIFTHS.index(chord.notes[0])
				largerIndex = max(prevChordRootIndex, currChordRootIndex)
				smallerIndex = min(prevChordRootIndex, currChordRootIndex)

				#min is needed to find the roll-around distance. (i.e. for [1, 2, 3], 1 and 3 have a dist 1)
				dist = min(largerIndex - smallerIndex, len(CIRCLE_OF_FIFTHS) - largerIndex + smallerIndex)
				#Make algorithm strongly avoid same chords if jazziness is high.
				dist = (dist + 12 - self.JAZZINESS_FACTOR) % 12
				if dist == 0:
					dist = 1
				fit -= dist * self.DISTANCE_WEIGHT
			if chord in nonKeyChords: 
				fit *= self.OFF_KEY_WEIGHT
			fitDict[chord] = fit
		return keyWithMaxFit(fitDict)
	
	#All Files are converted to musicxml
	def processMusicXML(self):
		finalChords = []
		currMeasure = []

		# Get time divisions
		timeSignature = self.m21File.getTimeSignatures()[0].numerator
		global LENGTH_WEIGHT
		LENGTH_WEIGHT = 1.0 / timeSignature

		# Finds key name by number of sharps in the scale
		keyScale = getScale(CIRCLE_OF_FIFTHS[self.m21File.parts[0].measure(1).keySignature.sharps])

		# Creates list of chords that are in the scale of the key signature
		global keyChords 
		keyChords = getChords(keyScale)
		global nonKeyChords
		nonKeyChords = []
		for note in CHROMATIC_SCALE:
			for chord in getChords(getScale(note)):
				if str(chord) not in [str(x) for x in keyChords] and str(chord) not in [str(x) for x in nonKeyChords]:
					nonKeyChords.append(chord)
		
		downBeat = True
		#for first note of each voice in each measure, add to currMeasure with downbeat true (check for chord)
		m21FileMeasures = self.m21File.parts[0].getElementsByClass(m21.stream.Measure)
		for measure in m21FileMeasures.getElementsByClass('Measure'):
			for note in measure.flatten().notes: #Check to make sure different voices are getting a new downbeat
				if note.isChord:
					for chordNote in note:
						currMeasure.append(nt.Note(chordNote.pitch.midi, chordNote.quarterLength, downBeat))
				else:
					currMeasure.append(nt.Note(note.pitch.midi, note.quarterLength, downBeat))
				downBeat = False
			downBeat = True
			resultChord = self.processMeasure(currMeasure, finalChords)
			finalChords.append(resultChord)
			#add harmony to measure with resultChord
			measure.insert(m21.harmony.ChordSymbol(str(resultChord)))
			currMeasure = []

		return finalChords

	def printResults(self, finalChords):
		print("Final chords:")
		measureCount = 1
		for chord in finalChords:
			print("Measure", str(measureCount), str(chord))
			measureCount += 1

	def runMingus(self, filename):
		self.m21File = m21.converter.parse(filename)
		finalChords = self.processMusicXML()
		self.printResults(finalChords)
		print("Inserting chords into original file...")
		print("Saving file...")
		splitFile = filename.split(".")
		self.m21File.write(splitFile[1], splitFile[0] + '_output.' + splitFile[1])
		print("Done!")


def getChords(scale):
	chords = []
	for note in range(len(scale)):
		chords.append(chord.Chord(scale[note], scale[(note + 2) % len(scale)], scale[(note + 4) % len(scale)]))
	return chords

def getScale(key):
	majorSteps = [2, 2, 1, 2, 2, 2, 1]
	minorSteps = [2, 1, 2, 2, 1, 2, 2]
	scale = []
	if 'b' in key:
		key = key.replace('b', '#')
		key = key.replace(key[0], CHROMATIC_SCALE[((CHROMATIC_SCALE.index(key[0]) + 10) % 12)])
	if '#' in key:
		curr = CHROMATIC_SCALE.index(key[0:2])
	else:
		curr = CHROMATIC_SCALE.index(key[0])

	if key[-1] == 'm':
		for i in range(7):
			scale.append(CHROMATIC_SCALE[curr % 12])
			curr += minorSteps[i]
	else:
		for i in range(7):
			scale.append(CHROMATIC_SCALE[curr % 12])
			curr += majorSteps[i]

	return scale

def keyWithMaxFit(fitDict):
	vals=list(fitDict.values())
	keys=list(fitDict.keys())
	return keys[vals.index(max(vals))]

def updateWindow(*args):
	string = window["OUTPUT"].get()
	for arg in args:
		string += str(arg) + " "
	string += "\n\n"
	window["OUTPUT"].update(string)

def main():
	global print
	print = updateWindow
	mingusRunner = MingusRunner()
	psg.theme("DarkBrown")

	layout = [[psg.Text("Enter the file you'd like to harmonize: ")],
			[psg.Input(key="-I-", do_not_clear=False), psg.FileBrowse(key="-IN-")], 
			[psg.Button("Submit")], 
			[psg.Text(key="OUTPUT")]]
	global window
	window = psg.Window("Mingus", layout, size=(600, 400), grab_anywhere=True, resizable=True)

	psg.set_options(element_padding=(10,10))

	while True:
		event, values = window.read()
		if event == psg.WIN_CLOSED:
			break
		elif event == "Submit":
			filename = values["-IN-"]
			print("\nProcessing...\n")
			mingusRunner.runMingus(filename)
	
	window.close()

if __name__ == '__main__':
	main()     