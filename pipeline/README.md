
# Documentation for Pipeline Classes and Methods

## Overview
This code defines a framework for building pipelines where data passes through multiple processing stages. Each stage transforms the input into an iterable output, and stages are composed to form a complete pipeline. The key components include:

1. **PipelineStage**: Abstract base class for a single stage in the pipeline.
2. **IdentityStage**: A concrete implementation of `PipelineStage` that returns its input unchanged.
3. **PipelineBase**: Abstract base class for a sequence of stages forming a pipeline.
4. **InMemoryPipeline**: A concrete implementation of `PipelineBase` that processes the pipeline in memory.

---

## Class Details

### `PipelineStage`
**Definition**:
```python
@dataclass
class PipelineStage(ABC, Generic[TStageInput, TStageResult], metaclass=TypeAnnotatedMeta):
```
This is an abstract base class representing a single stage in a pipeline. Subclasses must implement the `run` method.

**Attributes**:
- None explicitly defined.

**Methods**:
1. `run(self, input: TStageInput) -> Iterable[TStageResult]`
   - Abstract method to be implemented by subclasses.
   - **Input**: A value of type `TStageInput`.
   - **Output**: An iterable of `TStageResult`.

2. `__call__(self, input: TStageInput) -> Iterable[TStageResult]`
   - Calls the `run` method to process the input.
   - Allows the stage to be invoked as a callable.

**Usage Example**:
```python
class MultiplyByTwoStage(PipelineStage[int, int]):
    def run(self, input: int) -> Iterable[int]:
        return [input * 2]

stage = MultiplyByTwoStage()
print(list(stage(5)))  # Output: [10]
```

---

### `IdentityStage`
**Definition**:
```python
@dataclass
class IdentityStage(PipelineStage[TStageInput, TStageInput]):
```
A concrete implementation of `PipelineStage` that returns the input unchanged.

**Methods**:
1. `run(self, input: TStageInput) -> Iterable[TStageInput]`
   - Returns the input wrapped in a list.

**Usage Example**:
```python
stage = IdentityStage()
print(list(stage("hello")))  # Output: ["hello"]
```

---

### `PipelineBase`
**Definition**:
```python
class PipelineBase(ABC, Generic[TPipelineInput, TPipelineResult], metaclass=TypeAnnotatedMeta):
```
An abstract base class for a pipeline consisting of multiple stages. Subclasses must implement the `run` method.

**Attributes**:
- `stages`: A list of `PipelineStage` instances.

**Methods**:
1. `__init__(self, stages: Iterable[PipelineStage[Any, Any]] = None)`
   - Validates the compatibility of stages and initializes the pipeline.
   - **Raises**:
     - `ValueError` if no stages are provided.
     - `TypeError` if the stages are incompatible.

2. `_validate_stages(self, stages_list: list[PipelineStage[Any, Any]]) -> list[PipelineStage[Any, Any]]`
   - Checks that the input and output types of adjoining stages match.

3. `run(self, input: TPipelineInput) -> list[TPipelineResult]`
   - Abstract method to be implemented by subclasses.

4. `__call__(self, input: TPipelineInput) -> list[TPipelineResult]`
   - Invokes the `run` method.

**Usage Example**:
```python
# Subclassing PipelineBase
class ExamplePipeline(PipelineBase[int, int]):
    def run(self, input: int) -> list[int]:
        results = input
        for stage in self.stages:
            results = list(stage(results))
        return results

pipeline = ExamplePipeline([MultiplyByTwoStage()])
print(pipeline(3))  # Output: [6]
```

---

### `InMemoryPipeline`
**Definition**:
```python
class InMemoryPipeline(PipelineBase[TPipelineInput, TPipelineResult]):
```
A concrete implementation of `PipelineBase` that processes data in memory.

**Methods**:
1. `__init__(self, stages: Iterable[PipelineStage[Any, Any]] = None)`
   - Calls the superclass constructor to initialize stages.

2. `run(self, input: TPipelineInput) -> list[TPipelineResult]`
   - Processes the input through all stages and flattens the results.

**Usage Example**:
```python
pipeline = InMemoryPipeline([
    MultiplyByTwoStage(),
    MultiplyByTwoStage()
])
print(pipeline(2))  # Output: [8]
```

---

## Key Concepts
1. **Type Validation**: Ensures stages are compatible by checking input and output types.

2. **Composability**: Stages are reusable and can be combined into pipelines.

3. **Generics**: Leverages Python generics to support various input and output types.

---

## Summary
This framework provides a robust way to build composable and type-safe data pipelines. Users can define custom stages by subclassing `PipelineStage`, validate and sequence them using `PipelineBase`, and process data using `InMemoryPipeline` or other implementations.
