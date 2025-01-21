
from dataclasses import dataclass
import json

import sys
import pathlib
sys.path.insert(0, str(pathlib.Path(__file__).resolve().parent.parent))
sys.path.insert(0, str(pathlib.Path(__file__).resolve().parent.parent.parent / "generics" / "generics"))
from pipeline.pipeline import to_filename
from pipeline.library import WriteJsonToFile, FormatPrintToConsole


@to_filename(lambda _: "mock_file")
@dataclass
class MockInput:
    data: str

    def __str__(self):
        return self.data


def test_format_print_to_console_no_formatters():
    input_data = MockInput(data="test data")
    stage = FormatPrintToConsole()
    assert stage.to_string(input_data) == "test data"


def test_format_print_to_console_content_formatter():
    input_data = MockInput(data="test data")
    stage = FormatPrintToConsole(content_formatter=lambda x: f"Content: {x.data}\n")
    assert stage.to_string(input_data) == "Content: test data\n"


def test_format_print_to_console_prefix_formatter():
    input_data = MockInput(data="test data")
    stage = FormatPrintToConsole(prefix_formatter=lambda x: f"Prefix: {x.data}\n")
    assert stage.to_string(input_data) == "Prefix: test data\ntest data"


def test_format_print_to_console_postfix_formatter():
    input_data = MockInput(data="test data")
    stage = FormatPrintToConsole(postfix_formatter=lambda x: f"\nPostfix: {x.data}")
    assert stage.to_string(input_data) == "test data\nPostfix: test data"


def test_format_print_to_console_content_and_prefix_formatters():
    input_data = MockInput(data="test data")
    stage = FormatPrintToConsole(
        content_formatter=lambda x: f"Content: {x.data}\n",
        prefix_formatter=lambda x: f"Prefix: {x.data}\n"
    )
    assert stage.to_string(input_data) == "Prefix: test data\nContent: test data\n"


def test_format_print_to_console_content_and_postfix_formatters():
    input_data = MockInput(data="test data")
    stage = FormatPrintToConsole(
        content_formatter=lambda x: f"Content: {x.data}\n",
        postfix_formatter=lambda x: f"Postfix: {x.data}\n"
    )
    assert stage.to_string(input_data) == "Content: test data\nPostfix: test data\n"


def test_format_print_to_console_prefix_and_postfix_formatters():
    input_data = MockInput(data="test data")
    stage = FormatPrintToConsole(
        prefix_formatter=lambda x: f"Prefix: {x.data}\n",
        postfix_formatter=lambda x: f"\nPostfix: {x.data}\n"
    )
    assert stage.to_string(input_data) == "Prefix: test data\ntest data\nPostfix: test data\n"


def test_format_print_to_console_all_formatters():
    input_data = MockInput(data="test data")
    stage = FormatPrintToConsole(
        content_formatter=lambda x: f"Content: {x.data}\n",
        prefix_formatter=lambda x: f"Prefix: {x.data}\n",
        postfix_formatter=lambda x: f"Postfix: {x.data}\n"
    )
    assert stage.to_string(input_data) == "Prefix: test data\nContent: test data\nPostfix: test data\n"


def test_write_json_to_file_to_json():
    input_data = MockInput(data="test data")
    stage = WriteJsonToFile(target_directory=".")
    expected_json = json.dumps({"data": "test data"}, indent=4)
    assert stage.to_json(input_data) == expected_json


def test_write_json_to_file_to_json_empty_data():
    input_data = MockInput(data="")
    stage = WriteJsonToFile(target_directory=".")
    expected_json = json.dumps({"data": ""}, indent=4)
    assert stage.to_json(input_data) == expected_json


def test_write_json_to_file_to_json_special_characters():
    input_data = MockInput(data="test data with special characters: !@#$%^&*()")
    stage = WriteJsonToFile(target_directory=".")
    expected_json = json.dumps({"data": "test data with special characters: !@#$%^&*()"}, indent=4)
    assert stage.to_json(input_data) == expected_json


def test_write_json_to_file_to_json_unicode_characters():
    input_data = MockInput(data="test data with unicode: üñîçødë")
    stage = WriteJsonToFile(target_directory=".")
    expected_json = json.dumps({"data": "test data with unicode: üñîçødë"}, indent=4)
    assert stage.to_json(input_data) == expected_json
