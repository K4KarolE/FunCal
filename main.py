
import os
from pathlib import Path
import sys
import webbrowser

from PyQt6.QtCore import Qt
from PyQt6.QtGui import QFont, QIcon 
from PyQt6.QtWidgets import (
    QFileDialog,
    QApplication,
    QListWidget,
    QListWidgetItem,
    QPushButton,
    QVBoxLayout,
    QWidget
    ) 



app = QApplication(sys.argv)
window = QWidget()
window.resize(650, 250)
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


''' MULTIPLE SUBS - ALL SUBS IN THE GIVEN DIRECTORY AND IT`S SUBDIRECTORIES '''
def button_bulk_subtitle_clicked():
    dialog_add_directory = QFileDialog()
    dialog_add_directory.setFileMode(QFileDialog.FileMode.Directory)
    dialog_add_directory.setWindowTitle("Select a directory")
    dialog_add_directory.exec()
    if dialog_add_directory.result():
        for dir_path, dir_names, file_names in os.walk(dialog_add_directory.selectedFiles()[0]):
            bulk_subs(dir_path, file_names)


def bulk_subs(dir_path, file_names):
    for file in file_names:
        if file[-4:] == '.srt':
            sub_path = Path(dir_path, file)
            grouped_actions(sub_path, CONFIRMATION_TEXT)


''' NAMING / REMOVAL / LISTING '''
def grouped_actions(sub_path, CONFIRMATION_TEXT):
    sub_name = Path(sub_path).stem
    if CONFIRMATION_TEXT in sub_name:
        sub_list_name = f'{sub_name} \u2713'    # \u2713 = check mark
        sub_new_name = f'{sub_name}.srt'
    else:
        sub_list_name = f'{CONFIRMATION_TEXT} - {sub_name} \u2713'
        sub_new_name = f'{CONFIRMATION_TEXT} - {sub_name}.srt'
    try:
        sub_ad_removal(sub_path, sub_list_name, sub_new_name)
        QListWidgetItem(sub_list_name, listWidget)
    except:
        sub_list_name = f'{sub_name} - ERROR \u2573'
        QListWidgetItem(sub_list_name, listWidget)


''' AUDIO DESCRIPTION REMOVAL  '''
def sub_ad_removal(sub_path, sub_list_name, sub_new_name): 
    parent_directory = Path(sub_path).parent
    file = open(sub_path, mode='r', encoding='utf-8', errors='ignore')  # avoiding text encoding errors
    newFile = open(Path(parent_directory, sub_new_name), mode='w', encoding='utf-8')
    sub_dic[sub_list_name] = parent_directory
    
    fileList = list(file)
    slicedList = []
    words_to_remove = []
    rows_to_remove = []
    spec_char_look_for = '( ) [ ]'.split()

    for i in range(len(fileList)):    
        sliced = fileList[i].split()   
        slicedList.append(sliced)

    ''' 
        Removing the whole row/line containing
        audio description like: "(CHAINS RATTLING)"
    '''
    for row in slicedList:
        for word in row:
            if ('(' in word and ')' not in word or
                    '[' in word and ']' not in word):
                rows_to_remove.append(row)
    
    for _ in rows_to_remove:
        slicedList.remove(_)
    rows_to_remove.clear()

              
    ''' 
        Removing one word commentary from line like:
        "(SCOFFS) Don't be ridiculous."
    '''
    for row_index, row in enumerate(slicedList):
        for word in row:
            if (any(spec_char in spec_char_look_for[:2] for spec_char in word) or
                any(spec_char in spec_char_look_for[2:] for spec_char in word)) :     
                words_to_remove.append([row_index, word])

    for _ in words_to_remove:
        row_index, word = _[0], _[1]
        slicedList[row_index].remove(word)

        '''
            5
            00:00:51,079 --> 00:00:54,449
            -
                        to
            5
            00:00:51,079 --> 00:00:54,449

         '''
        if len(slicedList[row_index]) == 1:
            word_or_symbol = slicedList[row_index][0]
            if len(word_or_symbol) == 1 and not word_or_symbol.isdecimal():
                rows_to_remove.append(slicedList[row_index])
    for _ in rows_to_remove:
        slicedList.remove(_)
    

    ''' File compiling '''
    for i in slicedList:             
        newFile.writelines(' '.join(i))
        newFile.write('\n')              
    
    file.close()
    newFile.close()


''' OPEN THE SUB`S DIRECTORY '''
def open_directory():
    webbrowser.open(sub_dic[listWidget.currentItem().text()])
listWidget.itemDoubleClicked.connect(open_directory)


''' BUTTONS '''
button_single_subtitle = QPushButton(window, text='Select Subtitle - Single Sub')
button_single_subtitle.setCursor(Qt.CursorShape.PointingHandCursor)
button_single_subtitle.clicked.connect(button_single_subtitle_clicked)
button_single_subtitle.setFont(QFont('Times', 10, 500))

button_bulk_subtitle = QPushButton(window, text='Select Directory - Multiple Subs')
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