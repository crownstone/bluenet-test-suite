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

behaviour_store_folder_field = Text(
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

fileselector = Select(
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

filename_for_saving_field = Text(
    value="new_file_name",
    placeholder="file_name",
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

def get_current_file():
    return "".join([
        behaviour_store_folder_field.value, "/",
        fileselector.value if fileselector.value else "defaultname",
        BEHAVIOURSTORE_FILE_EXT
    ])

def file_path_invalid():
    # check if behaviour_store_folder_field.value is ok
    return False

def reload_file_selector(button=None):
    # load file selector and update current working folder
    try:
        fileselector.options = sorted(
            [fil[:-len(BEHAVIOURSTORE_FILE_EXT)] for fil in os.listdir(behaviour_store_folder_field.value) if
                                fil.endswith(BEHAVIOURSTORE_FILE_EXT)]
        )
    except:
        fileselector.disabled=True
        with error_output_field:
            print("somethng bad happened")
    finally:
        fileselector.disabled=False

def reload_file_editor_from_file_selector():
    reload_store_file_editor(get_current_file())

def reload_button_click(button):
    reload_file_editor_from_file_selector()

def create_button_click(button):
    if file_path_invalid():
        with error_output_field:
            print("path invalid!")
        return

    path_and_filename = get_current_file()

    if not os.path.exists(path_and_filename):
        with open(path_and_filename, 'w') as created_file:
            reload_file_selector()
            fileselector.value=filename_for_saving_field.value  # set value to newly created file
            json.dump(BehaviourStore().__dict__, created_file, indent=4)

    # immediately reload file as well
    reload_file_editor_from_file_selector()

def delete_button_click(button):
    if file_path_invalid():
        with error_output_field:
            print("file path invalid!")
        return
    try:
        os.remove(get_current_file())
    except:
        pass
    reload_file_selector()

def on_file_selector_value_update(change):
    pass
    # filename_for_saving_field.value = change['new']

############################
#    Interaction setup     #
############################

loadbutton.on_click(reload_file_selector)

reloadbutton.on_click(reload_button_click)
deletebutton.on_click(delete_button_click)

createbutton.on_click(create_button_click)

# when selecting another value from dropdown, update the write_file name to match
fileselector.observe(on_file_selector_value_update, 'value')

############################
#       Construction       #
############################

def BehaviourStoreFolderEditor():
    reload_file_selector()
    if not filename_for_saving_field.value:
        # if no valid behaviours are found while reloading, the observable will clean out
        # filename_for_saving_field value too thoroughly. Reset it to default:
        filename_for_saving_field.value = "new_behaviour_store_0"

    return VBox(children=[
            MakeHBox_single([behaviour_store_folder_field, loadbutton], ['95%', '5%']),
            MakeHBox_single([fileselector, reloadbutton, deletebutton], ['90%', '5%', '5%']),
            MakeHBox_single([filename_for_saving_field, savebutton, createbutton], ['90%', '5%', '5%']),
            MakeHBox_single([fileeditor], ['100%']),
            error_output_field
        ]
    )
