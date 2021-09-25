import os
import sys
from typing import List
from unittest.mock import patch

import pytest

from directories import read_from_input, ExplorerError, read_from_file, main


@patch('builtins.input')
@patch('directories.Explorer.parse')
@pytest.mark.timeout(5)
@pytest.mark.parametrize('commands', [
    ['CREATE apples', 'LIST', 'EXIT'],
    ['create apples', 'list', 'exit'],
    ['EXIT']
])
def test_read_from_input(parse_method, input_method, capsys, commands: List[str]):
    side_effect_generator = (command for command in commands)
    input_method.side_effect = side_effect_generator
    read_from_input()
    assert parse_method.call_count == len(commands) - 1
    parse_args = [parse_method.call_args_list[idx][0][0] for idx in range(len(commands) - 1)]
    assert parse_args == commands[:-1]

    expected_string = ''.join(f'{command}\n' for command in commands[:-1])
    assert capsys.readouterr().out == expected_string


@patch('builtins.input')
@patch('directories.Explorer.parse')
def test_read_from_input_errors(parse_method, input_method, capsys):
    exception_text = 'TestExplorerError'
    commands = ['CREATE apples', 'LIST', 'EXIT']
    side_effect_generator = (command for command in commands)
    input_method.side_effect = side_effect_generator

    parse_method.side_effect = ExplorerError(exception_text)
    read_from_input()
    expected_string = [f'{command}\n{exception_text}\n' for command in commands[:-1]]
    assert capsys.readouterr().out == ''.join(expected_string)
    assert parse_method.call_count == len(commands) - 1


@pytest.fixture()
def create_commands_file(commands):
    file_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'statics', 'commands.txt')
    with open(file_path, 'w') as file:
        file.writelines([f'{command}\n' for command in commands])
    yield file_path
    os.remove(file_path)


@patch('directories.Explorer.parse')
@pytest.mark.parametrize('commands', [
    ['CREATE apples', 'LIST'],
    ['create apples', 'list'],
    []
])
def test_read_from_file(parse_method, capsys, create_commands_file, commands):
    read_from_file(create_commands_file)
    assert parse_method.call_count == len(commands)

    parse_args = [parse_method.call_args_list[idx][0][0] for idx in range(len(commands))]
    assert parse_args == [f'{command}\n' for command in commands]

    expected_string = ''.join([f'{command}\n' for command in commands])
    assert capsys.readouterr().out == expected_string


@patch('directories.Explorer.parse')
@pytest.mark.parametrize('commands', [
    ['CREATE apples', 'LIST'],
])
def test_read_from_file_errors(parse_method, capsys, create_commands_file, commands):
    exception_text = 'TestExplorerError'
    parse_method.side_effect = ExplorerError(exception_text)

    read_from_file(create_commands_file)

    assert parse_method.call_count == len(commands)
    expected_string = ''.join(f'{command}\n{exception_text}\n' for command in commands)
    assert capsys.readouterr().out == expected_string


@patch('directories.read_from_input')
def test_run_directories_input(read_from_input):
    with patch.object(sys, 'argv', ['directories.py']):
        main()

    assert read_from_input.call_count


@patch('directories.read_from_file')
def test_run_directories_file(read_from_file):
    file_path = 'test.txt'
    with patch.object(sys, 'argv', ['directories.py', file_path]):
        main()

    assert read_from_file.call_count
    assert read_from_file.call_args[0][0] == file_path
