import pytest
from pipeline.pipeline.pipeline import PipelineStage, Pipeline
from dataclasses import dataclass, field
from collections.abc import Callable


@dataclass
class InitialStage(PipelineStage[int, int]):
    @classmethod
    def double(cls, x: int) -> list[int]:
        return [2 * x]

    def __init__(self):
        self.transform = self.double


@dataclass
class IntermediateStage(PipelineStage[int, str]):
    def tostring(self, x: int) -> list[str]:
        return [str(x)]

    def __init__(self):
        self.transform = self.tostring


@dataclass
class FinalStage(PipelineStage[str, str]):
    transform: Callable[[str], list[str]] = field(default_factory=lambda: lambda x: [x.upper()])


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
        transform: Callable[[str], list[int]] = field(default_factory=lambda: lambda x: [len(x)])

    stage1 = InitialStage()
    mismatched_stage = MismatchedStage()

    with pytest.raises(TypeError):
        Pipeline[int, int]([stage1, mismatched_stage])


def test_pipeline_input_output_type_match():
    @dataclass
    class StringStage(PipelineStage[str, str]):
        transform: Callable[[str], list[str]] = field(default_factory=lambda: lambda x: [x.upper()])

    with pytest.raises(TypeError):
        Pipeline[int, str]([InitialStage(), StringStage()])


def test_pipeline_stage_with_transform_only():
    @dataclass
    class TransformOnlyStage(PipelineStage[int, int]):
        def __init__(self):
            self.transform = lambda x: [x + 1]

    stage = TransformOnlyStage()
    result = stage(5)
    assert result == [6], "PipelineStage with transform only should correctly transform input."


@dataclass
class ProduceOnlyStage(PipelineStage[int, int]):
    def __init__(self):
        self.produce = lambda: [1, 2, 3]


def test_pipeline_stage_with_produce_only():
    stage = ProduceOnlyStage()
    result = stage(None)
    assert result == [1, 2, 3], "PipelineStage with produce only should correctly produce output."


def test_pipeline_stage_with_consume_only():
    consumed_results = []

    @dataclass
    class ConsumeOnlyStage(PipelineStage[int, None]):
        def __init__(self):
            self.consume = lambda x: consumed_results.append(x)

    stage = ConsumeOnlyStage()
    stage(5)
    assert consumed_results == [5], "PipelineStage with consume only should correctly consume input."


def test_pipeline_stage_with_transform_and_consume():
    consumed_results = []

    @dataclass
    class TransformAndConsumeStage(PipelineStage[int, int]):
        def __init__(self):
            self.transform = lambda x: [x + 1]
            self.consume = lambda x: consumed_results.append(x)

    stage = TransformAndConsumeStage()
    result = stage(5)
    assert result == [6], "PipelineStage with transform and consume should correctly transform input."
    assert consumed_results == [6], "PipelineStage with transform and consume should correctly consume transformed input."


def test_pipeline_stage_with_produce_and_consume():
    consumed_results = []

    @dataclass
    class ProduceAndConsumeStage(PipelineStage[None, int]):
        def __init__(self):
            self.produce = lambda: [1, 2, 3]
            self.consume = lambda x: consumed_results.append(x)

    stage = ProduceAndConsumeStage()
    result = stage(None)
    assert result == [1, 2, 3], "PipelineStage with produce and consume should correctly produce output."
    assert consumed_results == [1, 2, 3], "PipelineStage with produce and consume should correctly consume produced output."


def test_pipeline_stage_with_all_methods():
    consumed_results = []

    @dataclass
    class AllMethodsStage(PipelineStage[int, int]):
        def __init__(self):
            self.transform = lambda x: [x + 1]
            self.produce = lambda: [10]
            self.consume = lambda x: consumed_results.append(x)

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
    assert result == [(20-3), (((5+1)*2)-3)], "Pipeline should correctly process through complex stage combinations."
    assert consumed_results == [17, 9], "Pipeline should correctly consume results from complex stage combinations."
