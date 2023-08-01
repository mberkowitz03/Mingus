import interface
from mingus import Runner
import os, subprocess, platform
from PySimpleGUI import WIN_CLOSED

def main():
    runner = Runner()

    interface.open()

    while True:
        event, values = interface.readWindow()
        if event == WIN_CLOSED or event == "Exit":
            break
        elif event == "Submit":
            filename = values["-IN-"]
            print("Processing...")
            runner.run(filename)
            interface.makeButtonsVisible()
        elif event == "Cancel":
            os.remove(interface.outputFilePath(filename))
            interface.clear()
            interface.makeButtonsInvisible()
        elif event == "Open":
            filepath = interface.outputFilePath(filename)
            if platform.system() == 'Darwin':       # macOS
                subprocess.call(('open', filepath))
            elif platform.system() == 'Windows':    # Windows
                os.startfile(filepath)
            else:                                   # linux variants
                subprocess.call(('xdg-open', filepath))
    
    interface.close()
    
if __name__ == '__main__':
    main() 