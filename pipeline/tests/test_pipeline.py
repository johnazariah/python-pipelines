import pytest
from pipeline.pipeline.pipeline import InMemoryPipeline, PipelineStage


class InitialStage(PipelineStage[int, int]):
    def run(self, input: int) -> list[int]:
        return [input * 2]


class IntermediateStage(PipelineStage[int, str]):
    def run(self, input: int) -> list[str]:
        return [str(input)]


class FinalStage(PipelineStage[str, str]):
    def run(self, input: str) -> list[str]:
        return [input.upper()]


def test_pipeline_with_stages():
    stage1 = InitialStage()
    stage2 = InitialStage()
    pipeline = InMemoryPipeline[int, int]([stage1, stage2])

    result = pipeline(5)
    assert result == [20], "InMemoryPipeline should correctly process with two stages doubling the input."


def test_pipeline_with_no_stages():
    pipeline = InMemoryPipeline[int, int]()

    result = pipeline(5)
    assert result == [5], "InMemoryPipeline with no stages should return input unchanged."


def test_pipeline_valid_type_chain():
    initial_stage = InitialStage()
    intermediate_stage = IntermediateStage()
    final_stage = FinalStage()
    pipeline = InMemoryPipeline[int, str]([initial_stage, intermediate_stage, final_stage])

    result = pipeline(10)
    assert result == ["20"], "InMemoryPipeline with a valid type chain should process input correctly through intermediate stages."


def test_pipeline_invalid_type_chain():
    class MismatchedStage(PipelineStage[str, int]):
        def run(self, input: str) -> list[int]:
            return [len(input)]

    stage1 = InitialStage()
    mismatched_stage = MismatchedStage()

    with pytest.raises(TypeError):
        InMemoryPipeline[int, int]([stage1, mismatched_stage])


def test_pipeline_input_output_type_match():
    class StringStage(PipelineStage[str, str]):
        def run(self, input: str) -> list[str]:
            return [input.upper()]

    with pytest.raises(TypeError):
        InMemoryPipeline[int, str]([InitialStage(), StringStage()])
