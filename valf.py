import gi
import os
import errno

gi.require_version("Gtk", "3.0")
gi.require_version("Vte" , "2.91")
from gi.repository import Gtk, Vte
from gi.repository import GLib

HOME = "HOME"
SHELLS = [ "/bin/bash" ]

class MainWindow(Gtk.Window):
    def __init__(self):
        Gtk.Window.__init__(self, title="Hosts")
        self.set_border_width(10)

        # all informations and host names
        self.data = []
        self.hostNames = [] 
        self.editListbox = None
        # values from edit section
        # items are Gtk.Entry
        self.editAttributeValues = []
        self.editAttributes = []

        self.mandatoryAttributes = ['Host', 'Hostname']

        self.control()

        # extract data from config
        self.fileToData()

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
        self.hostDataListStore = Gtk.ListStore(str) # 1 column, host names.


        for row in self.hostNames:
            _list = [row]
            self.hostDataListStore.append(_list)

        # TreeView the data that is displayed.
        self.hostTreeView = Gtk.TreeView(model = self.hostDataListStore)

        # Render data / build columns
        # only render "host" column
        renderer = Gtk.CellRendererText()
        column = Gtk.TreeViewColumn("Host" , renderer , text = 0)
        # column.set_sort_column_id(0) sorting mess things up.
        self.hostTreeView.append_column(column)
        self.hostTreeView.connect("row-activated", self.row_double_click)

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

         # add "save button" , add it to the button box.
        self.saveButton = Gtk.Button.new_with_label("Save")
        self.saveButton.connect("clicked", self.on_save_clicked)
        self.buttonBox.pack_start(self.saveButton, True, True, 0)

        # show attributes of selected host in the right side (2/3 side)
        # create an empty label in order to cover 2/3 of the gui.
        self.rightBox = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=6)
        self.grid.attach(self.rightBox, 1 , 0 , 2, 1)


        # add "save button" , add it to the button box.
        self.editBtnBox = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL, spacing=6)
        self.addAttrBtn = Gtk.Button.new_with_label("Add Attribute")
        self.addAttrBtn.connect("clicked", self.on_add_attribute)
        self.editBtnBox.pack_start(self.addAttrBtn, True, True, 0)

        self.deleteAttrBtn = Gtk.Button.new_with_label("Delete Attribute")
        self.deleteAttrBtn.connect("clicked", self.on_delete_attribute)
        self.editBtnBox.pack_start(self.deleteAttrBtn, True, True, 0)
        # add this button to the editbox after listbox gets added to box. It happens inside the function update_selected_host

    def row_double_click(self, widget, row, col):
        index = row[0]
        win = ConnectionWindow(self.data[index])
        win.show()


    def add_host(self, newHost, newAttr):
        _list = [newHost['Host']]
        self.data.append(newHost)
        self.hostDataListStore.append(_list)


    def on_add_clicked(self, widget):
        win = AddHostWindow(self.add_host)
        win.show()

    def on_add_attribute(self, widget):
        row = Gtk.ListBoxRow()
        box = Gtk.Box(spacing = 15)

        newAttr = Gtk.Entry()
        newAttr.set_text("Key")

        newAttrValue = Gtk.Entry()
        newAttrValue.set_text("Value")

        box.pack_start(newAttr, True, True, 0)
        box.pack_start(newAttrValue, True, True, 0)

        row.add(box)
        self.editListbox.add(row)
        self.editListbox.show_all()

        self.editAttributes.append(newAttr)
        self.editAttributeValues.append(newAttrValue)

    def on_delete_attribute(self, widget):
        print(len(self.editAttributes))
        if self.editListbox.get_selected_row():
            index = self.editListbox.get_selected_row().get_index()
            attr = self.editAttributes[index]
            if type(attr) == str:
                if self.editAttributes[index] in self.mandatoryAttributes:
                    print("you can not delete this attribute. its a mandatory attribute")
                    
                else:
                    self.editAttributes.pop(index)
                    self.editAttributeValues.pop(index)
                    self.editListbox.remove(self.editListbox.get_selected_row())
            else:
                if self.editAttributes[index].get_text() in self.mandatoryAttributes:
                    print("you can not delete this attribute. its a mandatory attribute")
                    
                else:
                    self.editAttributes.pop(index)
                    self.editAttributeValues.pop(index)
                    self.editListbox.remove(self.editListbox.get_selected_row()) # doesnt delete with index, deletes with widget.
 
        else:
            print("you need to select an attribute first.")

    def on_delete_clicked(self, widget):
        if self.row:
            deletedIndex = self.model.get_path(self.row)[0]
            self.hostDataListStore.remove(self.row)
            print(deletedIndex)
            self.data.pop(deletedIndex)

        else:
            print("there's no host to delete.")

    def on_save_clicked(self, widget):
        # some editing might have happened to a host
        updatedHostData = {}
        for i,attr in enumerate(self.editAttributes):
            if type(attr) == str:
                updatedHostData[attr] = self.editAttributeValues[i].get_text()
            else:
                updatedHostData[attr.get_text()] = self.editAttributeValues[i].get_text()


        index = self.model.get_path(self.row)[0]
        self.data[index] = updatedHostData
        self.hostDataListStore[index] = [updatedHostData['Host']]

        # recreate edit list box, in order to change entries to label.
        self.clearEditListBox()
        self.displayRightList()

        self.updateConfig()

    def updateConfig(self):
        with open("config", "w") as fileObject:
            for _data in self.data:
                for key in _data.keys():
                    if _data[key].strip() != "":
                        line = key + " " + _data[key] +"\n"
                        fileObject.write(line)
                    
                fileObject.write("\n")


    def update_selected_host(self , selection):

        if not self.editListbox:
            self.editListbox = Gtk.ListBox()
            self.rightBox.pack_start(self.editListbox, True, True, 0)
            self.rightBox.pack_start(self.editBtnBox, True, True, 0)

        self.model , self.row = selection.get_selected()

        # delete displayed info in the right part (2/3 part)
        # host ...
        # hostname ... etc. delete those.
        self.clearEditListBox()

        # display right box
        self.displayRightList()


    def clearEditListBox(self):
        if self.editListbox:
            childrens = self.editListbox.get_children()
            for child in childrens:
                self.editListbox.remove(child)

    # check whether there is .ssh folder or not
    # check whether there is config and known_hosts file inside .ssh folder or not
    # if there is no .ssh folder, create one.
    # if there is no config/known_hosts file, create an empty one
    def control(self):
        curPath = os.getcwd()
        names = curPath.split("/")
        path = f"/{names[1]}/{names[2]}"
        os.chdir(path)

        """ alternative way.
        directories = os.listdir()
        # if there is no .ssh, create it!
        if ".ssh" not in directories:
            os.mkdir(".ssh") """ 
        
        try:
            # Create target Directory
            os.mkdir(".ssh")
            print(".ssh is created") 
        except FileExistsError:
            print(".ssh already exists.") 

        for fileName in ["config", "known_hosts"]:
            try:
                open(path +"/.ssh/" + fileName, "x")
                print(fileName + " is created.")
            except FileExistsError:
                print(fileName + " already exists.")


    def fileToData(self):
        curPath = os.getcwd()
        names = curPath.split("/")
        pcName = names[2] 

        path = f"/{names[1]}/{names[2]}/.ssh"
        os.chdir(path)
        with open("config", "r") as fileObject:

            for line in fileObject:
                processedLine = line.strip().split(" ")
                if processedLine[0] == "Host":
                    self.hostNames.append(processedLine[1])
                    self.data.append({processedLine[0] : processedLine[1]})

                elif processedLine[0] != "":
                    self.data[len(self.data) - 1][processedLine[0]] = processedLine[1]

        
    def displayRightList(self):
        # reset attribute values.
        self.editAttributeValues = []
        self.editAttributes = []
        # we already know the data and selected index
        if self.row:
            hostData = self.data[self.model.get_path(self.row)[0]]

            maxKeyLength = 0
            for key in hostData.keys():
                if len(key) > maxKeyLength:
                    maxKeyLength = len(key)

            print(maxKeyLength)

            for key in hostData.keys():
                row = Gtk.ListBoxRow()
                mini_box = Gtk.Box(spacing = 30)
                label = Gtk.Label(label = key + " " * (2 * (maxKeyLength - len(key))))
                label.set_xalign(0.0)

                entry = Gtk.Entry()
                entry.set_text(hostData[key])
                entry.set_alignment(xalign = 0)

                mini_box.pack_start(label, True, True, 0)
                mini_box.pack_start(entry, True, True, 0)
                row.add(mini_box)
                self.editListbox.add(row)

                self.editAttributeValues.append(entry)
                self.editAttributes.append(key)        

                self.show_all()

class AddHostWindow(Gtk.Window):
    def __init__(self,callback):
        self.newHost = None
        self.callback = callback
        self.data = {}
        self.mandatoryEntries = ['Host', 'Hostname']
        self.optionalAttributes = [] # items are Gtk.Entry()
        self.attributeValues = [] # items are Gtk.Entry() , mandatory + optional

        Gtk.Window.__init__(self, title="Add Host")
        self.set_border_width(10)
        
        
        self.box = Gtk.Box(orientation=Gtk.Orientation.VERTICAL)
        self.add(self.box)
        
        self.listbox = Gtk.ListBox()
        self.box.pack_start(self.listbox, True, True, 0)

        for column in self.mandatoryEntries:
            row = Gtk.ListBoxRow()
            mini_box = Gtk.Box(spacing = 30)

            label = Gtk.Label(label = column)
            entry = Gtk.Entry()
            mini_box.pack_start(label, True, True, 0)
            mini_box.pack_start(entry, True, True, 0)
            row.add(mini_box)
            self.listbox.add(row)

            # we will need these entry's later when we need to add a new host.
            self.attributeValues.append(entry)

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

        self.optionalAttributes.append(newAttr)
        self.attributeValues.append(newAttrValue)

    def addHost(self, widget):
        cond = True
        self.newHost = {}

        for i in range(len(self.mandatoryEntries)):
            if self.attributeValues[i].get_text().strip() == "":
                cond = False
                print("host and hostnames are mandatory, fill them.")

        if cond:
            for i in range(len(self.mandatoryEntries)):
                self.newHost[self.mandatoryEntries[i]] = self.attributeValues[i].get_text()

            for i in range(len(self.optionalAttributes)):
                self.newHost[self.optionalAttributes[i].get_text()] = self.attributeValues[i + len(self.mandatoryEntries)].get_text()

            self.callback(self.newHost, self.optionalAttributes)
            self.destroy()

    def exit(self, widget):
        self.destroy()


class ConnectionWindow(Gtk.Window):
    def __init__(self, data):
        Gtk.Window.__init__(self, title="Bağlan")
        self.set_border_width(10)
        self.data = data
        self.terminal = Vte.Terminal()
        self.terminal.spawn_sync(
                Vte.PtyFlags.DEFAULT,
                os.environ[HOME],
                SHELLS,
                [],
                GLib.SpawnFlags.DO_NOT_REAP_CHILD,
                None,
                None,
                )
        
        self.command = None
        self.isTerminalOpen = False


        self.buttons = list()
        for btn_name in ["dummy1", "dummy2", "dummy3", "Bağlan"]:
            button = Gtk.Button(label = btn_name)
            self.buttons.append(button)

            if btn_name == "Bağlan":
                button.connect("clicked", self.on_clicked_connect)
                

        self.grid = Gtk.Grid()
        self.grid.set_column_homogeneous(True)
        self.grid.set_row_homogeneous(True)
        self.add(self.grid)

        self.grid.add(self.buttons[0])
        for i, button in enumerate(self.buttons[1 : ]):
            self.grid.attach(button, 0 , i + 1, 1 , 1)
            #self.grid.attach_next_to(button, self.buttons[i], Gtk.PositionType.BOTTOM, 3, 10)

        self.rightBox = Gtk.Box()

        #self.grid.attach(self.label, 1 , 0 , 2, 1)
        self.grid.attach(self.rightBox, 1 , 0 , 2, len(self.buttons))
        self.show_all()


    
    def on_clicked_connect(self, widget):
        if not self.isTerminalOpen:

            self.rightBox.add(self.terminal)
            self.show_all()
            self.isTerminalOpen = True

        self.command = f"ssh {self.data['Host']}\n"
        self.terminal.feed_child_binary(self.command.encode("utf-8"))
        #print(self.terminal.get_text())






win = MainWindow()
win.connect("destroy", Gtk.main_quit)
win.show_all()
Gtk.main()
