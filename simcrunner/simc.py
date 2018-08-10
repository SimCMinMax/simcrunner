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

from datetime import datetime
from typing import List, Dict, Union, Optional, TypeVar


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


class File:
    """
    Represents a file.
    """

    file_path: str
    check_extension: bool
    EXTENSION: str

    def __init__(self, file_path: str, check_extension: bool=False):
        self.file_path = file_path
        self.check_extension = check_extension

    @property
    def file_name(self) -> str:
        file_ = self.file_path
        if self.check_extension and not file_.endswith(self.EXTENSION):
            file_ += self.EXTENSION
        return os.path.abspath(file_)


class Profile(File, SingleArg):
    """
    Represents a profile file.
    """

    EXTENSION: str = '.simc'

    @property
    def simc_arg(self) -> str:
        return self.file_name


class FileExport(File, KeyValueArg):
    """
    Arguments to export simc result to a given file.
    """

    def __init__(self, file_path, check_extension: bool=False):
        os.makedirs(os.path.dirname(file_path) or '.', exist_ok=True)
        super().__init__(file_path, check_extension)

    @property
    def arg(self) -> Arg:
        return self.file_name


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


class ProfileSet(HasArguments, SimcArg):
    """
    Represents a single profileset.
    """

    name: str

    def __init__(self, name: str, *args: Union[str, SimcArg], **kwargs: Arg):
        self.name = name
        super().__init__(*args, **kwargs)

    @property
    def profile_name(self) -> str:
        return f'"{self.name}"' if ' ' in self.name else self.name

    def append_to(self, args: List[str]=[]) -> List[str]:
        new_args = args.copy()
        operator = '='
        for arg in self.args_list:
            new_args.append(f'profileset.{self.profile_name}{operator}{arg}')
            operator = '+='
        return new_args


class Simc(HasArguments):
    """
    simc runner.
    """

    simc_path: str
    export_path: str
    history: List[Dict[str, str]]

    def __init__(self,
                 *args: Union[str, SimcArg],
                 simc_path: Optional[str]=None,
                 export_path: Optional[str]=None,
                 **kwargs: Arg):
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
        self.export_path = export_path or 'simcrunner_export.simc'
        self.history = []
        super().__init__(*args, **kwargs)

    @property
    def executable(self) -> str:
        """
        Return the name of the simc executable, depending on the platform.
        """
        ext = '.exe' if platform.system() == 'Windows' else ''
        return os.path.join(self.simc_path, f'simc{ext}')
    
    def export(self, file_path: Optional[str]=None):
        """
        Exports the query arguments to a simc file.
        """
        file_path = file_path or self.export_path
        print(file_path)
        os.makedirs(os.path.dirname(file_path) or '.', exist_ok=True)
        with open(file_path, 'w+') as f:
            f.write('# Simc file generated by simcrunner\n')
            f.write(f'# Created: {datetime.now()}\n')
            f.write('# Website: https://github.com/simcminmax/simcrunner\n')
            for arg in self.args_list:
                f.write(f'{arg}\n')
    
    @property
    def last_query(self):
        return self.history[-1]
    
    @property
    def last_output(self):
        return self.history[-1].get('output', None)

    @property
    def last_error(self):
        return self.history[-1].get('error', None)

    def run(self):
        """
        Run simc with the given arguments.
        """
        run_list = [self.executable] + self.args_list
        query = {
            'query': ' '.join(run_list)
        }
        try:
            logging.info(f'Executing: {" ".join(run_list)}')
            simc_process = subprocess.Popen(run_list,
                                            stdout=subprocess.PIPE,
                                            stderr=subprocess.PIPE)
            out, err = simc_process.communicate()
            query['returncode'] = simc_process.returncode
            if out:
                output = out.decode('utf-8')
                query['output'] = output
                logging.info(f'Return code: {simc_process.returncode}')
                logging.info(f'Full output: \n{output}')
            if err:
                error = err.decode('utf-8')
                query['error'] = error
                logging.warning(f'Return code: {simc_process.returncode}')
                logging.warning(f'Full error: \n{error}')
        except OSError as e:
            logging.error(f'Simc process failed with error {e.errno}')
            logging.error(e.strerror)
            logging.error(e.filename)
            logging.error(f'Exporting query to {self.export_path}.')
            self.export()
        self.history.append(query)
