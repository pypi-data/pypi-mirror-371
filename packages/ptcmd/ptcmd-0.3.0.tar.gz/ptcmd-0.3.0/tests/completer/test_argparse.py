import argparse
from unittest.mock import Mock

import pytest
from prompt_toolkit.document import Document

from ptcmd.completer import ArgparseCompleter


@pytest.fixture
def simple_parser() -> argparse.ArgumentParser:
    """Create a simple ArgumentParser for testing."""
    parser = argparse.ArgumentParser()
    parser.add_argument("-a", "--alpha", help="Alpha option")
    parser.add_argument("-b", "--beta", help="Beta option")
    parser.add_argument("positional", help="A positional argument", choices=["file1", "file2", "file3"])
    parser.add_argument("optional_pos", nargs="?", help="An optional positional argument")
    parser.add_argument("--choice", choices=["opt1", "opt2", "opt3"])
    parser.add_argument("--flag", action="store_true")
    parser.add_argument("--level", type=int)
    return parser


@pytest.fixture
def subcommand_parser() -> argparse.ArgumentParser:
    """Create an ArgumentParser with subcommands for testing."""
    parser = argparse.ArgumentParser()
    subparsers = parser.add_subparsers(dest="command")

    # First subcommand
    cmd1 = subparsers.add_parser("cmd1")
    cmd1.add_argument("--cmd1-opt", help="Command 1 option")
    cmd1.add_argument("cmd1_arg", help="Command 1 argument")

    # Second subcommand
    cmd2 = subparsers.add_parser("cmd2")
    cmd2.add_argument("--cmd2-opt", help="Command 2 option")
    cmd2.add_argument("cmd2_arg", choices=["a", "b", "c"], help="Command 2 argument")

    return parser


@pytest.fixture
def subcommand_completer(subcommand_parser: argparse.ArgumentParser) -> ArgparseCompleter:
    """Create an ArgparseCompleter instance with subcommands for testing."""
    return ArgparseCompleter(subcommand_parser)


@pytest.fixture
def completer(simple_parser: argparse.ArgumentParser) -> ArgparseCompleter:
    """Create an ArgparseCompleter instance for testing."""
    return ArgparseCompleter(simple_parser)


def test_init(simple_parser: argparse.ArgumentParser) -> None:
    """Test that the completer initializes correctly."""
    completer = ArgparseCompleter(simple_parser)
    assert completer._parser == simple_parser


def test_complete_option_prefix(completer: ArgparseCompleter) -> None:
    """Test completion of option prefixes."""
    # Create a document with a partial option
    document = Document(text="-a", cursor_position=2)
    complete_event = Mock()

    # Get completions
    completions = list(completer.get_completions(document, complete_event))

    # Should match -a and --alpha
    assert len(completions) == 1
    assert completions[0].text == "-a"
    assert completions[0].start_position == -2
    # Verify help text is included
    assert "Alpha option" in completions[0].display_meta_text


def test_complete_long_option_prefix(completer: ArgparseCompleter) -> None:
    """Test completion of long option prefixes."""
    # Create a document with a partial long option
    document = Document(text="--a", cursor_position=3)
    complete_event = Mock()

    # Get completions
    completions = list(completer.get_completions(document, complete_event))

    # Should match --alpha
    assert len(completions) == 1
    assert completions[0].text == "--alpha"
    assert completions[0].start_position == -3
    # Verify help text is included
    assert "Alpha option" in completions[0].display_meta_text


def test_subcommand_completion(subcommand_completer: ArgparseCompleter) -> None:
    """Test completion of subcommands."""
    # Test completing subcommands
    document = Document(text="c", cursor_position=1)
    completions = list(subcommand_completer.get_completions(document, Mock()))
    assert len(completions) == 2
    assert any(c.text == "cmd1" for c in completions)
    assert any(c.text == "cmd2" for c in completions)

    # Test completing after subcommand
    document = Document(text="cmd1 arg1 ", cursor_position=10)
    completions = list(subcommand_completer.get_completions(document, Mock()))
    assert len(completions) == 3
    assert any(c.text == "--cmd1-opt" for c in completions)


def test_subcommand_option_completion(subcommand_completer: ArgparseCompleter) -> None:
    """Test completion of subcommand options."""
    # Test completing subcommand options
    document = Document(text="cmd1 --cmd", cursor_position=10)
    completions = list(subcommand_completer.get_completions(document, Mock()))
    assert len(completions) == 1
    assert completions[0].text == "--cmd1-opt"


def test_subcommand_arg_completion(subcommand_completer: ArgparseCompleter) -> None:
    """Test completion of subcommand arguments."""
    # Test completing subcommand arguments with choices
    document = Document(text="cmd2 ", cursor_position=5)
    completions = list(subcommand_completer.get_completions(document, Mock()))
    assert len(completions) == 3
    assert any(c.text in ["a", "b", "c"] for c in completions), completions

    # Test completing after subcommand option
    document = Document(text="cmd2 --cmd2-opt ", cursor_position=16)
    completions = list(subcommand_completer.get_completions(document, Mock()))
    assert len(completions) == 0


def test_handle_unclosed_quotes(subcommand_completer: ArgparseCompleter) -> None:
    """Test handling of unclosed quotes."""
    # Create a document with unclosed quotes
    document = Document(text='cmd1 "unclosed ', cursor_position=14)
    complete_event = Mock()

    # Get completions - should not raise an exception
    list(subcommand_completer.get_completions(document, complete_event))


def test_empty_input(completer: ArgparseCompleter) -> None:
    """Test completion with empty and partial input for positional arguments."""
    # Test empty input case
    empty_doc = Document(text="", cursor_position=0)
    complete_event = Mock()

    completions = list(completer.get_completions(empty_doc, complete_event))
    option_texts = [c.text for c in completions]
    assert len(completions) == 3  # file1, file2, file3
    assert set(option_texts) == {"file1", "file2", "file3"}

    # Test partial input case
    partial_doc = Document(text="f", cursor_position=1)
    completions = list(completer.get_completions(partial_doc, Mock()))
    assert len(completions) == 3
    assert all(c.text in ["file1", "file2", "file3"] for c in completions)


def test_choice_value_completion(completer: ArgparseCompleter) -> None:
    """Test completion of choice values."""
    # Test completing choice option values
    document = Document(text="--choice o", cursor_position=10)
    completions = list(completer.get_completions(document, Mock()))
    assert len(completions) == 3  # opt1, opt2 and opt3
    assert any(c.text == "opt1" for c in completions)
    assert any(c.text == "opt2" for c in completions)
    assert any(c.text == "opt3" for c in completions)


def test_flag_completion(completer: ArgparseCompleter) -> None:
    """Test completion of flag options."""
    # Test completing flag options
    document = Document(text="--fl", cursor_position=4)
    completions = list(completer.get_completions(document, Mock()))
    assert len(completions) == 1
    assert completions[0].text == "--flag"


def test_mixed_completion(completer: ArgparseCompleter) -> None:
    """Test completion with mixed positional and option arguments."""
    # Test completing after positional argument
    document = Document(text="file1 --c", cursor_position=9)
    completions = list(completer.get_completions(document, Mock()))
    assert len(completions) == 1
    assert completions[0].text == "--choice"


def test_help_text_in_completions(completer: ArgparseCompleter) -> None:
    """Test that help text appears in completions."""
    # Test option help text
    document = Document(text="-a", cursor_position=2)
    completions = list(completer.get_completions(document, Mock()))
    assert any("Alpha option" in c.display_meta_text for c in completions)

    # Test positional argument help text
    document = Document(text="f", cursor_position=1)
    completions = list(completer.get_completions(document, Mock()))
    assert any("A positional argument" in c.display_meta_text for c in completions), completions


def test_positional_ordering(completer: ArgparseCompleter) -> None:
    """Test that positional arguments are completed in correct order."""
    # First positional
    document = Document(text="f", cursor_position=1)
    completions = list(completer.get_completions(document, Mock()))
    assert all(c.text in ["file1", "file2", "file3"] for c in completions)

    # After first positional, should suggest options or next positional
    document = Document(text="file1 ", cursor_position=6)
    completions = list(completer.get_completions(document, Mock()))
    assert len(completions) == 0

def test_remainder_argument() -> None:
    """Test REMAINDER type argument handling."""
    parser = argparse.ArgumentParser()
    parser.add_argument("files", nargs=argparse.REMAINDER)
    completer = ArgparseCompleter(parser)

    # Test completing after REMAINDER argument
    document = Document(text="file1 file2 ", cursor_position=12)
    completions = list(completer.get_completions(document, Mock()))
    assert len(completions) == 0

def test_double_dash_handling() -> None:
    """Test -- separator handling."""
    parser = argparse.ArgumentParser()
    parser.add_argument("--option")
    parser.add_argument("files", nargs="*")
    completer = ArgparseCompleter(parser)

    # Test completing after --
    document = Document(text="--option val -- ", cursor_position=16)
    completions = list(completer.get_completions(document, Mock()))
    assert len(completions) == 0

def test_complex_argument_state() -> None:
    """Test complex argument state transitions."""
    parser = argparse.ArgumentParser()
    parser.add_argument("--multi", nargs=2)
    parser.add_argument("files", nargs="*")
    completer = ArgparseCompleter(parser)

    # Test partial multi-arg option
    document = Document(text="--multi first ", cursor_position=14)
    completions = list(completer.get_completions(document, Mock()))
    assert len(completions) == 0

def test_error_handling() -> None:
    """Test error handling paths."""
    parser = argparse.ArgumentParser()
    parser.add_argument("--option", nargs=1)
    completer = ArgparseCompleter(parser)

    # Test with invalid input that would cause shlex to fail
    document = Document(text="--option 'unclosed", cursor_position=18)
    completions = list(completer.get_completions(document, Mock()))
    assert len(completions) == 0

def test_negative_number_handling() -> None:
    """Test handling of negative numbers that look like flags."""
    parser = argparse.ArgumentParser()
    parser.add_argument("--number", type=int)
    parser.add_argument("files", nargs="*")
    completer = ArgparseCompleter(parser)

    # Test with negative number
    document = Document(text="-123 ", cursor_position=5)
    completions = list(completer.get_completions(document, Mock()))
    assert len(completions) == 0

def test_remainder_argument_consumption() -> None:
    """Test REMAINDER argument consumes all remaining input."""
    parser = argparse.ArgumentParser()
    parser.add_argument("--opt")
    parser.add_argument("files", nargs=argparse.REMAINDER)
    completer = ArgparseCompleter(parser)

    # Test with REMAINDER argument
    document = Document(text="--opt value file1 file2 ", cursor_position=23)
    completions = list(completer.get_completions(document, Mock()))
    assert len(completions) == 0

def test_abbreviated_options() -> None:
    """Test completion of abbreviated options."""
    parser = argparse.ArgumentParser(allow_abbrev=True)
    parser.add_argument("--verbose", action="store_true")
    parser.add_argument("--version", action="store_true")
    completer = ArgparseCompleter(parser)

    # Test abbreviated option
    document = Document(text="--ver", cursor_position=5)
    completions = list(completer.get_completions(document, Mock()))
    assert len(completions) == 2
    assert any(c.text == "--verbose" for c in completions)
    assert any(c.text == "--version" for c in completions)

def test_invalid_action_handling() -> None:
    """Test handling when action is None."""
    parser = argparse.ArgumentParser()
    completer = ArgparseCompleter(parser)

    # Test with invalid option that doesn't match any action
    document = Document(text="--invalid", cursor_position=9)
    completions = list(completer.get_completions(document, Mock()))
    assert len(completions) == 0

def test_required_argument_handling() -> None:
    """Test handling of required arguments."""
    parser = argparse.ArgumentParser(add_help=False)
    parser.add_argument("--required", required=True)
    completer = ArgparseCompleter(parser)

    # Test with missing required argument
    document = Document(text="", cursor_position=0)
    completions = list(completer.get_completions(document, Mock()))
    assert len(completions) == 1
    assert completions[0].text == "--required"

def test_quoted_argument_handling() -> None:
    """Test handling of quoted arguments."""
    parser = argparse.ArgumentParser()
    parser.add_argument("--path")
    completer = ArgparseCompleter(parser)

    # Test with quoted argument
    document = Document(text='--path "some path"', cursor_position=18)
    completions = list(completer.get_completions(document, Mock()))
    assert len(completions) == 0

def test_nargs_optional_handling() -> None:
    """Test handling of nargs=OPTIONAL arguments."""
    parser = argparse.ArgumentParser()
    parser.add_argument("--opt", nargs=argparse.OPTIONAL)
    completer = ArgparseCompleter(parser)

    # Test with optional argument
    document = Document(text="--opt ", cursor_position=6)
    completions = list(completer.get_completions(document, Mock()))
    assert len(completions) == 0
