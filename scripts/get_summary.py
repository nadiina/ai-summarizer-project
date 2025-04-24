import os
from libs.utils_shared import load_example_document
from libs.tokens import TokenTracker
from prompts.summary import summary_prompt
from settings.llm_processor import DocumentLLMProcessor


def process_summary(file_path: str, text: str) -> str:
    processor = DocumentLLMProcessor(
        name="summary",
        prompt_builder=summary_prompt,
        log_jsonl="summary.jsonl",
        title_prefix="Підсумок",
        count_sections=False
    )
    tracker = TokenTracker(
        model_name=processor.model,
        prompt=f"{processor.title_prefix} of {os.path.basename(file_path)}"
    )
    return processor.run(file_path, text, tracker)


def get_summary():
    path, text = load_example_document()
    return process_summary(path, text)
