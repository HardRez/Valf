import gi
import paramiko
import scpclient
import os.path

gi.require_version("Gtk", "3.0")
from gi.repository import Gtk
from paramiko import SSHClient
from scp import SCPClient

class FileChooserWindow(Gtk.Window):

    def __init__(self):
        Gtk.Window.__init__(self, title="FileChooser Example")

        box = Gtk.Box(spacing=6)
        self.add(box)

        button1 = Gtk.Button(label="Choose File")
        button1.connect("clicked", self.on_file_clicked)
        box.add(button1)

    def on_file_clicked(self, widget):
        dialog = Gtk.FileChooserDialog(
            title="Please choose a file", parent=self, action=Gtk.FileChooserAction.OPEN
        )
        dialog.add_buttons(
            Gtk.STOCK_CANCEL,
            Gtk.ResponseType.CANCEL,
            Gtk.STOCK_OPEN,
            Gtk.ResponseType.OK,
        )

        self.add_filters(dialog)

        response = dialog.run()
        if response == Gtk.ResponseType.OK:
            print("Open clicked")
            print("File selected: " + dialog.get_filename())
            fileName = dialog.get_filename()
            sendFileFunction(fileName)

        elif response == Gtk.ResponseType.CANCEL:
            print("Cancel clicked")

        dialog.destroy()

    def add_filters(self, dialog):
        filter_text = Gtk.FileFilter()
        filter_text.set_name("Text files")
        filter_text.add_mime_type("text/plain")
        dialog.add_filter(filter_text)

        filter_py = Gtk.FileFilter()
        filter_py.set_name("Python files")
        filter_py.add_mime_type("text/x-python")
        dialog.add_filter(filter_py)

        filter_any = Gtk.FileFilter()
        filter_any.set_name("Any files")
        filter_any.add_pattern("*")
        dialog.add_filter(filter_any)

    

def sendFileFunction(fname):
    print(fname)
    connection = SSHClient()
    connection.load_system_host_keys()
    connection.set_missing_host_key_policy(paramiko.AutoAddPolicy())
    connection.connect(hostname="192.168.1.8",username="hardrez", password="rez1999", port="22")
    ftp_client = connection.open_sftp()
    ftp_client.put(fname, '/home/hardrez/' + pathManipulation(fname))
    ftp_client.close()

def pathManipulation(filePath):
    manFileName = os.path.basename(filePath)
    print(manFileName)
    return manFileName

win = FileChooserWindow()
win.connect("destroy", Gtk.main_quit)
win.show_all()
Gtk.main()