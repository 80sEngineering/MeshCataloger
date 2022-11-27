import sys
from pathlib import Path

from PyQt6.QtGui import QIcon
from PyQt6.QtCore import QSize
from PyQt6.QtWidgets import QApplication, QMainWindow, QPushButton, QVBoxLayout, QHBoxLayout, QWidget, \
    QFileDialog, QLabel

from Viewer import Viewer


class MainWindow(QMainWindow):
    def __init__(self):
        super(MainWindow, self).__init__()
        self.setWindowTitle('MeshCataloger')
        self.setMinimumSize(QSize(500, 500))
        self.mesh_viewer = Viewer()
        view_layout = QVBoxLayout()
        bottom_layout = self.init_button_and_text()
        view_layout.addWidget(self.mesh_viewer)
        view_layout.addLayout(bottom_layout)
        view = QWidget()
        view.setLayout(view_layout)
        self.setCentralWidget(view)

    def init_button_and_text(self):
        file_button = QPushButton("Browse")
        layout = QHBoxLayout()
        file_button.setCheckable(True)
        file_button.setFixedSize(100, 50)
        file_button.clicked.connect(self.clicked_file_button)
        text = QLabel("Please select a file.")
        layout.addWidget(text)
        layout.addWidget(file_button)
        return layout

    def clicked_file_button(self):
        home_directory = str(Path.home())
        data = QFileDialog.getOpenFileName(self, 'Open file', home_directory, filter="*.stl")
        file_name = data[0]
        self.mesh_viewer.show_stl(file_name)


def main():
    app = QApplication(sys.argv)
    window = MainWindow()
    window.show()
    sys.exit(app.exec())


if __name__ == '__main__':
    main()
