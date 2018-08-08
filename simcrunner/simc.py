#!/usr/bin/env python
"""
simc
A simc runner to run simulationcraft with given arguments in python.
Created by Romain Mondon-Cancel on 2018-08-02 11:08:59
"""

import platform
import subprocess
import os

from typing import List, Union, Optional


class SimcArg:
    """
    Abstract class representing simc arguments for dynamic constructions.
    """

    def __init__(self):
        pass

    def append_to(self, args: List[str]=[]) -> List[str]:
        pass


class SingleArg(SimcArg):
    """
    Represents a single literal argument.
    """

    simc_arg: str

    def __init__(self, simc_arg: str):
        self.simc_arg = simc_arg

    def append_to(self, args: List[str]=[]) -> List[str]:
        return args + [self.simc_arg]


class KeyValueArg(SingleArg):
    """
    Represents a key-value pair argument.
    """

    key: str
    value: str

    def __init__(self, key: str, value: str):
        self.key = key
        self.value = value

    @property
    def simc_arg(self) -> str:
        return f'{self.key}={self.value}'


class Profile(SingleArg):
    """
    Represents a profile file.
    """

    file_path: str
    add_suffix: bool
    SUFFIX: str = '.simc'

    def __init__(self, file_path: str, add_suffix: bool=False):
        self.file_path = file_path
        self.add_suffix = add_suffix

    @property
    def simc_arg(self) -> str:
        file_ = self.file_path
        if self.add_suffix:
            file_ += self.SUFFIX
        return file_


class FileExport(KeyValueArg):
    """
    Arguments to export simc result to a given file.
    """

    EXTENSION: str
    file_path: str
    add_suffix: bool

    def __init__(self, file_path, add_suffix: bool=False):
        os.makedirs(os.path.dirname(file_path), exist_ok=True)
        self.file_path = file_path
        self.add_suffix = add_suffix

    @property
    def value(self):
        value = self.file_path
        if not value.endswith(self.EXTENSION):
            value += self.EXTENSION
        return value


class JsonExport(FileExport):
    """
    Arguments to export simc result to a given json file.
    """

    EXTENSION: str = '.json'
    key: str = 'json2'


class HtmlExport(FileExport):
    """
    Arguments to export simc result to a given html file.
    """

    EXTENSION: str = '.html'
    key: str = 'html'


class Arguments(SimcArg):
    """
    Generate arguments for simc from key-value pairs.
    """

    args: List[SingleArg] = []

    def __init__(self, *args: Union[str, SingleArg], **kwargs: str):
        for arg in args:
            self.add_arg(arg)
        for key, arg in kwargs.items():
            self.add_arg(KeyValueArg(key, arg))

    def add_arg(self, arg: Union[str, SingleArg]):
        if isinstance(arg, SingleArg):
            self.args.append(arg)
        else:
            self.args.append(SingleArg(arg))

    def append_to(self, args: List[str]=[]) -> List[str]:
        new_args = args.copy()
        for arg in self.args:
            new_args = arg.append_to(new_args)
        return new_args


class Simc:
    """
    simc runner.
    """

    simc_path: str
    args: List[SimcArg]

    def __init__(self, *args: Union[str, SimcArg],
                 simc_path: Optional[str]=None):
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
        self.set_args(*args)

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
            res = arg.append_to(res)
        return res

    def set_args(self, *args: Union[str, SimcArg]):
        """
        Set args in a functional form.
        """
        self.args = []
        return self.add_args(*args)

    def add_args(self, *args):
        """
        Append args in a functional form.
        """
        for arg in args:
            self.add_arg(arg)
        return self
    
    def add_arg(self, arg):
        if type(arg) is str:
            self.args.append(SingleArg(arg))
        else:
            self.args.append(arg)
        return self

    def run(self):
        """
        Run simc with the given arguments.
        """
        simc_process = subprocess.Popen([self.executable] + self.run_args)
        simc_process.wait()
