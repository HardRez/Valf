import gi
import os

gi.require_version("Gtk", "3.0")
from gi.repository import Gtk


class MainWindow(Gtk.Window):
    def __init__(self , path):
        Gtk.Window.__init__(self, title="Hosts")
        self.set_border_width(10)

        # row and column data
        self.rows = []
        self.columns = []
        
        # extract data from config
        self.fileToData(path)

        #  last model & row
        self.model = None
        self.row = None

        # create grid
        self.grid = Gtk.Grid()
        self.grid.set_column_homogeneous(True)
        # self.grid.set_row_homogeneous(True)
        self.add(self.grid)

        # create the box which contains host names & buttons
        # add it into grid.
        self.box = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=6)                
        self.grid.add(self.box)

        # create the ListStore
        # convert data to ListStore
        argType = [str] * len(self.columns)
        self.hostDataListStore = Gtk.ListStore(*argType)


        for row in self.rows:
            self.hostDataListStore.append(row)

        # TreeView the data that is displayed.
        self.hostTreeView = Gtk.TreeView(model = self.hostDataListStore)

        # Render data / build columns
        for i , col_title in enumerate(self.columns):
            # render / draw the data
            renderer = Gtk.CellRendererText()

            # create columns
            column = Gtk.TreeViewColumn(col_title , renderer , text = i)

            # make columns sortable
            column.set_sort_column_id(i)

            # add column to treeview
            self.hostTreeView.append_column(column)

        # Handle Selection
        self.selectedRow = self.hostTreeView.get_selection()
        self.selectedRow.connect("changed", self.update_selected_host)

        # add treeview to box
        self.box.pack_start(self.hostTreeView, True, True, 0)


        # create a mini box which contains the buttons.
        # add this minibox to bigger box.
        self.buttonBox = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL, spacing=6)
        self.box.pack_start(self.buttonBox, True, True, 0)

        # add "create button" , add it to the button box.
        self.addButton = Gtk.Button.new_with_label("Add Host")
        self.addButton.connect("clicked", self.on_add_clicked)
        self.buttonBox.pack_start(self.addButton, True, True, 0)

        # add "delete button" , add it to the button box.
        self.deleteButton = Gtk.Button.new_with_label("Delete Host")
        self.deleteButton.connect("clicked", self.on_delete_clicked)
        self.buttonBox.pack_start(self.deleteButton, True, True, 0)

        # create an empty label in order to cover 2/3 of the gui.
        self.emptyLabel = Gtk.Label(label = "")
        self.grid.attach(self.emptyLabel, 1 , 0 , 2, 1)

    def popUpCallBack(self, newHost, newAttr):
        # no new attributes.   
        if len(newHost) == len(self.columns):
            self.hostDataListStore.append(newHost)

        # need to rearrange data for every row.
        else:
            numberOfNewAttr = len(newHost) - len(self.columns)

            for i in range(len(self.rows)):
                self.rows[i].extend(["-"] * numberOfNewAttr)

            self.rows.append(newHost)

            for new_attr in newAttr:
                self.columns.append(new_attr.get_text())
            

            # delete all columns
            for column in self.hostTreeView.get_columns():
                self.hostTreeView.remove_column(column)

            # create ListStore from scratch.
            argType = [str] * len(self.columns)
            self.hostDataListStore = Gtk.ListStore(*argType)

            # add rows to the list store
            for row in self.rows:
                self.hostDataListStore.append(row)
            # set model.
            self.hostTreeView.set_model(model=self.hostDataListStore)

            # add columns.    
            for i in range(len(self.columns)):
                renderer = Gtk.CellRendererText()
                column = Gtk.TreeViewColumn(self.columns[i] , renderer , text = i)
                self.hostTreeView.append_column(column)
            
            """
            # alternative way to append column
            renderer = Gtk.CellRendererText()
            for i in range(numberOfNewAttr):
                self.hostTreeView.insert_column_with_attributes(-1, newAttr[i].get_text(),renderer)"""

            # update config
            self.updateConfig()


    def on_add_clicked(self, widget):
        win = PopUpWindow(self.popUpCallBack, self.columns)
        win.show()

    def on_delete_clicked(self, widget):
        if self.row:
            self.hostDataListStore.remove(self.row)
            
            # remove deleted from rows so config can get updated.
            # self.model.get_path(self.row) returns a Gtk.TreePath item even though when we print it it shows an integer
            # self.model.get_path(self.row)[0] gives the index as an integer.
            deletedIndex = self.model.get_path(self.row)[0]
            self.rows.pop(deletedIndex)
            self.updateConfig()
        else:
            print("there's no host to delete.")


    def update_selected_host(self , selection):
        self.model , self.row = selection.get_selected()


    def fileToData(self,path):
        data = []
        os.chdir(path)
        with open("config", "r") as fileObject:

            for line in fileObject:
                processedLine = line.strip().split(" ")
                if processedLine[0] == "Host":
                    data.append({processedLine[0] : processedLine[1]})

                elif processedLine[0] != "":
                    data[len(data) - 1][processedLine[0]] = processedLine[1]

                # add attribute to columns list
                if processedLine[0] not in self.columns and processedLine[0] != "":
                    self.columns.append(processedLine[0])
        
        for sample in data:
            newRow = ["-"] * len(self.columns)
            for key in sample.keys():
                index = self.columns.index(key)
                newRow[index] = sample[key]
            
            self.rows.append(newRow)
            
        


    def updateConfig(self):
        with open("config", "w") as fileObject:
            for row in self.rows:
                for i,column in enumerate(self.columns):
                    line = column + " " + row[i] +"\n"
                    fileObject.write(line)
                
                fileObject.write("\n")


class PopUpWindow(Gtk.Window):
    def __init__(self,callback,columns):
        self.newHost = None
        self.callback = callback
        self.columns = columns

        self.newAttributes = [] # items are Gtk.Entry()
        self.newAttributesValues = [] # items are Gtk.Entry()

        Gtk.Window.__init__(self, title="Add Host")
        self.set_border_width(10)
        
        
        self.box = Gtk.Box(orientation=Gtk.Orientation.VERTICAL)
        self.add(self.box)
        
        self.listbox = Gtk.ListBox()
        self.box.pack_start(self.listbox, True, True, 0)

        for column in self.columns:
            row = Gtk.ListBoxRow()
            mini_box = Gtk.Box(spacing = 30)

            label = Gtk.Label(label = column)
            entry = Gtk.Entry()
            mini_box.pack_start(label, True, True, 0)
            mini_box.pack_start(entry, True, True, 0)
            row.add(mini_box)
            self.listbox.add(row)

            # we will need these entry's later when we need to add a new host.
            self.newAttributesValues.append(entry)

        self.buttonBox = Gtk.Box(spacing = 15)

        self.addAttr = Gtk.Button.new_with_label("New Attribute")
        self.addAttr.connect("clicked", self.addAttribute)

        self.addButton = Gtk.Button.new_with_label("Add")
        self.addButton.connect("clicked", self.addHost)
        self.exitButton = Gtk.Button.new_with_label("Exit")
        self.exitButton.connect("clicked", self.exit)

        self.buttonBox.pack_start(self.addAttr, True, True, 0)
        self.buttonBox.pack_start(self.addButton, True, True, 0)
        self.buttonBox.pack_start(self.exitButton, True, True, 0)

        self.box.pack_start(self.buttonBox, True, True, 0)
        self.show_all()


    def addAttribute(self, widget):
        row = Gtk.ListBoxRow()
        box = Gtk.Box(spacing = 15)

        newAttr = Gtk.Entry()
        newAttr.set_text("Key")

        newAttrValue = Gtk.Entry()
        newAttrValue.set_text("Value")

        box.pack_start(newAttr, True, True, 0)
        box.pack_start(newAttrValue, True, True, 0)

        row.add(box)
        self.listbox.add(row)
        self.listbox.show_all()

        self.newAttributes.append(newAttr)
        self.newAttributesValues.append(newAttrValue)

    def addHost(self, widget):
        self.newHost = []

        for i in range(len(self.columns)):
            if self.newAttributesValues[i]:
                self.newHost.append(self.newAttributesValues[i].get_text())
            else:
                self.newHost.append("-")

        for i in range(len(self.newAttributes)):
            self.newHost.append(self.newAttributesValues[i + len(self.columns)].get_text())

        self.callback(self.newHost, self.newAttributes)
        self.destroy()

    def exit(self, widget):
        self.destroy()


print(os.getcwd())
path = "/home/nogigen/.ssh"

win = MainWindow(path)
win.connect("destroy", Gtk.main_quit)
win.show_all()
Gtk.main()
