import os
import glob

UPLOAD_FOLDER = os.path.join(os.path.dirname(os.path.abspath(__file__)), '..', 'uploads')
ALLOWED_EXTENSIONS = {'txt'}


def get_upload_folder():
    os.makedirs(UPLOAD_FOLDER, exist_ok=True)
    return UPLOAD_FOLDER


def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS


def get_example_docs_path() -> str:
    script_dir = os.path.dirname(os.path.abspath(__file__))
    return os.path.join(os.path.dirname(script_dir), "example_docs")


def choose_document_file(docs_dir: str) -> str:
    file_paths = glob.glob(os.path.join(docs_dir, "*.txt"))
    if not file_paths:
        raise FileNotFoundError(f"У папці {docs_dir} немає .txt файлів.")

    print("Оберіть файл для обробки:")
    for i, path in enumerate(file_paths, 1):
        print(f"[{i}] {os.path.basename(path)}")

    while True:
        choice = input("Введіть номер: ")
        if choice.isdigit() and 1 <= int(choice) <= len(file_paths):
            return file_paths[int(choice) - 1]
        print("Некоректний вибір. Спробуйте ще раз.")


def read_text_file(path: str) -> str:
    """Зчитує текстовий файл з кодуванням UTF-8."""
    with open(path, encoding="utf-8") as f:
        return f.read()


def load_example_document():
    docs_dir = get_example_docs_path()
    path = choose_document_file(docs_dir)
    text = read_text_file(path)
    return path, text
