from bs4 import BeautifulSoup
from flask import Flask, redirect, render_template, request, send_file, url_for
from flask_wtf import FlaskForm
import requests
from wtforms import TextAreaField, StringField, FileField
from io import BytesIO
import tempfile
from PyPDF2 import PdfReader
from docx import Document
import os

app = Flask(__name__)
app.config['SECRET_KEY'] = 'vbhogadhi'

class InputForm(FlaskForm):
    text = TextAreaField('Text')
    url = StringField('URL')
    file = FileField('PDF File')

@app.route('/', methods=['GET', 'POST'])
def index():
    if request.method == 'POST':
        text = request.form.get('text')
        url = request.form.get('url')
        file = request.files['file']

        if (text and file) or (text and url) or (url and file) or (text and file and url):
            pass
        elif text:
            output_file_name = "Summarized_Data.txt"
            txt_file_path = save_text_to_txt(text)
            return send_file(BytesIO(text.encode('utf-8')), as_attachment=True, download_name=output_file_name)
        elif file:
            file_extension = os.path.splitext(file.filename)[1].lower()
            if file_extension == '.pdf':
                text = extract_text_from_pdf(file)
                output_file_name = "output.txt"
                txt_file_path = save_text_to_txt(text)
                return send_file(BytesIO(text.encode('utf-8')), as_attachment=True, download_name=output_file_name)
            elif file_extension in ('.doc', '.docx'):
                text = extract_text_from_doc(file)
                output_file_name = "output.txt"
                txt_file_path = save_text_to_txt(text)
                return send_file(BytesIO(text.encode('utf-8')), as_attachment=True, download_name=output_file_name)
            else:
                return "Unsupported file format"
        elif url:
            text = extract_text_from_url(url)
            output_file_name = "output.txt"
            txt_file_path = save_text_to_txt(text)
            return send_file(BytesIO(text.encode('utf-8')), as_attachment=True, download_name=output_file_name)
        else:
            return "Invalid"

    form = InputForm()
    return render_template('index.html', form=form)

def save_text_to_txt(text):
    temp_txt = tempfile.NamedTemporaryFile(mode='w', delete=False, encoding='utf-8')
    temp_txt.write(text)
    temp_txt.close()
    return temp_txt.name

def extract_text_from_pdf(file):
    pdf_reader = PdfReader(file)
    text = ''
    for page in pdf_reader.pages:
        text += page.extract_text()
    return text

def extract_text_from_url(url):
    response = requests.get(url)
    soup = BeautifulSoup(response.text, 'html.parser')
    text = soup.get_text()
    return text

def extract_text_from_doc(doc_file):
    docx_text = ""
    doc = Document(doc_file)
    for para in doc.paragraphs:
        docx_text += para.text + "\n"
    return docx_text

if __name__ == '__main__':
    app.run(debug=True)
