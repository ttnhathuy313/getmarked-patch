import subprocess

def convert_docx_to_html(path_to_docx, path_to_media):
    subprocess.call(['pandoc', '--extract-media=' + path_to_media, '--wrap=none', path_to_docx, '-o', 'usecase.html'])