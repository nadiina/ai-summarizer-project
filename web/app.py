import os
from flask import request, Flask, render_template
from werkzeug.utils import secure_filename

from libs.utils_shared import read_text_file, get_upload_folder, allowed_file
from libs.logger import get_logger, log_info, log_warning, log_error, log_debug
from scripts.get_contents import process_contents
from scripts.get_summary import process_summary

app = Flask(__name__)
UPLOAD_FOLDER = get_upload_folder()
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER

logger = get_logger(__name__)


def process_file(file_path, action):
    log_debug(f"Обробка файлу за шляхом {file_path} з дією '{action}'")
    text = read_text_file(file_path)

    if action == 'get_summary':
        result = process_summary(file_path, text)
    elif action == 'get_contents':
        result = process_contents(file_path, text)
    else:
        log_error(f"Невідома дія: {action}")
        raise ValueError("Невідома дія")

    log_info(f"Файл '{file_path}' успішно оброблено для дії '{action}'")
    return result


@app.route('/', methods=['GET', 'POST'])
def index():
    log_info(f"Отримано {request.method} запит на '/' від {request.remote_addr}")
    result = None
    error = None

    if request.method == 'POST':
        action = request.form.get('action')
        file = request.files.get('file')
        log_debug(f"Отримано форму: дія='{action}', файл='{file.filename if file else None}'")

        if file and allowed_file(file.filename):
            filename = secure_filename(file.filename)
            file_path = os.path.join(app.config['UPLOAD_FOLDER'], filename)
            try:
                file.save(file_path)
                # log_info(f"Файл збережено за шляхом {file_path}")
            except Exception as e:
                log_error(f"Не вдалося зберегти файл '{filename}': {e}")
                error = "Не вдалося зберегти файл. Спробуйте ще раз."
                return render_template("index.html", result=result, error=error)

            try:
                result = process_file(file_path, action)
            except Exception as e:
                log_error(f"Помилка під час обробки файлу '{filename}': {e}")
                error = str(e)
            finally:
                if os.path.exists(file_path):
                    try:
                        os.remove(file_path)
                        log_debug(f"Тимчасовий файл видалено: {file_path}")
                    except Exception as e:
                        log_warning(f"Не вдалося видалити файл {file_path}: {e}")
        else:
            log_warning(f"Невдала спроба завантаження файлу: ім'я='{file.filename if file else None}', дія='{action}'")
            error = "Будь ласка, завантажте правильний .txt файл."

    if result is not None:
        result = str(result)
    return render_template("index.html", result=result, error=error)


if __name__ == '__main__':
    log_info("Запуск Flask-додатку")
    app.run(debug=True)
