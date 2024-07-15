#!/usr/bin/python
# main.py
import sys
import re
import os
import subprocess
from PyQt6.QtWidgets import QApplication, QMessageBox
from gui import TranslatorApp
from transformers import AutoTokenizer, AutoModelForSeq2SeqLM
from langdetect import detect, LangDetectException

# Palabras clave especiales de Ren'Py
SPECIAL_KEYWORDS = ["define", "label", "scene", "show", "hide", "play", "stop", "pause", "queue", "window", "with", "menu", "jump", "call", "return", "if", "elif", "else"]

def is_text_in_target_language(text, target_language_code):
    try:
        detected_language = detect(text)
        return detected_language == target_language_code
    except LangDetectException:
        return False

def should_translate_line(line):
    """Determina si una línea debe ser traducida o no."""
    stripped_line = line.strip()
    if any(stripped_line.startswith(keyword) for keyword in SPECIAL_KEYWORDS):
        return False
    if '{' in stripped_line or '}' in stripped_line or '[' in stripped_line or ']' in stripped_line:
        return False
    return True

def read_lines_with_fallback(file_path, encodings=['utf-8', 'latin-1', 'iso-8859-1']):
    """Intenta leer un archivo con diferentes codificaciones hasta que tenga éxito."""
    for encoding in encodings:
        try:
            with open(file_path, 'r', encoding=encoding) as file:
                return file.readlines()
        except UnicodeDecodeError:
            continue
    # Si todas las codificaciones fallan, volver a leer el archivo ignorando errores
    with open(file_path, 'r', encoding='utf-8', errors='ignore') as file:
        return file.readlines()

def ensure_spaces_around_brackets(text):
    """Asegura que haya espacios alrededor de las variables en corchetes."""
    text = re.sub(r'\[([^\]]+)\]', r' [\1] ', text)
    return text

def preserve_html_colors(text):
    """Preserva los colores HTML dentro de las frases."""
    return re.sub(r'(<[^>]+>)', r' \1 ', text)

def translate_text_in_file(file_path, tokenizer, model, device, max_length, num_beams, temperature, repetition_penalty, length_penalty, no_repeat_ngram_size, progress_callback):
    lines = read_lines_with_fallback(file_path)

    translated_lines = []
    total_lines = len(lines)
    if progress_callback:
        progress_callback(0)

    index = 0
    while index < total_lines:
        line = lines[index]
        stripped_line = line.strip()

        if not should_translate_line(line):
            translated_lines.append(line)
            index += 1
            continue

        if stripped_line.startswith("translate CUSTOM"):
            variable_name = stripped_line.split()[2].strip(":")
            translated_lines.append(line)
            index += 1

            if index < total_lines:
                next_line = lines[index]
                stripped_next_line = next_line.strip()
                if stripped_next_line.startswith("#") or stripped_next_line.startswith("translate"):
                    translated_lines.append(next_line)
                elif '"' in stripped_next_line and not stripped_next_line.startswith("old"):
                    parts = stripped_next_line.split('"')
                    if len(parts) > 1:
                        original_text = parts[1].strip()

                        if is_text_in_target_language(original_text, "es"):
                            translated_lines.append(next_line)
                        else:
                            try:
                                original_text_parts = re.split(r'(\[.*?\]|\{.*?\}|\<.*?\>)', original_text)
                                translated_text_parts = []
                                for part in original_text_parts:
                                    if re.match(r'[\[\]\{\}\<\>]', part):
                                        translated_text_parts.append(part)
                                    else:
                                        inputs = tokenizer(part, return_tensors="pt").to(device)
                                        translated_ids = model.generate(
                                            inputs["input_ids"],
                                            max_length=max_length,
                                            num_beams=num_beams,
                                            temperature=temperature,
                                            repetition_penalty=repetition_penalty,
                                            length_penalty=length_penalty,
                                            no_repeat_ngram_size=no_repeat_ngram_size,
                                            early_stopping=True
                                        )
                                        translated_text = tokenizer.decode(translated_ids[0], skip_special_tokens=True)
                                        translated_text_parts.append(translated_text)

                                translated_text = ''.join(translated_text_parts)
                                translated_text = ensure_spaces_around_brackets(translated_text)
                                translated_text = preserve_html_colors(translated_text)
                            except Exception as e:
                                translated_text = f'{original_text}  # Error: {str(e)}'

                            indentation = next_line[:next_line.index(stripped_next_line)]
                            translated_line = f'{indentation}translate CUSTOM {variable_name}:\n'
                            translated_line += f'{indentation}    "{translated_text}"\n'
                            translated_lines.append(translated_line)
                    else:
                        translated_lines.append(next_line)
                else:
                    translated_lines.append(next_line)
            else:
                translated_lines.append(line)
        elif stripped_line.startswith("#") or stripped_line.startswith("translate"):
            translated_lines.append(line)
        else:
            if '"' in stripped_line and stripped_line.count('"') >= 2 and not stripped_line.startswith("old"):
                parts = stripped_line.split('"')
                if len(parts) >= 3:
                    text_to_translate = parts[1].strip()

                    if is_text_in_target_language(text_to_translate, "es"):
                        translated_lines.append(line)
                    else:
                        try:
                            text_parts = re.split(r'(\[.*?\]|\{.*?\}|\<.*?\>)', text_to_translate)
                            translated_parts = []
                            for part in text_parts:
                                if re.match(r'[\[\]\{\}\<\>]', part):
                                    translated_parts.append(part)
                                else:
                                    inputs = tokenizer(part, return_tensors="pt").to(device)
                                    translated_ids = model.generate(
                                        inputs["input_ids"],
                                        max_length=max_length,
                                        num_beams=num_beams,
                                        temperature=temperature,
                                        repetition_penalty=repetition_penalty,
                                        length_penalty=length_penalty,
                                        no_repeat_ngram_size=no_repeat_ngram_size,
                                        early_stopping=True
                                    )
                                    translated_text = tokenizer.decode(translated_ids[0], skip_special_tokens=True)
                                    translated_parts.append(translated_text)

                            translated_text = ''.join(translated_parts)
                            translated_text = ensure_spaces_around_brackets(translated_text)
                            translated_text = preserve_html_colors(translated_text)
                        except Exception as e:
                            translated_text = f'{text_to_translate}  # Error: {str(e)}'

                        indentation = line[:line.index(stripped_line)]
                        translated_line = f'{indentation}{parts[0]}"{translated_text}"{parts[2]}\n'
                        translated_lines.append(translated_line)
                else:
                    translated_lines.append(line)
            else:
                translated_lines.append(line)

        index += 1
        if progress_callback:
            progress_callback(int((index + 1) / total_lines * 100))

    with open(file_path, 'w', encoding='utf-8') as file:
        file.writelines(translated_lines)

if __name__ == '__main__':
    app = QApplication(sys.argv)

    model_name = "Helsinki-NLP/opus-mt-en-es"
    tokenizer = AutoTokenizer.from_pretrained(model_name)
    model = AutoModelForSeq2SeqLM.from_pretrained(model_name).to("cuda")

    main_window = TranslatorApp(model_name, tokenizer, model, "cuda")
    main_window.translate_text_in_file = lambda file_path: translate_text_in_file(
        file_path,
        tokenizer,
        model,
        "cuda",
        main_window.max_length_slider.value(),
        main_window.num_beams_slider.value(),
        main_window.temperature_slider.value() / 10.0,
        main_window.repetition_penalty_slider.value() / 10.0,
        main_window.length_penalty_slider.value() / 10.0,
        main_window.no_repeat_ngram_size_slider.value(),
        main_window.progress_bar.setValue
    )

    sys.exit(app.exec())

