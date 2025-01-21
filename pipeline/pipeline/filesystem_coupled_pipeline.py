# Copyright (c) 2024 Contributors
# Authors: Christian Smith; John Azariah
# All rights reserved.

import os
import msgspec
from typing import Any
from collections.abc import Iterable
from dataclasses import dataclass

from .pipeline import EnhancedPipeline, PipelineStageEnhancer, Pipeline, PipelineStage


@dataclass
class FileSystemContext:
    document_root: str


@dataclass
class FileSystemEnhancer(PipelineStageEnhancer[FileSystemContext]):
    def __init__(self, stage: PipelineStage[Any, Any], stage_index: int, stage_count: int):
        super().__init__(stage=stage, stage_index=stage_index, stage_count=stage_count)
        self.input_subfolder = f"stage_{stage_index}"
        self.output_subfolder = f"stage_{stage_index + 1}"
        self.json_encoder = msgspec.json.Encoder()

    def generate_inputs(self, context: FileSystemContext) -> Iterable[Any]:
        input_folder = os.path.join(context.document_root, self.input_subfolder)
        for filename in os.listdir(input_folder):
            if filename.endswith(".json"):
                with open(os.path.join(input_folder, filename), "rb") as f:
                    yield msgspec.json.decode(f.read(), type=self.stage.TStageInput, strict=False)  # TODO: JOHN - active bug here - this doesn't decorate the object with the filename attribute

    def process_output(self, context: FileSystemContext, result: Any, result_index: int, result_count: int) -> None:
        def write_json_to_file(result: Any, filename: str) -> None:
            os.makedirs(os.path.join(context.document_root, self.output_subfolder), exist_ok=True)
            output_file_name = os.path.join(context.document_root, self.output_subfolder, filename)
            with open(output_file_name, "wb") as f:
                f.write(self.json_encoder.encode(result))

        if getattr(result, "filename", None) is not None:
            match (result_index, result_count):
                case (1, 1):
                    write_json_to_file(result, f"{result.filename}.json")  # note - this uses the attribute injected by the `to_filename` decorator
                case (_, _):
                    write_json_to_file(result, f"{result.filename}_{result_index}.json")  # note - this uses the attribute injected by the `to_filename` decorator
        else:
            print(f"Warning: No filename attribute found on result object {result}. Writing result to generic filename.")
            write_json_to_file(result, f"result_{result_index}.json")


class FileSystemCoupledPipeline(EnhancedPipeline[FileSystemEnhancer, FileSystemContext]):
    def __init__(self, document_root: str, pipeline: Pipeline[Any, Any]):
        super().__init__(context=FileSystemContext(document_root=document_root), pipeline=pipeline)
