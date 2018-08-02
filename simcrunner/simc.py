#!/usr/bin/env python
"""
simc
A simc runner to run simulationcraft with given arguments in python.
Created by Romain Mondon-Cancel on 2018-08-02 11:08:59
"""

import platform
import subprocess
import os
import logging

from typing import List, Dict, Union, Optional


class SimcArgs:
    """
    Abstract class representing simc arguments for dynamic constructions.
    """

    def __init__(self):
        pass

    def args(self) -> List[str]:
        pass


class Simc:
    """
    simc runner.
    """

    simc_path: str
    args: List[Union[str, List[str], SimcArgs]]

    def __init__(self, *args, simc_path: Optional[str]=None):
        if not simc_path:
            try:
                simc_path = os.environ['SIMC_PATH']
            except KeyError:
                raise AttributeError(
                    'The Simc class requires that either the parameter '
                    '"simc_path" is provided or the environment variable '
                    '"SIMC_PATH" is defined.'
                )
        self.simc_path = simc_path
        self.args = list(args)

    @property
    def executable(self) -> str:
        """
        Return the name of the simc executable, depending on the platform.
        """
        ext = '.exe' if platform.system() == 'Windows' else ''
        return os.path.join(self.simc_path, f'simc{ext}')

    @property
    def run_args(self) -> List[str]:
        res = []
        for arg in self.args:
            if type(arg) is str:
                res += [arg]
                continue
            if type(arg) is list:
                res += arg
                continue
            if isinstance(arg, SimcArgs):
                res += arg.args()
                continue
            logging.warning(f'Argument {arg} has invalid type {type(arg)};'
                            'ignored.')
        return res

    def set_args(self, *args):
        """
        Set args in a functional form.
        """
        self.args = list(args)
        return self

    def add_args(self, *args):
        """
        Append args in a functional form.
        """
        self.args += list(args)
        return self

    def get_arg(self, arg):
        return arg if type(arg) is str else arg.args()

    def run(self):
        """
        Run simc with the given arguments.
        """
        simc_process = subprocess.Popen([self.executable] + self.run_args)
        simc_process.wait()


class FileExport(SimcArgs):
    """
    Arguments to export simc result to a given file.
    """

    path: str
    file_name: str
    extension: str
    arg_name: str

    def __init__(self, file_name: str, extension: str,
                 arg_name: str, path: str=''):
        self.file_name = file_name
        self.extension = extension
        self.arg_name = arg_name
        self.path = path

    @property
    def full_file_name(self):
        if self.file_name[-len(self.extension):] == self.extension:
            ext = ''
        else:
            ext = self.extension
        return self.file_name + ext

    def args(self) -> List[str]:
        if not os.path.exists(self.path):
            os.makedirs(self.path)
        full_path = os.path.join(self.path, self.full_file_name)
        return [f'{self.arg_name}={full_path}']


class JsonExport(FileExport):
    """
    Arguments to export simc result to a given json file.
    """

    def __init__(self, file_name: str, json_path: str=''):
        super().__init__(file_name, '.json', 'json2', json_path)


class HtmlExport(SimcArgs):
    """
    Arguments to export simc result to a given html file.
    """

    def __init__(self, file_name: str, html_path: str=''):
        super().__init__(file_name, '.html', 'html', html_path)


class Profiles(SimcArgs):
    """
    Arguments for profile files arguments for simc.
    """

    base_path: str
    files: List[str]
    append_suffix: bool

    def __init__(self, files: Union[str, List[str]], base_path: str='',
                 append_suffix: bool=False):
        self.base_path = base_path
        self.files = [files] if type(files) is str else files
        self.append_suffix = append_suffix

    def format_file_name(self, file_name):
        full_file_name = file_name
        if self.append_suffix:
            full_file_name += '.simc'
        return full_file_name

    def args(self) -> List[str]:
        return [os.path.join(self.base_path, self.format_file_name(file_name))
                for file_name in self.files]


class KeyValueArgs(SimcArgs):
    """
    Generate arguments for simc from key-value pairs.
    """

    kwargs: Dict[str, str]

    def __init__(self, **kwargs):
        self.kwargs = kwargs

    def to_arg(self, key, value):
        return f'{key}={value}'

    def args(self) -> List[str]:
        return [self.to_arg(key, value) for key, value in self.kwargs.items()]
