

from collections.abc import Callable
from dataclasses import dataclass, asdict
import json
import pathlib
import os

from .pipeline import TStageInput, TStageResult, PipelineStage


@dataclass
class FormatPrintToConsole(PipelineStage[TStageInput, TStageResult]):
    """
    This pipeline stage prints the input to the console.

    Attributes:
        content_formatter (Callable[[TPipelineInput], str] | None):
            An optional function that formats the input content.
        prefix_formatter (Callable[[TPipelineInput], str] | None):
            An optional function that formats the input prefix.
        postfix_formatter (Callable[[TPipelineInput], str] | None):
            An optional function that formats the input postfix.

    Methods:
        to_string(input: TPipelineInput) -> str:
            Formats the input to a string.
        consume(input: TPipelineInput) -> None:
            Prints the string representation of the input to the console.
    """

    content_formatter: Callable[[TStageInput], str] | None = None
    prefix_formatter: Callable[[TStageInput], str] | None = None
    postfix_formatter: Callable[[TStageInput], str] | None = None

    def to_string(self, input: TStageInput) -> str:
        return f"""\
{self.prefix_formatter(input) if self.prefix_formatter else ""}\
{self.content_formatter(input) if self.content_formatter else f"{input}"}\
{self.postfix_formatter(input) if self.postfix_formatter else ""}"""

    def consume(self, input: TStageInput) -> None:
        print(self.to_string(input))


@dataclass
class WriteJsonToFile(PipelineStage[TStageInput, TStageResult]):
    """
    This pipeline stage writes the input object to a JSON file.

    Ensure that the input object is serializable to JSON.
    Ensure that the input object is decorated with the `to_filename` decorator.

    Attributes:
        target_directory (str):
            [Mandatory] The directory where the JSON files will be written.

    Methods:
        get_filename(input: TPipelineInput) -> str:
            Returns the filename for the JSON file.
            Override this method to customize the filename.
            By default, if the input object has a `filename` attribute, it will be used.
        consume(input: TPipelineInput) -> None:
            Writes the input to a JSON file with the filename provided by the filename_extractor function.
    """
    target_directory: str

    def __post_init__(self):
        pathlib.Path(self.target_directory).mkdir(parents=True, exist_ok=True)

    def get_filename(self, input: TStageInput) -> str:
        if getattr(input, "filename", None) is not None:
            return input.filename
        else:
            pass

    def to_json(self, input: TStageInput) -> str:
        return json.dumps(asdict(input), indent=4)

    def consume(self, input: TStageInput) -> None:
        full_file_name = os.path.join(self.target_directory, self.get_filename(input))
        with open(full_file_name, "w", encoding='utf-8') as file:
            file.write(self.to_json(input))
