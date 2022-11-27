import sys
from pathlib import Path

from PyQt6.QtCore import QSize, Qt
from PyQt6.QtGui import QPixmap
from PyQt6.QtWidgets import QApplication, QMainWindow, QPushButton, QVBoxLayout, QHBoxLayout, QWidget, \
    QFileDialog, QLabel, QLineEdit, QSplitter, QDoubleSpinBox

from Viewer import Viewer


class MainWindow(QMainWindow):
    def __init__(self):
        super(MainWindow, self).__init__()
        self.setWindowTitle('MeshCataloger')
        self.mesh_viewer = Viewer()
        self.text = QLabel()
        self.button = QPushButton()
        self.viewer_size = QSize()

        split_view = QSplitter(Qt.Orientation.Horizontal)
        split_view.addWidget(self.init_left_view())
        split_view.addWidget(self.init_right_view())

        self.setCentralWidget(split_view)
        self.setMinimumSize(750, 500)
        self.init_aiming_dot()

    def init_left_view(self):
        left_layout = QVBoxLayout()
        bottom_layout = self.init_button_and_text()
        left_layout.addWidget(self.mesh_viewer)
        left_layout.addLayout(bottom_layout)
        left_view = QWidget()
        left_view.setLayout(left_layout)
        self.viewer_size = left_view.size() - QSize(0, 50)
        return left_view

    def init_right_view(self):
        right_layout = QVBoxLayout()

        text_input_instruction = QLabel()
        text_input_instruction.setText("Serial number format")
        right_layout.addWidget(text_input_instruction)

        text_input = QLineEdit()
        # text_input.setPlaceholderText("Enter text")
        right_layout.addWidget(text_input)

        iteration_input_instruction = QLabel()
        iteration_input_instruction.setText("Number of iterations")
        right_layout.addWidget(iteration_input_instruction)

        iteration_number_input = QDoubleSpinBox()
        right_layout.addWidget(iteration_number_input)

        right_layout.addStretch()

        right_view = QWidget()
        right_view.setLayout(right_layout)
        return right_view

    def init_button_and_text(self):
        self.button.setText("Load file")
        layout = QHBoxLayout()
        self.button.setFixedSize(100, 50)
        self.button.clicked.connect(self.clicked_file_button)
        self.text.setText("Please select a file")
        layout.addWidget(self.text)
        layout.addWidget(self.button)
        return layout

    def init_aiming_dot(self):
        aiming_dot = QLabel(self)
        scaling_down = QSize(6, 6)
        pixmap = QPixmap("red_dot.png").scaled(scaling_down)
        aiming_dot.setPixmap(pixmap)
        middle_coordinates = self.viewer_size / 2
        aiming_dot.move(middle_coordinates.width(), middle_coordinates.height() + 8)

    """
    def resizeEvent(self, event):
        print("Window_resized")
        QMainWindow.resizeEvent(self, event)
    """

    def clicked_file_button(self):
        home_directory = str(Path.home())
        data = QFileDialog.getOpenFileName(self, 'Open file', home_directory, filter="*.stl")
        file_name = data[0]
        self.mesh_viewer.show_stl(file_name)
        self.text.setText("Select a face ( aim + right click )")
        self.button.setText("Select face")
        self.button.disconnect()
        self.button.clicked.connect(self.clicked_face_button)

    def clicked_face_button(self):
        for item in self.mesh_viewer.displayed_items:
            if item['name'] == "face":
                selected_face = item['mesh']
                self.text.setText(str(selected_face))


def main():
    app = QApplication(sys.argv)
    window = MainWindow()
    window.show()
    sys.exit(app.exec())


if __name__ == '__main__':
    main()
