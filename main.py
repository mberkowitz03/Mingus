import music21 as m21
global MARGIN_OF_ERROR, LENGTH_WEIGHT, CHORD_WEIGHT, DOWNBEAT_WEIGHT, DISTANCE_WEIGHT, JAZZINESS_FACTOR, CHROMATIC_SCALE, CIRCLE_OF_FIFTHS
MARGIN_OF_ERROR = 0.005
CHORD_WEIGHT = [1.2,0.8,1]
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

def isMajorThird(root, third):
    return (CHROMATIC_SCALE.index(root) + 4) % 12 == CHROMATIC_SCALE.index(third)

def getChords(scale):
    chords = []
    for note in range(len(scale)):
        chords.append(Chord(scale[note], scale[(note + 2) % len(scale)], scale[(note + 4) % len(scale)]))
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


def processMeasure(currMeasure, finalChords):
    print("Processing measure")
    #PROCESSING HERE
    fitDict = {}
    for chord in keyChords:
        fit = 0
        for note in currMeasure:
            if note.note in chord.notes:
                fit += (note.beatLength * LENGTH_WEIGHT) * (CHORD_WEIGHT[chord.notes.index(note.note)] + (int(note.isDownbeat) * DOWNBEAT_WEIGHT))
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
            dist = (dist + 11 * JAZZINESS_FACTOR) % 12
            if dist == 0:
                dist = 1
            fit -= dist * DISTANCE_WEIGHT

        fitDict[chord] = fit
    return keyWithMaxFit(fitDict)

def processMusicXML():
    #initialize variables
    finalChords = []
    currMeasure = []
    currMeasureLength = 0.0

    downBeat = False
    #start looping through the file
    timeSignature = m21File.getTimeSignatures()[0].numerator
    global LENGTH_WEIGHT
    LENGTH_WEIGHT = 1.0 / timeSignature
    #set number of divisions or something
    keyScale = getScale(CIRCLE_OF_FIFTHS[m21File.parts[0].measure(1).keySignature.sharps])
    global keyChords 
    keyChords = getChords(keyScale)
    global nonKeyChords
    nonKeyChords = []
    for note in CHROMATIC_SCALE:
        for chord in getChords(getScale(note)):
            if str(chord) not in [str(x) for x in keyChords] and str(chord) not in [str(x) for x in nonKeyChords]:
                nonKeyChords.append(chord)
    
    #for first note of each voice in each measure, add to currMeasure with downbeat true (check for chord)
    #continue until you reach next measure tag
    #set note beat length from duration tag w divisions.
                #If note can simply fit and not end measure
    
    #PROCESSING To Find the best chord for this measure
    #finalChords.append(processMeasure(currMeasure, finalChords))
    #currMeasure = []
    #end loop

    #if reach end of track and currMeasure not empty
        #finalChords.append(processMeasure(currMeasure, finalChords))
    return finalChords

def printResults(finalChords):
    print("Final chords:")
    measureCount = 1
    for chord in finalChords:
        print("Measure", str(measureCount), str(chord))
        measureCount += 1

def keyWithMaxFit(fitDict):
    vals=list(fitDict.values())
    keys=list(fitDict.keys())
    return keys[vals.index(max(vals))]
#MAIN FUNCTION
def main():

    fileName = input("Enter the path to the file you'd like to process: ")
    print("\nProcessing...\n")

    global m21File
    m21File = m21.converter.parse(fileName)
    finalChords = processMusicXML()
    printResults(finalChords)

if __name__ == '__main__':
    main()     