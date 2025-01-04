# Copyright (c) 2024 Contributors
# Authors: Christian Smith; John Azariah
# All rights reserved.

from functools import reduce
from dataclasses import dataclass
from typing import Generic, TypeVar, Any
from abc import ABC, abstractmethod
from collections.abc import Iterable

from generics.generics.generics import TypeAnnotatedMeta


TStageInput = TypeVar('TStageInput')
TStageResult = TypeVar('TStageResult')


@dataclass
class PipelineStage(ABC, Generic[TStageInput, TStageResult], metaclass=TypeAnnotatedMeta):
    """This is a 'fat-function' representing a stage in a pipeline

    It effectively has the following signature:
        TStageInput -> Iterable[TStageResult]:

    Implement in a subclass with whatever context is required to run the stage.
    """
    @abstractmethod
    def run(self, input: TStageInput) -> Iterable[TStageResult]:
        pass

    def __call__(self, input: TStageInput) -> Iterable[TStageResult]:
        return self.run(input)


@dataclass
class IdentityStage(PipelineStage[TStageInput, TStageInput]):
    def run(self, input: TStageInput) -> Iterable[TStageInput]:
        return [input]


TPipelineInput = TypeVar('TPipelineInput')
TPipelineResult = TypeVar('TPipelineResult')


class PipelineBase(ABC, Generic[TPipelineInput, TPipelineResult], metaclass=TypeAnnotatedMeta):
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

    @abstractmethod
    def run(self, input: TPipelineInput) -> list[TPipelineResult]:
        pass

    def __call__(self, input: TPipelineInput) -> list[TPipelineResult]:
        return self.run(input)


class InMemoryPipeline(PipelineBase[TPipelineInput, TPipelineResult]):
    def __init__(self, stages: Iterable[PipelineStage[Any, Any]] = None):
        super().__init__(stages)

    def run(self, input: TPipelineInput) -> list[TPipelineResult]:
        def flatten(nested_iterables: Iterable[Iterable[TPipelineResult]]) -> Iterable[TPipelineResult]:
            for iterable in nested_iterables:
                yield from iterable

        results = [input]
        for stage in self.stages:
            results = list(flatten(stage(r) for r in results))

        return results
