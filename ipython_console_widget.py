# Set the QT API to PyQt4
import os
os.environ['QT_API'] = 'pyqt'
import sip
sip.setapi("QString", 2)
sip.setapi("QVariant", 2)
from PyQt5.QtWidgets import *
from qtconsole.rich_ipython_widget import RichJupyterWidget
from qtconsole.manager import QtKernelManager
import sys
import logging
from qtconsole.qt import QtCore
import logger

class ipython_logger(QWidget):
    def __init__(self):
        super().__init__()
        self.logger = logging.getLogger('traitlets')
        self.layout = QVBoxLayout()
        self.setLayout(self.layout)
        self.layout.addWidget(QIPythonWidget())
        self.layout.addWidget(logger.Logger_Widget(self.logger, 0, 0))


class QIPythonWidget(RichJupyterWidget):
    """ Convenience class for a live IPython console widget. We can replace the standard banner using the
    customBanner argument"""
    kernel_status_signal = QtCore.pyqtSignal(object)
    def __init__(self, customBanner=None, *args, **kwargs):
        if customBanner != None:
            self.banner = customBanner
        super().__init__()

        self.font_size = 6
        self.kernel_manager = QtKernelManager()
        self.kernel_manager.start_kernel()
        self.kernel_manager.kernel.gui = 'qt'
        self.kernel_client = self._kernel_manager.client()
        self.kernel_client.start_channels()
        self.kernel_client.iopub_channel.message_received.connect(self.update_kernel_status)
        def stop():
            self.kernel_client.stop_channels()
            self.kernel_manager.shutdown_kernel()

        self.exit_requested.connect(stop)
        self.init_logging_level()

    def init_logging_level(self):
        self.logging_level = {}
        for i in range(101):
            if logging.getLevelName(i)[:5] != 'Level':
                self.logging_level[logging.getLevelName(i)] = i

    def _handle_stream(self, msg):
        """ Handle stdout, stderr, and stdin.
        """

        self.log.debug("stream: %s", msg.get('content', ''))
        for level in self.logging_level.keys():
            if level in msg['content']['text']:
                self.kernel_status_signal.emit(self.logging_level[level])
        if self.include_output(msg):
            self.flush_clearoutput()
            self.append_stream(msg['content']['text'])

    def update_kernel_status(self, msg):
        try:
            if msg['header']['msg_type'] == 'status':
                self.kernel_status = msg['content']['execution_state']
                self.kernel_status_signal.emit(self.kernel_status)
        except Exception as e:
            print(e)

    def shutdown_kernel(self):
        self.kernel_client.stop_channels()
        self.kernel_manager.shutdown_kernel()

    def restart_kernel(self):
        self.kernel_client.stop_channels()
        self.kernel_manager.shutdown_kernel()
        self.kernel_manager = QtKernelManager()
        self.kernel_manager.start_kernel()
        self.kernel_manager.kernel.gui = 'qt'
        self.kernel_client = self._kernel_manager.client()
        self.kernel_client.start_channels()
        self.kernel_client.iopub_channel.message_received.connect(self.update_kernel_status)

    def pushVariables(self, variableDict):
        """ Given a dictionary containing name / value pairs, push those variables to the IPython console widget """
        self.kernel_manager.kernel.shell.push(variableDict)

    def clearTerminal(self):
        """ Clears the terminal """
        self._control.clear()

    def printText(self, text):
        """ Prints some plain text to the console """
        self._append_plain_text(text)

    def executeCommand(self, command):
        self.printText(command + '\n')
        """ Execute a command in the frame of the console widget """
        self._execute(command, False)


if __name__ == "__main__":
    FORMAT = '%(asctime)s | %(name)s | %(module)s |  %(levelname)s: %(message)s'
    logging.basicConfig(format=FORMAT)
    app = QApplication(sys.argv)
    main = QIPythonWidget()
    main.show()
    sys.exit(app.exec_())

