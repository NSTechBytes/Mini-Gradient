import sys
from PyQt5.QtWidgets import (QApplication, QWidget, QPushButton, QLabel, QFileDialog, QVBoxLayout, 
                             QColorDialog, QMessageBox, QLineEdit, QHBoxLayout, QProgressBar, QComboBox)
from PyQt5.QtCore import Qt, QThread, pyqtSignal
from PyQt5.QtGui import QIcon
from PIL import Image, ImageDraw
import os

class GradientWorker(QThread):
    progressChanged = pyqtSignal(int)
    completed = pyqtSignal()

    def __init__(self, image_paths, gradient1, gradient2, output_folder, resolution):
        super().__init__()
        self.image_paths = image_paths
        self.gradient1 = gradient1
        self.gradient2 = gradient2
        self.output_folder = output_folder
        self.resolution = resolution

    def run(self):
        total_images = len(self.image_paths)
        for index, img_path in enumerate(self.image_paths):
            self.apply_gradient_to_image(img_path)
            progress = int((index + 1) / total_images * 100)
            self.progressChanged.emit(progress)
        self.completed.emit()

    def apply_gradient_to_image(self, img_path):
        img = Image.open(img_path).convert("RGBA")

        if self.resolution == 'Original':
            width, height = img.size
        else:
            width, height = map(int, self.resolution.split('x'))

        img = img.resize((width, height))

        gradient = Image.new('RGBA', (width, height))
        draw = ImageDraw.Draw(gradient)

        for i in range(height):
            ratio = i / height
            r = int(self.gradient1[0] * (1 - ratio) + self.gradient2[0] * ratio)
            g = int(self.gradient1[1] * (1 - ratio) + self.gradient2[1] * ratio)
            b = int(self.gradient1[2] * (1 - ratio) + self.gradient2[2] * ratio)

            for j in range(width):
                pixel = img.getpixel((j, i))
                if pixel[3] > 0:  # Apply gradient only to non-transparent pixels
                    draw.point((j, i), fill=(r, g, b, pixel[3]))

        blended = Image.alpha_composite(img, gradient)

        # Save the image to the selected output folder with the original name
        base_name = os.path.basename(img_path)
        save_path = os.path.join(self.output_folder, base_name)
        blended.save(save_path)

class MiniGradient(QWidget):
    def __init__(self):
        super().__init__()

        self.initUI()

    def initUI(self):
        self.setWindowTitle('Mini Gradient')
        self.setGeometry(300, 300, 400, 400)
        self.setFixedSize(600,500)
        self.setWindowIcon(QIcon('icons/Mini Gradient.png'))  # Set the window icon

        layout = QVBoxLayout()

        # Buttons for selecting images and gradients
        self.select_images_btn = QPushButton(QIcon('icons/add.png'), 'Select PNG Images', self)
        self.select_images_btn.clicked.connect(self.select_images)
        layout.addWidget(self.select_images_btn)

        # Input fields for RGB values of first and second gradient colors
        color_layout1 = QHBoxLayout()
        self.gradient1_label = QLabel('First Color (RGB):', self)
        self.gradient1_r = QLineEdit(self)
        self.gradient1_g = QLineEdit(self)
        self.gradient1_b = QLineEdit(self)
        self.gradient1_btn = QPushButton(QIcon('icons/picker.png'), 'Pick First Color', self)
        self.gradient1_btn.clicked.connect(self.select_gradient1)
        color_layout1.addWidget(self.gradient1_label)
        color_layout1.addWidget(self.gradient1_r)
        color_layout1.addWidget(self.gradient1_g)
        color_layout1.addWidget(self.gradient1_b)
        color_layout1.addWidget(self.gradient1_btn)
        layout.addLayout(color_layout1)

        color_layout2 = QHBoxLayout()
        self.gradient2_label = QLabel('Second Color (RGB):', self)
        self.gradient2_r = QLineEdit(self)
        self.gradient2_g = QLineEdit(self)
        self.gradient2_b = QLineEdit(self)
        self.gradient2_btn = QPushButton(QIcon('icons/picker.png'), 'Pick Second Color', self)
        self.gradient2_btn.clicked.connect(self.select_gradient2)
        color_layout2.addWidget(self.gradient2_label)
        color_layout2.addWidget(self.gradient2_r)
        color_layout2.addWidget(self.gradient2_g)
        color_layout2.addWidget(self.gradient2_b)
        color_layout2.addWidget(self.gradient2_btn)
        layout.addLayout(color_layout2)

        # Resolution Selection
        self.resolution_label = QLabel('Resolution (Original or Custom):', self)
        self.resolution_combo = QComboBox(self)
        self.resolution_combo.addItem('Original')
        self.resolution_combo.addItem('1920x1080')
        self.resolution_combo.addItem('1280x720')
        self.resolution_combo.addItem('800x600')

        self.custom_width = QLineEdit(self)
        self.custom_height = QLineEdit(self)
        self.custom_width.setPlaceholderText('Width')
        self.custom_height.setPlaceholderText('Height')

        layout.addWidget(self.resolution_label)
        layout.addWidget(self.resolution_combo)
        layout.addWidget(self.custom_width)
        layout.addWidget(self.custom_height)

        # Button for selecting output folder
        self.select_output_btn = QPushButton(QIcon('icons/save.png'), 'Select Output Folder', self)
        self.select_output_btn.clicked.connect(self.select_output_folder)
        layout.addWidget(self.select_output_btn)

        self.apply_gradient_btn = QPushButton(QIcon('icons/apply.png'), 'Apply Gradient and Save', self)
        self.apply_gradient_btn.clicked.connect(self.apply_gradient)
        layout.addWidget(self.apply_gradient_btn)

        # Progress Bar and Percentage
        self.progress_bar = QProgressBar(self)
        self.progress_bar.setValue(0)
        layout.addWidget(self.progress_bar)

        self.label = QLabel('Select PNG images, gradient colors, and output folder', self)
        self.label.setAlignment(Qt.AlignCenter)
        layout.addWidget(self.label)

        self.setLayout(layout)

        self.image_paths = []
        self.output_folder = ''
        self.gradient1 = (255, 0, 0)  # Default gradient color 1 (red)
        self.gradient2 = (0, 0, 255)  # Default gradient color 2 (blue)

    def select_images(self):
        options = QFileDialog.Options()
        files, _ = QFileDialog.getOpenFileNames(self, "Select PNG Images", "", "PNG Files (*.png)", options=options)
        if files:
            self.image_paths = files
            self.label.setText(f"{len(files)} images selected")

    def select_output_folder(self):
        folder = QFileDialog.getExistingDirectory(self, "Select Output Folder")
        if folder:
            self.output_folder = folder
            self.label.setText(f"Output folder selected: {self.output_folder}")

    def select_gradient1(self):
        color = QColorDialog.getColor()
        if color.isValid():
            self.gradient1 = color.getRgb()[:3]
            self.gradient1_r.setText(str(self.gradient1[0]))
            self.gradient1_g.setText(str(self.gradient1[1]))
            self.gradient1_b.setText(str(self.gradient1[2]))
            self.label.setText(f"First Gradient Color: {self.gradient1}")

    def select_gradient2(self):
        color = QColorDialog.getColor()
        if color.isValid():
            self.gradient2 = color.getRgb()[:3]
            self.gradient2_r.setText(str(self.gradient2[0]))
            self.gradient2_g.setText(str(self.gradient2[1]))
            self.gradient2_b.setText(str(self.gradient2[2]))
            self.label.setText(f"Second Gradient Color: {self.gradient2}")

    def apply_gradient(self):
        # Get the RGB values from the input fields if available
        try:
            self.gradient1 = (int(self.gradient1_r.text()), int(self.gradient1_g.text()), int(self.gradient1_b.text()))
            self.gradient2 = (int(self.gradient2_r.text()), int(self.gradient2_g.text()), int(self.gradient2_b.text()))
        except ValueError:
            QMessageBox.warning(self, 'Invalid RGB Value', 'Please enter valid RGB values for both colors.')
            return

        if not self.image_paths:
            QMessageBox.warning(self, 'No Images Selected', 'Please select PNG images first.')
            return

        if not self.output_folder:
            QMessageBox.warning(self, 'No Output Folder Selected', 'Please select an output folder.')
            return

        # Get custom resolution if selected
        if self.resolution_combo.currentText() == 'Original':
            resolution = 'Original'
        else:
            try:
                custom_width = int(self.custom_width.text())
                custom_height = int(self.custom_height.text())
                resolution = f"{custom_width}x{custom_height}"
            except ValueError:
                QMessageBox.warning(self, 'Invalid Resolution', 'Please enter valid width and height.')
                return

        # Create a worker thread for applying the gradient
        self.worker = GradientWorker(self.image_paths, self.gradient1, self.gradient2, self.output_folder, resolution)
        self.worker.progressChanged.connect(self.update_progress)
        self.worker.completed.connect(self.reset_gui)
        self.worker.start()

    def update_progress(self, value):
        self.progress_bar.setValue(value)

    def reset_gui(self):
        self.progress_bar.setValue(0)
        self.image_paths = []
        self.output_folder = ''
        self.gradient1 = (255, 0, 0)
        self.gradient2 = (0, 0, 255)
        self.gradient1_r.clear()
        self.gradient1_g.clear()
        self.gradient1_b.clear()
        self.gradient2_r.clear()
        self.gradient2_g.clear()
        self.gradient2_b.clear()
        self.custom_width.clear()
        self.custom_height.clear()
        self.resolution_combo.setCurrentIndex(0)  # Reset to 'Original'
        self.label.setText('Operation Complete! Select PNG images, gradient colors, and output folder')

if __name__ == '__main__':
    app = QApplication(sys.argv)
    ex = MiniGradient()
    ex.show()
    sys.exit(app.exec_())
