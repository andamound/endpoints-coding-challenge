from typing import List
from unittest.mock import patch

import pytest
from directories import Explorer, ExplorerError


@pytest.mark.parametrize('create_directories, expected_result', [
    (['fruits'], {'fruits': {}}),
    (['fruits/'], {'fruits': {}}),
    (['fruits', 'foods'], {'fruits': {}, 'foods': {}}),
    (['fruits', 'fruits/apples'], {'fruits': {'apples': {}}}),
])
def test_create(create_directories: List[str], expected_result: dict):
    explorer = Explorer()
    for directory in create_directories:
        explorer.create(directory)

    assert expected_result == explorer.get_directories()


@pytest.mark.parametrize('create_directories, expected_error_text', [
    ([''], 'path is empty'),
    (['/'], 'path is empty'),
    (['fruits', 'fruits/apples/red'], 'apples does not exist'),
    (['fruits', 'fruits/apples', 'fruits/apples'], 'apples already exist'),
])
def test_create_errors(create_directories: List[str], expected_error_text: str):
    explorer = Explorer()
    with pytest.raises(ExplorerError) as excinfo:
        for directory in create_directories:
            explorer.create(directory)

    assert expected_error_text in str(excinfo)


@pytest.mark.parametrize('create_directories, delete_directory, expected_result', [
    (['fruits'], 'fruits', {}),
    (['fruits'], 'fruits/', {}),
    (['fruits', 'fruits/apples'], 'fruits/apples', {'fruits': {}}),
    (['fruits', 'fruits/apples'], 'fruits', {}),
])
def test_delete(create_directories: List[str], delete_directory: str, expected_result: dict):
    explorer = Explorer()
    for directory in create_directories:
        explorer.create(directory)
    explorer.delete(delete_directory)

    assert expected_result == explorer.get_directories()


@pytest.mark.parametrize('create_directories, delete_directories, expected_error_text', [
    (['fruits'], [''], 'path is empty'),
    (['fruits'], ['/'], 'path is empty'),
    (['fruits'], ['apples'], 'apples does not exist'),
    (['fruits', 'fruits/apples'], ['apples'], 'apples does not exist'),
    (['fruits'], ['fruits/apples'], 'fruits/apples does not exist'),
    (['fruits', 'fruits/apples', 'fruits/apples/red'], ['fruits/apples', 'fruits/apples/red'], 'apples does not exist'),
])
def test_delete_error(create_directories: List[str], delete_directories: List[str], expected_error_text: str):
    explorer = Explorer()
    for directory in create_directories:
        explorer.create(directory)

    with pytest.raises(ExplorerError) as excinfo:
        for directory in delete_directories:
            explorer.delete(directory)

    assert expected_error_text in str(excinfo)


@pytest.mark.parametrize('create_directories, from_dir, to_dir, expected_result', [
    (['fruits', 'apples'], 'apples', 'fruits', {'fruits': {'apples': {}}}),
    (['fruits', 'apples'], 'apples/', 'fruits/', {'fruits': {'apples': {}}}),
    (['fruits', 'fruits/apples', 'foods'], 'fruits', 'foods', {'foods': {'fruits': {'apples': {}}}}),
    (['fruits', 'fruits/apples', 'foods'], 'fruits/apples', 'foods', {'foods': {'apples': {}}, 'fruits': {}}),
])
def test_move(create_directories: List[str], from_dir: str, to_dir: str, expected_result: dict):
    explorer = Explorer()
    for directory in create_directories:
        explorer.create(directory)

    explorer.move(from_dir, to_dir)

    assert expected_result == explorer.get_directories()


@pytest.mark.parametrize('create_directories, from_dir, to_dir, expected_error_text', [
    (['fruits'], '', 'fruits', '"From" directory is empty'),
    (['fruits'], '/', 'fruits', '"From" directory is empty'),
    (['fruits'], 'fruits', '', '"To" directory is empty'),
    (['fruits'], 'fruits', '/', '"To" directory is empty'),
    (
            ['fruits', 'fruits/apples', 'fruits/apples/red'],
            'fruits/apples', 'fruits/apples/red',
            '"From" directory exist in "To" directory'
    ),
    (['fruits', 'foods', 'fruits/apples'], 'fruits', 'foods/grains', 'grains does not exist'),
    (['fruits', 'foods', 'fruits/apples'], 'fruits/grains/squash', 'foods', 'grains does not exist'),
    (['fruits', 'foods', 'fruits/apples'], 'foods/grains', 'fruits', 'grains does not exist'),
])
def test_move_errors(create_directories: List[str], from_dir: str, to_dir: str, expected_error_text: str):
    explorer = Explorer()
    for directory in create_directories:
        explorer.create(directory)
    with pytest.raises(ExplorerError) as excinfo:
        explorer.move(from_dir, to_dir)

    assert expected_error_text in str(excinfo)


@pytest.mark.parametrize('create_directories, nested_directories, expected_result', [
    ([], [], {}),
    (['fruits'], ['fruits'], {}),
    (['fruits'], [], {'fruits': {}}),
    (['fruits', 'fruits/apples'], ['fruits'], {'apples': {}}),
    (['fruits', 'fruits/apples', 'fruits/apples/red'], ['fruits', 'apples'], {'red': {}}),
])
def test_get_last_obj(create_directories: List[str], nested_directories: List[str], expected_result: dict):
    explorer = Explorer()
    for directory in create_directories:
        explorer.create(directory)

    assert expected_result == explorer._get_last_obj(nested_directories)


@pytest.mark.parametrize('create_directories, nested_directories, expected_error_text', [
    ([], ['fruits'], 'fruits does not exist'),
    (['fruits'], ['fruits', 'apples'], 'apples does not exist'),
    (['fruits'], ['fruits', 'apples', 'red'], 'apples does not exist'),
])
def test_get_last_errors(create_directories: List[str], nested_directories: List[str], expected_error_text: str):
    explorer = Explorer()
    for directory in create_directories:
        explorer.create(directory)

    with pytest.raises(ExplorerError) as excinfo:
        explorer._get_last_obj(nested_directories)

    assert expected_error_text in str(excinfo)


@pytest.mark.parametrize('create_directories, expected_result', [
    ([], []),
    (['fruits'], ['fruits']),
    (['fruits', 'fruits/apples'], ['fruits', '  apples']),
    (
            ['fruits', 'fruits/apples', 'foods', 'foods/grains', 'foods/grains/squash'],
            ['foods', '  grains', '    squash', 'fruits', '  apples']
    ),
])
def test_list(capsys, create_directories: List[str], expected_result: List[str]):
    explorer = Explorer()
    for directory in create_directories:
        explorer.create(directory)
    explorer.list()
    expected_string = '\n'.join(expected_result)
    if expected_string:
        expected_string += '\n'
    assert capsys.readouterr().out == expected_string


@patch('directories.Explorer.create')
@patch('directories.Explorer.delete')
@patch('directories.Explorer.move')
@patch('directories.Explorer.list')
@pytest.mark.parametrize('command', [
    'CREATE fruits',
    'DELETE fruits',
    'MOVE fruits apples',
    'LIST',
    'list',
])
def test_parse(list_function, move_function, delete_function, create_function, command: str):
    explorer = Explorer()
    explorer.parse(command)
    methods = {
        'CREATE': create_function,
        'DELETE': delete_function,
        'MOVE': move_function,
        'LIST': list_function
    }

    function, *args = command.split()

    assert methods[function.upper()].call_count == 1
    assert list(methods[function.upper()].call_args.args) == args


@pytest.mark.parametrize('command, expected_error_text', [
    ('', 'Empty command'),
    ('RANDOM_STRING', 'Unknown command'),
    ('CREATE', 'argument error'),
    ('CREATE apples fruits', 'argument error'),
    ('DELETE', 'argument error'),
    ('DELETE apples fruits', 'argument error'),
    ('MOVE', 'argument error'),
    ('MOVE apples', 'argument error'),
    ('MOVE apples fruits red', 'argument error'),
    ('LIST apples', 'argument error'),
])
def test_parse_errors(command: str, expected_error_text: str):
    explorer = Explorer()
    with pytest.raises(ExplorerError) as excinfo:
        explorer.parse(command)

    assert expected_error_text in str(excinfo)
