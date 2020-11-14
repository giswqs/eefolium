# Installation

## Earth Engine Account

To use **eefolium**, you must first [sign up](https://earthengine.google.com/signup/) for a [Google Earth Engine](https://earthengine.google.com/) account.
You cannot use Google Earth Engine unless your application has been approved. Once you receive the application approval email, you can log in to
the [Earth Engine Code Editor](https://code.earthengine.google.com/) to get familiar with the JavaScript API.

![signup](https://i.imgur.com/ng0FzUT.png)

## Install from PyPI

**eefolium** is available on [PyPI](https://pypi.org/project/eefolium/). To install **eefolium**, run this command in your terminal:

    pip install eefolium

## Install from conda-forge

**eefolium** is also available on [conda-forge](https://anaconda.org/conda-forge/eefolium). If you have
[Anaconda](https://www.anaconda.com/distribution/#download-section) or [Miniconda](https://docs.conda.io/en/latest/miniconda.html) installed on your computer, you can create a conda Python environment to install eefolium:

    conda create -n gee python
    conda activate gee
    conda install mamba -c conda-forge
    mamba install eefolium -c conda-forge

Optionally, you can install some [Jupyter notebook extensions](https://github.com/ipython-contrib/jupyter_contrib_nbextensions), which can improve your productivity in the notebook environment. Some useful extensions include Table of Contents, Gist-it, Autopep8, Variable Inspector, etc. See this [post](https://towardsdatascience.com/jupyter-notebook-extensions-517fa69d2231) for more information.

    conda install jupyter_contrib_nbextensions -c conda-forge

Check the **YouTube** video below on how to install eefolium using conda.

[![eefolium](http://img.youtube.com/vi/h0pz3S6Tvx0/0.jpg)](http://www.youtube.com/watch?v=h0pz3S6Tvx0 "Install eefolium")

## Install from GitHub

To install the development version from GitHub using [Git](https://git-scm.com/), run the following command in your terminal:

    pip install git+https://github.com/giswqs/eefolium

## Upgrade eefolium

If you have installed **eefolium** before and want to upgrade to the latest version, you can run the following command in your terminal:

    pip install -U eefolium

If you use conda, you can update eefolium to the latest version by running the following command in your terminal:

    mamba update -c conda-forge eefolium

To install the development version from GitHub directly within Jupyter notebook without using Git, run the following code:

    import eefolium
    eefolium.update_package()

## Use Docker

To use eefolium in a Docker container, check out this [page](https://hub.docker.com/r/bkavlak/eefolium).
