import sys
from pathlib import Path

from PyQt6.QtCore import QSize
from PyQt6.QtGui import QPixmap
from PyQt6.QtWidgets import QApplication, QMainWindow, QPushButton, QVBoxLayout, QHBoxLayout, QWidget, \
    QFileDialog, QLabel

from Viewer import Viewer


class MainWindow(QMainWindow):
    def __init__(self):
        super(MainWindow, self).__init__()
        self.setWindowTitle('MeshCataloger')
        self.setFixedSize(QSize(640, 500))
        self.mesh_viewer = Viewer()
        view_layout = QVBoxLayout()
        bottom_layout = self.init_button_and_text()
        view_layout.addWidget(self.mesh_viewer)
        view_layout.addLayout(bottom_layout)
        view = QWidget()
        view.setLayout(view_layout)
        self.setCentralWidget(view)
        self.init_aiming_dot()

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

    def init_aiming_dot(self): # TODO a cleaner
        aiming_dot = QLabel(self)
        scaling_down = QSize(8,8)
        pixmap = QPixmap("green_dot.png").scaled(scaling_down)
        aiming_dot.setPixmap(pixmap)
        middle_coordinates = (
        int(self.frameSize().width() / 2)-4, int(self.frameSize().height() / 2)-4)
        aiming_dot.move(middle_coordinates[0], middle_coordinates[1]-42)
        print(self.mesh_viewer.frameSize().width(), self.mesh_viewer.frameSize().height())


def main():
    app = QApplication(sys.argv)
    window = MainWindow()
    window.show()
    sys.exit(app.exec())


if __name__ == '__main__':
    main()
