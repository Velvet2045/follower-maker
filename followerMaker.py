import shutil
import os, pickle
from PyQt5 import QtCore, QtGui, QtWidgets
import threading, time
from update import *
from socket import *
import ctypes
from os.path import expanduser

PGM_VERSION = 1.5

ERROR_NONE = 0
ERROR_DRIVER = 1
ERROR_UNIDENTIFIED_USER = 2
ERROR_OLD_VERSION = 3
ERROR_FAIL_TO_GET_URL = 4
ERROR_FAIL_TO_DOWNLOAD = 5

TBL_USE_ACCOUNT = 0
TBL_ID = 1
TBL_PW = 2
TBL_USE_LIKE = 3
TBL_USE_FOLLOW = 4
TBL_USE_COMMENT = 5
TBL_USE_FILTER = 6
TBL_HASHTAGS = 7
TBL_COMMENTS = 8
TBL_FILTERS = 9
TBL_REPEAT_CNT = 10
TBL_TAG_SHIFT = 11
TBL_SPEED = 12
TBL_MAX = 13

MODE_TAGRUN = 0
MODE_IDRUN = 1
MODE_UNFOLLOW1 = 2
MODE_UNFOLLOW2 = 3

PORT = 8081
SERVER_SOCK = socket(AF_INET, SOCK_STREAM)

def receive(txtView, sock):
    while True:
        recvData = sock.recv(1024)
        if not recvData:
            break
        s = "[Client] %s" % recvData.decode('utf-8')
        printLog(txtView, s)
    sock.close()

def printLog(txtView, log):
    now = time.localtime()
    s = "INFO [%04d-%02d-%02d %02d:%02d:%02d] " % (now.tm_year, now.tm_mon, now.tm_mday, now.tm_hour, now.tm_min, now.tm_sec)
    if txtView:
        txtView.append(str(s + log))
    else:
        print(str(s + log))
        msg = ctypes.windll.user32.MessageBoxW(None, str(log), "Follow Maker Noti", 0)

def getBrowserDir():
    return ("%s\\InstaPy\\assets\\chromedriver.exe") % expanduser("~")

def copyBrower():
    pastePath = "{}\\InstaPy\\assets".format(expanduser("~"))
    if not os.path.isdir(pastePath):
        os.makedirs(os.path.join(pastePath))
    if not os.path.isfile(getBrowserDir()):
        shutil.copy("chromedriver.exe", pastePath)

def runInstaPy():
    file = "{}\\run\\run.exe".format(os.getcwd())

    if os.path.isfile(file):
        print('run parser: {}'.format(file))
        os.popen(file)
    else:
        print('fail to run parser: {}'.format(file))

def runInstaller():
    file = "{}\\installer\\installer.exe".format(os.getcwd())

    if os.path.isfile(file):
        print('run installer: {}'.format(file))
        os.popen(file)
    else:
        print('fail to run installer: {}'.format(file))

def runProcessKiller():
    file = "{}\\ProgramInstaller.exe".format(os.getcwd())

    if os.path.isfile(file):
        print('run ProgramInstaller: {}'.format(file))
        os.popen(file)
    else:
        print('fail to run ProgramInstaller: {}'.format(file))

def runChromeKiller():
    file = "{}\\ChromeCloser.exe".format(os.getcwd())

    if os.path.isfile(file):
        print('run runChromeKiller: {}'.format(file))
        os.popen(file)
    else:
        print('fail to run runChromeKiller: {}'.format(file))

def check_version_counter(macId, curVer, driverPath):
    bRunning = True
    while bRunning:
        time.sleep(6 * 60 * 60)
        # errCode = ERROR_UNIDENTIFIED_USER
        bResult, errCode, errMsg = check_version(macId, curVer, driverPath)
        if errCode == ERROR_UNIDENTIFIED_USER:
            bRunning = False

        elif errCode == ERROR_OLD_VERSION:
            msg = ctypes.windll.user32.MessageBoxW(None, "??????????????? ???????????? ???????????????????", "Follow Maker Noti", 4)
            if msg == 6:
                bResult, errCode, errMsg = downlaod_updatefile(getBrowserDir())
                if bResult:
                    installer = threading.Thread(target=runInstaller())
                    installer.start()
                    bRunning = False

                else:
                    printLog(None, errMsg)

    processKiller = threading.Thread(target=runProcessKiller())
    processKiller.start()

def getAccountData():
    if os.path.isfile('db/tbA.p'):
        with open('db/tbA.p', 'rb') as file:
            accounts = pickle.load(file)
    else:
        accounts = None

    return accounts

def getHashtagData():
    if os.path.isfile('db/tbH.p'):
        with open('db/tbH.p', 'rb') as file:
            hashtags = pickle.load(file)
    else:
        hashtags = None

    return hashtags

def getCommentData():
    if os.path.isfile('db/tbC.p'):
        with open('db/tbC.p', 'rb') as file:
            comments = pickle.load(file)
    else:
        comments = None

    return comments

def getFilterData():
    if os.path.isfile('db/tbF.p'):
        with open('db/tbF.p', 'rb') as file:
            filters = pickle.load(file)
    else:
        filters = None

    return filters

def setMode(mode):
    with open('db/tbU.p', 'wb') as file:
        pickle.dump(mode, file)

class StoppableThread(threading.Thread):
    """Thread class with a stop() method. The thread itself has to check
    regularly for the stopped() condition."""

    def __init__(self, func, args):
        super(StoppableThread, self).__init__()
        self._stop_event = threading.Event()
        self.func = func
        self.args = args

    def run(self):
        self.func(*self.args)

    def stop(self):
        self._stop_event.set()

    def stopped(self):
        return self._stop_event.is_set()

class AccountDialog(QtWidgets.QDialog):
    def __init__(self):
        super().__init__()
        self.setupUi()
        self.bSetAccount = False

    def setupUi(self):
        self.setObjectName("Dialog")
        self.resize(746, 391)
        self.tableAccount = QtWidgets.QTableWidget(self)
        self.tableAccount.setGeometry(QtCore.QRect(30, 80, 691, 241))
        self.tableAccount.setObjectName("tableWidget")
        self.tableAccount.setColumnCount(0)
        self.tableAccount.setRowCount(0)
        self.horizontalLayoutWidget = QtWidgets.QWidget(self)
        self.horizontalLayoutWidget.setGeometry(QtCore.QRect(30, 20, 691, 41))
        self.horizontalLayoutWidget.setObjectName("horizontalLayoutWidget")
        self.horizontalLayout = QtWidgets.QHBoxLayout(self.horizontalLayoutWidget)
        self.horizontalLayout.setContentsMargins(0, 0, 0, 0)
        self.horizontalLayout.setObjectName("horizontalLayout")
        self.btnAdd = QtWidgets.QPushButton(self.horizontalLayoutWidget)
        self.btnAdd.setObjectName("btnAdd")
        self.horizontalLayout.addWidget(self.btnAdd)
        self.btnAdd.clicked.connect(self.btnAddClicked)
        self.btnDel = QtWidgets.QPushButton(self.horizontalLayoutWidget)
        self.btnDel.setObjectName("btnDel")
        self.horizontalLayout.addWidget(self.btnDel)
        self.btnDel.clicked.connect(self.btnDelClicked)
        self.btnClear = QtWidgets.QPushButton(self.horizontalLayoutWidget)
        self.btnClear.setObjectName("btnClear")
        self.horizontalLayout.addWidget(self.btnClear)
        self.btnClear.clicked.connect(self.btnClearClicked)
        self.btnTagRun = QtWidgets.QPushButton(self)
        self.btnTagRun.setGeometry(QtCore.QRect(30, 340, 162, 34))
        self.btnTagRun.setObjectName("btnTagRun")
        self.btnTagRun.clicked.connect(self.btnTagRunClicked)
        self.btnIdRun = QtWidgets.QPushButton(self)
        self.btnIdRun.setGeometry(QtCore.QRect(200, 340, 162, 34))
        self.btnIdRun.setObjectName("btnIdRun")
        self.btnIdRun.clicked.connect(self.btnIdRunClicked)
        self.btnUnfollow1 = QtWidgets.QPushButton(self)
        self.btnUnfollow1.setGeometry(QtCore.QRect(370, 340, 112, 34))
        self.btnUnfollow1.setObjectName("btnUnfollow1")
        self.btnUnfollow1.clicked.connect(self.btnUnfollow1Clicked)
        self.btnUnfollow2 = QtWidgets.QPushButton(self)
        self.btnUnfollow2.setGeometry(QtCore.QRect(490, 340, 112, 34))
        self.btnUnfollow2.setObjectName("btnUnfollow2")
        self.btnUnfollow2.clicked.connect(self.btnUnfollow2Clicked)
        self.btnCancel = QtWidgets.QPushButton(self)
        self.btnCancel.setGeometry(QtCore.QRect(610, 340, 112, 34))
        self.btnCancel.setObjectName("btnCancel")
        self.btnCancel.clicked.connect(self.btnCancelClicked)

        self.retranslateUi()
        QtCore.QMetaObject.connectSlotsByName(self)

        self.makeTable()
        self.loadPickleData()
        self.saveData()

    def retranslateUi(self):
        _translate = QtCore.QCoreApplication.translate
        self.setWindowTitle(_translate("Dialog", "?????? ??????"))
        self.btnAdd.setText(_translate("Dialog", "?????? ??????"))
        self.btnDel.setText(_translate("Dialog", "?????? ??????"))
        self.btnClear.setText(_translate("Dialog", "?????? ??????"))
        self.btnTagRun.setText(_translate("Dialog", "?????? ?????? ??????"))
        self.btnIdRun.setText(_translate("Dialog", "????????? ?????? ??????"))
        self.btnUnfollow1.setText(_translate("Dialog", "??????X ??????"))
        self.btnUnfollow2.setText(_translate("Dialog", "?????? ??????"))
        self.btnCancel.setText(_translate("Dialog", "??????"))

    def btnTagRunClicked(self):
        self.saveData()
        setMode(MODE_TAGRUN)
        printLog(None, "???????????? ?????? ?????????/??????/????????? ??????")
        self.close()

    def btnIdRunClicked(self):
        self.saveData()
        setMode(MODE_IDRUN)
        printLog(None, "????????? ?????? ?????????/??????/????????? ??????")
        self.close()

    def btnUnfollow1Clicked(self):
        self.saveData()
        setMode(MODE_UNFOLLOW1)
        printLog(None, "?????? ?????? ?????? ???????????? ??????")
        self.close()

    def btnUnfollow2Clicked(self):
        self.saveData()
        setMode(MODE_UNFOLLOW2)
        printLog(None, "?????? ?????? ???????????? ??????")
        self.close()

    def btnCancelClicked(self):
        self.close()

    def btnAddClicked(self):
        rowCount = self.tableAccount.rowCount()
        self.tableAccount.setRowCount(rowCount + 1)

        # add check box
        chkUse = QtWidgets.QCheckBox()
        chkUse.setStyleSheet("margin-left:50%; margin-right:50%;")
        self.tableAccount.setCellWidget(rowCount, TBL_USE_ACCOUNT, chkUse)

        # set id
        txtId = QtWidgets.QTableWidgetItem()
        self.tableAccount.setItem(rowCount, TBL_ID, txtId)

        # set password star
        txtPw = QtWidgets.QLineEdit()
        txtPw.setEchoMode(QtWidgets.QLineEdit.Password)
        self.tableAccount.setCellWidget(rowCount, TBL_PW, txtPw)

        # add check box
        chkUseLike = QtWidgets.QCheckBox()
        chkUseLike.setStyleSheet("margin-left:50%; margin-right:50%;")
        self.tableAccount.setCellWidget(rowCount, TBL_USE_LIKE, chkUseLike)

        # add check box
        chkUseFollow = QtWidgets.QCheckBox()
        chkUseFollow.setStyleSheet("margin-left:50%; margin-right:50%;")
        self.tableAccount.setCellWidget(rowCount, TBL_USE_FOLLOW, chkUseFollow)

        # add check box
        chkUseComment = QtWidgets.QCheckBox()
        chkUseComment.setStyleSheet("margin-left:50%; margin-right:50%;")
        self.tableAccount.setCellWidget(rowCount, TBL_USE_COMMENT, chkUseComment)

        # add check box
        chkUseFilter = QtWidgets.QCheckBox()
        chkUseFilter.setStyleSheet("margin-left:50%; margin-right:50%;")
        self.tableAccount.setCellWidget(rowCount, TBL_USE_FILTER, chkUseFilter)

        cmbHashtag = QtWidgets.QComboBox()
        if os.path.isfile('db/tbH.p'):
            with open('db/tbH.p', 'rb') as file:
                hashtags = pickle.load(file)
            for row in range(0, len(hashtags)):
                cmbHashtag.addItem(hashtags[row][0])
        else:
            cmbHashtag.addItem('None')
        self.tableAccount.setCellWidget(rowCount, TBL_HASHTAGS, cmbHashtag)

        cmbComment = QtWidgets.QComboBox()
        if os.path.isfile('db/tbC.p'):
            with open('db/tbC.p', 'rb') as file:
                comments = pickle.load(file)
            for row in range(0, len(comments)):
                cmbComment.addItem(comments[row][0])
        else:
            cmbComment.addItem('None')
        self.tableAccount.setCellWidget(rowCount, TBL_COMMENTS, cmbComment)

        cmbFilter = QtWidgets.QComboBox()
        if os.path.isfile('db/tbF.p'):
            with open('db/tbF.p', 'rb') as file:
                filters = pickle.load(file)
            for row in range(0, len(filters)):
                cmbFilter.addItem(filters[row][0])
        else:
            cmbFilter.addItem('None')
        self.tableAccount.setCellWidget(rowCount, TBL_FILTERS, cmbFilter)

        # add default text
        txtRepeatCount = QtWidgets.QTableWidgetItem('1')
        self.tableAccount.setItem(rowCount, TBL_REPEAT_CNT, txtRepeatCount)

        txtTagShift = QtWidgets.QTableWidgetItem('50')
        self.tableAccount.setItem(rowCount, TBL_TAG_SHIFT, txtTagShift)

    def btnDelClicked(self):
        selectedRow = self.tableAccount.currentIndex().row()
        self.tableAccount.removeRow(selectedRow)

    def btnClearClicked(self):
        rowCount = self.tableAccount.rowCount()
        for row in reversed(range(rowCount)):
            self.tableAccount.removeRow(row)

    def makeTable(self):
        # single selection mode
        self.tableAccount.setSelectionMode(1)

        # set rows, columns
        self.tableAccount.setColumnCount(TBL_MAX)
        self.tableAccount.setRowCount(1)

        # set column header
        self.tableAccount.setHorizontalHeaderLabels(['?????? ??????', '?????????', '????????????',
                                                     '????????? ??????', '????????? ??????', '?????? ??????',
                                                     '????????? ??????', 'TAG/ID ??????', '?????? ??????',
                                                     '?????? ??????', '??? ?????? ???', '?????? ??? ??????',
                                                     '?????? ??????'])
        self.tableAccount.horizontalHeaderItem(0).setToolTip('????????????...')
        self.tableAccount.setColumnWidth(TBL_USE_ACCOUNT, 120)
        self.tableAccount.setColumnWidth(TBL_ID, 120)
        self.tableAccount.setColumnWidth(TBL_PW, 120)
        self.tableAccount.setColumnWidth(TBL_USE_LIKE, 120)
        self.tableAccount.setColumnWidth(TBL_USE_FOLLOW, 120)
        self.tableAccount.setColumnWidth(TBL_USE_COMMENT, 120)
        self.tableAccount.setColumnWidth(TBL_USE_FILTER, 120)
        self.tableAccount.setColumnWidth(TBL_COMMENTS, 120)
        self.tableAccount.setColumnWidth(TBL_HASHTAGS, 120)
        self.tableAccount.setColumnWidth(TBL_FILTERS, 120)
        self.tableAccount.setColumnWidth(TBL_REPEAT_CNT, 120)
        self.tableAccount.setColumnWidth(TBL_TAG_SHIFT, 120)
        self.tableAccount.setColumnWidth(TBL_SPEED, 120)

        accounts = None
        rowCount = 1
        if os.path.isfile('db/tbA.p'):
            with open('db/tbA.p', 'rb') as file:
                accounts = pickle.load(file)
                # print(accounts)
                rowCount = len(accounts)

        self.tableAccount.setRowCount(rowCount)

        for row in range(0, rowCount):
            # add check box
            chkUse = QtWidgets.QCheckBox()
            chkUse.setStyleSheet("margin-left:50%; margin-right:50%;")
            if accounts:
                chkUse.setChecked(accounts[row][TBL_USE_ACCOUNT])
            self.tableAccount.setCellWidget(row, TBL_USE_ACCOUNT, chkUse)

            # set id
            txtId = QtWidgets.QTableWidgetItem()
            if accounts:
                txtId = QtWidgets.QTableWidgetItem(str(accounts[row][TBL_ID]))
            self.tableAccount.setItem(row, TBL_ID, txtId)

            # set password star
            txtPw = QtWidgets.QLineEdit()
            txtPw.setEchoMode(QtWidgets.QLineEdit.Password)
            if accounts:
                txtPw.setText(str(accounts[row][TBL_PW]))
            self.tableAccount.setCellWidget(row, TBL_PW, txtPw)

            chkUseLike = QtWidgets.QCheckBox()
            chkUseLike.setStyleSheet("margin-left:50%; margin-right:50%;")
            if accounts:
                chkUseLike.setChecked(accounts[row][TBL_USE_LIKE])
            self.tableAccount.setCellWidget(row, TBL_USE_LIKE, chkUseLike)

            chkUseFollow = QtWidgets.QCheckBox()
            chkUseFollow.setStyleSheet("margin-left:50%; margin-right:50%;")
            if accounts:
                chkUseFollow.setChecked(accounts[row][TBL_USE_FOLLOW])
            self.tableAccount.setCellWidget(row, TBL_USE_FOLLOW, chkUseFollow)

            chkUseComment = QtWidgets.QCheckBox()
            chkUseComment.setStyleSheet("margin-left:50%; margin-right:50%;")
            if accounts:
                chkUseComment.setChecked(accounts[row][TBL_USE_COMMENT])
            self.tableAccount.setCellWidget(row, TBL_USE_COMMENT, chkUseComment)

            chkUseFilter = QtWidgets.QCheckBox()
            chkUseFilter.setStyleSheet("margin-left:50%; margin-right:50%;")
            if accounts:
                chkUseFilter.setChecked(accounts[row][TBL_USE_FILTER])
            self.tableAccount.setCellWidget(row, TBL_USE_FILTER, chkUseFilter)

            cmbHashtag = QtWidgets.QComboBox()
            if os.path.isfile('db/tbH.p'):
                with open('db/tbH.p', 'rb') as file:
                    hashtags = pickle.load(file)
                for cnt in range(0, len(hashtags)):
                    cmbHashtag.addItem(hashtags[cnt][0])
            else:
                cmbHashtag.addItem('None')

            if accounts:
                cmbHashtag.setCurrentIndex(int(accounts[row][TBL_HASHTAGS]))
            self.tableAccount.setCellWidget(row, TBL_HASHTAGS, cmbHashtag)

            cmbComment = QtWidgets.QComboBox()
            if os.path.isfile('db/tbC.p'):
                with open('db/tbC.p', 'rb') as file:
                    comments = pickle.load(file)
                for cnt in range(0, len(comments)):
                    cmbComment.addItem(comments[cnt][0])
            else:
                cmbComment.addItem('None')
            if accounts:
                cmbComment.setCurrentIndex(int(accounts[row][TBL_COMMENTS]))
            self.tableAccount.setCellWidget(row, TBL_COMMENTS, cmbComment)

            cmbFilter = QtWidgets.QComboBox()
            if os.path.isfile('db/tbF.p'):
                with open('db/tbF.p', 'rb') as file:
                    filters = pickle.load(file)
                for cnt in range(0, len(filters)):
                    cmbFilter.addItem(filters[cnt][0])
            else:
                cmbFilter.addItem('None')
            if accounts:
                cmbFilter.setCurrentIndex(int(accounts[row][TBL_FILTERS]))
            self.tableAccount.setCellWidget(row, TBL_FILTERS, cmbFilter)

            # add default text
            txtRepeatCount = QtWidgets.QTableWidgetItem('1')
            if accounts:
                txtRepeatCount = QtWidgets.QTableWidgetItem(accounts[row][TBL_REPEAT_CNT])
            self.tableAccount.setItem(row, TBL_REPEAT_CNT, txtRepeatCount)

            txtTagShift = QtWidgets.QTableWidgetItem('50')
            if accounts:
                txtTagShift = QtWidgets.QTableWidgetItem(accounts[row][TBL_TAG_SHIFT])
            self.tableAccount.setItem(row, TBL_TAG_SHIFT, txtTagShift)

            cmbSpeed = QtWidgets.QComboBox()
            cmbSpeed.addItem('0')
            cmbSpeed.addItem('1')
            cmbSpeed.addItem('2')
            cmbSpeed.addItem('3')
            cmbSpeed.addItem('4')
            if accounts:
                cmbSpeed.setCurrentIndex(int(accounts[row][TBL_SPEED]))
            self.tableAccount.setCellWidget(row, TBL_SPEED, cmbSpeed)

    def loadPickleData(self):
        rowCount = self.tableAccount.rowCount()
        hashtags = getHashtagData()
        if hashtags:
            for cnt in range(0, rowCount):
                self.tableAccount.cellWidget(cnt, TBL_HASHTAGS).clear()
                for row in range(0, len(hashtags)):
                    self.tableAccount.cellWidget(cnt, TBL_HASHTAGS).addItem(hashtags[row][0])
        else:
            self.tableAccount.cellWidget(0, TBL_HASHTAGS).addItem('None')

        comments = getCommentData()
        if comments:
            for cnt in range(0, rowCount):
                self.tableAccount.cellWidget(cnt, TBL_COMMENTS).clear()
                for row in range(0, len(comments)):
                    self.tableAccount.cellWidget(cnt, TBL_COMMENTS).addItem(comments[row][0])
        else:
            self.tableAccount.cellWidget(0, TBL_COMMENTS).addItem('None')

        filters = getFilterData()
        if filters:
            for cnt in range(0, rowCount):
                self.tableAccount.cellWidget(cnt, TBL_FILTERS).clear()
                for row in range(0, len(filters)):
                    self.tableAccount.cellWidget(cnt, TBL_FILTERS).addItem(filters[row][0])
        else:
            self.tableAccount.cellWidget(0, TBL_FILTERS).addItem('None')

    def saveData(self):
        rowCount = self.tableAccount.rowCount()
        accounts = []

        for row in range(rowCount):
            accounts.append([])
            chkBox1 = self.tableAccount.cellWidget(row, TBL_USE_ACCOUNT)
            if isinstance(chkBox1, QtWidgets.QCheckBox):
                accounts[row].append(chkBox1.isChecked())

            txtId = 'None'
            if self.tableAccount.item(row, TBL_ID):
                txtId = self.tableAccount.item(row, TBL_ID).text()
            accounts[row].append(txtId)

            cellPw = self.tableAccount.cellWidget(row, TBL_PW)
            if isinstance(cellPw, QtWidgets.QLineEdit):
                accounts[row].append(cellPw.text())

            for col in range(TBL_USE_LIKE, TBL_USE_FILTER + 1):
                chkBox2 = self.tableAccount.cellWidget(row, col)
                if isinstance(chkBox2, QtWidgets.QCheckBox):
                    accounts[row].append(chkBox2.isChecked())

            for col in range(TBL_HASHTAGS, TBL_FILTERS + 1):
                cmbBox2 = self.tableAccount.cellWidget(row, col)
                if isinstance(cmbBox2, QtWidgets.QComboBox):
                    accounts[row].append(cmbBox2.currentIndex())

            for col in range(TBL_REPEAT_CNT, TBL_TAG_SHIFT + 1):
                value = '1'
                if self.tableAccount.item(row, col):
                    value = self.tableAccount.item(row, col).text()
                accounts[row].append(value)

            cmbSpeed = self.tableAccount.cellWidget(row, TBL_SPEED)
            if isinstance(cmbSpeed, QtWidgets.QComboBox):
                accounts[row].append(cmbSpeed.currentIndex())

        with open('db/tbA.p', 'wb') as file:
            pickle.dump(accounts, file)

        self.bSetAccount = True

    def delAccountLog(self):
        selectedRow = self.tableAccount.currentIndex().row()
        txtId = 'None'
        if self.tableAccount.item(selectedRow, TBL_ID):
            txtId = self.tableAccount.item(selectedRow, TBL_ID).text()

        if not txtId == 'None':
            logPath = "%s/InstaPy/logs/%s" % (expanduser("~"), txtId)
            if os.path.isdir(logPath):
                shutil.rmtree(logPath)
                msg = "[%s] ?????? ?????? ??????" % txtId
                printLog(self.txtLog, msg)

class HashtagDialog(QtWidgets.QDialog):
    def __init__(self):
        super().__init__()
        self.setupUi()

    def setupUi(self):
        self.setObjectName("Dialog")
        self.resize(746, 391)
        self.tableWidget = QtWidgets.QTableWidget(self)
        self.tableWidget.setGeometry(QtCore.QRect(30, 80, 691, 241))
        self.tableWidget.setObjectName("tableWidget")
        self.tableWidget.setColumnCount(0)
        self.tableWidget.setRowCount(0)
        self.horizontalLayoutWidget = QtWidgets.QWidget(self)
        self.horizontalLayoutWidget.setGeometry(QtCore.QRect(30, 20, 691, 41))
        self.horizontalLayoutWidget.setObjectName("horizontalLayoutWidget")
        self.horizontalLayout = QtWidgets.QHBoxLayout(self.horizontalLayoutWidget)
        self.horizontalLayout.setContentsMargins(0, 0, 0, 0)
        self.horizontalLayout.setObjectName("horizontalLayout")
        self.btnAdd = QtWidgets.QPushButton(self.horizontalLayoutWidget)
        self.btnAdd.setObjectName("btnAdd")
        self.horizontalLayout.addWidget(self.btnAdd)
        self.btnAdd.clicked.connect(self.btnAddClicked)
        self.btnDel = QtWidgets.QPushButton(self.horizontalLayoutWidget)
        self.btnDel.setObjectName("btnDel")
        self.horizontalLayout.addWidget(self.btnDel)
        self.btnDel.clicked.connect(self.btnDelClicked)
        self.btnClear = QtWidgets.QPushButton(self.horizontalLayoutWidget)
        self.btnClear.setObjectName("btnClear")
        self.horizontalLayout.addWidget(self.btnClear)
        self.btnClear.clicked.connect(self.btnClearClicked)
        self.btnSave = QtWidgets.QPushButton(self)
        self.btnSave.setGeometry(QtCore.QRect(490, 340, 112, 34))
        self.btnSave.setObjectName("btnSave")
        self.btnSave.clicked.connect(self.btnSaveClicked)
        self.btnCancel = QtWidgets.QPushButton(self)
        self.btnCancel.setGeometry(QtCore.QRect(610, 340, 112, 34))
        self.btnCancel.setObjectName("btnCancel")
        self.btnCancel.clicked.connect(self.btnCancelClicked)
        self.retranslateUi()
        QtCore.QMetaObject.connectSlotsByName(self)

        self.makeTable()

    def retranslateUi(self):
        _translate = QtCore.QCoreApplication.translate
        self.setWindowTitle(_translate("Dialog", "TAG/ID ??????"))
        self.btnAdd.setText(_translate("Dialog", "?????? ??????"))
        self.btnDel.setText(_translate("Dialog", "?????? ??????"))
        self.btnClear.setText(_translate("Dialog", "?????? ??????"))
        self.btnSave.setText(_translate("Dialog", "??????"))
        self.btnCancel.setText(_translate("Dialog", "??????"))

    def btnSaveClicked(self):
        rowCount = self.tableWidget.rowCount()
        colCount = self.tableWidget.columnCount()
        hashtags = []

        for row in range(rowCount):
            label = "??????%d" % (row + 1)
            if self.tableWidget.item(row, 0):
                label = self.tableWidget.item(row, 0).text()

            hashtags.append([])
            hashtags[row].append(label)
            for col in range(1, colCount):
                val = 'None'
                if self.tableWidget.item(row, col):
                    val = self.tableWidget.item(row, col).text()

                hashtags[row].append(val)

        with open('db/tbH.p', 'wb') as file:
            pickle.dump(hashtags, file)

        self.close()

    def btnCancelClicked(self):
        self.close()

    def btnAddClicked(self):
        rowCount = self.tableWidget.rowCount()
        self.tableWidget.setRowCount(rowCount + 1)

        # add default text
        txtGroup = "??????%d" % (rowCount + 1)
        txtItem = QtWidgets.QTableWidgetItem(txtGroup)
        self.tableWidget.setItem(rowCount, 0, txtItem)

    def btnDelClicked(self):
        selectedRow = self.tableWidget.currentIndex().row()
        self.tableWidget.removeRow(selectedRow)

    def btnClearClicked(self):
        rowCount = self.tableWidget.rowCount()
        for row in reversed(range(rowCount)):
            self.tableWidget.removeRow(row)

    def makeTable(self):
        # single selection mode
        self.tableWidget.setSelectionMode(1)

        # set rows, columns
        self.tableWidget.setColumnCount(11)
        self.tableWidget.setRowCount(1)

        # set column header
        self.tableWidget.setHorizontalHeaderLabels(['?????????', '?????????1', '?????????2',
                                                    '?????????3', '?????????4', '?????????5',
                                                    '?????????6', '?????????7', '?????????8',
                                                    '?????????9', '?????????10'])
        self.tableWidget.horizontalHeaderItem(0).setToolTip('?????????...')
        self.tableWidget.setColumnWidth(0, 120)
        for index in range(1, 11):
            self.tableWidget.setColumnWidth(index, 90)

        if os.path.isfile('db/tbH.p'):
            with open('db/tbH.p', 'rb') as file:
                hashtags = pickle.load(file)
                self.tableWidget.setRowCount(len(hashtags))
            for row in range(0, len(hashtags)):
                for col in range(0, len(hashtags[row])):
                    item = QtWidgets.QTableWidgetItem(hashtags[row][col])
                    self.tableWidget.setItem(row, col, item)
        else:
            txtItem = QtWidgets.QTableWidgetItem("None")
            self.tableWidget.setItem(0, 0, txtItem)

class CommentDialog(QtWidgets.QDialog):
    def __init__(self):
        super().__init__()
        self.setupUi()

    def setupUi(self):
        self.setObjectName("Dialog")
        self.resize(746, 391)
        self.tableWidget = QtWidgets.QTableWidget(self)
        self.tableWidget.setGeometry(QtCore.QRect(30, 80, 691, 241))
        self.tableWidget.setObjectName("tableWidget")
        self.tableWidget.setColumnCount(0)
        self.tableWidget.setRowCount(0)
        self.horizontalLayoutWidget = QtWidgets.QWidget(self)
        self.horizontalLayoutWidget.setGeometry(QtCore.QRect(30, 20, 691, 41))
        self.horizontalLayoutWidget.setObjectName("horizontalLayoutWidget")
        self.horizontalLayout = QtWidgets.QHBoxLayout(self.horizontalLayoutWidget)
        self.horizontalLayout.setContentsMargins(0, 0, 0, 0)
        self.horizontalLayout.setObjectName("horizontalLayout")
        self.btnAdd = QtWidgets.QPushButton(self.horizontalLayoutWidget)
        self.btnAdd.setObjectName("btnAdd")
        self.horizontalLayout.addWidget(self.btnAdd)
        self.btnAdd.clicked.connect(self.btnAddClicked)
        self.btnDel = QtWidgets.QPushButton(self.horizontalLayoutWidget)
        self.btnDel.setObjectName("btnDel")
        self.horizontalLayout.addWidget(self.btnDel)
        self.btnDel.clicked.connect(self.btnDelClicked)
        self.btnClear = QtWidgets.QPushButton(self.horizontalLayoutWidget)
        self.btnClear.setObjectName("btnClear")
        self.horizontalLayout.addWidget(self.btnClear)
        self.btnClear.clicked.connect(self.btnClearClicked)
        self.btnSave = QtWidgets.QPushButton(self)
        self.btnSave.setGeometry(QtCore.QRect(490, 340, 112, 34))
        self.btnSave.setObjectName("btnSave")
        self.btnSave.clicked.connect(self.btnSaveClicked)
        self.btnCancel = QtWidgets.QPushButton(self)
        self.btnCancel.setGeometry(QtCore.QRect(610, 340, 112, 34))
        self.btnCancel.setObjectName("btnCancel")
        self.btnCancel.clicked.connect(self.btnCancelClicked)
        self.retranslateUi()
        QtCore.QMetaObject.connectSlotsByName(self)

        self.makeTable()

    def retranslateUi(self):
        _translate = QtCore.QCoreApplication.translate
        self.setWindowTitle(_translate("Dialog", "?????? ??????"))
        self.btnAdd.setText(_translate("Dialog", "?????? ??????"))
        self.btnDel.setText(_translate("Dialog", "?????? ??????"))
        self.btnClear.setText(_translate("Dialog", "?????? ??????"))
        self.btnSave.setText(_translate("Dialog", "??????"))
        self.btnCancel.setText(_translate("Dialog", "??????"))

    def btnSaveClicked(self):
        rowCount = self.tableWidget.rowCount()
        colCount = self.tableWidget.columnCount()
        comments = []

        for row in range(rowCount):
            label = "??????%d" % (row + 1)
            if self.tableWidget.item(row, 0):
                label = self.tableWidget.item(row, 0).text()
            comments.append([])
            comments[row].append(label)
            for col in range(1, colCount):
                val = 'None'
                if self.tableWidget.item(row, col):
                    val = self.tableWidget.item(row, col).text()
                comments[row].append(val)

        with open('db/tbC.p', 'wb') as file:
            pickle.dump(comments, file)

        self.close()

    def btnCancelClicked(self):
        self.close()

    def btnAddClicked(self):
        rowCount = self.tableWidget.rowCount()
        self.tableWidget.setRowCount(rowCount + 1)

        # add default text
        txtGroup = "??????%d" % (rowCount + 1)
        txtItem = QtWidgets.QTableWidgetItem(txtGroup)
        self.tableWidget.setItem(rowCount, 0, txtItem)

    def btnDelClicked(self):
        selectedRow = self.tableWidget.currentIndex().row()
        self.tableWidget.removeRow(selectedRow)

    def btnClearClicked(self):
        rowCount = self.tableWidget.rowCount()
        for row in reversed(range(rowCount)):
            self.tableWidget.removeRow(row)

    def makeTable(self):
        # single selection mode
        self.tableWidget.setSelectionMode(1)

        # set rows, columns
        self.tableWidget.setColumnCount(11)
        self.tableWidget.setRowCount(1)

        # set column header
        self.tableWidget.setHorizontalHeaderLabels(['?????? ?????????', '??????1', '??????2',
                                                    '??????3', '??????4', '??????5',
                                                    '??????6', '??????7', '??????8',
                                                    '??????9', '??????10'])
        self.tableWidget.horizontalHeaderItem(0).setToolTip('?????? ?????????...')
        self.tableWidget.setColumnWidth(0, 120)
        for index in range(1, 11):
            self.tableWidget.setColumnWidth(index, 90)

        if os.path.isfile('db/tbC.p'):
            with open('db/tbC.p', 'rb') as file:
                comments = pickle.load(file)
            self.tableWidget.setRowCount(len(comments))
            for row in range(0, len(comments)):
                for col in range(0, len(comments[row])):
                    item = QtWidgets.QTableWidgetItem(comments[row][col])
                    self.tableWidget.setItem(row, col, item)
        else:
            txtItem = QtWidgets.QTableWidgetItem("None")
            self.tableWidget.setItem(0, 0, txtItem)

class FilterDialog(QtWidgets.QDialog):
    def __init__(self):
        super().__init__()
        self.setupUI()

    def setupUI(self):
        self.setObjectName("Dialog")
        self.resize(746, 391)
        self.tableWidget = QtWidgets.QTableWidget(self)
        self.tableWidget.setGeometry(QtCore.QRect(30, 80, 691, 241))
        self.tableWidget.setObjectName("tableWidget")
        self.tableWidget.setColumnCount(0)
        self.tableWidget.setRowCount(0)
        self.horizontalLayoutWidget = QtWidgets.QWidget(self)
        self.horizontalLayoutWidget.setGeometry(QtCore.QRect(30, 20, 691, 41))
        self.horizontalLayoutWidget.setObjectName("horizontalLayoutWidget")
        self.horizontalLayout = QtWidgets.QHBoxLayout(self.horizontalLayoutWidget)
        self.horizontalLayout.setContentsMargins(0, 0, 0, 0)
        self.horizontalLayout.setObjectName("horizontalLayout")
        self.btnAdd = QtWidgets.QPushButton(self.horizontalLayoutWidget)
        self.btnAdd.setObjectName("btnAdd")
        self.horizontalLayout.addWidget(self.btnAdd)
        self.btnAdd.clicked.connect(self.btnAddClicked)
        self.btnDel = QtWidgets.QPushButton(self.horizontalLayoutWidget)
        self.btnDel.setObjectName("btnDel")
        self.horizontalLayout.addWidget(self.btnDel)
        self.btnDel.clicked.connect(self.btnDelClicked)
        self.btnClear = QtWidgets.QPushButton(self.horizontalLayoutWidget)
        self.btnClear.setObjectName("btnClear")
        self.horizontalLayout.addWidget(self.btnClear)
        self.btnClear.clicked.connect(self.btnClearClicked)
        self.btnSave = QtWidgets.QPushButton(self)
        self.btnSave.setGeometry(QtCore.QRect(490, 340, 112, 34))
        self.btnSave.setObjectName("btnSave")
        self.btnSave.clicked.connect(self.btnSaveClicked)
        self.btnCancel = QtWidgets.QPushButton(self)
        self.btnCancel.setGeometry(QtCore.QRect(610, 340, 112, 34))
        self.btnCancel.setObjectName("btnCancel")
        self.btnCancel.clicked.connect(self.btnCancelClicked)
        self.retranslateUi()
        QtCore.QMetaObject.connectSlotsByName(self)

        self.makeTable()

    def retranslateUi(self):
        _translate = QtCore.QCoreApplication.translate
        self.setWindowTitle(_translate("Dialog", "?????? ?????? ??????"))
        self.btnAdd.setText(_translate("Dialog", "?????? ??????"))
        self.btnDel.setText(_translate("Dialog", "?????? ??????"))
        self.btnClear.setText(_translate("Dialog", "?????? ??????"))
        self.btnSave.setText(_translate("Dialog", "??????"))
        self.btnCancel.setText(_translate("Dialog", "??????"))

    def btnSaveClicked(self):
        rowCount = self.tableWidget.rowCount()
        colCount = self.tableWidget.columnCount()
        filters = []

        for row in range(rowCount):
            label = "??????%d" % (row + 1)
            if self.tableWidget.item(row, 0):
                label = self.tableWidget.item(row, 0).text()

            filters.append([])
            filters[row].append(label)
            for col in range(1, colCount):
                val = 'None'
                if self.tableWidget.item(row, col):
                    val = self.tableWidget.item(row, col).text()

                filters[row].append(val)

        with open('db/tbF.p', 'wb') as file:
            pickle.dump(filters, file)

        self.close()

    def btnCancelClicked(self):
        self.close()

    def btnAddClicked(self):
        rowCount = self.tableWidget.rowCount()
        self.tableWidget.setRowCount(rowCount + 1)

        # add default text
        txtGroup = "??????%d" % (rowCount + 1)
        txtItem = QtWidgets.QTableWidgetItem(txtGroup)
        self.tableWidget.setItem(rowCount, 0, txtItem)

    def btnDelClicked(self):
        selectedRow = self.tableWidget.currentIndex().row()
        self.tableWidget.removeRow(selectedRow)

    def btnClearClicked(self):
        rowCount = self.tableWidget.rowCount()
        for row in reversed(range(rowCount)):
            self.tableWidget.removeRow(row)

    def makeTable(self):
        # single selection mode
        self.tableWidget.setSelectionMode(1)

        # set rows, columns
        self.tableWidget.setColumnCount(11)
        self.tableWidget.setRowCount(1)

        # set column header
        self.tableWidget.setHorizontalHeaderLabels(['?????? ?????????', '??????1', '??????2',
                                                    '??????3', '??????4', '??????5',
                                                    '??????6', '??????7', '??????8',
                                                    '??????9', '??????10'])
        self.tableWidget.horizontalHeaderItem(0).setToolTip('?????? ?????????...')
        self.tableWidget.setColumnWidth(0, 120)
        for index in range(1, 11):
            self.tableWidget.setColumnWidth(index, 90)

        if os.path.isfile('db/tbF.p'):
            with open('db/tbF.p', 'rb') as file:
                filters = pickle.load(file)
            self.tableWidget.setRowCount(len(filters))
            for row in range(0, len(filters)):
                for col in range(0, len(filters[row])):
                    item = QtWidgets.QTableWidgetItem(filters[row][col])
                    self.tableWidget.setItem(row, col, item)
        else:
            txtItem = QtWidgets.QTableWidgetItem("None")
            self.tableWidget.setItem(0, 0, txtItem)

class Ui_MainWindow(object):

    def setupUi(self, MainWindow):
        MainWindow.setObjectName("MainWindow")
        MainWindow.resize(920, 356)
        self.centralwidget = QtWidgets.QWidget(MainWindow)
        self.centralwidget.setObjectName("centralwidget")
        self.grpLog = QtWidgets.QGroupBox(self.centralwidget)
        self.grpLog.setGeometry(QtCore.QRect(10, 80, 891, 231))
        self.grpLog.setObjectName("grpLog")
        self.txtLog = QtWidgets.QTextBrowser(self.grpLog)
        self.txtLog.setGeometry(QtCore.QRect(20, 30, 851, 181))
        self.txtLog.setObjectName("txtLog")
        self.horizontalLayoutWidget_2 = QtWidgets.QWidget(self.centralwidget)
        self.horizontalLayoutWidget_2.setGeometry(QtCore.QRect(10, 10, 711, 61))
        self.horizontalLayoutWidget_2.setObjectName("horizontalLayoutWidget_2")
        self.horizontalLayout_2 = QtWidgets.QHBoxLayout(self.horizontalLayoutWidget_2)
        self.horizontalLayout_2.setSizeConstraint(QtWidgets.QLayout.SetDefaultConstraint)
        self.horizontalLayout_2.setContentsMargins(0, 0, 0, 0)
        self.horizontalLayout_2.setObjectName("horizontalLayout_2")
        self.btnSetHashtag = QtWidgets.QPushButton(self.horizontalLayoutWidget_2)
        self.btnSetHashtag.setObjectName("btnSetHashtag")
        self.horizontalLayout_2.addWidget(self.btnSetHashtag)
        self.btnSetComment = QtWidgets.QPushButton(self.horizontalLayoutWidget_2)
        self.btnSetComment.setObjectName("btnSetComment")
        self.horizontalLayout_2.addWidget(self.btnSetComment)
        self.btnSetFilter = QtWidgets.QPushButton(self.horizontalLayoutWidget_2)
        self.btnSetFilter.setObjectName("btnSetFilter")
        self.horizontalLayout_2.addWidget(self.btnSetFilter)
        # self.chkHeadless = QtWidgets.QCheckBox(self.horizontalLayoutWidget_2)
        # self.chkHeadless.setObjectName("chkHeadless")
        # self.horizontalLayout_2.addWidget(self.chkHeadless)
        # self.horizontalLayoutWidget = QtWidgets.QWidget(self.centralwidget)
        # self.horizontalLayoutWidget.setGeometry(QtCore.QRect(10, 90, 711, 51))
        # self.horizontalLayoutWidget.setObjectName("horizontalLayoutWidget")
        # self.horizontalLayout = QtWidgets.QHBoxLayout(self.horizontalLayoutWidget_2)
        # self.horizontalLayout.setContentsMargins(0, 0, 0, 0)
        # self.horizontalLayout.setObjectName("horizontalLayout")
        self.btnStart = QtWidgets.QPushButton(self.horizontalLayoutWidget_2)
        self.btnStart.setObjectName("btnStart")
        self.horizontalLayout_2.addWidget(self.btnStart)
        self.btnStop = QtWidgets.QPushButton(self.horizontalLayoutWidget_2)
        self.btnStop.setObjectName("btnStop")
        self.horizontalLayout_2.addWidget(self.btnStop)
        MainWindow.setCentralWidget(self.centralwidget)
        self.statusbar = QtWidgets.QStatusBar(MainWindow)
        self.statusbar.setObjectName("statusbar")
        MainWindow.setStatusBar(self.statusbar)

        self.btnSetHashtag.clicked.connect(self.btnSetHashtagClicked)
        self.btnSetHashtag.setIcon(QtGui.QIcon('icon/hashtag.png'))
        self.btnSetComment.clicked.connect(self.btnSetCommentClicked)
        self.btnSetComment.setIcon(QtGui.QIcon('icon/comments.svg'))
        self.btnSetFilter.clicked.connect(self.btnSetFilterClicked)
        self.btnSetFilter.setIcon(QtGui.QIcon('icon/like-ban.svg'))
        self.btnStart.clicked.connect(self.btnStartClicked)
        self.btnStart.setIcon(QtGui.QIcon('icon/start.png'))
        self.btnStop.clicked.connect(self.btnStopClicked)
        self.btnStop.setIcon(QtGui.QIcon('icon/pause.svg'))

        self.retranslateUi(MainWindow)
        QtCore.QMetaObject.connectSlotsByName(MainWindow)

        self.threads = []
        self.bRetryConnect = False
        self.bSetAccount = False
        self.bRunState = False

        printLog(self.txtLog, "???????????? ??????")
        self.btnStop.setEnabled(False)

        macAdr = get_mac_address()
        version_checker = StoppableThread(check_version_counter, (macAdr[0], PGM_VERSION, getBrowserDir()))
        version_checker.daemon = True
        version_checker.start()

        if not os.path.isdir('db'):
            os.makedirs('db')

    def retranslateUi(self, MainWindow):
        _translate = QtCore.QCoreApplication.translate
        wndTitle = "Follower Maker v%.1f (??????: ????????? ????????? ??????)" % PGM_VERSION
        MainWindow.setWindowTitle(_translate("MainWindow", wndTitle))
        MainWindow.setWindowIcon(QtGui.QIcon('icon/instagram.png'))
        self.grpLog.setTitle(_translate("MainWindow", "??????"))
        self.btnSetHashtag.setText(_translate("MainWindow", "TAG/ID ??????"))
        self.btnSetComment.setText(_translate("MainWindow", "?????? ??????"))
        self.btnSetFilter.setText(_translate("MainWindow", "?????? ??????"))
        self.btnStart.setText(_translate("MainWindow", "?????? ??????"))
        self.btnStop.setText(_translate("MainWindow", "?????? ??????"))
        # self.chkHeadless.setText(_translate("MainWindow", "??? ?????????"))


    def btnSetHashtagClicked(self):
        dlg = HashtagDialog()
        dlg.exec_()
        self.bSetAccount = False

    def btnSetCommentClicked(self):
        dlg = CommentDialog()
        dlg.exec_()
        self.bSetAccount = False

    def btnSetFilterClicked(self):
        dlg = FilterDialog()
        dlg.exec_()
        self.bSetAccount = False

    def btnStartClicked(self):
        self.btnSetHashtag.setEnabled(False)
        self.btnSetComment.setEnabled(False)
        self.btnSetFilter.setEnabled(False)
        self.btnStart.setEnabled(False)
        self.btnStop.setEnabled(True)
        self.bSetAccount = False
        dlg = AccountDialog()
        dlg.exec_()
        if dlg.bSetAccount:
            self.bSetAccount = True

        if self.bSetAccount:
            printLog(self.txtLog, "?????? ??????")
            accounts = getAccountData()
            hashtags = getHashtagData()

            if not accounts or not hashtags:
                return

            # call run.py
            if not self.bRetryConnect:
                SERVER_SOCK.bind(('', PORT))
                self.bRetryConnect = True
            SERVER_SOCK.listen(1)

            parser = threading.Thread(target=runInstaPy())
            parser.daemon = True
            parser.start()

            self.connectionSock, self.addr = SERVER_SOCK.accept()
            printLog(self.txtLog, "[Server] ?????? ??????")

            # if self.chkHeadless.isChecked():
            #     self.connectionSock.send('True'.encode('utf-8'))
            # else:
            self.connectionSock.send('False'.encode('utf-8'))

            receiver = StoppableThread(receive, (self.txtLog, self.connectionSock,))
            receiver.daemon = True
            receiver.start()
            self.bRunState = True


    def btnStopClicked(self):
        self.btnSetHashtag.setEnabled(True)
        self.btnSetComment.setEnabled(True)
        self.btnSetFilter.setEnabled(True)
        self.btnStart.setEnabled(True)
        self.btnStop.setEnabled(False)
        if self.bRunState:
            printLog(self.txtLog, "?????? ??????")
            self.connectionSock.send('Terminate'.encode('utf-8'))
            self.bRunState = False
            # chromeKiller = threading.Thread(target=runChromeKiller())
            # chromeKiller.start()

    def btnNoticeClicked(self):
        bResult, errCode, errMsg = get_notification(getBrowserDir())
        if bResult:
            printLog(None, errMsg)




if __name__ == "__main__":
    import sys
    app = QtWidgets.QApplication(sys.argv)
    MainWindow = QtWidgets.QMainWindow()
    ui = Ui_MainWindow()
    copyBrower()
    macAdr = get_mac_address()
    bResult, errCode, errMsg = check_version(macAdr[0], PGM_VERSION, getBrowserDir())
    # bResult = True
    # errCode = ERROR_NONE
    # errMsg = 'Debug Mode'
    printLog(None, errMsg)
    if bResult:
        ui.setupUi(MainWindow)
        MainWindow.show()

    else:
        if errCode == ERROR_UNIDENTIFIED_USER:
            msg = ctypes.windll.user32.MessageBoxW(None, "???????????? ?????? ????????? ???????????????????", "Follow Maker Noti", 4)
            if msg == 6:
                bResult, errCode, errMsg = apply_use(macAdr[0], getBrowserDir())
                printLog(None, errMsg)

        elif errCode == ERROR_OLD_VERSION:
            msg = ctypes.windll.user32.MessageBoxW(None, "??????????????? ???????????? ???????????????????", "Follow Maker Noti", 4)
            if msg == 6:
                bResult, errCode, errMsg = downlaod_updatefile(getBrowserDir())
                if bResult:
                    printLog(None, "??????????????? ?????? ??????????????? ???????????????.")
                    installer = threading.Thread(target=runInstaller())
                    installer.start()
                    sys.exit()
                else:
                    printLog(None, errMsg)

            ui.setupUi(MainWindow)
            MainWindow.show()

    sys.exit(app.exec_())

