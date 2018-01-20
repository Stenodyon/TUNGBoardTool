from tkinter import *
from tkinter.filedialog import askopenfilename, asksaveasfilename
import json
import re

from os.path import basename

class MainFrame(Frame):
    def __init__(self):
        Frame.__init__(self)
        self.master.title("Board Extractor")
        self.master.rowconfigure(5, weight=1)
        self.master.columnconfigure(5, weight=1)
        self.grid(sticky=W+E+N+S)

        self.data = None

        self.openbutton = Button(self, text="Open", command=self.load_file, width=10)
        self.openbutton.grid(row=0, column=0)
        self.savebutton = Button(self, text="Save", command=self.save_file, width=10)
        self.savebutton.grid(row=0, column=1)

    def load_file(self):
        filename = askopenfilename(filetypes=[("TUNG saves", "*.tung")])
        if filename:
            print("Chosen file: %s" % filename)
            self.master.title("%s - Board Extractor" % basename(filename))
            with open(filename, "r") as infile:
                contents = infile.read()
            contents = re.sub("mscorlib\"(\\w*)\\}", "mscorlib\", \"value\":\"\\1\"}", contents)
            data = json.loads(contents)
            with open("jsonout.txt", "w") as logfile:
                print(json.dumps(data, sort_keys=True, indent=4), file=logfile)
            self.data = data
        else:
            print("No file chosen")

    def save_file(self):
        filename = asksaveasfilename(filetypes=[("TUNG saves", "*.tung")])
        if filename:
            encoded = json.dumps(self.data)
            # To anyone reading this part:
            #  Yes, I am ashamed of what it does, but it works
            index = encoded.find("CustomDataArray")
            custompart = re.sub("__type\":(.*?),\\s\"value\":\\s*\"(.*?)\"", "__type\":\\1\\2", encoded[index:])
            encoded = encoded[:index] + custompart
            with open(filename, "w") as outfile:
                outfile.write(encoded)
        else:
            print("No file chosen")

def main():
    MainFrame().mainloop()

if __name__ == "__main__":
    main()
