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
        self.grid(sticky=W+E+N+S, padx=5, pady=5)

        self.data = None
        self.boards = []
        self.current_board = None

        self.openbutton = Button(self, text="Open World", command=self.load_file, width=10)
        self.openbutton.grid(row=0, column=0)
        self.savebutton = Button(self, text="Save World", command=self.save_file, width=10, state=DISABLED)
        self.savebutton.grid(row=0, column=1)

        self.label = Label(self, text="Boards (labels)")
        self.label.grid(row=1, column=0, columnspan=2)

        listframe = Frame(self)
        self.boardlist = Listbox(listframe, selectmode=SINGLE, width=50)
        self.boardlist.pack(side="left", fill="y")
        self.boardlist.bind("<<ListboxSelect>>", self.on_listbox_select)

        scrollbar = Scrollbar(listframe, orient="vertical")
        scrollbar.config(command=self.boardlist.yview)
        scrollbar.pack(side="right", fill="y")

        self.boardlist.config(yscrollcommand=scrollbar.set)
        listframe.grid(row=2, column=0, columnspan=2)

        self.exportbutton = Button(self, text="Export Board", command=self.export_board, width=10, state=DISABLED)
        self.exportbutton.grid(row=3, column=0)
        self.importbutton = Button(self, text="Import Board", command=self.import_board, width=10, state=DISABLED)
        self.importbutton.grid(row=3, column=1)

    def set_data(self, data):
        self.data = data
        self.boards = data["TopLevelObjects"]["value"]
        self.boardlist.delete(0, END)
        for board in self.boards:
            labels = self.get_labels(board)
            name = "Unlabeled"
            if len(labels) > 0:
                name = ", ".join(labels)
            self.boardlist.insert(END, name)
        self.importbutton['state'] = NORMAL
        self.savebutton['state'] = NORMAL

    def add_board(self, board):
        data = self.data
        data["TopLevelObjects"]["value"].append(board)
        self.set_data(data)

    def get_labels(self, board):
        labels = []
        for child in board["Children"]:
            if child["ObjectType"] == "Panel Label":
                labels.append(child["CustomDataArray"][0]["value"])
        return labels

    def on_listbox_select(self, event):
        self.current_board = int(event.widget.curselection()[0])
        self.exportbutton["state"] = NORMAL

    def load_file(self):
        filename = askopenfilename(filetypes=[("TUNG saves", "*.tung")])
        if filename:
            print("Chosen file: %s" % filename)
            self.master.title("%s - Board Extractor" % basename(filename))
            with open(filename, "r") as infile:
                contents = infile.read()
            # To anyone reading this part:
            #  Yes, I am ashamed of what it does, but it works
            index = contents.find("CustomDataArray")
            custompart = re.sub("mscorlib\"(.*?)\\}", "mscorlib\", \"value\":\\1}", contents[index:])
            contents = contents[:index] + custompart
            #with open("jsonin.txt", "w") as logfile:
            #    logfile.write(contents)
            data = json.loads(contents)
            #with open("jsonout.txt", "w") as logfile:
            #    print(json.dumps(data, sort_keys=True, indent=4), file=logfile)
            tlobjs = data["TopLevelObjects"]["value"]
            if not isinstance(tlobjs, list):
                data["TopLevelObjects"]["value"] = [tlobjs]
            self.set_data(data)
        else:
            print("No file chosen")

    def save_file(self):
        filename = asksaveasfilename(filetypes=[("TUNG saves", "*.tung")])
        if filename:
            encoded = json.dumps(self.data)
            # To anyone reading this part:
            #  Yes, I am ashamed of what it does, but it works
            index = encoded.find("CustomDataArray")
            custompart = re.sub("__type\":(.*?),\\s\"value\":\\s*", "__type\":\\1", encoded[index:])
            encoded = encoded[:index] + custompart
            with open(filename, "w") as outfile:
                outfile.write(encoded)
        else:
            print("No file chosen")

    def export_board(self):
        filename = asksaveasfilename(filetypes=[("TUNG Boad File", "*.btf")])
        if filename:
            board = self.boards[self.current_board]
            contents = json.dumps(board)
            with open(filename, "w") as boardfile:
                boardfile.write(contents)

    def import_board(self):
        filename = askopenfilename(filetypes=[("TUNG Boad File", "*.btf")])
        if filename:
            with open(filename, "r") as boardfile:
                contents = boardfile.read()
            board = json.loads(contents)
            self.add_board(board)

def main():
    MainFrame().mainloop()

if __name__ == "__main__":
    main()
