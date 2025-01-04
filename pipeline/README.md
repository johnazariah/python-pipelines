
# Pipeline Framework Documentation

## Overview
This framework provides a modular and extensible pipeline structure for transforming data through a series of stages. Each stage is responsible for producing, transforming, and consuming data as needed. The framework includes base classes for pipelines and stages, along with contextual processing capabilities.

---

## Modules

### **PipelineStage**
A generic class representing a single stage in the pipeline. This class provides flexibility to define various types of stages such as producing data, transforming data, or consuming data, and can be used in isolation or as part of a larger pipeline.

#### Attributes:
- **produce**: A callable that produces an iterable of results. If `produce` is not specified, this step is skipped.
- **transform**: A callable that accepts an input of type `TStageInput` and returns an iterable of `TStageResult`. This is typically used to apply a transformation to the input data.
- **consume**: A callable that processes each result produced or transformed by the stage. If specified, `consume` is applied to all results in the stage.

#### Methods:
- **run(input: TStageInput)**: Executes the stage by:
  1. Calling `produce` (if defined) to generate initial results.
  2. Applying the `transform` function to the input data.
  3. Combining the results of `produce` and `transform`. The `produce` values will precede the `transform` values.
  4. Optionally passing the combined results to the `consume` function.

  Returns an iterable of results.

- **__call__(input: TStageInput)**: A shorthand for invoking the `run` method, enabling the stage to be used like a function.

#### Key Behaviors:
- If both `produce` and `transform` are defined, their results are combined.
- If neither `produce` nor `transform` is defined, the input is returned as the result.
- The `consume` function is applied to all results but does not alter the returned output.

#### Example:
```python
# Define a stage that produces static values and applies a transformation
stage = PipelineStage(
    produce=lambda: [1, 2, 3],
    transform=lambda x: [x * 2],
    consume=lambda r: print(f"Consumed: {r}")
)

output = stage(5)  # Produces: [1, 2, 3], Transforms: [10], Output: [1, 2, 3, 10]
# Output to consume: Consumed: 1, Consumed: 2, Consumed: 3, Consumed: 10
```

#### Use Cases:
- **Data Generation**: Use `produce` to create an initial dataset, e.g., reading files or fetching data from an API.
- **Data Transformation**: Apply `transform` to modify or filter the input data.
- **Data Consumption**: Use `consume` for side effects such as logging, storing results, or triggering downstream actions.

---

### **IdentityStage**
A subclass of `PipelineStage` that passes input through without modification.

#### Attributes:
- **transform**: Defaults to a lambda function that returns the input as an iterable.

#### Example:
```python
identity = IdentityStage()
output = identity(5)  # Output: [5]
```

---

### **Pipeline**
A sequence of stages that progressively transforms input data.

#### Attributes:
- **stages**: A list of `PipelineStage` instances.

#### Methods:
- **__init__(stages: Iterable[PipelineStage])**: Validates and initializes the pipeline stages.
- **run(input: TPipelineInput)**: Executes the pipeline, passing data through each stage.
- **__call__(input: TPipelineInput)**: Alias for `run`.

#### Key Behaviors:
- Ensures type compatibility between stages during initialization.
- Processes input iteratively through all stages, allowing intermediate results to flow to subsequent stages.
- Returns a flattened list of results after processing through all stages.

#### Example:
```python
pipeline = Pipeline(stages=[IdentityStage()])
output = pipeline.run(5)  # Output: [5]
```

---

### **ContextualPipelineStage**
An abstract base class for a pipeline stage that operates within a specific context. This is particularly useful for scenarios where stages need access to shared state or resources.

#### Attributes:
- **stage**: The `PipelineStage` to execute.
- **stage_index**: The index of the stage in the pipeline.
- **stage_count**: The total number of stages in the pipeline.

#### Methods:
- **generate_inputs(context: TPipelineContext)**: Abstract method to generate inputs from the context. Subclasses must implement this to define how input data is sourced.
- **process_output(context: TPipelineContext, result: Any, result_index: int, result_count: int)**: Abstract method to process outputs within the context. Subclasses must implement this to define how results are handled or stored.
- **run(context: TPipelineContext)**: Executes the stage within the given context by sourcing inputs, processing them through the stage, and handling outputs.
- **__call__(context: TPipelineContext)**: Alias for `run`.

#### Key Behaviors:
- Orchestrates the interaction between the stage and the shared context.
- Supports fine-grained control over how inputs are sourced and outputs are processed.

#### Example:
```python
class CustomContextualStage(ContextualPipelineStage):
    def generate_inputs(self, context):
        return context['data']

    def process_output(self, context, result, result_index, result_count):
        context['results'].append(result)
```

---

### **ContextualPipeline**
An abstract base class for pipelines that operate within a specific context. Designed for use cases where shared state or resources must be managed across multiple stages.

#### Attributes:
- **pipeline**: The `Pipeline` instance to execute.
- **context**: The context object shared across the pipeline stages.

#### Methods:
- **lift(stage: PipelineStage, stage_index: int, stage_count: int)**: Abstract method to lift a stage into a contextual stage. This is used to wrap regular pipeline stages with context-awareness.
- **run()**: Executes all stages in the pipeline within the given context, managing the flow of data and results between stages.

#### Key Behaviors:
- Provides a higher-level abstraction over standard pipelines by incorporating shared state.
- Facilitates the extension of pipeline functionality for domain-specific use cases, such as batch processing or distributed computation.

#### Example:
```python
class MyContextualPipeline(ContextualPipeline):
    def lift(self, stage, stage_index, stage_count):
        return CustomContextualStage(stage=stage, stage_index=stage_index, stage_count=stage_count)
```

---

### **FileSystemContext**
A data class that represents the file system context used in a pipeline. Encapsulates information about the root directory for file-based operations.

#### Attributes:
- **document_root**: The root directory for input and output operations.

#### Key Behaviors:
- Acts as a shared resource for file system-based pipelines, ensuring consistent paths for input and output.

#### Example:
```python
context = FileSystemContext(document_root="/data")
```

---

### **FileSystemCoupledPipelineStage**
A contextual pipeline stage tailored for file system operations. Extends the functionality of `ContextualPipelineStage` to handle file-based inputs and outputs.

#### Attributes:
- **input_subfolder**: The input folder name for the stage.
- **output_subfolder**: The output folder name for the stage.
- **json_decoder**: A JSON decoder for reading input files.
- **json_encoder**: A JSON encoder for writing output files.

#### Methods:
- **__post_init__()**: Initializes default subfolder names and JSON encoders/decoders if not provided.
- **generate_inputs(context: FileSystemContext)**: Reads and decodes JSON files from the input folder.
- **process_output(context: FileSystemContext, result: Any, result_index: int, result_count: int)**: Writes JSON files to the output folder based on the result index.

#### Key Behaviors:
- Automates the reading and writing of JSON files for pipeline stages.
- Supports configurable subfolder structures for stage-specific inputs and outputs.

#### Example:
```python
context = FileSystemContext(document_root="/data")
stage = FileSystemCoupledPipelineStage(stage=my_stage, stage_index=0, stage_count=1)
inputs = list(stage.generate_inputs(context))
stage.process_output(context, result=inputs[0], result_index=1, result_count=1)
```

---

### **FileSystemCoupledPipeline**
A contextual pipeline designed to operate with file system inputs and outputs. Facilitates the integration of pipelines with structured file storage.

#### Attributes:
- **context**: A `FileSystemContext` instance containing the document root.
- **pipeline**: The base pipeline to execute.

#### Methods:
- **lift(stage: Pipeline[Any, Any], stage_index: int, stage_count: int)**: Converts a base pipeline stage into a `FileSystemCoupledPipelineStage`.
- **__init__(document_root: str, pipeline: Pipeline[Any, Any])**: Initializes the pipeline with a document root and stages.

#### Key Behaviors:
- Provides a seamless interface for pipelines that require file-based inputs and outputs.
- Ensures consistent handling of file paths and operations across stages.

#### Example:
```python
pipeline = Pipeline(stages=[IdentityStage()])
fs_pipeline = FileSystemCoupledPipeline(document_root="/data", pipeline=pipeline)
fs_pipeline.run()
```
