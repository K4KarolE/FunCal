
from PyQt6.QtWidgets import QApplication, QWidget, QListWidget, QVBoxLayout, QListWidgetItem, QPushButton
from PyQt6.QtWidgets import QFileDialog 
from PyQt6.QtCore import QUrl, Qt
from PyQt6.QtGui import QMovie, QIcon, QFont

# from PyQt6.QtWidgets import QTabWidget, QLabel
# from PyQt6.QtWidgets import QLineEdit
# from PyQt6.QtCore import QSize, QTimer, QTime

import sys
from pathlib import Path
import webbrowser


app = QApplication(sys.argv)
window = QWidget()
window.resize(500, 300)
window.setWindowIcon(QIcon('skins/icon.png'))
listWidget = QListWidget()
window.setWindowTitle("Subtitle Audio Description Removal")
sub_dic = {}

def button_single_subtitle_clicked():
    dialog_add_subtitle = QFileDialog()
    dialog_add_subtitle.setWindowTitle("Select an SRT file")
    dialog_add_subtitle.setNameFilter("SRT files (*.srt)")
    dialog_add_subtitle.exec()
    if dialog_add_subtitle.exec and dialog_add_subtitle.selectedFiles():
        sub_path = dialog_add_subtitle.selectedFiles()[0]
        sub_name = Path(sub_path).stem
        sub_name_completed = f'{sub_name} - AUDIO DESC. REMOVED \u2713'
        removal(sub_path, sub_name_completed)
        QListWidgetItem(sub_name_completed, listWidget)


def removal(sub_path, sub_name_completed): 
    parent_folder = Path(sub_path).parent
    file = open(sub_path,'r+')
    new_file_name = f"{sub_name_completed}.srt"
    newFile = open(Path(parent_folder, new_file_name),'w')  
    sub_dic[sub_name_completed] = parent_folder
    
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


button_single_subtitle = QPushButton(window, text='Select Subtitle')
button_single_subtitle.setCursor(Qt.CursorShape.PointingHandCursor)
button_single_subtitle.clicked.connect(button_single_subtitle_clicked)
button_single_subtitle.setFont(QFont('Times', 10, 600))


# DOUBLE-CLICK IN THE RESULT --> OPEN THE FOLDER
def open_folder():
    webbrowser.open(sub_dic[listWidget.currentItem().text()])  
listWidget.itemDoubleClicked.connect(open_folder)

    
window_layout = QVBoxLayout(window)
window_layout.addWidget(button_single_subtitle)
window_layout.addWidget(listWidget)
window.setLayout(window_layout)

window.show()

sys.exit(app.exec())
