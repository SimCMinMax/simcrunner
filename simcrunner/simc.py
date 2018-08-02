#!/usr/bin/env python
"""
simc
A simc runner to run simulationcraft with given arguments in python.
Created by Romain Mondon-Cancel on 2018-08-02 11:08:59
"""

import platform
import subprocess
import os

from typing import List, Dict


class Simc:
    """
    simc runner.
    """

    simc_folder: str
    args: List[str]

    def __init__(self, simc_folder: str, *args):
        self.simc_folder = simc_folder
        self.args = args
    
    @property
    def simc_executable(self):
        """
        Return the name of the simc executable, depending on the platform.
        """
        ext = '.exe' if platform.system() == 'Windows' else ''
        return f'simc{ext}'
    
    def run(self):
        """
        Run simc with the given arguments.
        """
        simc_process = subprocess.Popen([self.simc_executable] + self.args)


class SimcArgs:
    """
    Abstract class representing simc arguments for dynamic constructions.
    """

    def __init__(self):
        pass

    def args(self, *args, **kwargs) -> List[str]:
        pass


class FileExport(SimcArgs):
    """
    Arguments to export simc result to a given file.
    """

    folder: str
    extension: str
    arg_name: str

    def __init__(self, folder: str='.', extension: str, arg_name: str):
        self.folder = folder

    def add_extension(file_name):
        if file_name[-len(self.extension):] == self.extension:
            ext = ''
        else:
            ext = self.extension
        return file_name + ext

    def args(self, file_name: str) -> List[str]:
        file_name = self.add_extension(file_name)
        path = os.path.join(self.folder, file_name)
        return [f'{self.arg_name}={path}']


class JsonExport(FileExport):
    """
    Arguments to export simc result to a given json file.
    """

    def __init__(self, json_folder: str='.'):
        super().__init__(json_folder, '.json', 'json2')


class HtmlExport(SimcArgs):
    """
    Arguments to export simc result to a given html file.
    """

    def __init__(self, json_folder: str='.'):
        super().__init__(json_folder, '.html', 'html')


class KeyValueArgs(SimcArgs):
    """
    Generate arguments for simc from key-value pairs.
    """

    kwargs: Dict[str]

    def __init__(self, **kwargs):
        self.kwargs = kwargs
    
    def to_arg(self, key, value):
        return f'{key}={value}'

    def args(self, **kwargs) -> List[str]:
        full_kwargs = {}
        full_kwargs.update(self.kwargs)
        full_kwargs.update(kwargs)
        return [self.to_arg(key, value) for key, value in full_kwargs.items()]
