# Python-Script-Monitor

### Special thanks to 
1. [https://github.com/jupyter/qtconsole] created `qtconsole` which is the core gui I used in my code.

## Why Am I creating this repo?
people love python. we use python running a lot of process at backend. 
For e.g., one may have a script running 24/7 scrapping stock tick price from yahoo.com, or one may have a python script send report everyday. Windows Task Schedule works great for it, however, we never know if a script is failed or not. Thats why I decide to build this gui monitor system and hopefully it can help me keep in track all my python script is successfully runing or not.

## Requirement
##### python env:

| python version        | availability |
| ------------- |:-------------:|
|python 3.6| available |
|< python 3.5 | untested     |
|python 2.x| unavailable |

##### module
PyQt5 `pip install pyqt5`

qtconsole `pip install qtconsole`

## Features
1. color indicator of each python shell working status
* red: IDLE
* green: BUSY

2. color indicator for catch the log level inside script
* load `example.json` and run to test it




## How to 
1. run `python_python_script_monitor_main.py`
2. click `+` to create a new instance of qt-jupyter console
3. choose the `*.py` file path
4. run your python script
__Optional__
1. single click the left panel button to switch between script
2. double click the left panel name button to change script name; press `Enter` after finished editing
3. under `menu` at the top left, you can save/load your configuration files (current script path and name)
