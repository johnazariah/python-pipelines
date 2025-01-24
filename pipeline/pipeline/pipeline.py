# Copyright (c) 2024 Contributors
# Authors: Christian Smith; John Azariah
# All rights reserved.

from functools import reduce, wraps
from dataclasses import dataclass
from typing import Generic, TypeVar, Any
from collections.abc import Iterable, Callable
from abc import ABC, abstractmethod

from generics import TypeAnnotatedMeta

TStageInput = TypeVar('TStageInput')
TStageResult = TypeVar('TStageResult')
TStageOther = TypeVar('TStageOther')

TPipelineInput = TypeVar('TPipelineInput')
TPipelineResult = TypeVar('TPipelineResult')
TPipelineStageAdapter = TypeVar('TPipelineStageAdapter')
TPipelineContext = TypeVar('TPipelineContext')

TIgnore = TypeVar('TIgnore')


# Custom decorator to generate filename
def to_filename(lambda_func):
    """Use this decorator to specify the filename for a dataclass instance.

    This decorator injects a `filename` attribute into the dataclass instance, which will be generated using the provided lambda function.
    Do not specify the extension for the filename. The extension will be added automatically based on the file format by the pipeline.
    """
    def decorator(cls):
        original_init = cls.__init__

        @wraps(original_init)
        def new_init(self, *args, **kwargs):
            original_init(self, *args, **kwargs)
            # Generate the filename using the provided lambda function
            self.filename = lambda_func(self)

        cls.__init__ = new_init
        return cls
    return decorator


# # Example usage
# @to_filename(lambda obj: f"{obj.first_name}_{obj.last_name}_{obj.id}")
# @dataclass
# class User:
#     first_name: str
#     last_name: str
#     id: int

# # Test the decorated dataclass
# user1 = User(first_name="John", last_name="Doe", id=123)
# print(user1.filename)  # Output: John_Doe_123


@dataclass
class PipelineStage(Generic[TStageInput, TStageResult], metaclass=TypeAnnotatedMeta):
    """This is a base class for a generic pipeline stage."""

    def produce(self) -> Iterable[TStageResult]:
        return []

    def transform(self, input: TStageInput) -> Iterable[TStageResult]:
        return []

    def consume(self, result: TStageResult) -> None:
        return

    def run(self, input: TStageInput) -> Iterable[TStageResult]:
        produce_results = list(self.produce()) if self.produce else [input]
        transform_results = list(self.transform(input)) if self.transform else []
        results = produce_results + transform_results if produce_results or transform_results else [input]
        if self.consume:
            list(map(self.consume, results))
        return results

    def __call__(self, input: TStageInput) -> Iterable[TStageResult]:
        return self.run(input)

    def __rshift__(self, other: "PipelineStage[TStageResult, TStageOther]") -> "PipelineStage[TStageInput, TStageOther]":
        if self.TStageResult != other.TStageInput:
            raise TypeError(
                f"Output type of {self} ({self.TStageResult}) does not match input type of {other} ({other.TStageInput})."
            )

        class CombinedStage(PipelineStage[self.TStageInput, other.TStageResult]):
            def transform(_self, input: self.TStageInput) -> Iterable[TStageOther]:
                """Sequentially transform data from both stages."""
                intermediate_results = self.run(input)
                final_results = []
                for intermediate in intermediate_results:
                    final_results.extend(other.run(intermediate))
                return final_results

        return CombinedStage()


@dataclass
class IdentityStage(PipelineStage[TStageInput, TStageInput]):
    transform: Callable[[TStageInput], Iterable[TStageInput]] = lambda x: [x]


class Pipeline(Generic[TPipelineInput, TPipelineResult], metaclass=TypeAnnotatedMeta):
    """This is a base class for a pipeline of stages

    It takes as its only argument a list of stages, which progressively transform
    an input of type `TPipelineInput` to an output sequence of type `TPipelineResult`.

    The stages are validated to ensure that the input and output types of adjoining stages are compatible.

    By default, the pipeline composes and runs its stages in memory.
    Subclass as necessary and implement the `run` method to effect other forms of composition.
    """
    def __init__(self, stages: Iterable[PipelineStage[Any, Any]] = None):
        """Validates that the stages passed in are compatible with each other and with the expected input and output types."""
        self.stages = self._validate_stages(list(stages or [IdentityStage[self.TPipelineInput, self.TPipelineInput]()]))

    def _validate_stages(
        self, stages_list: list[PipelineStage[Any, Any]]
    ) -> list[PipelineStage[Any, Any]]:
        if not stages_list:
            raise ValueError("PipelineBase must have at least one stage.")

        def validate_type(expected_input_type, stage):
            if expected_input_type != stage.TStageInput:
                raise TypeError(
                    f"Input type of {stage} ({stage.TStageInput}) does not match {expected_input_type}."
                )
            return stage.TStageResult

        if self.TPipelineResult != reduce(validate_type, stages_list, self.TPipelineInput):
            raise TypeError(
                f"Output type of the last stage ({stages_list[-1].TStageResult}) does not match {self.TPipelineResult}."
            )

        return stages_list

    def run(self, input: TPipelineInput) -> list[TPipelineResult]:
        def flatten(nested_iterables: list[list[TPipelineResult]]) -> Iterable[TPipelineResult]:
            for iterable in nested_iterables:
                yield from iterable

        results = [input]
        for stage in self.stages:
            results = list(flatten(stage(r) for r in results))

        return results

    def __call__(self, input: TPipelineInput) -> list[TPipelineResult]:
        return self.run(input)


class PipelineStageEnhancer(ABC, Generic[TPipelineContext], metaclass=TypeAnnotatedMeta):
    def __init__(self, stage: PipelineStage[Any, Any], stage_index: int, stage_count: int):
        self.stage = stage
        self.stage_index = stage_index
        self.stage_count = stage_count

    @abstractmethod
    def generate_inputs(self, context: TPipelineContext) -> Iterable[Any]:
        pass

    @abstractmethod
    def process_output(self, context: TPipelineContext, result: Any, result_index: int, result_count: int) -> None:
        pass

    def run(self, context: TPipelineContext) -> TPipelineContext:
        def process_outputs(context, results: list[Any]):
            result_count = len(results)
            for index, result in enumerate(results, start=1):
                self.process_output(context, result, result_index=index, result_count=result_count)
            return context

        match list(self.stage.produce()):
            case None | []:
                return reduce(lambda ctx, input: process_outputs(ctx, self.stage(input)), list(self.generate_inputs(context)), context)
            case produce_results:
                return process_outputs(context, produce_results)

    def __call__(self, context: TPipelineContext) -> TPipelineContext:
        return self.run(context)


@dataclass
class EnhancedPipeline(ABC, Generic[TPipelineStageAdapter, TPipelineContext], metaclass=TypeAnnotatedMeta):
    pipeline: Pipeline[Any, Any]
    context: TPipelineContext

    def __post_init__(self):
        stage_count = len(self.pipeline.stages)
        self.contextual_stages = [
            self.TPipelineStageAdapter(stage, stage_index=index, stage_count=stage_count)
            for index, stage in enumerate(self.pipeline.stages)
        ]

    def run(self) -> TPipelineContext:
        return reduce(lambda context, contextual_stage: contextual_stage(context), self.contextual_stages, self.context)

    def __call__(self) -> TPipelineContext:
        return self.run()
