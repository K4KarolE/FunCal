
from PyQt6.QtWidgets import QApplication, QWidget, QListWidget, QVBoxLayout
from PyQt6.QtWidgets import QFileDialog, QListWidgetItem, QPushButton 
from PyQt6.QtCore import Qt
from PyQt6.QtGui import QIcon, QFont

import os
import sys
import webbrowser
from pathlib import Path


app = QApplication(sys.argv)
window = QWidget()
window.resize(450, 250)
window.setWindowIcon(QIcon(str(Path(Path(__file__).parent, 'docs/icon.png'))))
window.setWindowTitle("Subtitle Audio Description Removal")
listWidget = QListWidget()
sub_dic = {}
CONFIRMATION_TEXT = 'AUDIO DESC. REMOVED'


''' SINGLE SUB '''
def button_single_subtitle_clicked():
    dialog_add_subtitle = QFileDialog()
    dialog_add_subtitle.setWindowTitle("Select an SRT file")
    dialog_add_subtitle.setNameFilter("SRT files (*.srt)")
    dialog_add_subtitle.exec()
    if dialog_add_subtitle.result():
        sub_path = dialog_add_subtitle.selectedFiles()[0]
        grouped_actions(sub_path, CONFIRMATION_TEXT)


''' MULTIPLE SUBS - ALL SUBS IN THE GIVEN FOLDER AND IT`S SUBFOLDER '''
def button_bulk_subtitle_clicked():
    dialog_add_folder = QFileDialog()
    dialog_add_folder.setFileMode(QFileDialog.FileMode.Directory)
    dialog_add_folder.setWindowTitle("Select a folder")
    dialog_add_folder.exec()
    if dialog_add_folder.result():
        for dir_path, dir_names, file_names in os.walk(dialog_add_folder.selectedFiles()[0]):
            bulk_subs(dir_path, file_names)
        for sub_dir in dir_names:
            for sub_dir_path, sub_dir_names, sub_file_names in os.walk(dir_path, sub_dir):
                bulk_subs(sub_dir_path, sub_file_names)


def bulk_subs(dir_path, file_names):
    for file in file_names:
        if file[-4:] == '.srt':
            sub_path = Path(dir_path, file)
            grouped_actions(sub_path, CONFIRMATION_TEXT)


''' NAMING / REMOVAL / LISTING '''
def grouped_actions(sub_path, CONFIRMATION_TEXT):
    sub_name = Path(sub_path).stem
    if CONFIRMATION_TEXT in sub_name:
        sub_list_name = f'{sub_name} \u2713'
        sub_new_name = f'{sub_name}.srt'
    else:
        sub_list_name = f'{sub_name} - {CONFIRMATION_TEXT} \u2713'
        sub_new_name = f'{sub_name} - {CONFIRMATION_TEXT}.srt'
    try:
        sub_ad_removal(sub_path, sub_list_name, sub_new_name)
        QListWidgetItem(sub_list_name, listWidget)
    except:
        sub_list_name = f'{sub_name} - ERROR \u2573'
        QListWidgetItem(sub_list_name, listWidget)


''' AUDIO DESCRIPTION REMOVAL  '''
def sub_ad_removal(sub_path, sub_list_name, sub_new_name): 
    parent_folder = Path(sub_path).parent
    file = open(sub_path, errors='ignore')  # avoiding text encoding errors
    newFile = open(Path(parent_folder, sub_new_name),'w')  
    sub_dic[sub_list_name] = parent_folder
    
    fileList = list(file)
    slicedList = []

    for i in range(len(fileList)):    
        sliced = fileList[i].split()   # cutting up the text
        slicedList.append(sliced)      # collecting the new/transformed items in a new list       
    for i in slicedList:
        for k in i:
            if ('(' in k and ')' in k or
                '[' in k and ']' in k):     # removing one word commentary from line like: "(SCOFFS) Don't be ridiculous."
                i.remove(k)
            elif ('(' in k and ')' not in k or
                    '[' in k and ']' not in k):     # removing multiple words commentary from lines like: "(CHAINS RATTLING)" 
                slicedList.remove(i)                # very small chance: there are lines where both previous conditions are true
                                                    # and we remove a line with a non-commentary text
    for i in slicedList:             
        newFile.writelines(' '.join(i))  # add a space between the list items
        newFile.write('\n')              

    file.close()
    newFile.close()


''' DOUBLE-CLICK IN THE RESULT LIST --> OPEN THE FOLDER '''
def open_folder():
    webbrowser.open(sub_dic[listWidget.currentItem().text()])  
listWidget.itemDoubleClicked.connect(open_folder)


''' BUTTONS '''
button_single_subtitle = QPushButton(window, text='Select Subtitle - Single Sub')
button_single_subtitle.setCursor(Qt.CursorShape.PointingHandCursor)
button_single_subtitle.clicked.connect(button_single_subtitle_clicked)
button_single_subtitle.setFont(QFont('Times', 10, 500))

button_bulk_subtitle = QPushButton(window, text='Select Folder - Multiple Subs')
button_bulk_subtitle.setCursor(Qt.CursorShape.PointingHandCursor)
button_bulk_subtitle.clicked.connect(button_bulk_subtitle_clicked)
button_bulk_subtitle.setFont(QFont('Times', 10, 500))


''' LAYOUT '''
window_layout = QVBoxLayout(window)
window_layout.addWidget(button_single_subtitle)
window_layout.addWidget(button_bulk_subtitle)
window_layout.addWidget(listWidget)
window.setLayout(window_layout)

window.show()

sys.exit(app.exec())