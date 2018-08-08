# simcrunner

A python package to run simulationcraft.

## Introduction

As I frequently work on python, and want to run simc as a process from python
to run simulations with different sets of parameters, I wrote this package as
a wrapper to more easily run successive simc simulations with different
arguments.

## Development

This package is still in alpha development, and will most likely contain bugs.
Its scope is currently only to run simc from python easily and flexibly; I
might add in the future a module to more easily parse `json` exports, though
Python probably already does that easily enough.

## Installation

To install this package, simply use

```sh
pip install git+https://github.com/simcminmax/simcrunner.git
```

## Usage

The package `simcrunner` exposes a couple classes: the main class `Simc`, which
handles the processus runner to run `simc`, and a couple classes to handle more
flexibly the most common arguments, such as file exports (`JsonExport` and
`HtmlExport`), key-value arguments (`KeyValueArgs`) and profiles
(`Profiles`).

A typical example would be:

```py
import os
from simcrunner import Simc, JsonExport, Arguments, Profile
simc_path = os.path.join('~', 'simc')
runner = Simc(simc_path=simc_path)
json_export = JsonExport(os.path.join('results', 'simc_export.json'))
profile = Profile(os.path.join(simc_path, 'profiles', 'Tier21',
                               'T21_Rogue_Assassination.simc'))
main_args = Arguments(profile, iterations=1000)
(runner
    .add_args(main_args)
    .add_args('target_error=0.05', 'threads=6')
    .add_args(json_export)
    .run())
```