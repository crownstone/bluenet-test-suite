from ipywidgets import Layout, Text, Button, Select, VBox, Output, Label

from behaviourstoreeditor.icons import *
from behaviourstoreeditor.utils import *
from behaviourstoreeditor.behaviourstoreserialisation import *

from behaviourstoreeditor.behaviourstorefileeditor import *

import os, json


BEHAVIOURSTORE_FILE_EXT = ".behaviourstore.json"

class BehaviourStoreFolderEditor:
    def __init__(self):
        self.error_output_field = Output()  # used for error reporting
        self.setup_folder_name_widgets()
        self.setup_read_file_name_widgets()
        self.setup_write_file_name_widgets()
        self.fileeditor = BehaviourStoreFileEditor()
        self.setup_main_widget()
        self.setup_interaction()
        self.reload_file_selector()

    def setup_folder_name_widgets(self):
        self.folder_name_widget = Text(
            value=os.getcwd(),
            placeholder=os.getcwd(),
            description='Folder:',
            layout=Layout(width='100%')
        )

        self.loadbutton = Button(
            tooltip='Load store files',
            disabled=False,
            icon='upload',
            layout=Layout(width='100%')
        )

        self.folderselectionwidgets = MakeHBox_single([self.folder_name_widget,
                                                       self.loadbutton], ['95%', '5%'])

    def setup_read_file_name_widgets(self):
        self.read_file_name_widget = Select(
            options=[],
            description='Read file:',
            disabled=True
        )

        self.reloadbutton = Button(
            tooltip='Reload from file',
            disabled=False,
            icon=icon_reload,
            layout=Layout(width='100%')
        )

        self.deletebutton = Button(
            tooltip='Delete store file',
            disabled=False,
            icon=icon_delete,
            layout=Layout(width='100%')
        )

        self.readfilenamewidgets = MakeHBox_single([self.read_file_name_widget,
                                                    self.reloadbutton,
                                                    self.deletebutton],
                                                   ['90%', '5%', '5%'])

    def setup_write_file_name_widgets(self):
        self.write_file_name_widget = Text(
            value=None,
            placeholder="Write new file name",
            description='Write file:',
            layout=Layout(width='100%')
        )

        self.createbutton = Button(
            tooltip='Create store file',
            disabled=False,
            icon=icon_create,
            layout=Layout(width='100%')
        )

        self.savebutton = Button(
            tooltip='Save to file',
            disabled=False,
            icon=icon_save,
            layout=Layout(width='100%')
        )

        self.writefilenamewidgets = MakeHBox_single([self.write_file_name_widget,
                                                     self.savebutton,
                                                     self.createbutton],
                                                    ['90%', '5%', '5%'])

    def setup_main_widget(self):
        self.main_widget = VBox(children=[
            self.folderselectionwidgets,
            self.readfilenamewidgets,
            self.writefilenamewidgets,
            self.fileeditor.get_widgets(),
            self.error_output_field
        ]
        )

    def setup_interaction(self):
        """
        Installs observe and click handlers. Must only be called once to prevent multiple execution of handlers on click.
        """
        self.loadbutton.on_click(lambda x: self.reload_file_selector(x))
        self.reloadbutton.on_click(lambda x: self.reload_button_click(x))
        self.deletebutton.on_click(lambda x: self.delete_button_click(x))
        self.createbutton.on_click(lambda x: self.create_button_click(x))
        self.savebutton.on_click(lambda x: self.save_button_click(x))

        # when selecting another value from dropdown, update the write_file name to match
        self.read_file_name_widget.observe(lambda x: self.on_file_selector_value_update(x), 'value')

    def get_widgets(self):
        """
        Returns the 'top level' widget so that it can be embedded into another one or displayed in a cell.
        """
        return self.main_widget

    def get_current_file(self, file_name_widget):
        """
        This method returns the value of the file_name_widget, with prepended the path
        from the  and the BEHAVIOURSTORE_FILE_EXT appended.

        Returns None if the widget value evaluates to false in boolean context.

        file_name_widget should be one of [read_file_name_widget, write_file_name_widget].
        """
        if not file_name_widget.value:
            return None
        return "".join([
            self.folder_name_widget.value, "/",
            file_name_widget.value,
            BEHAVIOURSTORE_FILE_EXT
        ])

    def reload_file_selector(self, button=None):
        """
        loads file selector options with files having the correct extension found in the current working folder.
        """
        try:
            next_option_list = sorted(
                [fil[:-len(BEHAVIOURSTORE_FILE_EXT)] for fil in os.listdir(self.folder_name_widget.value) if
                 fil.endswith(BEHAVIOURSTORE_FILE_EXT)])

            self.read_file_name_widget.options = next_option_list

        except Exception as e:
            self.read_file_name_widget.disabled = True
            with self.error_output_field:
                print("Something bad happened while reloading file selector.")
                print(e)
        finally:
            self.read_file_name_widget.disabled = False

    def reload_button_click(self, button=None):
        """
        Reload the behaviour file editor given the currently selected read file.
        """
        self.fileeditor.update_content(self.get_current_file(self.read_file_name_widget))

    def create_button_click(self, button):
        path_and_filename = self.get_current_file(self.write_file_name_widget)

        if not path_and_filename:
            with self.error_output_field:
                print("write file name can't be empty")
            return

        if not os.path.exists(path_and_filename):
            with open(path_and_filename, 'w') as created_file:
                self.reload_file_selector()
                self.read_file_name_widget.value=self.write_file_name_widget.value  # set value to newly created file
                json.dump(BehaviourStore().__dict__, created_file, indent=4)
        else:
            with self.error_output_field:
                print("file already exists, not changing anything")

        self.reload_button_click()

    def delete_button_click(self, button):
        try:
            os.remove(self.get_current_file(self.read_file_name_widget))
        except:
            with self.error_output_field:
                print("Failed to delete selected file!")
            return

        self.reload_file_selector()
        self.fileeditor.update_content(None)

    def save_button_click(self, button):
        if self.fileeditor:
            self.fileeditor.save_all_entry_changes(self.get_current_file(self.write_file_name_widget))

    def on_file_selector_value_update(self, change):
        self.write_file_name_widget.value = change['new'] if change['new'] else ""
