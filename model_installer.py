#!/usr/bin/python

# The example is for french to spanish, but here -> https://github.com/Helsinki-NLP/Opus-MT-train/tree/master/models -> you can chose another.

from transformers import MarianMTModel, MarianTokenizer

def translate_text(model_name="Helsinki-NLP/opus-mt-fr-es", text=""):
    # Load model and tokenizer
    tokenizer = MarianTokenizer.from_pretrained(model_name)
    model = MarianMTModel.from_pretrained(model_name)

    # Tokenize the text
    tokens = tokenizer(text, return_tensors="pt", padding=True)

    # Perform the translation
    translated_tokens = model.generate(**tokens)

    # Decode the translation
    translation = tokenizer.decode(translated_tokens[0], skip_special_tokens=True)
    return translation

if __name__ == "__main__":
    # Translate a sample text
    sample_text = "Hello, how are you?"
    translation = translate_text(text=sample_text)
    print(f"Translation: {translation}")
