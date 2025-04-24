import os
import json
import traceback

from libs.context import ProcessingContextManager
from settings.llm_client import load_openai_client
from settings.llm_utils import make_log_entry
from libs.logger import get_logger
from libs.tokens import TokenTracker


class DocumentLLMProcessor:
    def __init__(self, name, prompt_builder, log_jsonl, model_name=None, title_prefix=None, count_sections=False):
        project_root = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
        self.log_dir = os.path.join(project_root, "logs")
        self.logger = get_logger(name, self.log_dir)
        self.client = load_openai_client()
        self.prompt_builder = prompt_builder
        self.model = os.getenv("LLM_MODEL", model_name or "gpt-4o-mini")
        self.log_jsonl = log_jsonl
        self.title_prefix = title_prefix or name
        self.count_sections = count_sections

    def _generate(self, text, token_tracker: TokenTracker):
        try:
            messages = self.prompt_builder(text)
            resp = self.client.chat.completions.create(
                model=self.model,
                messages=messages,
                timeout=int(os.getenv("LLM_TIMEOUT", 60))
            )
            if hasattr(resp.usage, 'prompt_tokens'):
                token_tracker.add_prompt_tokens(resp.usage.prompt_tokens)
            token_tracker.add_completion_tokens(resp.usage.completion_tokens)
            content = resp.choices[0].message.content.strip()
            if self.count_sections:
                count = content.count("\n1.") + (1 if content.startswith("1.") else 0)
                return content, count
            return content
        except Exception as e:
            self.logger.error(f"Error during generation: {e}\n{traceback.format_exc()}")
            raise

    def _log(self, file_name, output, token_tracker: TokenTracker):
        try:
            os.makedirs(self.log_dir, exist_ok=True)
            log_path = os.path.join(self.log_dir, self.log_jsonl)
            if self.count_sections:
                content, count = output
                payload = {"section_count": count, "content": content}
            else:
                payload = {"summary": output}

            if token_tracker:
                payload.update({
                    "prompt_tokens": token_tracker.prompt_tokens,
                    "completion_tokens": token_tracker.completion_tokens,
                    "total_tokens": token_tracker.get_total_tokens(),
                    "elapsed_seconds": token_tracker.get_elapsed_time()
                })

            entry = make_log_entry(file_name, payload)
            with open(log_path, "a", encoding="utf-8") as f:
                f.write(json.dumps(entry, ensure_ascii=False) + "\n")
        except Exception as e:
            self.logger.error(f"Error while logging output: {e}\n{traceback.format_exc()}")
            raise

    def run(self, path: str, text: str, tracker: TokenTracker):
        try:
            with ProcessingContextManager() as ctx:
                output = self._generate(text, tracker)

                header = f"=== {self.title_prefix}: {os.path.basename(path)} ==="
                print(f"\n{header}\n")
                if self.count_sections:
                    content, _ = output
                    print(content)
                    result = content
                else:
                    print(output)
                    result = output

                self.logger.info(f"{self.title_prefix} згенеровано успішно.")
                self._log(os.path.basename(path), output, tracker)
                tracker.write_report()

            self.logger.info(f"Total processing time (incl. logging): {ctx.duration:.2f} seconds.")
            return result

        except Exception as e:
            self.logger.error(f"Error during document processing: {e}\n{traceback.format_exc()}")
            raise
