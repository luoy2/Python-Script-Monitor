from PyQt5 import QtWidgets, QtGui, QtCore, uic
from ipython_console_page_widget import QIPythonWidget
import os
import logging
import sys
import traceback
import logger
import ctypes
import json


def clean(item):
    """Clean up the memory by closing and deleting the item if possible."""
    if isinstance(item, list) or isinstance(item, dict):
        for _ in range(len(item)):
            clean(list(item).pop())
    else:
        try:
            item.close()
        except (RuntimeError, AttributeError):  # deleted or no close method
            pass
        try:
            item.deleteLater()
        except (
        RuntimeError, AttributeError):  # deleted or no deleteLater method
            pass


# end clean

class myContainerWidget(QtWidgets.QWidget,
                        uic.loadUiType('ui/single_container_widget.ui')[0]):
    change_tab_color_signal = QtCore.pyqtSignal(int, object)
    """ Main GUI Widget including a button and IPython Console widget inside vertical layout """

    def __init__(self):
        super().__init__()
        self.setupUi(self)
        self.init_ui()
        self.tab_index = 0
        # This allows the variable foo and method print_process_id to be accessed from the ipython console

    def init_ui(self):
        self.ipyConsole = QIPythonWidget(
            customBanner="Welcome to the embedded ipython console\n")
        self.ipyConsole.kernel_status_signal.connect(
            self.emit_status_and_index)
        self.kernel_layout.addWidget(self.ipyConsole)
        self.execute_button.clicked.connect(self.execute_program)
        self.end_button.clicked.connect(self.restart_kernel)
        self.open_souce_button.clicked.connect(self.select_source_file)
        self.source_path_edit.textChanged.connect(
            lambda: self.execute_button.setEnabled(True))

    def emit_status_and_index(self, status):
        self.change_tab_color_signal.emit(self.tab_index, status)

    def select_source_file(self):
        file_name = QtWidgets.QFileDialog.getOpenFileName()
        self.source_path_edit.setText(file_name[0])

    def restart_kernel(self):
        self.ipyConsole.restart_kernel()
        self.execute_button.setEnabled(True)
        self.change_tab_color_signal.emit(self.tab_index, 'idle')

    def execute_program(self):
        self.file_path = self.source_path_edit.text()
        self.file_name = self.file_path.split('/')[-1]
        self.needed_dir = os.path.dirname(self.file_path)
        logging.info(self.needed_dir)
        self.ipyConsole.executeCommand("import os")
        self.ipyConsole.executeCommand("import logging")
        self.ipyConsole.executeCommand("import sys")
        self.ipyConsole.executeCommand(
            "sys.path.append(r'{0}')".format(self.needed_dir))
        self.ipyConsole.executeCommand(
            "os.chdir(r'{0}')".format(self.needed_dir))
        # self.ipyConsole.executeCommand(
        #     "os.chdir(os.path.dirname(r'{0}'))".format(self.file_path))
        self.ipyConsole.executeCommand(
            "%run {0}".format(self.file_path))
        self.execute_button.setEnabled(False)
        self.end_button.setEnabled(True)


class EditablePushButton(QtWidgets.QPushButton):
    color_change_signal = QtCore.pyqtSignal(int, object)
    delete_signal = QtCore.pyqtSignal(bool)



    def __init__(self, text=' '):
        super().__init__()
        self.text = text
        self.setText(self.text)
        self.setCheckable(True)
        self.editor_handler()
        self.right_click_handler()
        self.signal_handler()
        self.setStyleSheet('''
                QPushButton:hover{  
                    background-color: grey; 
                    border-style: outset;  
                }
                ''')


    def editor_handler(self):
        self._editor = QtWidgets.QLineEdit(self)
        self._editor.setWindowFlags(QtCore.Qt.Popup)
        self._editor.setFocusProxy(self)
        self._editor.editingFinished.connect(self.handleEditingFinished)
        self._editor.installEventFilter(self)

    def right_click_handler(self):
        self.popMenu = QtWidgets.QMenu(self)
        self.delete_action = QtWidgets.QAction('delete', self)
        self.delete_action.triggered.connect(self.delete_widget)
        self.popMenu.addAction(self.delete_action)
        # self.popMenu.addSeparator()

    def signal_handler(self):
        self.setContextMenuPolicy(QtCore.Qt.CustomContextMenu)
        self.customContextMenuRequested.connect(self.on_context_menu)
        self.color_change_signal.connect(self.change_status)

    def on_context_menu(self, point):
        # show context menu
        self.popMenu.exec_(self.mapToGlobal(point))


    def change_status(self, index, level):
        try:
            if isinstance(level, str):
                if level == 'busy':
                    level = 0
                elif level == 'idle':
                    level = 60
                else:
                    level = 60
            red = str(min(200, int(0 + level / 60 * 200)))
            green = str(max(0, int(200 - level / 60 * 200)))

            qstyle_sheet = 'QPushButton:!hover{{ background-color : rgb({0}, {1}, 60); outline: none}}'.format(
                red, green)
            self.setStyleSheet(qstyle_sheet)
        except Exception as e:
            logging.exception(e)


    def eventFilter(self, widget, event):
        if ((
                            event.type() == QtCore.QEvent.MouseButtonPress and not self._editor.geometry().contains(
                        event.globalPos())) or (
                        event.type() == QtCore.QEvent.KeyPress and event.key() == QtCore.Qt.Key_Escape)):
            self._editor.hide()
            return True
        return QtWidgets.QPushButton.eventFilter(self, widget, event)


    def mouseDoubleClickEvent(self, event):
        rect = self.rect()
        self._editor.setFixedSize(rect.size())
        self._editor.move(self.parent().mapToGlobal(rect.topLeft()))
        if not self._editor.isVisible():
            self._editor.show()

    def handleEditingFinished(self):
        self.text = self._editor.text()
        self._editor.hide()
        self.setText(self.text)


    def delete_widget(self):
        try:
            close_msg = "Close {0}?".format(self.text)
            reply = QtWidgets.QMessageBox.question(None, 'Message',
                                               close_msg, QtWidgets.QMessageBox.Yes, QtWidgets.QMessageBox.No)
            if reply == QtWidgets.QMessageBox.Yes:
                logging.debug(
                    'trying to shut down {0}...'.format(self.text))
                self.deleteLater()
                self.delete_signal.emit(1)
        except Exception as e:
            logging.exception(e)




class myMainWindow(QtWidgets.QMainWindow,
                   uic.loadUiType("ui/main_window.ui")[0]):
    def __init__(self, if_auto=None):
        super().__init__()
        self.setupUi(self)
        self.button_group = QtWidgets.QButtonGroup()
        self.button_group.setExclusive(True)
        self.button_box_layout.setAlignment(QtCore.Qt.AlignTop)
        self.splitter.setStretchFactor(0, 0)
        self.splitter.setStretchFactor(1, 1)

        self.connect_signal()
        if len(if_auto) > 1:
            self.load_config('')
            for k in range(self.stacked_widget.count()):
                self.stacked_widget.widget(k).execute_program()
                QtWidgets.QApplication.processEvents()

    def connect_signal(self):
        self.add_widget_button.clicked.connect(self.create_new_page)
        self.save_config_action.triggered.connect(self.save_config)
        self.load_config_action.triggered.connect(self.load_config)

    def create_new_page(self,_, button_name='New Python Program', default_path='PATH_TO_FILE'):
        try:
            new_button = EditablePushButton(button_name)
            new_button.delete_signal.connect(self.delete_page)
            new_page = myContainerWidget()
            new_page.change_tab_color_signal.connect(new_button.change_status)
            new_page.source_path_edit.setText(default_path)
            self.stacked_widget.addWidget(new_page)
            self.button_box_layout.addWidget(new_button)
            self.button_group.addButton(new_button)
            self.stacked_widget.setCurrentIndex(self.stacked_widget.count())
            new_button.clicked.connect(self.switch_page)
        except Exception as e:
            print(e)

    def switch_page(self):
        try:
            index = self.button_box_layout.indexOf(self.sender())
            self.stacked_widget.setCurrentIndex(index)
        except Exception as e:
            print(e)

    def cleanUp(self):
        # Clean up everything
        for i in self.__dict__:
            item = self.__dict__[i]
            clean(item)

    def delete_page(self, _):
        try:
            index = self.button_box_layout.indexOf(self.sender())
            self.stacked_widget.widget(index).ipyConsole.shutdown_kernel()
            self.stacked_widget.widget(index).deleteLater()
        except Exception as e:
            print(e)

    def save_config(self, _):
        try:
            current_widigets = (self.button_box_layout.itemAt(i).widget() for i in
                                range(self.button_box_layout.count()))
            output_dict = {}
            for k, v in enumerate(current_widigets):
                output_dict[v.text] = self.stacked_widget.widget(k).source_path_edit.text()
            print(output_dict)
            filename = QtWidgets.QFileDialog.getSaveFileName(self, 'Save file', 'config', "JSON (*.json)")
            with open(filename[0], 'w') as f:
                json.dump(output_dict, f)
            QtWidgets.QMessageBox.information(self, "info", "file saved!")
        except Exception as e:
            print(e)


    def load_config(self, _):
        try:
            filename = QtWidgets.QFileDialog.getOpenFileNames(self, "Select File", "", "*.json")
            with open(filename[0][0], 'r') as f:
                config = json.load(f)
            for k, v in config.items():
                self.create_new_page(None, k, v)
                QtWidgets.QApplication.processEvents()
            QtWidgets.QMessageBox.information(self, "info", "Configuration Loaded")
        except Exception as e:
            print(e)


def main():
    try:
        app = QtWidgets.QApplication([])
        widget = myMainWindow(sys.argv)
        widget.show()
        app.aboutToQuit.connect(widget.cleanUp)
        app.exec_()
    except:
        logging.critical(sys.exc_info()[1:])
        logging.critical(traceback.print_exc())


if __name__ == '__main__':
    myappid = 'pythonscriptmonitor.version1.0'  # arbitrary string
    ctypes.windll.shell32.SetCurrentProcessExplicitAppUserModelID(myappid)
    main()
