import frappe
from deep_translator import GoogleTranslator 
import os
import json
import frappe.translate

def translate(text: str | list, target_lang: str='sw') -> str | list:
    """
    Translate text 
    """
    source = text
    if type(text) == str:
        source = [text]
    #return GoogleTranslator(source='auto', target=target_lang).translate(text)
    res = GoogleTranslator(source='auto', target=target_lang).translate_batch(source)
    return res[0] if type(text) == str else res

def generate_form_translations(doctype, target_lang: str='sw'):
    """
    Generate translations
    For each field, translate the label
    """ 
    # deploy_translations(target_lang) 
    # return
    file_path = initialize_translation_file(target_lang)    
    lines = []
    with open(file_path) as fp:
        entries = fp.readlines()
    
    #entries = [x for x in entries if x =='Sample Gender Field\n'] # entries[:10]
    res = translate(entries, target_lang)
    for i, line in enumerate(entries):
        line = line.strip("\n")
        #translated_text = translate(line, target_lang)
        translated_text = res[i]
        lines.append("{0}".format(translated_text))
        #append_translation_to_file(target_lang, line, translated_text)

    append_translation_to_file(target_lang, lines)
    deploy_translations(target_lang) 

def get_translated_file_path(lang: str) -> str:
    return '{lang}.txt'.format(lang=lang)

def get_untranslated_file_path(lang: str) -> str:
    return '{lang}_raw.txt'.format(lang=lang)

def initialize_translation_file(lang: str) -> str:
    """
    Export already existing translations to avoid losing them later
    """
    untranslated_file = get_untranslated_file_path(lang)
    frappe.translate.get_untranslated(lang, untranslated_file, app='participatory_backend')

    # truncate target file
    translated_file = get_translated_file_path(lang)
    with open(translated_file, 'w+') as fp:
        print("Truncated file")

    return untranslated_file

def append_translation_to_file(lang: str, translations: str | list):
    """
    Append translated `text` for the specified `key` to file 
    """
    path = get_translated_file_path(lang)
    # content = {}
    # if os.path.exists(path):
    #     with open(path) as fp:
    #         content = json.load(fp)
    # content[key] = text

    with open(path, 'a') as fp:
        if type(translations) == str:
            fp.writelines("{0}".format(translations))
        else:
            txt = "\n".join(translations)
            fp.writelines("{0}".format(txt))

def deploy_translations(lang='sw'):
    """
    Deploy translations by importing them. See https://frappeframework.com/docs/user/en/translations 
    """
    untranslated_file = get_untranslated_file_path(lang)
    translated_file = get_translated_file_path(lang)
    frappe.translate.update_translations(lang, untranslated_file, translated_file, app='participatory_backend')