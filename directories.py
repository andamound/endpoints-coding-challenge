import sys
from typing import List


class ExplorerError(Exception):
    pass


class Explorer:

    def __init__(self):
        self.__directories = {}
        self.__commands = {
            'CREATE': self.create,
            'MOVE': self.move,
            'DELETE': self.delete,
            'LIST': self.list,
        }

    def get_directories(self):
        return self.__directories

    def _get_last_obj(self, nested_directories: List[str]) -> dict:
        """
        Loops through directory list and returns last dict-object.
        If directory does not exist, raises InvalidPathError

        :param nested_directories: List[str]
        :return: dict
        """
        obj = self.__directories

        for directory in nested_directories:
            obj = obj.get(directory)
            if obj is None:
                raise ExplorerError(f"{directory} does not exist")

        return obj

    def parse(self, command: str) -> None:
        """
        Parse string command

        Command examples:
            - CREATE fruits/apples
            - MOVE fruits/apples foods
            - DELETE fruits
            - LIST

        :param command: str
        :return:
        """
        command = command.strip()
        if not command:
            raise ExplorerError('Empty command')
        action, *args = command.split()
        method = self.__commands.get(action.upper())

        if method is None:
            raise ExplorerError(f'Unknown command {action}')

        try:
            method(*args)
        except TypeError:
            raise ExplorerError(f'Cannot {command} - argument error')

    def create(self, directory_path: str) -> None:
        """
        Create new directory

        :param directory_path: str
        :return:
        """
        error_prefix = f'Cannot create {directory_path}'
        directory_path = directory_path.rstrip('/')
        if not directory_path:
            raise ExplorerError(f'{error_prefix} - path is empty')

        nested_directories = directory_path.split('/')
        try:
            parent = self._get_last_obj(nested_directories[:-1])
        except ExplorerError as e:
            raise ExplorerError(f'{error_prefix} - {str(e)}')

        if nested_directories[-1] in parent:
            raise ExplorerError(f'{error_prefix} - {nested_directories[-1]} already exists')

        parent[nested_directories[-1]] = {}

    def move(self, from_directory_path: str, to_directory_path: str) -> None:
        """
        Move directory to another directory

        :param from_directory_path: str
        :param to_directory_path: str
        :return:
        """
        error_prefix = f'Cannot move from {from_directory_path} to {to_directory_path}'
        from_directory_path = from_directory_path.rstrip('/')
        to_directory_path = to_directory_path.rstrip('/')
        if not from_directory_path:
            raise ExplorerError(f'{error_prefix} - "From" directory is empty')

        if not to_directory_path:
            raise ExplorerError(f'{error_prefix} - "To" directory is empty')

        if to_directory_path.startswith(from_directory_path):
            raise ExplorerError(f'{error_prefix} - "From" directory exist in "To" directory')

        nested_from_directories = from_directory_path.split('/')
        nested_to_directories = to_directory_path.split('/')

        try:
            from_parent = self._get_last_obj(nested_from_directories[:-1])
            to_parent = self._get_last_obj(nested_to_directories)
        except ExplorerError as e:
            raise ExplorerError(f'{error_prefix} - {str(e)}')

        if nested_from_directories[-1] not in from_parent:
            raise ExplorerError(f'{error_prefix} - {nested_from_directories[-1]} does not exist')

        move_obj = from_parent[nested_from_directories[-1]]

        del from_parent[nested_from_directories[-1]]
        to_parent[nested_from_directories[-1]] = move_obj

    def delete(self, directory_path: str) -> None:
        """
        Delete directory

        :param directory_path: str
        :return:
        """
        error_prefix = f'Cannot delete {directory_path}'
        directory_path = directory_path.rstrip('/')
        if not directory_path:
            raise ExplorerError(f'{error_prefix} - path is empty')

        nested_directories = directory_path.split('/')
        try:
            parent = self._get_last_obj(nested_directories[:-1])
        except ExplorerError as e:
            raise ExplorerError(f'{error_prefix} - {str(e)}')

        if nested_directories[-1] not in parent:
            raise ExplorerError(f'{error_prefix} - {directory_path} does not exist')

        del parent[nested_directories[-1]]

    def __get_pretty_list(self, directories_list: dict) -> List[str]:
        """
        Create pretty directories list

        :param directories_list: dict
        :return: List[str]
        """
        pretty_list = []
        for key in sorted(directories_list):
            pretty_list.append(key)
            pretty_list += [f'  {directory}' for directory in self.__get_pretty_list(directories_list[key])]

        return pretty_list

    def list(self) -> None:
        """
        Print directory list
        :return:
        """
        pretty_list = self.__get_pretty_list(self.__directories)
        for directory in pretty_list:
            print(directory)


def read_from_input():
    explorer = Explorer()
    while True:
        command = input()
        if command.upper() == 'EXIT':
            break
        print(command.strip())
        try:
            explorer.parse(command)
        except ExplorerError as e:
            print(str(e))


def read_from_file(file_path: str):
    explorer = Explorer()
    with open(file_path) as file:
        for command in file:
            print(command.strip())
            try:
                explorer.parse(command)
            except ExplorerError as e:
                print(str(e))


def main():
    if len(sys.argv) > 1:
        read_from_file(sys.argv[1])
    else:
        read_from_input()


if __name__ == "__main__":  # pragma: no cover
    main()
