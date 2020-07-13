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

fileeditor_header = BehaviourStoreFileEditorHeader()
fileeditor_content = BehaviourStoreFileEditorContent()
fileeditor_footer = BehaviourStoreFileEditorFooter()

fileeditor = VBox([fileeditor_header, fileeditor_content, fileeditor_footer])

############################
#   Callback definitions   #
############################

def get_current_file():
    return "".join([
        behaviour_store_folder_field.value, "/",
        filename_for_saving_field.value,
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

def delete_button_click(button):
    if file_path_invalid():
        with error_output_field:
            print("file path invalid!")
        return
    try:
        os.remove(behaviour_store_folder_field.value + "/" +
                  fileselector.value +
                  BEHAVIOURSTORE_FILE_EXT
                  )
    except:
        pass
    reload_file_selector()

############################
#    Interaction setup     #
############################

loadbutton.on_click(reload_file_selector)
createbutton.on_click(create_button_click)
deletebutton.on_click(delete_button_click)

############################
#       Construction       #
############################

def BehaviourStoreFolderEditor():
    reload_file_selector()

    return VBox(children=[
            MakeHBox_single([behaviour_store_folder_field, loadbutton], ['95%', '5%']),
            MakeHBox_single([fileselector, reloadbutton, deletebutton], ['90%', '5%', '5%']),
            MakeHBox_single([filename_for_saving_field, savebutton, createbutton], ['90%', '5%', '5%']),
            fileeditor,
            error_output_field
        ]
    )