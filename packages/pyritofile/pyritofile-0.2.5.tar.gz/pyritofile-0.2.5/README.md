# Pyritofile

Pyritofile is a Python library designed to read and manipulate basic league of legends files.
It is originally from [LtMAO](https://github.com/tarngaina/LtMAO/tree/master/src/LtMAO/pyRitoFile) project made by [Tarngaina](https://github.com/tarngaina) then published by me (GuiSaiUwU) to be used as a python package.

## Installation

Requires python **3.10** or higher.
Since its published in [PyPI](https://pypi.org/project/pyritofile/) to install its only required one simple CLI command:

```sh
pip install pyritofile
```

## Small Example Usage

To use pyritofile, you first need to import the class you want to use and instantiate, then you fill the data by using the read() method.

```python
from pyritofile import SKN

skn_file = SKN()
skn_file.read('Path/To/File.skn')
print(skn_file.__json__())
```

# Extra:
- [LeagueToolKit](https://github.com/LeagueToolkit/LeagueToolkit)
- [LtMAO](https://github.com/tarngaina/LtMAO)