# -*- coding: utf-8 -*-

from PyQt4.QtGui import *
from PyQt4.QtCore import *
import os
import sys
import sip
import string
from database import *
from constant import *

reload(sys)
sys.setdefaultencoding('UTF-8')

QTextCodec.setCodecForTr(QTextCodec.codecForName("utf8"))

class WorkThread(QThread):
    """command: [command, [params]]"""
    finishSignal = pyqtSignal(dict)
    def __init__(self, command, parent=None):
        super(WorkThread, self).__init__(parent)
        self.command = command

    def run(self):
        # 初始化
        if self.command[0]== COMMANDS[0]:
            status_code = init_database(DATABASE)
            if status_code:
                data = {'status': DATABASE_STATUS[status_code], 'result': []}
            else:
                params = "content, timestamp, status"
                data = select_table_all(DATABASE, TABLE, params)
        # 添加
        if self.command[0] == COMMANDS[1]:
            status_code = insert_table_one(DATABASE, TABLE, 'content', "'%s'" % self.command[1])
            if status_code:
                data = {'status': DATABASE_STATUS[status_code], 'result': []}
            else:
                params = "content, timestamp, status"
                data = select_table_all(DATABASE, TABLE, params)
        # 删除
        if self.command[0] == COMMANDS[2]:
            status_code = delete_items(DATABASE, TABLE, self.command[1])
            if status_code:
                data = {'status': DATABASE_STATUS[status_code], 'result': []}
            else:
                params = "content, timestamp, status"
                data = select_table_all(DATABASE, TABLE, params)
        # 标记为已完成
        if self.command[0] == COMMANDS[3]:
            status_code = update_status_done(DATABASE, TABLE, self.command[1])
            if status_code:
                data = {'status': DATABASE_STATUS[status_code], 'result': []}
            else:
                params = "content, timestamp, status"
                data = select_table_all(DATABASE, TABLE, params)
        # 标记为未完成
        if self.command[0] == COMMANDS[4]:
            status_code = update_status_undone(DATABASE, TABLE, self.command[1])
            if status_code:
                data = {'status': DATABASE_STATUS[status_code], 'result': []}
            else:
                params = "content, timestamp, status"
                data = select_table_all(DATABASE, TABLE, params)
        # 更新选中
        if self.command[0] == COMMANDS[5]:
            status_code = update_items(DATABASE, TABLE, self.command[1])
            if status_code:
                data = {'status': DATABASE_STATUS[status_code], 'result': []}
            else:
                params = "content, timestamp, status"
                data = select_table_all(DATABASE, TABLE, params)
            
        self.finishSignal.emit(data)

class Main(QWidget):
    def __init__(self, parent=None):
        super(Main, self).__init__(parent)
        self.initUI()
        params = "content, timestamp, status"
        data = select_table_all(DATABASE, TABLE, params)
        self.displayData(data['result'])

    def initUI(self):
        self.setWindowTitle(self.tr("Today"))
        self.resize(700, 400)
        self.setWindowIcon(QIcon('today.ico'))
        self.center()

        self.resultTable = QTableWidget()
        self.resultTable.setSelectionBehavior(QAbstractItemView.SelectRows)
        self.resultTable.setColumnCount(3)
        self.resultTable.setColumnWidth(0, 410)
        self.resultTable.setColumnWidth(1, 145)
        self.resultTable.setColumnWidth(2, 73)
        self.resultTable.setHorizontalHeaderLabels([self.tr('项目'), self.tr('时间'), self.tr('状态')])

        self.initPushButton = QPushButton(self.tr("初始化"))
        self.donePushButton = QPushButton(self.tr("已完成"))
        self.undonePushButton = QPushButton(self.tr("未完成"))
        self.updatePushButton = QPushButton(self.tr("更新选中"))
        self.deletePushButton = QPushButton(self.tr("删除选中"))

        settingLayout = QHBoxLayout()
        settingLayout.addStretch()
        settingLayout.addWidget(self.initPushButton)
        settingLayout.addWidget(self.donePushButton)
        settingLayout.addWidget(self.undonePushButton)
        settingLayout.addWidget(self.updatePushButton)
        settingLayout.addWidget(self.deletePushButton)

        self.contentLineEdit = QLineEdit()
        self.contentLineEdit.setMaximumWidth(585)
        self.contentLineEdit.setFixedWidth(585)
        self.addPushButton = QPushButton(self.tr("添加"))

        addLayout = QHBoxLayout()
        addLayout.addStretch()
        addLayout.addWidget(self.contentLineEdit)
        addLayout.addWidget(self.addPushButton)
        
        mainLayout = QVBoxLayout(self)
        mainLayout.setMargin(15)
        mainLayout.setSpacing(10)
        mainLayout.addWidget(self.resultTable)
        mainLayout.addLayout(settingLayout)
        mainLayout.addLayout(addLayout)

        # if os.path.isfile(DATABASE):
        #     self.initPushButton.setDisabled(True)

        self.connect(self.initPushButton, SIGNAL('clicked()'), self.initWork)
        self.connect(self.addPushButton, SIGNAL('clicked()'), self.addWork)        
        self.connect(self.donePushButton, SIGNAL('clicked()'), self.doneWork)
        self.connect(self.undonePushButton, SIGNAL('clicked()'), self.undoneWork)
        self.connect(self.deletePushButton, SIGNAL('clicked()'), self.deleteWork)
        self.connect(self.updatePushButton, SIGNAL('clicked()'), self.updateWork)

    def center(self):
        screen = QDesktopWidget().screenGeometry()
        size =  self.geometry()
        self.move((screen.width()-size.width())/2, (screen.height()-size.height())/2)

    def displayData(self, result):
        no = 1
        self.resultTable.setRowCount(len(result))
        for i, row in enumerate(result):
            for j, value in enumerate(row):
                if j == 2:
                    value = '已完成' if value else '未完成'
                self.resultTable.setItem(i, j, QTableWidgetItem(self.tr(str(value))))

    def initWork(self):
        self.initWorkThread = WorkThread([COMMANDS[0]])
        self.initWorkThread.finishSignal.connect(self.initWorkEnd)
        self.initWorkThread.start()

    def initWorkEnd(self, data):
        if data['status']:
            QMessageBox.information(self, 'Warning', self.tr(data['status']))
        else:
            self.displayData(data['result'])
            QMessageBox.information(self, self.tr("初始化"), self.tr("初始化完毕！"))

    def addWork(self):
        self.addWorkThread = WorkThread([COMMANDS[1], str(self.contentLineEdit.text())])
        self.addWorkThread.finishSignal.connect(self.addWorkEnd)
        self.addWorkThread.start()

    def addWorkEnd(self, data):
        self.contentLineEdit.setText('')
        if data['status']:
            QMessageBox.information(self, 'Warning', self.tr(data['status']))
        else:
            self.displayData(data['result'])
            # QMessageBox.information(self, self.tr("添加"), self.tr("添加成功！"))

    def doneWork(self):
        indexes = self.resultTable.selectedIndexes()
        rows = sorted(set(index.row() for index in indexes))

        if len(rows):
            timestamps = list()
            
            for row in rows:
                timestamp = self.resultTable.item(row, 1)
                timestamps.append(str(timestamp.text()))
            
            self.doneWorkThread = WorkThread([COMMANDS[3], timestamps])
            self.doneWorkThread.finishSignal.connect(self.doneWorkEnd)
            self.doneWorkThread.start()

    def doneWorkEnd(self, data):
        self.contentLineEdit.setText('')
        if data['status']:
            QMessageBox.information(self, 'Warning', self.tr(data['status']))
        else:
            self.displayData(data['result'])

    def undoneWork(self):
        indexes = self.resultTable.selectedIndexes()
        rows = sorted(set(index.row() for index in indexes))

        if len(rows):
            timestamps = list()
            
            for row in rows:
                timestamp = self.resultTable.item(row, 1)
                timestamps.append(str(timestamp.text()))
            
            self.undoneWorkThread = WorkThread([COMMANDS[4], timestamps])
            self.undoneWorkThread.finishSignal.connect(self.undoneWorkEnd)
            self.undoneWorkThread.start()

    def undoneWorkEnd(self, data):
        self.contentLineEdit.setText('')
        if data['status']:
            QMessageBox.information(self, 'Warning', self.tr(data['status']))
        else:
            self.displayData(data['result'])

    def deleteWork(self):
        indexes = self.resultTable.selectedIndexes()
        rows = sorted(set(index.row() for index in indexes))

        if len(rows):
            timestamps = list()
            
            for row in rows:
                timestamp = self.resultTable.item(row, 1)
                timestamps.append(str(timestamp.text()))
            
            self.deleteWorkThread = WorkThread([COMMANDS[2], timestamps])
            self.deleteWorkThread.finishSignal.connect(self.deleteWorkEnd)
            self.deleteWorkThread.start()

    def deleteWorkEnd(self, data):
        self.contentLineEdit.setText('')
        if data['status']:
            QMessageBox.information(self, 'Warning', self.tr(data['status']))
        else:
            self.displayData(data['result'])

    def updateWork(self):
        indexes = self.resultTable.selectedIndexes()
        rows = sorted(set(index.row() for index in indexes))

        if len(rows):
            data = dict()
            
            for row in rows:
                timestamp = self.resultTable.item(row, 1)
                content = self.resultTable.item(row, 0)
                print content
                print str(content)
                data[str(timestamp.text())] = str(content.text())
            
            self.updateWorkThread = WorkThread([COMMANDS[5], data])
            self.updateWorkThread.finishSignal.connect(self.updateWorkEnd)
            self.updateWorkThread.start()

    def updateWorkEnd(self, data):
        self.contentLineEdit.setText('')
        if data['status']:
            QMessageBox.information(self, 'Warning', self.tr(data['status']))
        else:
            self.displayData(data['result'])
            
if __name__ == "__main__":
    app = QApplication(sys.argv)

    main = Main()
    main.show()

    sip.setdestroyonexit(False)
    sys.exit(app.exec_())