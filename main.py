from mido import MidiFile

global MARGIN_OF_ERROR, LENGTH_WEIGHT, CHORD_WEIGHT, DOWNBEAT_WEIGHT, DISTANCE_WEIGHT, JAZZINESS_FACTOR, CHROMATIC_SCALE, CIRCLE_OF_FIFTHS
MARGIN_OF_ERROR = 0.005
CHORD_WEIGHT = [1.2,0.8,1]
LENGTH_WEIGHT = 1
DOWNBEAT_WEIGHT = 0.2
DISTANCE_WEIGHT = 0.1
JAZZINESS_FACTOR = 0
CHROMATIC_SCALE = ['C', 'C#', 'D', 'D#', 'E', 'F', 'F#', 'G', 'G#', 'A', 'A#', 'B']
CIRCLE_OF_FIFTHS = ['C', 'G', 'D', 'A', 'E', 'B', 'F#', 'C#', 'G#', 'D#', 'A#', 'F']

class Chord:
    notes = []

    def __init__(self, root, isMajor):
        rootIndex = CHROMATIC_SCALE.index(root)
        self.notes = [root, CHROMATIC_SCALE[(rootIndex + 3 + isMajor) % 12], root + 7]
    
    def __init__(self, root, third, fifth):
        self.notes = [root, third, fifth]

    def __repr__(self):
        returnStr = self.notes[0]
        if isMajorThird(self.notes[1], self.notes[2]):
            if isMajorThird(self.notes[0], self.notes[1]):
                returnStr += "aug"
            else:
                returnStr += "m"
        elif not isMajorThird(self.notes[0], self.notes[1]): 
            returnStr += "dim"
        
        return returnStr

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

