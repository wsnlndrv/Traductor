#!/usr/bin/python
# gui.py
import os
import subprocess
from PyQt6.QtWidgets import *
from PyQt6.QtCore import Qt, QTimer

class TranslatorApp(QMainWindow):
    def __init__(self, model_name, tokenizer, model, device):
        super().__init__()

        self.model_name = model_name
        self.tokenizer = tokenizer
        self.model = model
        self.device = device
        self.current_folder = None

        self.is_translating = False
        self.translation_timer = QTimer(self)
        self.translation_timer.timeout.connect(self.translate_text)

        self.initUI()

    def initUI(self):
        self.setWindowTitle('Translateador pofesioná')
        self.setGeometry(100, 100, 800, 900)

        main_widget = QWidget(self)
        self.setCentralWidget(main_widget)
        main_layout = QVBoxLayout()
        main_widget.setLayout(main_layout)

        self.model_label = QLabel(f"Current Model: {self.model_name}")
        main_layout.addWidget(self.model_label)

        sliders_layout = QVBoxLayout()

        # Row 1: max_length_slider and num_beams_slider
        row1_layout = QHBoxLayout()
        self.max_length_label = QLabel(f"Maximum Output Length: {512}")
        self.max_length_slider = QSlider(Qt.Orientation.Horizontal)
        self.max_length_slider.setMinimum(128)
        self.max_length_slider.setMaximum(1024)
        self.max_length_slider.setValue(512)
        self.max_length_slider.setTickPosition(QSlider.TickPosition.TicksBelow)
        self.max_length_slider.setTickInterval(64)
        self.max_length_slider.valueChanged.connect(self.update_slider_labels)
        row1_layout.addWidget(self.max_length_label)
        row1_layout.addWidget(self.max_length_slider)

        self.num_beams_label = QLabel(f"Number of Beams: {4}")
        self.num_beams_slider = QSlider(Qt.Orientation.Horizontal)
        self.num_beams_slider.setMinimum(1)
        self.num_beams_slider.setMaximum(8)
        self.num_beams_slider.setValue(4)
        self.num_beams_slider.setTickPosition(QSlider.TickPosition.TicksBelow)
        self.num_beams_slider.setTickInterval(1)
        self.num_beams_slider.valueChanged.connect(self.update_slider_labels)
        row1_layout.addWidget(self.num_beams_label)
        row1_layout.addWidget(self.num_beams_slider)
        sliders_layout.addLayout(row1_layout)

        # Row 2: temperature_slider and repetition_penalty_slider
        row2_layout = QHBoxLayout()
        self.temperature_label = QLabel(f"Temperature: {1.0}")
        self.temperature_slider = QSlider(Qt.Orientation.Horizontal)
        self.temperature_slider.setMinimum(1)
        self.temperature_slider.setMaximum(20)
        self.temperature_slider.setValue(10)
        self.temperature_slider.setTickPosition(QSlider.TickPosition.TicksBelow)
        self.temperature_slider.setTickInterval(1)
        self.temperature_slider.valueChanged.connect(self.update_slider_labels)
        row2_layout.addWidget(self.temperature_label)
        row2_layout.addWidget(self.temperature_slider)

        self.repetition_penalty_label = QLabel(f"Repetition Penalty: {1.2}")
        self.repetition_penalty_slider = QSlider(Qt.Orientation.Horizontal)
        self.repetition_penalty_slider.setMinimum(10)
        self.repetition_penalty_slider.setMaximum(20)
        self.repetition_penalty_slider.setValue(12)
        self.repetition_penalty_slider.setTickPosition(QSlider.TickPosition.TicksBelow)
        self.repetition_penalty_slider.setTickInterval(1)
        self.repetition_penalty_slider.valueChanged.connect(self.update_slider_labels)
        row2_layout.addWidget(self.repetition_penalty_label)
        row2_layout.addWidget(self.repetition_penalty_slider)
        sliders_layout.addLayout(row2_layout)

        # Row 3: length_penalty_slider and no_repeat_ngram_size_slider
        row3_layout = QHBoxLayout()
        self.length_penalty_label = QLabel(f"Length Penalty: {1.0}")
        self.length_penalty_slider = QSlider(Qt.Orientation.Horizontal)
        self.length_penalty_slider.setMinimum(1)
        self.length_penalty_slider.setMaximum(20)
        self.length_penalty_slider.setValue(10)
        self.length_penalty_slider.setTickPosition(QSlider.TickPosition.TicksBelow)
        self.length_penalty_slider.setTickInterval(1)
        self.length_penalty_slider.valueChanged.connect(self.update_slider_labels)
        row3_layout.addWidget(self.length_penalty_label)
        row3_layout.addWidget(self.length_penalty_slider)

        self.no_repeat_ngram_size_label = QLabel(f"No Repeat N-gram Size: {0}")
        self.no_repeat_ngram_size_slider = QSlider(Qt.Orientation.Horizontal)
        self.no_repeat_ngram_size_slider.setMinimum(0)
        self.no_repeat_ngram_size_slider.setMaximum(5)
        self.no_repeat_ngram_size_slider.setValue(0)
        self.no_repeat_ngram_size_slider.setTickPosition(QSlider.TickPosition.TicksBelow)
        self.no_repeat_ngram_size_slider.setTickInterval(1)
        self.no_repeat_ngram_size_slider.valueChanged.connect(self.update_slider_labels)
        row3_layout.addWidget(self.no_repeat_ngram_size_label)
        row3_layout.addWidget(self.no_repeat_ngram_size_slider)
        sliders_layout.addLayout(row3_layout)

        main_layout.addLayout(sliders_layout)


        self.progress_bar = QProgressBar()
        main_layout.addWidget(self.progress_bar)

        btn_layout = QHBoxLayout()
        main_layout.addLayout(btn_layout)

        self.select_folder_btn = QPushButton("Seleccionar carpeta")
        self.select_folder_btn.clicked.connect(self.select_folder)
        btn_layout.addWidget(self.select_folder_btn)

        self.load_files_btn = QPushButton("Cargar *.rpy")
        self.load_files_btn.clicked.connect(self.load_files)
        btn_layout.addWidget(self.load_files_btn)

        self.start_btn = QPushButton("Tranducir")
        self.start_btn.clicked.connect(self.start_translation)
        self.start_btn.setEnabled(False)
        btn_layout.addWidget(self.start_btn)

        self.stop_btn = QPushButton("Parar traducción")
        self.stop_btn.setEnabled(False)
        self.stop_btn.clicked.connect(self.stop_translation)
        btn_layout.addWidget(self.stop_btn)

        self.close_btn = QPushButton("Cerrar")
        self.close_btn.clicked.connect(self.close)
        btn_layout.addWidget(self.close_btn)

        new_btn_layout = QHBoxLayout()
        main_layout.addLayout(new_btn_layout)

        self.detect_btn = QPushButton("Detectar")
        self.detect_btn.clicked.connect(self.detect_files)
        new_btn_layout.addWidget(self.detect_btn)

        self.unzip_btn = QPushButton("Descomprimir")
        self.unzip_btn.clicked.connect(self.unzip_file)
        new_btn_layout.addWidget(self.unzip_btn)

        self.del_rpyc_btn = QPushButton("Eliminar-RpyC")
        self.del_rpyc_btn.clicked.connect(self.delete_rpyc_files)
        new_btn_layout.addWidget(self.del_rpyc_btn)

        self.unrpa_btn = QPushButton("UnRpa")
        self.unrpa_btn.clicked.connect(self.unrpa_files)
        new_btn_layout.addWidget(self.unrpa_btn)

        self.unpyc_btn = QPushButton("UnRpyC")
        self.unpyc_btn.clicked.connect(self.unpyc_files)
        new_btn_layout.addWidget(self.unpyc_btn)

        bottom_frame = QFrame()
        bottom_frame.setFrameShape(QFrame.Shape.StyledPanel)
        bottom_layout = QVBoxLayout()
        bottom_frame.setLayout(bottom_layout)

        self.file_list_widget = QListWidget()
        self.file_list_widget.setSelectionMode(QAbstractItemView.SelectionMode.MultiSelection)
        bottom_layout.addWidget(self.file_list_widget)

        main_layout.addWidget(bottom_frame)

        self.show()

    def update_slider_labels(self):
        self.max_length_label.setText(f"Maximum Output Length: {self.max_length_slider.value()}")
        self.num_beams_label.setText(f"Number of Beams: {self.num_beams_slider.value()}")
        self.temperature_label.setText(f"Temperature: {self.temperature_slider.value() / 10.0}")
        self.repetition_penalty_label.setText(f"Repetition Penalty: {self.repetition_penalty_slider.value() / 10.0}")
        self.length_penalty_label.setText(f"Length Penalty: {self.length_penalty_slider.value() / 10.0}")
        self.no_repeat_ngram_size_label.setText(f"No Repeat N-gram Size: {self.no_repeat_ngram_size_slider.value()}")

    def load_files(self):
        files, _ = QFileDialog.getOpenFileNames(self, "Select files to translate", "", "RPY Files (*.rpy)")
        self.file_list_widget.clear()
        self.files_to_translate = files
        self.file_list_widget.addItems(files)
        self.start_btn.setEnabled(True)

    def start_translation(self):
        self.is_translating = True
        self.translation_timer.start(100)
        self.start_btn.setEnabled(False)
        self.stop_btn.setEnabled(True)

    def stop_translation(self):
        self.is_translating = False
        self.translation_timer.stop()
        self.start_btn.setEnabled(True)
        self.stop_btn.setEnabled(False)
        QMessageBox.information(self, "Translation Stopped", "Translation process has been stopped.")

    def translate_text_in_file(self, file_path):
        self.parent().translate_text_in_file(file_path)

    def translate_text(self):
        if not self.files_to_translate:
            self.stop_translation()
            return

        file_path = self.files_to_translate.pop(0)
        self.translate_text_in_file(file_path)

    def select_folder(self):
        folder = QFileDialog.getExistingDirectory(self, "Select a folder")
        if folder:
            self.current_folder = folder
            self.detect_files()

    def detect_files(self):
        if self.current_folder:
            self.file_list_widget.clear()
            files = []
            for root, dirs, files_in_dir in os.walk(self.current_folder):
                for file in files_in_dir:
                    if file.endswith(('.rpy', '.rpa', '.rpyc')):
                        files.append(os.path.join(root, file))
            self.files_to_translate = files
            self.file_list_widget.addItems(files)
            self.start_btn.setEnabled(True)
        else:
            QMessageBox.warning(self, "No Folder Selected", "Please select a folder first.")

    def unzip_file(self):
        zip_file, _ = QFileDialog.getOpenFileName(self, "Select a .zip file to extract", "", "ZIP Files (*.zip)")
        if zip_file:
            destination_folder = QFileDialog.getExistingDirectory(self, "Select destination folder for extraction", "")
            if destination_folder:
                try:
                    subprocess.run(['unzip', '-q', zip_file, '-d', destination_folder], check=True)
                    QMessageBox.information(self, "Extraction Complete", "ZIP file extracted successfully.")
                except subprocess.CalledProcessError as e:
                    QMessageBox.critical(self, "Extraction Error", f"Failed to extract ZIP file.\nError: {str(e)}")

    def delete_rpyc_files(self):
        folder = QFileDialog.getExistingDirectory(self, "Select folder to delete .rpyc files recursively", "")
        if folder:
            try:
                for root, dirs, files in os.walk(folder):
                    for file in files:
                        if file.endswith(".rpyc"):
                            os.remove(os.path.join(root, file))
                QMessageBox.information(self, "Deletion Complete", ".rpyc files deleted successfully.")
            except Exception as e:
                QMessageBox.critical(self, "Deletion Error", f"Failed to delete .rpyc files.\nError: {str(e)}")

    def unrpa_files(self):
        rpa_file, _ = QFileDialog.getOpenFileName(self, "Select an .rpa file to extract", "", "RPA Files (*.rpa)")
        if rpa_file:
            destination_folder = os.path.dirname(rpa_file)
            try:
                # Ejecutar el comando unrpa
                subprocess.run(['unrpa', '-mp', destination_folder, rpa_file], check=True)
                # Renombrar el archivo .rpa a .rpb
                new_file_name = rpa_file.replace('.rpa', '.rpa-backup')
                os.rename(rpa_file, new_file_name)
                QMessageBox.information(self, "Extraction Complete", f"RPA file extracted successfully to {destination_folder}.\nOriginal RPA file renamed to {new_file_name}.")
            except subprocess.CalledProcessError as e:
                QMessageBox.critical(self, "Extraction Error", f"Failed to extract RPA file.\nError: {str(e)}")
            except Exception as e:
                QMessageBox.critical(self, "Renaming Error", f"Failed to rename RPA file.\nError: {str(e)}")

    def unpyc_files(self):
        files, _ = QFileDialog.getOpenFileNames(self, "Select .rpyc files to decompile", "", "RPYC Files (*.rpyc)")
        if files:
            destination_folder = QFileDialog.getExistingDirectory(self, "Select destination folder for decompiled files", "")
            if destination_folder:
                try:
                    for file in files:
                        output_file = os.path.join(destination_folder, os.path.basename(file).replace('.rpyc', '.rpy'))
                        subprocess.run(['unrpyc', file], check=True)
                    QMessageBox.information(self, "Decompilation Complete", "Selected .rpyc files have been decompiled successfully.")
                except subprocess.CalledProcessError as e:
                    QMessageBox.critical(self, "Decompilation Error", f"Failed to decompile .rpyc files.\nError: {str(e)}")
                except Exception as e:
                    QMessageBox.critical(self, "Decompilation Error", f"An error occurred during the decompilation process.\nError: {str(e)}")

    def closeEvent(self, event):
        if self.is_translating:
            self.stop_translation()
        event.accept()
