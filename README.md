# Python-Script-Monitor

### Special thanks to 
1. [https://github.com/jupyter/qtconsole] created `qtconsole` which is the core gui I used in my code.

## Why Am I creating this repo?
People love python. We use python to run a lot of processes at the back end. 
For e.g., one may have a script run 24/7 scrapping stock tick price from yahoo.com, or may have a python script sent report everyday. Windows Task Schedule works great for it, however, we never know if a script is failed or not. Thats why I decide to build this gui monitor system and hopefully it can help me keep track of all my python scripts and make sure they are successfully run.

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

[![create conda env](http://img.youtube.com/vi/hGsZjHFV3vo/0.jpg)](https://www.youtube.com/watch?v=hGsZjHFV3vo)

[![monitor walk through](http://img.youtube.com/vi/ZEiStEWXi_0/0.jpg)](https://www.youtube.com/watch?v=ZEiStEWXi_0)

## Example
I put two example files, one for testing log color change, another one for testing python shell status.

One can simply open them, and using `save config` function inside `menu` bar to see whats going on


## Known Bug
1. sometimes after stop the shell and quickly restart the shell, qt window crahsed
2. sometimes the status signal didn't emit to the button at left, thus button color does not change


## To do
1. add alerting function if any task went wrong
    * email
    * audio
    * skype
    * slack
    * sms
    
