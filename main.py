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

def processFile(mid):
    #initialize variables
    finalChords = []
    currMeasure = []
    currMeasureLength = 0.0
    nextMeasures = []
    nextMeasuresLength = 0.0

    downBeat = False

    for i in range(len(mid.tracks[0])):
        #getting metadata
        currMsg = (mid.tracks[0])[i]
        if(currMsg.type == 'time_signature'):
            timeSignature = [currMsg.dict()['numerator'], currMsg.dict()['denominator']]
            ticksPerQuarter = (currMsg.dict()['clocks_per_click'] * currMsg.dict()['notated_32nd_notes_per_beat'] * 2.5)
        elif(currMsg.type =='key_signature'):
            keyScale = getScale(currMsg.dict()['key'])
            print(keyScale)
            global keyChords 
            keyChords = getChords(keyScale)

        #getting notes
        elif(currMsg.type == 'note_on'):
            #Checking for start of a note, not end
            if(currMsg.dict()['velocity'] > 0):
                #This Could be updated to allow polyphony in the future, also not sure if it will work with all midi structures
                noteBeatLength = ((mid.tracks[0][i+1]).dict()['time'] + (mid.tracks[0][i+2]).dict()['time']) / ticksPerQuarter

                #See if the note will be the start of the measure
                downBeat = (currMeasureLength == 0.0) #could later add more complex downbeat system
                remainingLength = timeSignature[0] - currMeasureLength

                #If note can simply fit and not end measure
                if noteBeatLength < (remainingLength - MARGIN_OF_ERROR):
                    currMeasure.append(Note(currMsg.dict()['note'], noteBeatLength, downBeat))
                    currMeasureLength += noteBeatLength
                else:
                    currMeasureLength = timeSignature[0]
                    currMeasure.append(Note(currMsg.dict()['note'], remainingLength, downBeat))
                    #If we need syncopation across bars
                    if noteBeatLength > (remainingLength + MARGIN_OF_ERROR):
                        nextMeasures.append(Note(currMsg.dict()['note'], noteBeatLength - remainingLength, False)) #is next downbeat
                        nextMeasuresLength += noteBeatLength - remainingLength

                    #PROCESSING To Find the best chord for this measure
                    finalChords.append(processMeasure(currMeasure, finalChords))

                    #Cleaning things up now that the current measure is processed
                    currMeasure = nextMeasures
                    currMeasureLength = nextMeasuresLength
                    #fix for if next measure is longer than time signature
                    nextMeasures = []
                    nextMeasuresLength = 0.0
                    downBeat = False
        elif currMsg.type == 'end_of_track' and len(currMeasure) != 0:
            finalChords.append(processMeasure(currMeasure, finalChords))
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

    #ADD COMMAND LINE XML SUPPORT TO EXPORT A MSCZ FILE or MXL file with chords added??

    #read into mido from filename
    fileName = input("Enter the name of the midi file: ")
    mid = MidiFile(fileName)
    print("\nProcessing...\n")
    
    
    #GET CHORDS IN ORDER OF MEASURE
    finalChords = processFile(mid)

    #FINAL BLOCK
    printResults(finalChords)

if __name__ == '__main__':
    main()     