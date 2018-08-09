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

from typing import List, Union, Optional, TypeVar


Arg = TypeVar('Arg', str, int, float)


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
    arg: Arg

    def __init__(self, key: str, arg: Arg):
        self.key = key
        self.arg = arg

    @property
    def simc_arg(self) -> str:
        return f'{self.key}={self.arg}'


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
    def arg(self) -> Arg:
        arg = self.file_path
        if not arg.endswith(self.EXTENSION):
            arg += self.EXTENSION
        return arg


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

    args: List[SingleArg]

    def __init__(self, *args: Union[str, SingleArg], **kwargs: Arg):
        self.args = []
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


class HasArguments:
    """
    List of simc arguments.
    """

    args: List[SimcArg]

    def __init__(self, *args: Union[str, SimcArg], **kwargs: Arg):
        self.set_args(*args, **kwargs)

    def set_args(self, *args: Union[str, SimcArg], **kwargs: Arg):
        """
        Set args in a functional form.
        """
        self.args = []
        return self.add_args(*args, **kwargs)

    def add_args(self, *args: Union[str, SimcArg], **kwargs: Arg):
        """
        Append args in a functional form.
        """
        for arg in args:
            self.add_arg(arg)
        self.add_arg(Arguments(**kwargs))
        return self

    def add_arg(self, arg: Union[str, SimcArg]):
        if type(arg) is str:
            self.args.append(SingleArg(arg))
        else:
            self.args.append(arg)
        return self

    @property
    def args_list(self) -> List[str]:
        res = []
        for arg in self.args:
            res = arg.append_to(res)
        return res


class ProfileSet(HasArguments, SingleArg):
    """
    Represents a single profileset.
    """

    name: str

    def __init__(self, name: str, *args: Union[str, SimcArg], **kwargs: Arg):
        self.name = name
        super().__init__(*args, **kwargs)
    
    @property
    def simc_arg(self) -> str:
        return f'profileset."{self.name}"={"/".join(self.args_list)}'


class Simc(HasArguments):
    """
    simc runner.
    """

    verbose: bool
    simc_path: str

    def __init__(self, simc_path: Optional[str]=None,
                 *args: Union[str, SimcArg], verbose: bool=False,
                 **kwargs: Arg):
        print(args, kwargs)
        if not simc_path:
            try:
                simc_path = os.environ['SIMC_PATH']
            except KeyError:
                raise AttributeError(
                    'The Simc class requires that either the parameter '
                    '"simc_path" is provided or the environment variable '
                    '"SIMC_PATH" is defined.'
                )
        self.verbose = verbose
        self.simc_path = simc_path
        super().__init__(*args, **kwargs)

    @property
    def executable(self) -> str:
        """
        Return the name of the simc executable, depending on the platform.
        """
        ext = '.exe' if platform.system() == 'Windows' else ''
        return os.path.join(self.simc_path, f'simc{ext}')

    def run(self):
        """
        Run simc with the given arguments.
        """
        run_list = [self.executable] + self.args_list
        if self.verbose:
            logging.info(f'Executing: {" ".join(run_list)}')
        simc_process = subprocess.Popen(run_list)
        simc_process.wait()
