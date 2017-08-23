from PyQt5 import QtCore, QtWidgets
import logging
from logging.handlers import TimedRotatingFileHandler
import os
import errno


def make_sure_path_exists(path):
    try:
        os.makedirs(path)
    except OSError as exception:
        if exception.errno != errno.EEXIST:
            raise


class QPlainTextEditLogger(logging.Handler):
    level_color_dict = {
        'DEBUG': '<span style=\" font-size:8pt; color:#00aa00;\" >',
        'INFO': '<span style=\" font-size:8pt; color:#000000;\" >',
        'WARNING': '<span style=\" font-size:8pt; color:#c3c300;\" >',
        'ERROR': '<span style=\" font-size:8pt; color:#aa0000;\" >',
        'CRITICAL': '<span style=\" font-size:8pt; font-weight:600; color:#aa0000;\" >'}

    def __init__(self):
        super().__init__()
        self.widget = QtWidgets.QTextEdit()
        self.widget.setReadOnly(True)

    def emit(self, record):
        msg = self.format(record)
        splited = msg.split(' - ')
        time = splited[0]
        module = splited[1]
        level = splited[2]
        content = splited[3]
        colored_text = "<span style=\" font-size:8pt; color:#00aa00;\" >"
        colored_text += time
        colored_text += "</span>"
        colored_text += "<span style=\" font-size:8pt; font-weight:600; color:#800080;\" > - "
        colored_text += module
        colored_text += "</span>"
        colored_text += "<span style=\" font-size:8pt; font-weight:600; color:#000000;\" > - "
        colored_text += level
        colored_text += " - </span>"
        colored_text += self.level_color_dict[level]
        colored_text += content
        colored_text += "</span>"
        self.widget.append(colored_text)


class Logger_Widget(QtWidgets.QWidget, QPlainTextEditLogger):
    def __init__(self, root_logger, display_level, file_level):
        super().__init__()
        # gui logger
        logTextBox = QPlainTextEditLogger()
        # only show warning + logs
        logTextBox.setLevel(display_level)
        logTextBox.setFormatter(logging.Formatter(
            '%(asctime)s - %(module)s - %(levelname)s - %(message)s'))

        # time rotated file logger
        log_file_path = 'logs'
        make_sure_path_exists(log_file_path)
        rotated_time_handler = TimedRotatingFileHandler(
            log_file_path + '/{0}.log'.format(root_logger.name),
            when='midnight',
            interval=1,
            backupCount=5,
            utc=True)
        rotated_time_handler.suffix = "%Y-%m-%d"
        rotated_time_handler.setFormatter(logging.Formatter(
            '%(asctime)s | %(name)s | %(module)s |  %(levelname)s: %(message)s'))
        rotated_time_handler.setLevel(file_level)

        # get root logger

        root_logger.addHandler(logTextBox)
        root_logger.addHandler(rotated_time_handler)

        # You can control the logging level

        layout = QtWidgets.QVBoxLayout(self)
        layout.addWidget(logTextBox.widget)
        # logging.debug("this is a debugging message")
        # logging.info("this is an informational message")
        # logging.error("this is an error message")
        # logging.warning("this is a warning message")
        # logging.critical("this is a critical message")


if (__name__ == '__main__'):

    app = QtWidgets.QApplication([])
    dlg = Logger_Widget()
    dlg.show()
    dlg.raise_()
    app.exec_()
