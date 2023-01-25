CHROMATIC_SCALE = ['C', 'C#', 'D', 'D#', 'E', 'F', 'F#', 'G', 'G#', 'A', 'A#', 'B']

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