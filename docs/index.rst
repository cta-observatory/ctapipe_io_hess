ctapipe-io-hess
===============

A ctapipe plugin to read HESS DST data in ROOT format.

* **Version**: |version|
* **Date**: |today|

To use it, just install the plugin into the same environment as ctapipe (see
:ref:`installation`), and then tools like ``ctapipe-process`` will automatically
use it if you give a compatible file as input, for example:

.. code-block:: sh
   :caption: shell

    # Setup your analysis configuration

    ctapipe-quickstart --workdir my_analysis
    cd my_analysis

    # process a DST to a file with DL1 parameters and DL2 geometry

    ctapipe-process --config base_config.yaml --config ml_preprocessing_config.yaml\
        --input $HESSDST/run_12345_DST.root \
        --output run_12345.dl2.h5 \
        --log-level INFO \
        --progress



.. toctree::
    :maxdepth: 1
    :caption: Contents:
    :hidden:

    installation
    reference
    changelog
    tutorials/developer_help.ipynb



Indices and tables
------------------

* :ref:`genindex`
* :ref:`modindex`
* :ref:`search`
