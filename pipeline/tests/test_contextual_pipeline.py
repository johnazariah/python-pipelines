from pipeline.pipeline.pipeline import Pipeline, PipelineStage, ContextualPipelineStage, ContextualPipeline
from collections.abc import Iterable
from dataclasses import dataclass

from test_pipeline import InitialStage, IntermediateStage, FinalStage, ProduceOnlyStage


class DictCoupledPipelineStage(ContextualPipelineStage[dict]):
    def __init__(self, stage, stage_index, stage_count):
        super().__init__(stage=stage, stage_index=stage_index, stage_count=stage_count)

    def generate_inputs(self, context: dict) -> Iterable[int]:
        if self.stage_index == 0:
            return context.get("initial_inputs", [])
        else:
            return context.get(f"stage_{self.stage_index}", [])

    def process_output(self, context: dict, result: int, result_index: int, result_count: int) -> None:
        context.setdefault(f"stage_{self.stage_index + 1}", []).append(result)


class DictCoupledPipeline(ContextualPipeline[dict]):
    def lift(self, stage, stage_index, stage_count):
        return DictCoupledPipelineStage(stage=stage, stage_index=stage_index, stage_count=stage_count)


def test_contextual_pipeline():
    pipeline = Pipeline[int, str]([InitialStage(), IntermediateStage(), FinalStage()])
    context = {"initial_inputs": [5, 10]}

    contextual_pipeline = DictCoupledPipeline(pipeline, context)
    result_context = contextual_pipeline.run()

    assert result_context["stage_1"] == [10, 20], "ContextualPipeline should correctly process initial stage outputs."
    assert result_context["stage_2"] == ["10", "20"], "ContextualPipeline should correctly process intermediate stage outputs."
    assert result_context["stage_3"] == ["10", "20"], "ContextualPipeline should correctly process final stage outputs."


def test_first_stage_produce_function_is_called_if_provided():
    pipeline = Pipeline[int, str]([ProduceOnlyStage(), IntermediateStage(), FinalStage()])
    context = {}

    contextual_pipeline = DictCoupledPipeline(pipeline, context)
    result_context = contextual_pipeline.run()

    assert result_context["stage_1"] == [1, 2, 3], "ContextualPipeline should correctly process initial stage outputs."
    assert result_context["stage_2"] == ['1', '2', '3'], "ContextualPipeline should correctly process intermediate stage outputs."
    assert result_context["stage_3"] == ['1', '2', '3'], "ContextualPipeline should correctly process final stage outputs."


def test_first_stage_produce_function_is_called_if_provided_even_if_inputs_are_provided():
    pipeline = Pipeline[int, str]([ProduceOnlyStage(), IntermediateStage(), FinalStage()])
    context = {"initial_inputs": [5, 10]}  # inputs are provided but produce function should be called

    contextual_pipeline = DictCoupledPipeline(pipeline, context)
    result_context = contextual_pipeline.run()

    assert result_context["stage_1"] == [1, 2, 3], "ContextualPipeline should correctly process initial stage outputs."
    assert result_context["stage_2"] == ['1', '2', '3'], "ContextualPipeline should correctly process intermediate stage outputs."
    assert result_context["stage_3"] == ['1', '2', '3'], "ContextualPipeline should correctly process final stage outputs."


def test_contextual_pipeline_with_partial_inputs():
    pipeline = Pipeline[int, str]([InitialStage(), IntermediateStage(), FinalStage()])
    context = {"initial_inputs": [5]}

    contextual_pipeline = DictCoupledPipeline(pipeline, context)
    result_context = contextual_pipeline.run()

    assert result_context["stage_1"] == [10], "ContextualPipeline should correctly process initial stage outputs with partial inputs."
    assert result_context["stage_2"] == ["10"], "ContextualPipeline should correctly process intermediate stage outputs with partial inputs."
    assert result_context["stage_3"] == ["10"], "ContextualPipeline should correctly process final stage outputs with partial inputs."


def test_pipeline_with_consume_only_stage():
    @dataclass
    class ConsumeOnlyStage(PipelineStage[str, str]):
        result = ""

        def append(self, x: str):
            self.result += ", " + x  #  Do something explicitly garbage so we know we definitely consumed the output!

        def __init__(self):
            self.consume = self.append

    collector = ConsumeOnlyStage()

    pipeline = Pipeline[int, str]([InitialStage(), IntermediateStage(), FinalStage(), collector])
    context = {"initial_inputs": [5, 10]}

    contextual_pipeline = DictCoupledPipeline(pipeline, context)
    result_context = contextual_pipeline.run()

    assert result_context["stage_1"] == [10, 20], "ContextualPipeline should correctly process initial stage outputs."
    assert result_context["stage_2"] == ["10", "20"], "ContextualPipeline should correctly process intermediate stage outputs."
    assert result_context["stage_3"] == ["10", "20"], "ContextualPipeline should correctly process final stage outputs."
    assert collector.result == ", 10, 20", "ConsumeOnlyStage should correctly consume final stage outputs."