import os
from flask import Flask, request, jsonify
from werkzeug.utils import secure_filename

from libs.utils_shared import read_text_file
from libs.logger import get_logger, log_info, log_warning, log_error, log_debug
from scripts.get_contents import process_contents
from scripts.get_summary import process_summary

ALLOWED_EXTENSIONS = {'txt'}
MAX_CONTENT_LENGTH = 16 * 1024 * 1024  # 16 МБ

# Визначення кореневої теки проєкту
project_root = os.path.dirname(os.path.abspath(__file__))

# Ініціалізація логера
logger = get_logger(__name__)


def create_app():
    app = Flask(__name__)

    upload_folder = os.path.join(project_root, 'uploads')
    os.makedirs(upload_folder, exist_ok=True)
    app.config['UPLOAD_FOLDER'] = upload_folder
    app.config['MAX_CONTENT_LENGTH'] = MAX_CONTENT_LENGTH

    def allowed_file(filename: str) -> bool:
        return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

    def process_file(file_path: str, action: str) -> str:
        log_debug(f"Обробка файлу '{file_path}' з дією '{action}'")
        text = read_text_file(file_path)
        if action == 'get_contents':
            return process_contents(file_path, text)
        elif action == 'get_summary':
            return process_summary(file_path, text)
        else:
            log_error(f"Невідома дія: {action}")
            raise ValueError(f"Невідома дія: {action}")

    def handle_file_request(action: str):
        log_info(f"Отримано API-запит для дії '{action}'")

        if 'file' not in request.files:
            log_warning("Файл не знайдено у запиті")
            return jsonify({'error': 'Файл не був завантажений'}), 400

        file = request.files['file']
        if file.filename == '':
            log_warning("Файл не вибрано для завантаження")
            return jsonify({'error': 'Не вибрано файл'}), 400

        if not allowed_file(file.filename):
            log_warning(f"Недопустимий формат файлу: {file.filename}")
            return jsonify({'error': 'Дозволені лише файли .txt'}), 400

        filename = secure_filename(file.filename)
        file_path = os.path.join(app.config['UPLOAD_FOLDER'], filename)
        try:
            file.save(file_path)
            log_info(f"Файл '{filename}' збережено за шляхом '{file_path}'")
        except Exception as e:
            log_error(f"Помилка при збереженні файлу '{filename}': {e}")
            return jsonify({'error': 'Не вдалося зберегти файл'}), 500

        try:
            result = process_file(file_path, action)
            key = 'summary' if action == 'get_summary' else 'contents'
            log_info(f"Файл '{filename}' успішно оброблено з дією '{action}'")
            return jsonify({key: result})
        except Exception as e:
            log_error(f"Помилка при обробці файлу '{filename}': {e}")
            return jsonify({'error': str(e)}), 500
        finally:
            if os.path.exists(file_path):
                try:
                    os.remove(file_path)
                    log_debug(f"Тимчасовий файл '{file_path}' успішно видалено")
                except Exception as e:
                    log_warning(f"Не вдалося видалити тимчасовий файл '{file_path}': {e}")

    app.add_url_rule(
        '/api/v1/get_summary',
        endpoint='api_get_summary',
        view_func=lambda: handle_file_request('get_summary'),
        methods=['POST']
    )

    app.add_url_rule(
        '/api/v1/get_contents',
        endpoint='api_get_contents',
        view_func=lambda: handle_file_request('get_contents'),
        methods=['POST']
    )

    @app.route('/', methods=['GET'])
    def index():
        return jsonify({
            "message": "This API processes .txt documents. You can upload a text file and get its contents or summary.",
            "note": "Uploaded files must have a .txt extension.",
            "instructions": {
                "1": "Use POST requests to the specified endpoints with the parameter 'file' containing a .txt file.",
                "2": "The request format should be multipart/form-data.",
                "3": "Available endpoints:"
            },
            "endpoints": {
                "/api/v1/get_contents": {"description": "Returns the contents and theses of a text document.",
                                         "method": "POST", "required": "Parameter 'file'."},
                "/api/v1/get_summary": {"description": "Returns the summary of a text document.", "method": "POST",
                                        "required": "Parameter 'file'."}
            }
        })

    return app


if __name__ == '__main__':
    app = create_app()
    app.run(host='0.0.0.0', port=5000, debug=True)
