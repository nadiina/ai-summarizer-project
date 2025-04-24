import time
import traceback
from libs.logger import get_logger

logger = get_logger(__name__)


class ProcessingContextManager:
    def __enter__(self):
        self.start_time = time.time()
        logger.info("Процес аналізу текста розпочато.")
        return self

    def __exit__(self, exc_type, exc_value, tb):
        duration = time.time() - self.start_time
        self.duration = duration
        # logger.info(f"Processing finished in {duration:.2f} seconds.")
        if exc_type:
            is_critical = isinstance(exc_value, (KeyboardInterrupt, SystemExit, MemoryError))
            logger.error(
                f"Error: {exc_value}\n{''.join(traceback.format_exception(exc_type, exc_value, tb))}",
                exc_info=not is_critical
            )
            return not is_critical
        return True
