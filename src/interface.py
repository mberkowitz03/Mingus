import PySimpleGUI as psg

def readWindow():
	return window.read()

def makeButtonsVisible():
	window["Cancel"].update(visible=True)
	window["Open"].update(visible=True)

def makeButtonsInvisible():
	window["Cancel"].update(visible=False)
	window["Open"].update(visible=False)

def outputFilePath(filename):
	splitFile = filename.split(".")
	return splitFile[0] + '_output.' + splitFile[1]

def print(*args):
	window["OUTPUT"].print(' '.join(map(str, args)) + "\n")

def clear():
	window["OUTPUT"].update("")

def open():
	psg.theme("DarkBrown")

	layout = [[psg.Text("Enter the file you'd like to harmonize: ")],
			[psg.Input(key="-I-", do_not_clear=False), psg.FileBrowse(key="-IN-")], 
			[psg.Button("Submit"), psg.Exit(), psg.pin(psg.Cancel(visible=False, pad=((50, 0),(0,0)))), psg.pin(psg.Button("Open", visible=False))], 
			[psg.Multiline(key="OUTPUT", size=(400, 400), write_only=True, )]]
	
	global window
	window = psg.Window("Mingus", layout, size=(800, 600), grab_anywhere=True, resizable=True, font="Helvetica 14")

	psg.set_options(element_padding=(10,10))

def close():
	window.close()

def isClosed():
	return psg.WIN_CLOSED

#TODO
# Make gui more attractive
	# Change font?
# Change filebrowse to only allow supported filetypes
# investigate why import works incorrectly in muse 4
# Maybe add theory?
# Eventually Maybe add machine learning if I can find a suitable dataset