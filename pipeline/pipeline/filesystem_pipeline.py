# Copyright (c) 2024 Contributors
# Authors: Christian Smith; John Azariah
# All rights reserved.

import os
import msgspec
from typing import Any
from collections.abc import Iterable
from dataclasses import dataclass

from .pipeline import ContextualPipeline, ContextualPipelineStage, Pipeline


@dataclass
class FileSystemContext:
    document_root: str


@dataclass
class FileSystemCoupledPipelineStage(ContextualPipelineStage[FileSystemContext]):
    input_subfolder: str | None = None
    output_subfolder: str | None = None
    json_decoder = msgspec.json.Decoder()
    json_encoder = msgspec.json.Encoder()

    def generate_inputs(self, context: FileSystemContext) -> Iterable[Any]:
        input_folder = os.path.join(context.document_root, self.input_subfolder)
        for filename in os.listdir(input_folder):
            if filename.endswith(".json"):
                with open(os.path.join(input_folder, filename), "rb") as f:
                    yield self.json_decoder(f.read(), type=self.stage.TStageInput, strict=False)

    def process_output(self, context: FileSystemContext, result: Any, result_index: int, result_count: int) -> None:
        def write_json_to_file(result: Any, filename: str) -> None:
            os.makedirs(os.path.join(context.document_root, self.output_subfolder), exist_ok=True)
            output_file_name = os.path.join(context.document_root, self.output_subfolder, filename)
            with open(output_file_name, "wb") as f:
                f.write(self.json_encoder(result))

        match (result_index, result_count):
            case (1, 1):
                write_json_to_file(result, f"{result.id}.json")  # TODO: make this configurable
            case (_, _):
                write_json_to_file(result, f"{result.id}_{result_index}.json")  # TODO: make this configurable


class FileSystemCoupledPipeline(ContextualPipeline[FileSystemContext]):
    def __init__(self, document_root: str, pipeline: Pipeline[Any, Any]):
        super().__init__(context=FileSystemContext(document_root=document_root), pipeline=pipeline)
