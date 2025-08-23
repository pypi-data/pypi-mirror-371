# Phileas - a Python library for scientific experiment automation

Phileas is a Python library that eases the acquisition of hardware security
datasets. Its goal is to facilitate the setup of fault injection and
side-channel analysis experiments, using simple YAML configuration files to
describe both the experiment bench and the configurations of its instruments.
This provides basic building blocks towards the repeatability of such
experiments. Finally, it provides a transparent workflow that yields datasets
properly annotated to ease the data analysis stage.

-----

:::::::{grid} 2
:gutter: 5

:::::{grid-item-card} {octicon}`book` Introduction
:text-align: center

:::{button-ref} getting_started/introduction
:click-parent:
:outline:
:color: primary
:expand:

Overview of phileas features
:::::

:::::{grid-item-card} {octicon}`terminal` Installation
:text-align: center


:::{button-ref} getting_started/installation
:click-parent:
:outline:
:color: primary
:expand:

Installation instructions
:::::

:::::{grid-item-card} {octicon}`light-bulb` Examples
:text-align: center


:::{button-ref} examples/index
:click-parent:
:outline:
:color: primary
:expand:

Step-by-step examples
:::::


:::::{grid-item-card} {octicon}`tasklist` User guide
:text-align: center


:::{button-ref} user_guide/index
:click-parent:
:outline:
:color: primary
:expand:

Dive deeper into the different features
:::::

:::::{grid-item-card} {octicon}`code` API documentation
:text-align: center


:::{button-ref} api/index
:click-parent:
:outline:
:color: primary
:expand:

Browse the Python API documentation
:::::

:::::{grid-item-card} {octicon}`repo` Developer notes
:text-align: center

:::{button-ref} developer_notes/index
:click-parent:
:outline:
:color: primary
:expand:

Find out how to extend the library
:::::
::::::::::::

:::{toctree}
:maxdepth: 2
:hidden:

getting_started/index
examples/index
user_guide/index
api/index
developer_notes/index
:::
