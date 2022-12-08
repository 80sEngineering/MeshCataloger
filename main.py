import sys
from pathlib import Path

from PyQt6.QtCore import Qt
from PyQt6.QtWidgets import QApplication, QMainWindow, QPushButton, QVBoxLayout, QHBoxLayout, QGridLayout, QWidget, \
    QFileDialog, QLabel, QLineEdit, QSplitter, QDoubleSpinBox

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
        self.right_layout = QVBoxLayout()
        self.rotation_layout = QHBoxLayout()
        self.translate_layout = QHBoxLayout()
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
        self.right_layout.addStretch()
        text_input_instruction = QLabel()
        text_input_instruction.setText("Serial number format")
        """

        Function for custom formatting
        pg.SpinBox(value=4567, step=1, int=True, bounds=[0, None], format='0x{value:X}',
                   regex='(0x)?(?P<number>[0-9a-fA-F]+)$',
                   evalFunc=lambda s: ast.literal_eval('0x' + s)))
        """
        self.right_layout.insertWidget(0, text_input_instruction)

        self.text_input.setPlaceholderText("Part number *")
        self.right_layout.insertWidget(1, self.text_input)

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
        self.right_layout.insertLayout(2, upper_grid_layout)

        self.apply_number_button.setText("Apply serial number")
        self.apply_number_button.clicked.connect(self.clicked_apply_number)
        self.right_layout.insertWidget(3, self.apply_number_button)

        right_view = QWidget()
        right_view.setLayout(self.right_layout)
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
        self.hide_transformation_layout()

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
        if self.right_layout.layout().count() < 6:
            self.show_transformation_layout()
        self.mesh_viewer.show_char(files)

    def show_transformation_layout(self):
        x_label, y_label, z_label = QLabel("X:"), QLabel("Y:"), QLabel("Z:")
        x_rot_spin, y_rot_spin, z_rot_spin = QDoubleSpinBox(), QDoubleSpinBox(), QDoubleSpinBox()
        x_trans_spin, y_trans_spin, z_trans_spin = QDoubleSpinBox(), QDoubleSpinBox(), QDoubleSpinBox()
        widget_list = [x_label, x_rot_spin, y_label, y_rot_spin, z_label, z_rot_spin]
        for layout in range(2):
            for widget in widget_list:
                if type(widget) == QLabel:
                    widget.adjustSize()
                elif type(widget) == QDoubleSpinBox:
                    widget.setMaximum(1000)
                    widget.setMinimum(-1000)
                    widget.setSingleStep(5)
                if layout == 0:  # Rotation layout
                    self.rotation_layout.addWidget(widget)
                else:
                    self.translate_layout.addWidget(widget)

            x_label, y_label, z_label = QLabel("X:"), QLabel("Y:"), QLabel("Z:")
            widget_list = [x_label, x_trans_spin, y_label, y_trans_spin, z_label, z_trans_spin]

        self.rotation_layout.setSpacing(5)
        self.translate_layout.setSpacing(5)

        rotation_label = QLabel("Rotation")
        rotation_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.right_layout.insertWidget(4, rotation_label)
        self.right_layout.insertLayout(5, self.rotation_layout)

        translate_label = QLabel("Translation")
        translate_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.right_layout.insertWidget(6, translate_label)
        self.right_layout.insertLayout(7, self.translate_layout)

        apply_transformation_button = QPushButton("Apply transformation")
        apply_transformation_button.clicked.connect(
            lambda: self.apply_transformation(x_rot_spin, y_rot_spin, z_rot_spin, x_trans_spin, y_trans_spin,
                                              z_trans_spin))
        self.right_layout.insertWidget(8, apply_transformation_button)

    def hide_transformation_layout(self):
        items_to_remove = []
        for index in range(9, 3, -1):
            items_to_remove.append(self.right_layout.takeAt(index))
        for item in items_to_remove:
            if item.widget() is not None:
                item.widget().deleteLater()
            elif item.layout() is not None:
                while item.layout().count():
                    widget = item.layout().takeAt(0)
                    widget.widget().deleteLater()
        self.right_layout.addStretch()

    def apply_transformation(self, x_rot_spin, y_rot_spin, z_rot_spin, x_trans_spin, y_trans_spin, z_trans_spin):
        self.mesh_viewer.rotate_char([1, 0, 0], x_rot_spin.value())
        self.mesh_viewer.rotate_char([0, 1, 0], y_rot_spin.value())
        self.mesh_viewer.rotate_char([0, 0, 1], z_rot_spin.value())
        self.mesh_viewer.translate_char([1, 0, 0], x_trans_spin.value())
        self.mesh_viewer.translate_char([0, 1, 0], y_trans_spin.value())
        self.mesh_viewer.translate_char([0, 0, 1], z_trans_spin.value())


def main():
    app = QApplication(sys.argv)
    window = MainWindow()
    window.show()
    sys.exit(app.exec())


if __name__ == '__main__':
    main()
