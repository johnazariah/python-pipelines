import pytest
from dataclasses import dataclass
from collections.abc import Iterable

import sys
import pathlib
sys.path.insert(0, str(pathlib.Path(__file__).resolve().parent.parent))
sys.path.insert(0, str(pathlib.Path(__file__).resolve().parent.parent.parent / "generics" / "generics"))
from pipeline.pipeline import PipelineStage, Pipeline, TStageInput, TStageResult


@dataclass
class InitialStage(PipelineStage[int, int]):
    @classmethod
    def double(cls, x: int) -> int:
        return 2 * x

    def transform(self, input):
        yield self.double(input)


@dataclass
class IntermediateStage(PipelineStage[int, str]):
    def transform(self, x: int) -> list[str]:
        return [str(x)]


@dataclass
class FinalStage(PipelineStage[str, str]):
    def transform(self, x: str) -> list[str]:
        return [x.upper()]


def test_pipeline_with_stages():
    stage1 = InitialStage()
    stage2 = InitialStage()
    pipeline = Pipeline[int, int]([stage1, stage2])

    result = pipeline(5)
    assert result == [20], "Pipeline should correctly process with two stages doubling the input."


def test_pipeline_with_no_stages():
    pipeline = Pipeline[int, int]()

    result = pipeline(5)
    assert result == [5], "Pipeline with no stages should return input unchanged."


def test_pipeline_valid_type_chain():
    initial_stage = InitialStage()
    intermediate_stage = IntermediateStage()
    final_stage = FinalStage()
    pipeline = Pipeline[int, str]([initial_stage, intermediate_stage, final_stage])

    result = pipeline(10)
    assert result == ["20"], "Pipeline with a valid type chain should process input correctly through intermediate stages."


def test_pipeline_invalid_type_chain():
    @dataclass
    class MismatchedStage(PipelineStage[str, int]):
        def transform(self, x: str) -> list[int]:
            return [len(x)]

    stage1 = InitialStage()
    mismatched_stage = MismatchedStage()

    with pytest.raises(TypeError):
        Pipeline[int, int]([stage1, mismatched_stage])


def test_pipeline_input_output_type_match():
    @dataclass
    class StringStage(PipelineStage[str, str]):
        def transform(self, x: str) -> list[str]:
            return [x.upper()]

    with pytest.raises(TypeError):
        Pipeline[int, str]([InitialStage(), StringStage()])


def test_pipeline_stage_with_transform_only():
    @dataclass
    class TransformOnlyStage(PipelineStage[int, int]):
        def transform(self, x: int) -> Iterable[int]:
            yield x + 1

    stage = TransformOnlyStage()
    result = stage(5)
    assert result == [6], "PipelineStage with transform only should correctly transform input."


@dataclass
class ProduceOnlyStage(PipelineStage[int, int]):
    def produce(self):
        yield from [1, 2, 3]


def test_pipeline_stage_with_produce_only():
    stage = ProduceOnlyStage()
    result = stage(None)
    assert result == [1, 2, 3], "PipelineStage with produce only should correctly produce output."


def test_pipeline_stage_with_consume_only():
    consumed_results = []

    @dataclass
    class ConsumeOnlyStage(PipelineStage[int, None]):
        def consume(self, x: int):
            consumed_results.append(x)

    stage = ConsumeOnlyStage()
    stage(5)
    assert consumed_results == [5], "PipelineStage with consume only should correctly consume input."


def test_pipeline_stage_with_transform_and_consume():
    consumed_results = []

    @dataclass
    class TransformAndConsumeStage(PipelineStage[int, int]):
        def transform(self, x: int) -> list[int]:
            return [x + 1]

        def consume(self, x: int):
            consumed_results.append(x)

    stage = TransformAndConsumeStage()
    result = stage(5)
    assert result == [6], "PipelineStage with transform and consume should correctly transform input."
    assert consumed_results == [6], "PipelineStage with transform and consume should correctly consume transformed input."


def test_pipeline_stage_with_produce_and_consume():
    consumed_results = []

    @dataclass
    class ProduceAndConsumeStage(PipelineStage[None, int]):
        def produce(self):
            yield from [1, 2, 3]

        def consume(self, x: int):
            consumed_results.append(x)

    stage = ProduceAndConsumeStage()
    result = stage(None)
    assert result == [1, 2, 3], "PipelineStage with produce and consume should correctly produce output."
    assert consumed_results == [1, 2, 3], "PipelineStage with produce and consume should correctly consume produced output."


def test_produce_and_transform_combination():
    @dataclass
    class ProduceAndTransformStage(PipelineStage[None, int]):
        def produce(self):
            yield from [1, 2, 3]

        def transform(self, x: int) -> list[int]:
            return [x * 2]

    stage = ProduceAndTransformStage()
    result = stage(2)
    assert result == [1, 2, 3, 4], "PipelineStage with produce and transform should correctly produce and transform output."


def test_pipeline_stage_with_all_methods():
    consumed_results = []

    @dataclass
    class AllMethodsStage(PipelineStage[int, int]):
        def transform(self, x: int) -> list[int]:
            return [x + 1]

        def produce(self):
            yield from [10]

        def consume(self, x: int):
            consumed_results.append(x)

    stage = AllMethodsStage()
    result = stage(5)
    assert result == [10, 6], "PipelineStage with all methods should correctly transform input and produce output."
    assert consumed_results == [10, 6], "PipelineStage with all methods should correctly consume both transformed and produced output."


def test_pipeline_with_multiple_stages_and_methods():
    consumed_results = []

    @dataclass
    class Stage1(PipelineStage[int, int]):
        def __init__(self):
            self.produce = lambda: [10]

    @dataclass
    class Stage2(PipelineStage[int, int]):
        def __init__(self):
            self.transform = lambda x: [x + 1]

    @dataclass
    class Stage3(PipelineStage[int, int]):
        def __init__(self):
            self.transform = lambda x: [x * 2]

    @dataclass
    class Stage4(PipelineStage[int, int]):
        def __init__(self):
            self.consume = lambda x: consumed_results.append(x)

    stage1 = Stage1()
    stage2 = Stage2()
    stage3 = Stage3()
    stage4 = Stage4()
    pipeline = Pipeline[int, int]([stage1, stage2, stage3, stage4])

    result = pipeline(5)
    assert result == [22], "Pipeline should correctly process through multiple stages with various methods."
    assert consumed_results == [22], "Pipeline should correctly consume results from multiple stages."


def test_pipeline_with_complex_stage_combinations():
    consumed_results = []

    @dataclass
    class Stage1(PipelineStage[int, int]):
        def __init__(self):
            self.transform = lambda x: [x + 1]

    @dataclass
    class Stage2(PipelineStage[int, int]):
        def __init__(self):
            self.transform = lambda x: [x * 2]
            self.produce = lambda: [20]

    @dataclass
    class Stage3(PipelineStage[int, int]):
        def __init__(self):
            self.transform = lambda x: [x - 3]
            self.consume = lambda x: consumed_results.append(x)

    stage1 = Stage1()
    stage2 = Stage2()
    stage3 = Stage3()
    pipeline = Pipeline[int, int]([stage1, stage2, stage3])

    result = pipeline(5)
    assert result == [(20 - 3), (((5 + 1) * 2) - 3)], "Pipeline should correctly process through complex stage combinations."
    assert consumed_results == [17, 9], "Pipeline should correctly consume results from complex stage combinations."


# Custom subclass to override produce, transform, and consume methods
class CustomStage(PipelineStage[TStageInput, TStageResult]):
    def __init__(self, produce=None, transform=None, consume=None):
        super().__init__()
        if produce:
            self.produce = produce
        if transform:
            self.transform = transform
        if consume:
            self.consume = consume


# Both stages have transform only
def test_transform_only():
    stage1 = CustomStage[int, int](transform=lambda x: [x * 2])
    stage2 = CustomStage[int, str](transform=lambda x: [f"Value: {x}"])

    combined_stage = stage1 >> stage2
    result = list(combined_stage(3))

    assert result == ["Value: 6"]


# First stage has produce, second stage has transform
def test_produce_and_transform():
    stage1 = CustomStage[int, int](produce=lambda: [1, 2, 3], transform=lambda x: [x * 2])
    stage2 = CustomStage[int, str](transform=lambda x: [f"Value: {x}"])

    stage1_results = list(stage1(2))
    assert stage1_results == [1, 2, 3, 4]

    stage2_results = list(stage2(1))
    assert stage2_results == ["Value: 1"]

    combined_stage = stage1 >> stage2
    result = list(combined_stage(2))

    assert result == ["Value: 1", "Value: 2", "Value: 3", "Value: 4"]


# Both stages have consume
def test_transform_and_consume():
    consumed_values_stage1 = []
    consumed_values_stage2 = []

    stage1 = CustomStage[int, int](
        transform=lambda x: [x * 2],
        consume=lambda r: consumed_values_stage1.append(r)
    )

    stage2 = CustomStage[int, str](
        transform=lambda x: [f"Value: {x}"],
        consume=lambda r: consumed_values_stage2.append(r)
    )

    combined_stage = stage1 >> stage2
    result = list(combined_stage(5))

    assert result == ["Value: 10"]
    assert consumed_values_stage1 == [10]
    assert consumed_values_stage2 == ["Value: 10"]


# First stage has consume, second stage has transform
def test_consume_and_transform():
    consumed_values_stage1 = []

    stage1 = CustomStage[int, int](
        transform=lambda x: [x * 3],
        consume=lambda r: consumed_values_stage1.append(r)
    )

    stage2 = CustomStage[int, str](transform=lambda x: [f"Processed: {x}"])

    combined_stage = stage1 >> stage2
    result = list(combined_stage(4))

    assert result == ["Processed: 12"]
    assert consumed_values_stage1 == [12]


# First stage has produce and consume, second stage has consume
def test_produce_consume():
    consumed_values_stage1 = []
    consumed_values_stage2 = []

    stage1 = CustomStage[int, int](
        produce=lambda: [1, 2],
        transform=lambda x: [x + 1],
        consume=lambda r: consumed_values_stage1.append(r)
    )

    stage2 = CustomStage[int, str](
        transform=lambda x: [f"Number: {x}"],
        consume=lambda r: consumed_values_stage2.append(r)
    )

    combined_stage = stage1 >> stage2
    result = list(combined_stage(2))

    assert result == ["Number: 1", "Number: 2", "Number: 3"]
    assert consumed_values_stage1 == [1, 2, 3]
    assert consumed_values_stage2 == ["Number: 1", "Number: 2", "Number: 3"]


# Empty stages (no produce, transform, or consume)
def test_empty_stages():
    stage1 = CustomStage[int, int]()
    stage2 = CustomStage[int, int]()

    combined_stage = stage1 >> stage2
    result = list(combined_stage(5))

    assert result == [5]  # Default behavior should pass input through


# First stage has produce only, second stage has consume
def test_produce_only_and_consume():
    consumed_values_stage2 = []

    stage1 = CustomStage[int, int](produce=lambda: [5, 10])
    stage2 = CustomStage[int, str](
        transform=lambda x: [f"Processed: {x}"],
        consume=lambda r: consumed_values_stage2.append(r)
    )

    combined_stage = stage1 >> stage2
    result = list(combined_stage(0))  # Input should be ignored due to produce

    assert result == ["Processed: 5", "Processed: 10"]
    assert consumed_values_stage2 == ["Processed: 5", "Processed: 10"]


# First stage has transform only, second stage has produce (should be ignored)
def test_transform_then_produce():
    stage1 = CustomStage[int, int](transform=lambda x: [x * 2])
    stage2 = CustomStage[int, str](produce=lambda: ["injected"], transform=lambda x: [f"Processed: {x}"])

    combined_stage = stage1 >> stage2
    result = list(combined_stage(4))

    assert result == ["injected", "Processed: 8"]
