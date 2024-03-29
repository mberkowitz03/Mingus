import note as nt

class Chord:
	def __init__(self, root, isMajor):
		rootIndex = nt.CHROMATIC_SCALE.index(root)
		self.notes = (root, nt.CHROMATIC_SCALE[(rootIndex + 3 + isMajor) % 12], root + 7)
	
	def __init__(self, root, third, fifth):
		self.notes = (root, third, fifth)

	def __hash__(self):
		return hash((self.notes))

	def __eq__(self, other):
		return self.notes == other.notes

	def __repr__(self):
		return self.notes[0] + self.getQuality()

	def getQuality(self):
		if isMajorThird(self.notes[1], self.notes[2]):
			if isMajorThird(self.notes[0], self.notes[1]):
				return "aug"
			else:
				return "m"
		elif not isMajorThird(self.notes[0], self.notes[1]): 
			return "dim"
		else:
			return ""

def isMajorThird(root, third):
	return (nt.CHROMATIC_SCALE.index(root) + 4) % 12 == nt.CHROMATIC_SCALE.index(third)

def getChords(scale):
	# Gives all possible triads formed from a scale
	return {Chord(scale[note], scale[(note + 2) % len(scale)], scale[(note + 4) % len(scale)]) for note in range(len(scale))}