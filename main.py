#!/usr/bin/python

import sys
import torch
from PyQt6.QtWidgets import (QApplication, QMainWindow, QWidget, QVBoxLayout, QHBoxLayout, QLabel, QLineEdit, QPushButton, QSlider, QTextEdit)
from PyQt6.QtCore import Qt, QTimer
from transformers import MarianMTModel, MarianTokenizer

class TranslatorApp(QMainWindow):
    def __init__(self):
        super().__init__()

        # Configuración inicial del modelo y tokenizador
        self.model_name = "Helsinki-NLP/opus-mt-en-es"
        self.tokenizer = MarianTokenizer.from_pretrained(self.model_name)
        self.model = MarianMTModel.from_pretrained(self.model_name)
        self.device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
        self.model = self.model.to(self.device)

        self.is_translating = False
        self.translation_timer = QTimer(self)
        self.translation_timer.timeout.connect(self.translate_text)

        self.initUI()  # Llamar después de inicializar los atributos necesarios

    def initUI(self):
        self.setWindowTitle('Translator App')
        self.setGeometry(100, 100, 600, 300)  # Altura reducida

        # Widget principal y layout vertical
        main_widget = QWidget(self)
        self.setCentralWidget(main_widget)
        main_layout = QVBoxLayout()
        main_widget.setLayout(main_layout)

        # Etiqueta para mostrar el modelo actual
        self.model_label = QLabel(f"Modelo actual: {self.model_name}")
        main_layout.addWidget(self.model_label)

        # Sliders en una línea horizontal
        sliders_layout = QHBoxLayout()

        self.max_length_slider = QSlider(Qt.Orientation.Horizontal)
        self.max_length_slider.setMinimum(64)
        self.max_length_slider.setMaximum(512)
        self.max_length_slider.setValue(128)
        self.max_length_slider.setTickPosition(QSlider.TickPosition.TicksBelow)
        self.max_length_slider.setTickInterval(64)
        self.max_length_slider.valueChanged.connect(self.update_slider_labels)
        sliders_layout.addWidget(QLabel("Máxima longitud de salida:"))
        self.max_length_label = QLabel(f"{self.max_length_slider.value()}")
        sliders_layout.addWidget(self.max_length_label)
        sliders_layout.addWidget(self.max_length_slider)

        self.num_beams_slider = QSlider(Qt.Orientation.Horizontal)
        self.num_beams_slider.setMinimum(1)
        self.num_beams_slider.setMaximum(8)
        self.num_beams_slider.setValue(4)
        self.num_beams_slider.setTickPosition(QSlider.TickPosition.TicksBelow)
        self.num_beams_slider.setTickInterval(1)
        self.num_beams_slider.valueChanged.connect(self.update_slider_labels)
        sliders_layout.addWidget(QLabel("Número de beams:"))
        self.num_beams_label = QLabel(f"{self.num_beams_slider.value()}")
        sliders_layout.addWidget(self.num_beams_label)
        sliders_layout.addWidget(self.num_beams_slider)

        main_layout.addLayout(sliders_layout)

        # Frame y QTextEdit para el texto de origen
        source_frame = QWidget()
        source_layout = QVBoxLayout()
        source_frame.setLayout(source_layout)
        source_layout.addWidget(QLabel("Texto de Origen"))
        self.source_textedit = QTextEdit()
        source_layout.addWidget(self.source_textedit, 1)
        main_layout.addWidget(source_frame)

        # Frame y QTextEdit para el texto traducido
        target_frame = QWidget()
        target_layout = QVBoxLayout()
        target_frame.setLayout(target_layout)
        target_layout.addWidget(QLabel("Texto Traducido"))
        self.target_textedit = QTextEdit()
        self.target_textedit.setReadOnly(True)
        target_layout.addWidget(self.target_textedit, 1)
        main_layout.addWidget(target_frame)

        # Botones para controlar la traducción
        btn_layout = QHBoxLayout()
        main_layout.addLayout(btn_layout)

        self.start_btn = QPushButton("Iniciar Traducción")
        self.start_btn.clicked.connect(self.start_translation)
        btn_layout.addWidget(self.start_btn)

        self.stop_btn = QPushButton("Detener Traducción")
        self.stop_btn.setEnabled(False)
        self.stop_btn.clicked.connect(self.stop_translation)
        btn_layout.addWidget(self.stop_btn)

        self.close_btn = QPushButton("Cerrar")
        self.close_btn.clicked.connect(self.close)
        btn_layout.addWidget(self.close_btn)

        # Mostrar la ventana principal
        self.show()

    def update_slider_labels(self):
        self.max_length_label.setText(f"{self.max_length_slider.value()}")
        self.num_beams_label.setText(f"{self.num_beams_slider.value()}")

    def start_translation(self):
        if self.is_translating:
            QMessageBox.warning(self, "Advertencia", "Ya se está realizando una traducción.")
            return
        
        self.is_translating = True
        self.start_btn.setEnabled(False)
        self.stop_btn.setEnabled(True)

        # Iniciar el timer para la traducción continua
        self.translation_timer.start(1000)  # Cada segundo

    def stop_translation(self):
        self.is_translating = False
        self.translation_timer.stop()
        self.start_btn.setEnabled(True)
        self.stop_btn.setEnabled(False)

    def translate_text(self):
        # Obtener los valores de los sliders
        max_length = self.max_length_slider.value()
        num_beams = self.num_beams_slider.value()

        # Texto a traducir
        texto_en_ingles = self.source_textedit.toPlainText()

        # Traducción del texto
        inputs = self.tokenizer(texto_en_ingles, return_tensors="pt").to(self.device)
        translated_ids = self.model.generate(inputs["input_ids"], max_length=max_length, num_beams=num_beams, early_stopping=True)
        translated_text = self.tokenizer.decode(translated_ids[0], skip_special_tokens=True)

        # Mostrar resultados en el QTextEdit de destino
        self.target_textedit.setPlainText(translated_text)

    def closeEvent(self, event):
        # Detener la traducción al cerrar la ventana
        if self.is_translating:
            self.stop_translation()
        event.accept()

if __name__ == '__main__':
    app = QApplication(sys.argv)
    ex = TranslatorApp()
    sys.exit(app.exec())
