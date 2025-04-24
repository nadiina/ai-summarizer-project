import os
from libs.utils_shared import load_example_document
from libs.tokens import TokenTracker
from prompts.contents import contents_prompt
from settings.llm_processor import DocumentLLMProcessor

def process_contents(file_path: str, text: str) -> str:
    processor = DocumentLLMProcessor(
        name="contents",
        prompt_builder=contents_prompt,
        log_jsonl="contents.jsonl",
        title_prefix="Зміст",
        count_sections=False
    )
    tracker = TokenTracker(
        model_name=processor.model,
        prompt=f"{processor.title_prefix} of {os.path.basename(file_path)}"
    )
    return processor.run(file_path, text, tracker)


def get_contents():
    path, text = load_example_document()
    return process_contents(path, text)