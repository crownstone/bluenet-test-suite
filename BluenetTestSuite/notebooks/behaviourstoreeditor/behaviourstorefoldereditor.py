from ipywidgets import Layout, Text, Button, Select, VBox, Output, Label

from behaviourstoreeditor.icons import *
from behaviourstoreeditor.utils import *
from behaviourstoreeditor.behaviourstoreserialisation import *

from behaviourstoreeditor.behaviourstorefileeditor import *

import os, json


BEHAVIOURSTORE_FILE_EXT = ".behaviourstore.json"

############################
#    Widget definitions    #
############################

error_output_field = Output()  # used for error reporting

folder_name_widget = Text(
    value=os.getcwd(),
    placeholder=os.getcwd(),
    description='Folder:',
    layout=Layout(width='100%')
)

loadbutton = Button(
    tooltip='Load store files',
    disabled=False,
    icon='upload',
    layout=Layout(width='100%')
)

########################################

read_file_name_widget = Select(
    options=[],
    description='Read file:',
    disabled=True
)

reloadbutton = Button(
    tooltip='Reload from file',
    disabled=False,
    icon=icon_reload,
    layout=Layout(width='100%')
)

deletebutton = Button(
    tooltip='Delete store file',
    disabled=False,
    icon=icon_delete,
    layout=Layout(width='100%')
)

########################################

write_file_name_widget = Text(
    value=None,
    placeholder="Write new file name",
    description='Write file:',
    layout=Layout(width='100%')
)

createbutton = Button(
    tooltip='Create store file',
    disabled=False,
    icon=icon_create,
    layout=Layout(width='100%')
)

savebutton = Button(
    tooltip='Save to file',
    disabled=False,
    icon=icon_save,
    layout=Layout(width='100%')
)

########################################

fileeditor, reload_store_file_editor = BehaviourStoreFileEditor()

############################
#   Callback definitions   #
############################

def get_current_file(file_name_widget):
    """
    This method returns the value of the file_name_widget, with prepended the path
    from the  and the BEHAVIOURSTORE_FILE_EXT appended.

    Returns None if the widget value evaluates to false in boolean context.

    file_name_widget should be one of [read_file_name_widget, write_file_name_widget].
    """
    if not file_name_widget.value:
        return None
    return "".join([
        folder_name_widget.value, "/",
        file_name_widget.value,
        BEHAVIOURSTORE_FILE_EXT
    ])

def reload_file_selector(button=None):
    """
    loads file selector options with files having the correct extension found in the current working folder.
    """
    try:
        next_option_list = sorted(
            [fil[:-len(BEHAVIOURSTORE_FILE_EXT)] for fil in os.listdir(folder_name_widget.value) if
             fil.endswith(BEHAVIOURSTORE_FILE_EXT)])

        read_file_name_widget.options = next_option_list

    except Exception as e:
        read_file_name_widget.disabled = True
        with error_output_field:
            print("Something bad happened while reloading file selector.")
            print(e)
    finally:
        read_file_name_widget.disabled = False

def reload_button_click(button=None):
    """
    Reload the behaviour file editor given the currently selected read file.
    """
    reload_store_file_editor(get_current_file(read_file_name_widget))

def create_button_click(button):
    path_and_filename = get_current_file(write_file_name_widget)

    if not path_and_filename:
        with error_output_field:
            print("write file name can't be empty")
        return

    if not os.path.exists(path_and_filename):
        with open(path_and_filename, 'w') as created_file:
            reload_file_selector()
            read_file_name_widget.value=write_file_name_widget.value  # set value to newly created file
            json.dump(BehaviourStore().__dict__, created_file, indent=4)
    else:
        with error_output_field:
            print("file already exists, not changing anything")

    reload_button_click()

def delete_button_click(button):
    try:
        os.remove(get_current_file(read_file_name_widget))
    except:
        with error_output_field:
            print("Failed to delete selected file!")
        return

    reload_file_selector()
    reload_store_file_editor(None)

def on_file_selector_value_update(change):
    write_file_name_widget.value = change['new'] if change['new'] else ""

############################
#    Interaction setup     #
############################

loadbutton.on_click(reload_file_selector)

reloadbutton.on_click(reload_button_click)
deletebutton.on_click(delete_button_click)

createbutton.on_click(create_button_click)

# when selecting another value from dropdown, update the write_file name to match
read_file_name_widget.observe(on_file_selector_value_update, 'value')

############################
#       Construction       #
############################

def BehaviourStoreFolderEditor():
    reload_file_selector()

    return VBox(children=[
            MakeHBox_single([folder_name_widget, loadbutton], ['95%', '5%']),
            MakeHBox_single([read_file_name_widget, reloadbutton, deletebutton], ['90%', '5%', '5%']),
            MakeHBox_single([write_file_name_widget, savebutton, createbutton], ['90%', '5%', '5%']),
            MakeHBox_single([fileeditor], ['100%']),
            error_output_field
        ]
    )
