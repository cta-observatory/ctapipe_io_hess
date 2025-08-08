.. _installation:

Installation
============

User Installation
-----------------

As a user, install from pypi:

.. code-block:: shell

    $ pip install ctapipe-io-hess


Developer Setup
---------------

As a developer, clone the repository, create a virtual environment
and then install the package in development mode:

.. code-block:: shell

    git clone <URL>
    cd ctapipe-io-hess
    conda env create -f environment.yml
    conda activate ctapipe-io-hess
    pre-commit install
    pip install -e .[all]
    pytest

When committing changes, be aware that the pre-commit checks are quite picky and
will reject your commit until you fix what it wants! Use ``pre-commit run --all``
to show all errors, or just ``pre-commit run`` to see the errors associated with
your change.
