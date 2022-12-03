import sys
from pathlib import Path

from PyQt6.QtCore import Qt
from PyQt6.QtWidgets import QApplication, QMainWindow, QPushButton, QVBoxLayout, QHBoxLayout, QGridLayout, QWidget, \
    QFileDialog, QLabel, QLineEdit, QSplitter, QDoubleSpinBox, QDial

from Viewer import Viewer


class MainWindow(QMainWindow):
    def __init__(self):
        super(MainWindow, self).__init__()
        self.setWindowTitle('MeshCataloger')
        self.mesh_viewer = Viewer()
        self.text = QLabel()
        self.file_name = QLabel()
        self.load_button = QPushButton()
        self.text_input = QLineEdit()
        self.first_part_number = QDoubleSpinBox()
        self.last_part_number = QDoubleSpinBox()
        self.apply_number_button = QPushButton()
        print(self.frameSize())
        split_view = QSplitter(Qt.Orientation.Horizontal)
        split_view.addWidget(self.init_left_view())
        split_view.addWidget(self.init_right_view())
        self.setCentralWidget(split_view)

    def init_left_view(self):
        left_layout = QVBoxLayout()
        bottom_layout = self.init_button_and_text()
        left_layout.addWidget(self.mesh_viewer)
        left_layout.addLayout(bottom_layout)
        left_view = QWidget()
        left_view.setLayout(left_layout)
        return left_view

    def init_right_view(self):
        right_layout = QVBoxLayout()
        text_input_instruction = QLabel()
        text_input_instruction.setText("Serial number format")
        right_layout.addWidget(text_input_instruction)

        self.text_input.setPlaceholderText("Part number *")
        right_layout.addWidget(self.text_input)

        upper_grid_layout = QGridLayout()

        first_part_instruction = QLabel("First part number")
        upper_grid_layout.addWidget(first_part_instruction, 0, 0)

        self.first_part_number.setMaximum(9999)
        self.first_part_number.setDecimals(0)
        upper_grid_layout.addWidget(self.first_part_number, 1, 0)

        last_part_instruction = QLabel("Last part number")
        upper_grid_layout.addWidget(last_part_instruction, 0, 1)

        self.last_part_number.setMaximum(10000)
        self.last_part_number.setDecimals(0)
        upper_grid_layout.addWidget(self.last_part_number, 1, 1)
        right_layout.addLayout(upper_grid_layout)

        self.apply_number_button.setText("Apply serial number")
        self.apply_number_button.clicked.connect(self.clicked_apply_number)
        right_layout.addWidget(self.apply_number_button)

        rotation_label = QLabel("Rotation")
        rotation_label.resize(100, 100)
        rotation_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        right_layout.addWidget(rotation_label)

        rotation_layout = QHBoxLayout()

        x_label, y_label, z_label = QLabel("X:"), QLabel("Y:"), QLabel("Z:")
        x_dial, y_dial, z_dial = QDial(), QDial(), QDial()

        rotation_layout.addWidget(x_label)
        rotation_layout.addWidget(x_dial)
        rotation_layout.addWidget(y_label)
        rotation_layout.addWidget(y_dial)
        rotation_layout.addWidget(z_label)
        rotation_layout.addWidget(z_dial)

        right_layout.addLayout(rotation_layout)
        right_layout.addStretch()

        right_view = QWidget()
        right_view.setLayout(right_layout)
        return right_view

    def init_button_and_text(self):
        self.load_button.setText("Load file")
        layout = QHBoxLayout()
        self.load_button.clicked.connect(self.clicked_open_file)
        self.text.setText("Please select a file")
        layout.addWidget(self.text)
        layout.addWidget(self.load_button)
        return layout

    def clicked_open_file(self):
        home_directory = str(Path.home())
        data = QFileDialog.getOpenFileName(self, 'Open file', home_directory, filter="*.stl")
        file_name = data[0]
        self.file_name.setText(file_name[-20:])
        self.mesh_viewer.show_stl(file_name)
        self.mesh_viewer.grid.setVisible(True)
        self.mesh_viewer.axis.setVisible(True)
        self.text.setText("Select a face ( aim + right click )")
        self.load_button.setText("Close file")
        self.load_button.disconnect()
        self.load_button.clicked.connect(self.clicked_close_file)

    def clicked_close_file(self):
        while len(self.mesh_viewer.displayed_items) >= 4:
            self.mesh_viewer.remove_displayed_items("stl")
            self.mesh_viewer.remove_displayed_items("face")
            self.mesh_viewer.remove_displayed_items("char")
            self.mesh_viewer.remove_displayed_items("grid")
            self.mesh_viewer.remove_displayed_items("axis")
        self.mesh_viewer.setCameraParams(center=self.mesh_viewer.center)
        self.load_button.disconnect()
        self.load_button.clicked.connect(self.clicked_open_file)
        self.load_button.setText("Load file")
        self.file_name.setText("")
        self.text.setText("Please select a file")

    def clicked_apply_number(self):
        files = []  # files = ["p.stl","a.stl","r.stl","t.stl"]

        for letter in self.text_input.text():
            if letter == "*":
                stl_char_file = "*"
                files.append(stl_char_file)

            elif letter == " ":
                files.append("space")

            elif letter.isdigit():
                files.append("STL_Characters/" + letter + ".stl")

            else:
                if letter.islower():
                    stl_char_file = "STL_Characters/" + "lower_" + letter + ".stl"

                else:
                    stl_char_file = "STL_Characters/" + "upper_" + letter + ".stl"
                files.append(stl_char_file)

        self.mesh_viewer.show_char(files)


def main():
    app = QApplication(sys.argv)
    window = MainWindow()
    window.show()
    sys.exit(app.exec())


if __name__ == '__main__':
    main()
