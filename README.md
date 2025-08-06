# ctapipe-io-hess

A ctapipe io plugin for reading HESS DST data in ROOT format.

## Installation

You can install this package via `pip install ctapipe-io-hess`. That will also
install ctapipe if not already installed, and ctapipe tools with then
automatically use the plugin. Check that it is installed correctly by running:

``` sh
$ ctapipe-info --plugins

*** ctapipe_io plugins ***

     ctapipe_io_hess -- 0.1.dev4+ge42f6c8.d20250806
```

This may take a few seconds the first time you run it as ctapipe contains
modules that are compiled on-the-fly, but it should be faster after.


## Developer quick start:

To create a development environment with the things you need to test this package:

``` sh
$ git clone <URL>
$ conda env create -f environment.yml
$ conda activate ctapipe-io-hess
$ pre-commit install
$ pip install -e .[all]
$ pytest
```

When committing changes, be aware that the pre-commit checks are quite picky and
will reject your commit until you fix what it wants! Use `pre-commit run --all`
to show all errors, or just `pre-commit run` to see the errors associated with
your change.

## Project Structure / Packaging

This project uses `setuptools` for packaging and defines all necessary options
in the file `pyproject.toml`. `setup.py` and`setup.cfg` are not needed.

* `setuptools` documentation: https://setuptools.pypa.io/en/latest/userguide/index.html
* `Configuring setuptools with pyprojet.toml`: https://setuptools.pypa.io/en/latest/userguide/pyproject_config.html
* Relevant PEPs:
    * [PEP 517 – A build-system independent format for source trees](https://peps.python.org/pep-0517)
    * [PEP 518 – Specifying Minimum Build System Requirements for Python Projects](https://peps.python.org/pep-0518)
    * [PEP 621 – Storing project metadata in pyproject.toml](https://peps.python.org/pep-0621/)
    * [PEP 660 – Editable installs for pyproject.toml based builds (wheel based)](https://peps.python.org/pep-0660/)

We use the `src/` based layout, as this avoids several issues with editable installs and confusion with what
is imported (local directory or installed module).
See [setuptools/src-layout](https://setuptools.pypa.io/en/latest/userguide/package_discovery.html#src-layout).


### Editable installations

Editable installations in this setup  rely on PEP 660 (see above), support was introduced in `pip` 21.3 (released 2021-10)
and setuptools 64.0 (released 2022-08). The setuptools version is required in `pyproject.toml`.

To install in editable mode, use
```
$ pip install -e .
```

you can add extras, e.g. for developing and building the docs, use
```
$ pip install -e '.[dev,doc,test]'
```

or just
```
$ pip install -e '.[all]'
```


Keep in mind that editable installations have limitations as to what changes can take effect automatically
without rerunning `pip install -e .`. Python code changes to existing files take effect, but for example
adding new entry-points, changes to the source code of compiled extensions etc. will require rerunning the
installation.

See <https://setuptools.pypa.io/en/latest/userguide/development_mode.html#limitations>

## Versioning

This template uses `setuptools_scm` to automatically generate the version from the last git tag.
For local development, `setuptools_scm` will build a version development version. For releases,
version information is included in the sdist and wheel files and `setuptools_scm` is not used
when installing those. The setup is somewhat complex and was taken by astropy. It ensures that
the setuptools scm version is only used in development setups, not in the releases packages.

## Docs

Build the documentation in html format using:

```
$ make -C docs html
```

To view them, you can run:

```
$ python -m http.server -d docs/build/html
```

You can also install `sphinx-autobuild` and run

```
sphinx-autobuild docs docs/build/html
```
to get a continuously running and updating preview of the docs while you edit them.

Docs are automatically deployed on main and tags to gitlab pages.
