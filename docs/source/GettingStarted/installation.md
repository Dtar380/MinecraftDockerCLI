# Installation
## Prequisites
Before proceeding with the installation you need to make sure you have installed:
 - Python 3.13 with PIP
 - Docker Engine (Docker desktop on windows)
 - Docker Compose (Bundled with modern Docker Desktop installations)

## Methods
There are two methods of installing this APP:
 - [Python Package](#python-package)
 - [Building from source](#build-from-source)

## Python Package
```{note}
This is the recommended method
```
You can simply install the package via PIP since the APP is published on [pypi](https://pypi.org/project/MinecraftDockerCLI/).

We recommend to create a virtual environment for installing the package, although you can always install it in your root python install. <br>
To install the package in virtual environment you should run the following commands:
```
python3 -m venv .venv
./.venv/Scripts/activate
pip install MinecraftDockerCLI
```

## Build from source
For building from source you need to follow the next steps:
 - Clone the repo either downloading it from the github page or by running: <br>
    `git clone https://github.com/Dtar380/MinecraftDockerCLI.git`
 - Enter the folder of the repository you cloned and run: <br>
    `python -m pip install -e`
```{warning}
Do not errase the code from the cloned repository since the APP will be running from that source code
```
