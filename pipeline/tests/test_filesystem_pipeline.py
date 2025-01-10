import pytest
import shutil

from pipeline.pipeline.pipeline import Pipeline, PipelineStage
from pipeline.pipeline.filesystem_pipeline import FileSystemCoupledPipeline
from collections.abc import Iterable
from dataclasses import dataclass

@dataclass
class Initial:
    id: int
    value: int


@dataclass
class Intermediate:
    id: int
    value: str


@dataclass
class Intermediate2:
    id: int
    value: str


@dataclass
class ProduceOnlyStageEx(PipelineStage[None, Initial]):
    def produce(self) -> Iterable[Initial]:
        yield Initial(id=1, value=1)
        yield Initial(id=2, value=2)
        yield Initial(id=3, value=3)


@dataclass
class IntermediateStageEx(PipelineStage[Initial, Intermediate]):
    def transform(self, input: Initial) -> Iterable[Intermediate]:
        yield Intermediate(id=input.id, value=str(input.value))


@dataclass
class IntermediateStage2Ex(PipelineStage[Intermediate, Intermediate2]):
    def transform(self, input: Initial) -> Iterable[Intermediate]:
        yield Intermediate2(id=input.id, value=f"{input.value}_{input.value}")


@dataclass
class FinalStageEx(PipelineStage[Intermediate2, None]):
    def consume(self, input: Intermediate2) -> None:
        print(input)
        return None


@pytest.fixture
def clear_directory():
    shutil.rmtree("test_document_root", ignore_errors=True)


def test_filesystem_pipeline(clear_directory):
    pipeline = Pipeline[None, None]([ProduceOnlyStageEx(), IntermediateStageEx(), IntermediateStage2Ex(), FinalStageEx()])

    contextual_pipeline = FileSystemCoupledPipeline(document_root="test_document_root", pipeline=pipeline)
    contextual_pipeline.run()
