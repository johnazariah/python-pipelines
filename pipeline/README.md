
# Pipeline Framework Documentation

## Overview
This framework provides a modular and extensible pipeline structure for transforming data through a series of stages.
Each stage is responsible for producing, transforming, and consuming data as needed.
Its design emphasizes flexibility, type safety, and composability, making it suitable for various data transformation and workflow orchestration tasks.
The framework includes base classes for pipelines and stages, along with contextual processing capabilities.

---

## Modules

### **PipelineStage**
A generic class representing a single stage in the pipeline.
This class provides flexibility to define various types of stages such as producing data, transforming data, or consuming data, and can be used in isolation or as part of a larger pipeline.

#### Attributes:
- **produce**: Optional. A callable that produces an iterable of results. Generally used when the stage is the first stage of a pipeline and generates the starting data set.
- **transform**: Optional. A callable that accepts an input of type `TStageInput` and returns an iterable of `TStageResult`. This is typically used to apply a transformation to the input data.
- **consume**: Optional. A callable that processes each result produced or transformed by the stage. Generally used when the stage is the last stage of a pipeline and all data needs to be consumed somehow - say by writing it to a database.

#### Methods:
- **__rshift__(other)**: Chains this stage to another stage, after ensuring type compatibility. It creates a single new stage that sequentially applies both transformations. This is handy for doing debug operations, for example, or building a single stage from smaller stages.

- **run(input: TStageInput)**: Executes the stage by:
  1. Calling `produce` (if defined) to generate initial results.
  2. Applying `transform` (if defined) to any provided input data, generating a sequence of results.
  3. Combining the results of `produce` and `transform`. The `produce` values will precede the `transform` values.
  4. Applying `consume` (if defined) on each of these combined results.

  Returns the list of results as produced by step (3) above.

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
- If no stages are provided, a default identity stage is injected so that a pipeline acts as an identity operation.
- Ensures type compatibility between stages during initialization.
- Processes input iteratively through all stages, allowing intermediate results to flow to subsequent stages.
- Returns a flattened list of results after processing through all stages. This use of a list instead of a single value as the result allows for stages that perform operations that produce a set of results from a single input.

#### Example:
```python
pipeline = Pipeline[int, int](stages=[]) # a default stage of type IdentityStage[int, int] is automatically provided
output = pipeline.run(5)  # Output: [5]
```

---

### **EnhancedPipeline**
An abstract base class for pipelines that operate within a specific context. Designed for use cases where shared state or resources must be managed across multiple stages.

This construct allows control over a pipeline's execution by capturing each stage and enhancing it with a context, which wraps the pipeline's execution stage with control over how inputs to the stage are provided and how outputs from the stage are consumed.

The canonical example use case would be to execute a given pipeline within a file system, where each stage consumes data from a particular folder and writes outputs to another folder for the next stage to read from. The coupling logic between stages is independent of the functional logic of the stages themselves, and we can interject the file system between stages of _any_ pipeline using this approach.

#### Type Arguments
- **TPipelineStageAdapter**: This class is an specialization of the `PipelineStageEnhancer` interface, and provides the logic to wrap a `PipelineStage` with pre- and post- operations and execute that stage with a context passed in.
- **TPipelineContext**: This is the type of the context object that will be passed through all the stages of an enhanced pipeline.

#### Attributes:
- **pipeline**: The `Pipeline` instance to execute.
- **context**: The context object shared across the pipeline stages.

#### Methods:
- **run()**: Executes all stages in the pipeline within the given context, managing the flow of data and results between stages.

#### Key Behaviors:
- Provides a higher-level abstraction over standard pipelines by incorporating shared state and controllable execution context

---

### **PipelineStageEnhancer**
This class takes a pipeline stage and enhances it to run within a controlled environment sharing a context with all other stages.

Specifically, given a pipeline stage `p` and a shared context `c`, this class provides a way to:

1. Extract the inputs for the `p` from `c`
2. Apply the pipeline stage to each input, collecting the result set `r` for each input
3. Submits the flattened set of all the `r` sets to `c` for passing on to the next stage.

In the canonical file-system-coupled example, this enhancing class takes the context of a root directory name, opens a folder with the number of the given stage, reads each file to extract an input to `p`, invokes `p` with the input, and writes each of the result values into another folder named after the number of the succeeding stage.

In this way, a normal pipeline can be run in the context of a file system that collects all the intermediate data produced by each stage.

#### Type Arguments
- **TPipelineContext**: This is the type of the context object that will be passed through all the stages of an enhanced pipeline.

#### Attributes:
- **stage**: The `PipelineStage` to execute.
- **stage_index**: The index of the stage in the pipeline.
- **stage_count**: The total number of stages in the pipeline.

#### Methods:
- **generate_inputs(context: TPipelineContext)**: Abstract method to generate inputs from the context. Subclasses must implement this to define how input data is sourced from the context object provided.
- **process_output(context: TPipelineContext, result: Any, result_index: int, result_count: int)**: Abstract method to process outputs within the context. Subclasses must implement this to define how results are handled or stored with reference to the context object provided.
- **run(context: TPipelineContext)**: Executes the stage within the given context by sourcing inputs, processing them through the stage, and handling outputs.
- **__call__(context: TPipelineContext)**: Alias for `run`.

#### Key Behaviors:
- Orchestrates the interaction between stages through the shared context.
- Supports fine-grained control over how inputs are sourced and outputs are processed.

#### Example:

This is an example of controlled execution within a `dict`. This enhanced pipeline would take its inputs from the key associated with the stage in the dictionary, and write its outputs to a key associated with the following stage.

Once this enhanced pipeline is executed, the context dictionary would contain all the results of all of the stages of the pipeline in it.

```python
class DictionaryEnhancer(PipelineStageEnhancer[dict]):
    def generate_inputs(self, context: dict) -> Iterable[int]:
        if self.stage_index == 0:
            return context.get("initial_inputs", [])
        else:
            return context.get(f"stage_{self.stage_index}", [])

    def process_output(self, context: dict, result: int, result_index: int, result_count: int) -> None:
        context.setdefault(f"stage_{self.stage_index + 1}", []).append(result)


class DictCoupledPipeline(EnhancedPipeline[DictionaryEnhancer, dict]):
    pass
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

### **FileSystemEnhancer**
A contextual pipeline stage tailored for file system operations. Extends the functionality of `PipelineStageEnhancer` to handle file-based inputs and outputs.

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

---

### **FileSystemCoupledPipeline**
A contextual pipeline designed to operate with file system inputs and outputs. Facilitates the integration of pipelines with structured file storage.

#### Attributes:
- **context**: A `FileSystemContext` instance containing the document root.
- **pipeline**: The base pipeline to execute.

#### Methods:
- **run()**: Runs the given pipeline within the context of `FileSystemContext`. Specifically this means that each stage will read data from a folder and write the results into another folder under the `document_root` of the context.

#### Key Behaviors:
- Provides a seamless way of separating out file-persistance between stages in a pipeline.

#### Example:
```python
pipeline = Pipeline(stages=[IdentityStage()])
fs_pipeline = FileSystemCoupledPipeline(document_root="/data", pipeline=pipeline)
fs_pipeline.run()
```
