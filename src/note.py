CHROMATIC_SCALE = ['C', 'C#', 'D', 'D#', 'E', 'F', 'F#', 'G', 'G#', 'A', 'A#', 'B']
CIRCLE_OF_FIFTHS = ['C', 'G', 'D', 'A', 'E', 'B', 'F#', 'C#', 'G#', 'D#', 'A#', 'F']

class Note:
	note = ""
	beatLength = 0
	isDownbeat = False

	def __init__(self, note, beatLength, isDownbeat):
		self.note = CHROMATIC_SCALE[note % 12] #convert note number to note name
		self.beatLength = beatLength
		self.isDownbeat = isDownbeat

	def __repr__(self):
		return self.note

def getScale(key):
	majorSteps = [2, 2, 1, 2, 2, 2, 1]
	minorSteps = [2, 1, 2, 2, 1, 2, 2]
	if 'b' in key:
		key = key.replace('b', '#')
		key = key.replace(key[0], CHROMATIC_SCALE[((CHROMATIC_SCALE.index(key[0]) + 10) % 12)])
	if '#' in key:
		curr = CHROMATIC_SCALE.index(key[0:2])
	else:
		curr = CHROMATIC_SCALE.index(key[0])
	scale = []
	if key[-1] == 'm':
		for i in range(7):
			scale.append(CHROMATIC_SCALE[curr % 12])
			curr += minorSteps[i]
	else:
		for i in range(7):
			scale.append(CHROMATIC_SCALE[curr % 12])
			curr += majorSteps[i]

	return scale