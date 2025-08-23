from pathlib import Path
from typing import List

from py_app_dev.core.logging import logger

from pypeline.domain.execution_context import ExecutionContext
from pypeline.domain.pipeline import PipelineStep


class MyStep(PipelineStep[ExecutionContext]):
    def run(self) -> None:
        logger.info(f"Run {self.get_name()} found install dirs:")
        for install_dir in self.execution_context.install_dirs:
            logger.info(f" {install_dir}")
        logger.info(f"my_input: {self.execution_context.get_input('my_input')}")

    def get_inputs(self) -> List[Path]:
        return []

    def get_outputs(self) -> List[Path]:
        return []

    def get_name(self) -> str:
        return self.__class__.__name__

    def update_execution_context(self) -> None:
        pass
