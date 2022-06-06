# Violet Starter Kit

The Violet Starter Kit includes a couple of [images](./images) for you to use in your simulations.
In addition, it includes a [template](./flocking.py) which you can use to build the flocking simulation.

Simply click on the shiny green `Use this template` button at the top of this page to create your own GitHub repository.
From there, [clone your repository](https://docs.github.com/en/repositories/creating-and-managing-repositories/cloning-a-repository) with either:
- [GitHub Desktop](https://desktop.github.com) (recommended)
- [The GitHub CLI](https://cli.github.com)
- or manually with the `git clone` command

## Installing Violet

[Violet](https://github.com/m-rots/violet) is built on top of the latest and greatest Python features such as type hints, generics and dataclasses.
Therefore, you need to have a pretty recent version of Python installed: Python 3.9 or later.

On MacOS, it's pretty easy to update Python.
[Install Homebrew](https://brew.sh) if you haven't already and then run:

```shell
brew install python3
```

On Windows, it's even easier!
Head over to the [Microsoft Store](https://apps.microsoft.com/store/detail/python-310/9PJPW5LDXLZ5) and install Python 3.10 there!

Last but not least, install Violet and you're good to go!

```shell
pip3 install -U violet-simulator
```

## Running the code

Open the terminal and `cd` to the directory you just cloned.
Then run the following command to start the [`flocking.py`](./flocking.py) simulation:

```shell
python3 flocking.py
```
