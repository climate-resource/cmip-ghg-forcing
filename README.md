# Welcome to GHG forcing for CMIP

This repo is currently used as an onboarding project meant to familiarize me with the basic concepts required to work on GHG forcing for CMIP. Specifically, comparing satellite and ground-based measurements of GHG emissions using a basic fit.

In the future, this project should contain the clean, well documented pipeline to compute GHG forcings for CMIP.

## Status

* Scripts to download data from NOAA and AGAGE in /download
* Scripts for visualization of data in /visualization
* Scripts for simple linear fits of NOAA data and AGAGE data, for each location

TODO:
* Simple linear fit for all locations together
* Look into more complex fits including seasonality


### Download data
In the download folder, you can run each of the scripts there to download the corresponding datasets.

### Visualize data
Use and modify the scripts in the visualization folder to reproduce useful plots.

TODO: finish moving clean plots here
TODO: add comparison plots/gifs to

### Process data
NOT IMPLEMENTED YET
Here there will be scripts to for example provide a mapping between gb and sat data,


## Installation

We do all our environment management using [pixi](https://pixi.sh/latest).
To get started, you will need to make sure that pixi is installed
([instructions here](https://pixi.sh/latest),
we found that using the pixi provided script was best on a Mac).

To create the virtual environment, run

```sh
pixi install
pixi run pre-commit install
```

These steps are also captured in the `Makefile` so if you want a single
command, you can instead simply run `make virtual-enviroment`.

Having installed your virtual environment, you can now run commands in your
virtual environment using

```sh
pixi run <command>
```

For example, to run Python within the virtual environment, run

```sh
pixi run python
```

As another example, to run a notebook server, run

```sh
pixi run jupyter lab
```



### Contributing

TBD


### Repository structure

The repository is very basic. It imposes no structure on you so you can layout
your Python files, notebooks etc. in any way you wish. We do have a basic
`Makefile` which captures key commands in one place (for more thoughts on why
this makes sense, see
[general principles: automation](https://gitlab.com/znicholls/mullet-rse/-/blob/main/book/general-principles/automation.md)).
For an introduction to `make`, see
[this introduction from Software Carpentry](https://swcarpentry.github.io/make-novice/).
Having said this, if you're not interested in `make`, you can just copy the
commands out of the `Makefile` by hand and you will be 90% as happy for a
simple repository like this.

### Tools

In this repository, we use the following tools:

- git for version-control (for more on version control, see
  [general principles: version control](https://gitlab.com/znicholls/mullet-rse/-/blob/main/book/theory/version-control.md))
    - for these purposes, git is a great version-control system so we don't
      complicate things any further. For an introduction to Git, see
      [this introduction from Software Carpentry](http://swcarpentry.github.io/git-novice/).
- [Pixi](https://pixi.sh/latest/) for environment management
  (for more on environment management, see
  [general principles: environment management](https://gitlab.com/znicholls/mullet-rse/-/blob/main/book/theory/environment-management.md))
    - there are lots of environment management systems.
      Pixi works well in our experience and,
      for projects that need conda,
      it is the only solution we have tried that worked really well.
    - we track the `pixi.lock` file so that the environment
      is completely reproducible on other machines or by other people
      (e.g. if you want a colleague to take a look at what you've done)
- [pre-commit](https://pre-commit.com/) with some very basic settings to get some
  easy wins in terms of maintenance, specifically:
    - code formatting with [ruff](https://docs.astral.sh/ruff/formatter/)
    - basic file checks (removing unneeded whitespace, not committing large
      files etc.)
    - (for more thoughts on the usefulness of pre-commit, see
      [general principles: automation](https://gitlab.com/znicholls/mullet-rse/-/blob/main/book/general-principles/automation.md)
    - track your notebooks using
    [jupytext](https://jupytext.readthedocs.io/en/latest/index.html)
    (for more thoughts on the usefulness of Jupytext, see
    [tips and tricks: Jupytext](https://gitlab.com/znicholls/mullet-rse/-/blob/main/book/tips-and-tricks/managing-notebooks-jupytext.md))
        - this avoids nasty merge conflicts and incomprehensible diffs

## Original template

This project was generated from this template:
[basic python repository](https://gitlab.com/openscm/copier-basic-python-repository).
[copier](https://copier.readthedocs.io/en/stable/) is used to manage and
distribute this template.
