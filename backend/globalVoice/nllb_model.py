from transformers import AutoTokenizer, AutoModelForSeq2SeqLM, pipeline
import pycountry

class NLLBTranslator:
    # Initialise model
    def __init__(self):
        self.model_identifier = "facebook/nllb-200-1.3B"
        self.language_detection_identifier = "ivanlau/language-detection-fine-tuned-on-xlm-roberta-base"
        self.tokenizer = AutoTokenizer.from_pretrained(self.model_identifier)
        self.model = AutoModelForSeq2SeqLM.from_pretrained(self.model_identifier)
        self.languages = self.tokenizer.additional_special_tokens
        self.language_detection_pipeline = pipeline("text-classification", model=self.language_detection_identifier)

    # Translate input texts using model
    def translate_text(self, source_language_code, input_text, target_language_code):
        self.tokenizer = AutoTokenizer.from_pretrained(self.model_identifier, src_lang=source_language_code)
        input_ids = self.tokenizer.encode(input_text, return_tensors="pt")
        translated_ids = self.model.generate(input_ids, forced_bos_token_id=self.tokenizer.lang_code_to_id[target_language_code])
        translated_text = self.tokenizer.decode(translated_ids[0], skip_special_tokens=True)
        return translated_text
    
    # Returning all language codes supported by the model
    def get_language_codes(self):
        return [(lang_code, lang_code) for lang_code in self.languages]
    
    # Returning all language names supported by the model
    def get_language_names(self):
        self.language_codes = self.get_language_codes()
        language_names = [(lang_code, pycountry.languages.get(alpha_3=lang_code.split("_")[0]).name) for lang_code, _ in self.language_codes]
        return language_names
    
    # Detecting input language from provided text
    def detect_language(self, input_text):
        result = self.language_detection_pipeline(input_text)
        detected_language = result[0]["label"]
        print("detected language:", detected_language)
        return detected_language
    
nllb_translator = NLLBTranslator()