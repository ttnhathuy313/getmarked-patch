import json
from pandoc_convert import convert_docx_to_html
from preprocess import fix

"""
    path_to_doc: path to the docx file
    path_to_getmarked_output: path to the output of getmarked
    path_to_save_output: path to save the output of this function
    path_to_save_media: path to save the media files in the docx file
"""
def fix_missing_info(path_to_doc, path_to_getmarked_output, path_to_save_output, path_to_save_media):
    convert_docx_to_html(path_to_doc, path_to_save_media)
    fix(path_to_getmarked_output, path_to_save_output)

path_to_doc = './usecase2.docx'
path_to_getmarked_output = './output.json'
path_to_save_output = './fix-output.json'
# the media will be saved in path_to_save_media/media
path_to_save_media = './'

fix_missing_info(path_to_doc, path_to_getmarked_output, path_to_save_output, path_to_save_media)