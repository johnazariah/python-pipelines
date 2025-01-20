

from collections.abc import Callable
from dataclasses import dataclass, asdict
import json

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
    This pipeline stage writes the input to a JSON file.
    Attributes:
        filename_extractor (Callable[[TPipelineInput], str]):
            [Mandatory] A function that extracts the full filename from the input.
    Methods:
        consume(input: TPipelineInput) -> None:
            Writes the input to a JSON file with the filename provided by the filename_extractor function.
    """
    filename_extractor: Callable[[TStageInput], str]

    def to_json(self, input: TStageInput) -> str:
        return json.dumps(asdict(input), indent=4)

    def consume(self, input: TStageInput) -> None:
        full_file_name = self.filename_extractor(input)

        with open(full_file_name, "w", encoding='utf-8') as file:
            file.write(self.to_json(input))
