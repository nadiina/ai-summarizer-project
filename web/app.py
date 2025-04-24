import os
from flask import request, Flask, render_template
from werkzeug.utils import secure_filename

from libs.utils_shared import read_text_file, get_upload_folder, allowed_file
from scripts.get_contents import process_contents
from scripts.get_summary import process_summary

app = Flask(__name__)
UPLOAD_FOLDER = get_upload_folder()
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER


def process_file(file_path, action):
    text = read_text_file(file_path)

    if action == 'get_summary':
        return process_summary(file_path, text)
    elif action == 'get_contents':
        return process_contents(file_path, text)
    else:
        raise ValueError("Невідома дія")


@app.route('/', methods=['GET', 'POST'])
def index():
    result = None
    error = None

    if request.method == 'POST':
        action = request.form.get('action')
        file = request.files.get('file')

        if file and allowed_file(file.filename):
            filename = secure_filename(file.filename)
            file_path = os.path.join(app.config['UPLOAD_FOLDER'], filename)
            file.save(file_path)

            try:
                result = process_file(file_path, action)
            except Exception as e:
                error = str(e)
            # finally:
            #     if os.path.exists(file_path):
            #         os.remove(file_path)
        else:
            error = "Будь ласка, завантажте правильний .txt файл."

    if result is not None:
        result = str(result)
    return render_template("index.html", result=result, error=error)


if __name__ == '__main__':
    app.run(debug=True)
