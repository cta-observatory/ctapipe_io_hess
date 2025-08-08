"""
Configuration file for the Sphinx documentation builder.

This file only contains a selection of the most common options. For a full
list see the documentation:
https://www.sphinx-doc.org/en/master/usage/configuration.html
"""

# -- Project information -----------------------------------------------------
# import your own package here
import ctapipe_io_hess

project = "ctapipe_io_hess"
copyright = "CTAO"
author = "CTAO Computing Department"
version = ctapipe_io_hess.__version__
# The full version, including alpha/beta/rc tags.
release = version.split("+")[0]


# -- General configuration ---------------------------------------------------

# Add any Sphinx extension module names here, as strings. They can be
# extensions coming with Sphinx (named 'sphinx.ext.*') or your custom
# ones.
extensions = [
    "sphinx.ext.githubpages",
    "sphinx.ext.intersphinx",
    "sphinx.ext.autodoc",
    "sphinx.ext.autosummary",
    "numpydoc",
    "sphinx_changelog",
    "nbsphinx",
]

# Add any paths that contain templates here, relative to this directory.
templates_path = []

# List of patterns, relative to source directory, that match files and
# directories to ignore when looking for source files.
# This pattern also affects html_static_path and html_extra_path.
exclude_patterns = ["changes", ".virtual_documents", ".ipynb_checkpoints"]

# have all links automatically associated with the right domain.
default_role = "py:obj"


# intersphinx allows referencing other packages sphinx docs
intersphinx_mapping = {
    "python": ("https://docs.python.org/3/", None),
    "ctapipe": ("https://ctapipe.readthedocs.io/en/latest", None),
    "astropy": ("https://docs.astropy.org/en/stable", None),
    "matplotlib": ("https://matplotlib.org/stable", None),
    "numpy": ("https://numpy.org/doc/stable", None),
    "scipy": ("https://docs.scipy.org/doc/scipy", None),
    "traitlets": ("https://traitlets.readthedocs.io/en/stable/", None),
}

# -- Options for HTML output -------------------------------------------------

html_theme = "pydata_sphinx_theme"
html_theme_options = dict(
    navigation_with_keys=False,
    # setup for displaying multiple versions, also see setup in .gitlab-ci.yml
    # switcher=dict(
    #     json_url="http://cta-computing.gitlab-pages.cta-observatory.org/documentation/python-project-template/versions.json",  # noqa: E501
    #     version_match="latest" if ".dev" in version else f"v{version}",
    # ),
    # navbar_center=["version-switcher", "navbar-nav"],
    github_url="https://github.com/cta-observatory/ctapipe_io_hess",
    logo={"text": "ctapipe-io-hess"},
)

# Add any paths that contain custom static files (such as style sheets) here,
# relative to this directory. They are copied after the builtin static files,
# so a file named "default.css" will overwrite the builtin "default.css".
html_static_path = []


numpydoc_show_class_members = False
numpydoc_class_members_toctree = False

autodoc_default_options = {
    "show-inheritance": True,
    "members": True,
}

add_module_names = False
