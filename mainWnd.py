import random
import os, pickle
from PyQt5 import QtCore, QtGui, QtWidgets
import threading, requests, time
import instapy
import logging.handlers



# run instapy function..
def startActivity(row,
                  accounts,
                  hashtags,
                  comments,
                  filters,
                  txtLogger=None,
                  bHeadless=False):
    id = str(accounts[row][2])
    pwd = str(accounts[row][3])
    session = instapy.InstaPy(username=id, password=pwd, headless_browser=bHeadless,
                              show_logs=True, txt_logger=txtLogger)
    session.login()
    try:
        session.set_quota_supervisor(enabled=True,
                                     sleep_after=["likes", "comments", "follows", "unfollows",
                                                  "server_calls_h"], sleepyhead=True, stochastic_flow=True,
                                     notify_me=True,
                                     peak_likes=(120, 1020),
                                     peak_comments=(120, 1020),
                                     peak_follows=(120, 1020),
                                     peak_unfollows=(120, 1020),
                                     peak_server_calls=(None, 4700))

        valComments = []
        for col in range(1, 11):
            comment = comments[int(accounts[row][5])][col]
            if not comment == 'None':
                valComments.append(comment)

        if valComments:
            session.set_do_comment(enabled=True, percentage=25)
            session.set_comments(valComments)

        valFilters = []
        for col in range(1, 11):
            filter = filters[int(accounts[row][6])][col]
            # print(hashtag)
            if not filter == 'None':
                valFilters.append(filter)

        if valFilters:
            session.set_dont_like(tags=valFilters)

        valHashtags = []
        for col in range(1, 11):
            hashtag = hashtags[int(accounts[row][4])][col]
            # print(hashtag)
            if not hashtag == 'None':
                valHashtags.append(hashtag)

        if valHashtags:
            session.set_do_follow(enabled=True, percentage=50)
            session.like_by_tags(tags=valHashtags, amount=int(accounts[row][8]))
            printLog(txtLogger, "좋아요/댓글/팔로우 완료")
            s = "좋아요: %d개, 댓글: %d개, 팔로우: %d개" % (session.liked_img, session.commented, session.followed)
            printLog(txtLogger, s)

        instapy.InstaPy.end_sub(session)

    except:
        raise

def printLog(txtView, log):
    now = time.localtime()
    s = "INFO [%04d-%02d-%02d %02d:%02d:%02d] " % (now.tm_year, now.tm_mon, now.tm_mday, now.tm_hour, now.tm_min, now.tm_sec)
    txtView.append(str(s + log))

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
        self.setWindowTitle(_translate("Dialog", "태그 설정"))
        self.btnAdd.setText(_translate("Dialog", "그룹 추가"))
        self.btnDel.setText(_translate("Dialog", "선택 삭제"))
        self.btnClear.setText(_translate("Dialog", "모두 삭제"))
        self.btnSave.setText(_translate("Dialog", "저장"))
        self.btnCancel.setText(_translate("Dialog", "취소"))

    def btnSaveClicked(self):
        rowCount = self.tableWidget.rowCount()
        colCount = self.tableWidget.columnCount()
        hashtags = []

        for row in range(rowCount):
            label = "그룹%d" % (row + 1)
            if self.tableWidget.item(row, 0):
                label = self.tableWidget.item(row, 0).text()

            hashtags.append([])
            hashtags[row].append(label)
            for col in range(1, colCount):
                val = 'None'
                if self.tableWidget.item(row, col):
                    val = self.tableWidget.item(row, col).text()

                hashtags[row].append(val)

        with open('tbH.p', 'wb') as file:
            pickle.dump(hashtags, file)

        self.close()

    def btnCancelClicked(self):
        self.close()

    def btnAddClicked(self):
        rowCount = self.tableWidget.rowCount()
        self.tableWidget.setRowCount(rowCount + 1)

        # add default text
        txtGroup = "그룹%d" % (rowCount + 1)
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
        self.tableWidget.setHorizontalHeaderLabels(['태그 그룹명', '태그1', '태그2',
                                                    '태그3', '태그4', '태그5',
                                                    '태그6', '태그7', '태그8',
                                                    '태그9', '태그10'])
        self.tableWidget.horizontalHeaderItem(0).setToolTip('태그 그룹명...')
        self.tableWidget.setColumnWidth(0, 120)
        for index in range(1, 11):
            self.tableWidget.setColumnWidth(index, 90)

        if os.path.isfile('tbH.p'):
            with open('tbH.p', 'rb') as file:
                hashtags = pickle.load(file)
                self.tableWidget.setRowCount(len(hashtags))
            for row in range(0, len(hashtags)):
                for col in range(0, len(hashtags[row])):
                    item = QtWidgets.QTableWidgetItem(hashtags[row][col])
                    self.tableWidget.setItem(row, col, item)
        else:
            txtItem = QtWidgets.QTableWidgetItem("그룹1")
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
        self.setWindowTitle(_translate("Dialog", "댓글 설정"))
        self.btnAdd.setText(_translate("Dialog", "그룹 추가"))
        self.btnDel.setText(_translate("Dialog", "선택 삭제"))
        self.btnClear.setText(_translate("Dialog", "모두 삭제"))
        self.btnSave.setText(_translate("Dialog", "저장"))
        self.btnCancel.setText(_translate("Dialog", "취소"))

    def btnSaveClicked(self):
        rowCount = self.tableWidget.rowCount()
        colCount = self.tableWidget.columnCount()
        comments = []

        for row in range(rowCount):
            label = "그룹%d" % (row + 1)
            if self.tableWidget.item(row, 0):
                label = self.tableWidget.item(row, 0).text()
            comments.append([])
            comments[row].append(label)
            for col in range(1, colCount):
                val = 'None'
                if self.tableWidget.item(row, col):
                    val = self.tableWidget.item(row, col).text()
                comments[row].append(val)

        with open('tbC.p', 'wb') as file:
            pickle.dump(comments, file)

        self.close()

    def btnCancelClicked(self):
        self.close()

    def btnAddClicked(self):
        rowCount = self.tableWidget.rowCount()
        self.tableWidget.setRowCount(rowCount + 1)

        # add default text
        txtGroup = "그룹%d" % (rowCount + 1)
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
        self.tableWidget.setHorizontalHeaderLabels(['댓글 그룹명', '댓글1', '댓글2',
                                                    '댓글3', '댓글4', '댓글5',
                                                    '댓글6', '댓글7', '댓글8',
                                                    '댓글9', '댓글10'])
        self.tableWidget.horizontalHeaderItem(0).setToolTip('태그 그룹명...')
        self.tableWidget.setColumnWidth(0, 120)
        for index in range(1, 11):
            self.tableWidget.setColumnWidth(index, 90)

        if os.path.isfile('tbC.p'):
            with open('tbC.p', 'rb') as file:
                comments = pickle.load(file)
            self.tableWidget.setRowCount(len(comments))
            for row in range(0, len(comments)):
                for col in range(0, len(comments[row])):
                    item = QtWidgets.QTableWidgetItem(comments[row][col])
                    self.tableWidget.setItem(row, col, item)
        else:
            txtItem = QtWidgets.QTableWidgetItem("그룹1")
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
        self.setWindowTitle(_translate("Dialog", "제외 단어 설정"))
        self.btnAdd.setText(_translate("Dialog", "제외 추가"))
        self.btnDel.setText(_translate("Dialog", "선택 삭제"))
        self.btnClear.setText(_translate("Dialog", "모두 삭제"))
        self.btnSave.setText(_translate("Dialog", "저장"))
        self.btnCancel.setText(_translate("Dialog", "닫기"))

    def btnSaveClicked(self):
        rowCount = self.tableWidget.rowCount()
        colCount = self.tableWidget.columnCount()
        filters = []

        for row in range(rowCount):
            label = "그룹%d" % (row + 1)
            if self.tableWidget.item(row, 0):
                label = self.tableWidget.item(row, 0).text()

            filters.append([])
            filters[row].append(label)
            for col in range(1, colCount):
                val = 'None'
                if self.tableWidget.item(row, col):
                    val = self.tableWidget.item(row, col).text()

                filters[row].append(val)

        with open('tbF.p', 'wb') as file:
            pickle.dump(filters, file)

        self.close()

    def btnCancelClicked(self):
        self.close()

    def btnAddClicked(self):
        rowCount = self.tableWidget.rowCount()
        self.tableWidget.setRowCount(rowCount + 1)

        # add default text
        txtGroup = "그룹%d" % (rowCount + 1)
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
        self.tableWidget.setHorizontalHeaderLabels(['제외 그룹명', '제외1', '제외2',
                                                    '제외3', '제외4', '제외5',
                                                    '제외6', '제외7', '제외8',
                                                    '제외9', '제외10'])
        self.tableWidget.horizontalHeaderItem(0).setToolTip('제외 그룹명...')
        self.tableWidget.setColumnWidth(0, 120)
        for index in range(1, 11):
            self.tableWidget.setColumnWidth(index, 90)

        if os.path.isfile('tbF.p'):
            with open('tbF.p', 'rb') as file:
                filters = pickle.load(file)
            self.tableWidget.setRowCount(len(filters))
            for row in range(0, len(filters)):
                for col in range(0, len(filters[row])):
                    item = QtWidgets.QTableWidgetItem(filters[row][col])
                    self.tableWidget.setItem(row, col, item)
        else:
            txtItem = QtWidgets.QTableWidgetItem("그룹1")
            self.tableWidget.setItem(0, 0, txtItem)

class Ui_MainWindow(object):

    def setupUi(self, MainWindow):
        MainWindow.setObjectName("MainWindow")
        MainWindow.resize(1131, 821)
        self.centralwidget = QtWidgets.QWidget(MainWindow)
        self.centralwidget.setObjectName("centralwidget")
        self.grpAccount = QtWidgets.QGroupBox(self.centralwidget)
        self.grpAccount.setGeometry(QtCore.QRect(10, 110, 1111, 401))
        self.grpAccount.setObjectName("grpAccount")
        self.horizontalLayoutWidget = QtWidgets.QWidget(self.grpAccount)
        self.horizontalLayoutWidget.setGeometry(QtCore.QRect(20, 40, 738, 51))
        self.horizontalLayoutWidget.setObjectName("horizontalLayoutWidget")
        self.horizontalLayout = QtWidgets.QHBoxLayout(self.horizontalLayoutWidget)
        self.horizontalLayout.setContentsMargins(0, 0, 0, 0)
        self.horizontalLayout.setObjectName("horizontalLayout")
        self.btnAddAccount = QtWidgets.QPushButton(self.horizontalLayoutWidget)
        self.btnAddAccount.setObjectName("btnAddAccount")
        self.btnAddAccount.clicked.connect(self.btnAddAccountClicked)
        self.horizontalLayout.addWidget(self.btnAddAccount)
        self.btnDelAccount = QtWidgets.QPushButton(self.horizontalLayoutWidget)
        self.btnDelAccount.setObjectName("btnDelAccount")
        self.horizontalLayout.addWidget(self.btnDelAccount)
        self.btnDelAccount.clicked.connect(self.btnDelAccountClicked)
        self.btnClearAccount = QtWidgets.QPushButton(self.horizontalLayoutWidget)
        self.btnClearAccount.setObjectName("btnClearAccount")
        self.horizontalLayout.addWidget(self.btnClearAccount)
        self.btnClearAccount.clicked.connect(self.btnClearAccountClicked)
        self.btnSetAccount = QtWidgets.QPushButton(self.horizontalLayoutWidget)
        self.btnSetAccount.setObjectName("btnSetAccount")
        self.horizontalLayout.addWidget(self.btnSetAccount)
        self.btnSetAccount.clicked.connect(self.btnSetAccountClicked)
        self.btnDelAccLog = QtWidgets.QPushButton(self.horizontalLayoutWidget)
        self.btnDelAccLog.setObjectName("btnDelAccLog")
        self.horizontalLayout.addWidget(self.btnDelAccLog)
        self.tableAccount = QtWidgets.QTableWidget(self.grpAccount)
        self.tableAccount.setGeometry(QtCore.QRect(20, 100, 1071, 281))
        self.tableAccount.setObjectName("tableAccount")
        self.grpLog = QtWidgets.QGroupBox(self.centralwidget)
        self.grpLog.setGeometry(QtCore.QRect(10, 520, 1111, 231))
        self.grpLog.setObjectName("grpLog")
        self.txtLog = QtWidgets.QTextBrowser(self.grpLog)
        self.txtLog.setGeometry(QtCore.QRect(20, 40, 1071, 171))
        self.txtLog.setObjectName("txtLog")
        self.horizontalLayoutWidget_2 = QtWidgets.QWidget(self.centralwidget)
        self.horizontalLayoutWidget_2.setGeometry(QtCore.QRect(10, 10, 991, 80))
        self.horizontalLayoutWidget_2.setObjectName("horizontalLayoutWidget_2")
        self.horizontalLayout_2 = QtWidgets.QHBoxLayout(self.horizontalLayoutWidget_2)
        self.horizontalLayout_2.setSizeConstraint(QtWidgets.QLayout.SetDefaultConstraint)
        self.horizontalLayout_2.setContentsMargins(0, 0, 0, 0)
        self.horizontalLayout_2.setObjectName("horizontalLayout_2")
        self.btnNotice = QtWidgets.QToolButton(self.horizontalLayoutWidget_2)
        self.btnNotice.setObjectName("btnNotice")
        self.btnNotice.setIcon(QtGui.QIcon('icon/info.png'))
        self.btnNotice.setFixedSize(100, 70)
        self.btnNotice.clicked.connect(self.btnNoticeClicked)
        self.horizontalLayout_2.addWidget(self.btnNotice)
        self.btnSetHashtag = QtWidgets.QToolButton(self.horizontalLayoutWidget_2)
        self.btnSetHashtag.setObjectName("btnSetHashtag")
        self.btnSetHashtag.clicked.connect(self.btnSetHashtagClicked)
        self.btnSetHashtag.setIcon(QtGui.QIcon('icon/hashtag.png'))
        self.btnSetHashtag.setFixedSize(100, 70)
        self.horizontalLayout_2.addWidget(self.btnSetHashtag)
        self.btnSetComment = QtWidgets.QToolButton(self.horizontalLayoutWidget_2)
        self.btnSetComment.setObjectName("btnSetComment")
        self.btnSetComment.clicked.connect(self.btnSetCommentClicked)
        self.btnSetComment.setIcon(QtGui.QIcon('icon/comments.svg'))
        self.btnSetComment.setFixedSize(100, 70)
        self.horizontalLayout_2.addWidget(self.btnSetComment)
        self.btnSetFilter = QtWidgets.QToolButton(self.horizontalLayoutWidget_2)
        self.btnSetFilter.setObjectName("btnFilter")
        self.btnSetFilter.clicked.connect(self.btnSetFilterClicked)
        self.btnSetFilter.setIcon(QtGui.QIcon('icon/like-ban.svg'))
        self.btnSetFilter.setFixedSize(100, 70)
        self.horizontalLayout_2.addWidget(self.btnSetFilter)
        self.btnStart = QtWidgets.QToolButton(self.horizontalLayoutWidget_2)
        self.btnStart.setObjectName("btnSetFollowing")
        self.btnStart.clicked.connect(self.btnStartClicked)
        self.btnStart.setIcon(QtGui.QIcon('icon/start.png'))
        self.btnStart.setFixedSize(100, 70)
        self.horizontalLayout_2.addWidget(self.btnStart)
        self.btnStop = QtWidgets.QToolButton(self.horizontalLayoutWidget_2)
        self.btnStop.setObjectName("btnSetFollowing")
        self.btnStop.clicked.connect(self.btnStopClicked)
        self.btnStop.setIcon(QtGui.QIcon('icon/pause.svg'))
        self.btnStop.setFixedSize(100, 70)
        self.horizontalLayout_2.addWidget(self.btnStop)
        self.chkHeadless = QtWidgets.QCheckBox(self.horizontalLayoutWidget_2)
        self.chkHeadless.setObjectName("chkHeadless")
        self.horizontalLayout_2.addWidget(self.chkHeadless)

        MainWindow.setCentralWidget(self.centralwidget)
        self.menubar = QtWidgets.QMenuBar(MainWindow)
        self.menubar.setGeometry(QtCore.QRect(0, 0, 1131, 31))
        self.menubar.setObjectName("menubar")
        MainWindow.setMenuBar(self.menubar)
        self.statusbar = QtWidgets.QStatusBar(MainWindow)
        self.statusbar.setObjectName("statusbar")
        MainWindow.setStatusBar(self.statusbar)
        self.actionSet_Hashtag_Group = QtWidgets.QAction(MainWindow)
        self.actionSet_Hashtag_Group.setObjectName("actionSet_Hashtag_Group")
        self.actionSet_Comment_Group = QtWidgets.QAction(MainWindow)
        self.actionSet_Comment_Group.setObjectName("actionSet_Comment_Group")

        self.retranslateUi(MainWindow)
        QtCore.QMetaObject.connectSlotsByName(MainWindow)

        self.makeTable()
        self.threads = []
        printLog(self.txtLog, "프로그램 시작")

    def retranslateUi(self, MainWindow):
        _translate = QtCore.QCoreApplication.translate
        MainWindow.setWindowTitle(_translate("MainWindow", "Follower Maker v0.2"))
        MainWindow.setWindowIcon(QtGui.QIcon('icon/instagram.png'))
        self.grpAccount.setTitle(_translate("MainWindow", "계정 관리"))
        self.btnAddAccount.setText(_translate("MainWindow", "계정 추가"))
        self.btnDelAccount.setText(_translate("MainWindow", "선택 삭제"))
        self.btnClearAccount.setText(_translate("MainWindow", "모두 삭제"))
        self.btnDelAccLog.setText(_translate("MainWindow", "계정 로그 삭제"))
        self.chkHeadless.setText(_translate("MainWindow", "크롬창 숨김"))
        self.grpLog.setTitle(_translate("MainWindow", "로그"))
        self.btnNotice.setText(_translate("MainWindow", "공지 사항"))
        self.btnSetAccount.setText(_translate("MainWindow", "계정 설정 저장"))
        self.btnSetHashtag.setText(_translate("MainWindow", "태그 설정"))
        self.btnSetComment.setText(_translate("MainWindow", "댓글 설정"))
        self.btnSetFilter.setText(_translate("MainWindow", "제외 설정"))
        self.btnStart.setText(_translate("MainWindow", "작업 시작"))
        self.btnStop.setText(_translate("MainWindow", "작업 중지"))
        self.actionSet_Hashtag_Group.setText(_translate("MainWindow", "Set Hashtag Group"))
        self.actionSet_Comment_Group.setText(_translate("MainWindow", "Set Comment Group"))

    def makeTable(self):
        # single selection mode
        self.tableAccount.setSelectionMode(1)

        # set rows, columns
        self.tableAccount.setColumnCount(10)
        self.tableAccount.setRowCount(1)

        # set column header
        self.tableAccount.setHorizontalHeaderLabels(['사용 여부', '사이트', '아이디',
                                                     '비밀번호', '해시태그', '댓글',
                                                     '제외 단어', '총 반복 수', '태그 당 횟수',
                                                     '상태'])
        self.tableAccount.horizontalHeaderItem(0).setToolTip('사용여부...')
        self.tableAccount.setColumnWidth(0, 90)
        for index in range(1, 9):
            self.tableAccount.setColumnWidth(index, 120)
        self.tableAccount.setColumnWidth(9, 300)

        accounts = None
        rowCount = 1
        if os.path.isfile('tbA.p'):
            with open('tbA.p', 'rb') as file:
                accounts = pickle.load(file)
                # print(accounts)
                rowCount = len(accounts)

        self.tableAccount.setRowCount(rowCount)

        for row in range(0, rowCount):
            # add check box
            chkUse = QtWidgets.QCheckBox()
            if accounts:
                chkUse.setChecked(accounts[row][0])
            self.tableAccount.setCellWidget(row, 0, chkUse)

            # add combo box
            cmbSite = QtWidgets.QComboBox()
            cmbSite.addItem('인스타그램')
            self.tableAccount.setCellWidget(row, 1, cmbSite)

            # set id
            txtId = QtWidgets.QTableWidgetItem()
            if accounts:
                txtId = QtWidgets.QTableWidgetItem(str(accounts[row][2]))
            self.tableAccount.setItem(row, 2, txtId)

            # set password star
            txtPw = QtWidgets.QLineEdit()
            txtPw.setEchoMode(QtWidgets.QLineEdit.Password)
            if accounts:
                txtPw.setText(str(accounts[row][3]))
            self.tableAccount.setCellWidget(row, 3, txtPw)

            cmbHashtag = QtWidgets.QComboBox()
            if os.path.isfile('tbH.p'):
                with open('tbH.p', 'rb') as file:
                    hashtags = pickle.load(file)
                for cnt in range(0, len(hashtags)):
                    cmbHashtag.addItem(hashtags[cnt][0])
            else:
                cmbHashtag.addItem('그룹1')
            if accounts:
                cmbHashtag.setCurrentIndex(int(accounts[row][4]))
            self.tableAccount.setCellWidget(row, 4, cmbHashtag)

            cmbComment = QtWidgets.QComboBox()
            if os.path.isfile('tbC.p'):
                with open('tbC.p', 'rb') as file:
                    comments = pickle.load(file)
                for cnt in range(0, len(comments)):
                    cmbComment.addItem(comments[cnt][0])
            else:
                cmbComment.addItem('그룹1')
            if accounts:
                cmbComment.setCurrentIndex(int(accounts[row][5]))
            self.tableAccount.setCellWidget(row, 5, cmbComment)

            cmbFilter = QtWidgets.QComboBox()
            if os.path.isfile('tbF.p'):
                with open('tbF.p', 'rb') as file:
                    filters = pickle.load(file)
                for cnt in range(0, len(filters)):
                    cmbFilter.addItem(filters[cnt][0])
            else:
                cmbFilter.addItem('그룹1')
            if accounts:
                cmbFilter.setCurrentIndex(int(accounts[row][6]))
            self.tableAccount.setCellWidget(row, 6, cmbFilter)

            # add default text
            txtMaxLike = QtWidgets.QTableWidgetItem('1000')
            if accounts:
                txtMaxLike = QtWidgets.QTableWidgetItem(accounts[row][7])
            self.tableAccount.setItem(row, 7, txtMaxLike)

            txtTagShift = QtWidgets.QTableWidgetItem('50')
            if accounts:
                txtMaxLike = QtWidgets.QTableWidgetItem(accounts[row][8])
            self.tableAccount.setItem(row, 8, txtTagShift)

            txtStatus = QtWidgets.QTableWidgetItem('오늘: 좋아요[0] / 팔로우[0] / 댓글[0]')
            if accounts:
                txtMaxLike = QtWidgets.QTableWidgetItem(accounts[row][9])
            self.tableAccount.setItem(row, 9, txtStatus)

    def btnAddAccountClicked(self):
        rowCount = self.tableAccount.rowCount()
        self.tableAccount.setRowCount(rowCount + 1)

        # add check box
        chkUse = QtWidgets.QCheckBox()
        self.tableAccount.setCellWidget(rowCount, 0, chkUse)

        # add combo box
        cmbSite = QtWidgets.QComboBox()
        cmbSite.addItem('인스타그램')
        self.tableAccount.setCellWidget(rowCount, 1, cmbSite)

        # set id
        txtId = QtWidgets.QTableWidgetItem()
        self.tableAccount.setItem(rowCount, 2, txtId)

        # set password star
        txtPw = QtWidgets.QLineEdit()
        txtPw.setEchoMode(QtWidgets.QLineEdit.Password)
        self.tableAccount.setCellWidget(rowCount, 3, txtPw)

        cmbHashtag = QtWidgets.QComboBox()
        if os.path.isfile('tbH.p'):
            with open('tbH.p', 'rb') as file:
                hashtags = pickle.load(file)
            for row in range(0, len(hashtags)):
                cmbHashtag.addItem(hashtags[row][0])
        else:
            cmbHashtag.addItem('그룹1')
        self.tableAccount.setCellWidget(rowCount, 4, cmbHashtag)

        cmbComment = QtWidgets.QComboBox()
        if os.path.isfile('tbC.p'):
            with open('tbC.p', 'rb') as file:
                comments = pickle.load(file)
            for row in range(0, len(comments)):
                cmbComment.addItem(comments[row][0])
        else:
            cmbComment.addItem('그룹1')
        self.tableAccount.setCellWidget(rowCount, 5, cmbComment)

        cmbFilter = QtWidgets.QComboBox()
        if os.path.isfile('tbF.p'):
            with open('tbF.p', 'rb') as file:
                filters = pickle.load(file)
            for row in range(0, len(filters)):
                cmbFilter.addItem(filters[row][0])
        else:
            cmbFilter.addItem('그룹1')
        self.tableAccount.setCellWidget(rowCount, 6, cmbFilter)

        # add default text
        txtMaxLike = QtWidgets.QTableWidgetItem('1000')
        self.tableAccount.setItem(rowCount, 7, txtMaxLike)

        txtTagShift = QtWidgets.QTableWidgetItem('50')
        self.tableAccount.setItem(rowCount, 8, txtTagShift)

        txtStatus = QtWidgets.QTableWidgetItem('오늘: 좋아요[0] / 팔로우[0] / 댓글[0]')
        self.tableAccount.setItem(rowCount, 9, txtStatus)

    def btnDelAccountClicked(self):
        selectedRow = self.tableAccount.currentIndex().row()
        self.tableAccount.removeRow(selectedRow)

    def btnClearAccountClicked(self):
        rowCount = self.tableAccount.rowCount()
        for row in reversed(range(rowCount)):
            self.tableAccount.removeRow(row)

    def btnSetAccountClicked(self):
        accounts = self.getAccountData()
        # print(accounts)
        with open('tbA.p', 'wb') as file:
            pickle.dump(accounts, file)

    def btnSetHashtagClicked(self):
        dlg = HashtagDialog()
        dlg.exec_()
        self.loadPickleData()
        self.btnSetAccountClicked()

    def btnSetCommentClicked(self):
        dlg = CommentDialog()
        dlg.exec_()
        self.loadPickleData()
        self.btnSetAccountClicked()

    def btnSetFilterClicked(self):
        dlg = FilterDialog()
        dlg.exec_()
        self.loadPickleData()
        self.btnSetAccountClicked()

    def btnStartClicked(self):
        printLog(self.txtLog, "좋아요/댓글/팔로우 실행")
        self.btnSetAccountClicked()
        accounts = self.getAccountData()
        hashtags = self.getHashtagData()
        comments = self.getCommentData()
        filters = self.getFilterData()
        bHeadless = self.chkHeadless.isChecked()

        if not accounts or not hashtags or not comments or not filters:
            return

        self.threads.clear()
        self.threads = []
        for row in range(0, len(accounts)):
            if accounts[row][0]:
                # 로거 생성
                # logger = logging.getLogger(accounts[row][2])
                # logger.setLevel(logging.INFO)

                # logger_handler = GuiLogger()
                # logger_handler.edit = self.txtLog
                # logger_formatter = logging.Formatter(
                #     '%(levelname)s [%(asctime)s] [%(username)s]  %(message)s',
                #     datefmt='%Y-%m-%d %H:%M:%S')
                # logger_handler.setFormatter(logger_formatter)
                # logger.addHandler(logger_handler)
                # 데몬 쓰레드
                # t = threading.Thread(target=startActivity,
                #                       args=(row, accounts, hashtags, comments, filters, bHeadless,))
                t = StoppableThread(startActivity, (row, accounts, hashtags, comments, filters, self.txtLog, bHeadless,))
                self.threads.append(t)

        for t in self.threads:
            t.daemon = True
            t.start()

        # for t in threads:
        #     t.join()

         # print(accounts[row][2])

    def btnStopClicked(self):
        printLog(self.txtLog, "좋아요/댓글/팔로우 중지")
        for t in self.threads:
            t.stop()
            t.join()

    def btnNoticeClicked(self):
        printLog(self.txtLog, "공지사항")

    def loadPickleData(self):
        rowCount = self.tableAccount.rowCount()
        hashtags = self.getHashtagData()
        if hashtags:
            for cnt in range(0, rowCount):
                self.tableAccount.cellWidget(cnt, 4).clear()
                for row in range(0, len(hashtags)):
                    self.tableAccount.cellWidget(cnt, 4).addItem(hashtags[row][0])
        else:
            self.tableAccount.cellWidget(0, 4).addItem('그룹1')

        comments = self.getCommentData()
        if comments:
            for cnt in range(0, rowCount):
                self.tableAccount.cellWidget(cnt, 5).clear()
                for row in range(0, len(comments)):
                    self.tableAccount.cellWidget(cnt, 5).addItem(comments[row][0])
        else:
            self.tableAccount.cellWidget(0, 5).addItem('그룹1')

        filters = self.getFilterData()
        if filters:
            for cnt in range(0, rowCount):
                self.tableAccount.cellWidget(cnt, 6).clear()
                for row in range(0, len(filters)):
                    self.tableAccount.cellWidget(cnt, 6).addItem(filters[row][0])
        else:
            self.tableAccount.cellWidget(0, 6).addItem('그룹1')


    def getAccountData(self):
        rowCount = self.tableAccount.rowCount()
        accounts = []

        for row in range(rowCount):
            accounts.append([])
            chkBox = self.tableAccount.cellWidget(row, 0)
            if isinstance(chkBox, QtWidgets.QCheckBox):
                accounts[row].append(chkBox.isChecked())

            cmbBox1 = self.tableAccount.cellWidget(row, 1)
            if isinstance(cmbBox1, QtWidgets.QComboBox):
                index1 = "%d" % cmbBox1.currentIndex()
                accounts[row].append(index1)

            txtId = 'None'
            if self.tableAccount.item(row, 2):
                txtId = self.tableAccount.item(row, 2).text()
            accounts[row].append(txtId)

            cellPw = self.tableAccount.cellWidget(row, 3)
            if isinstance(cellPw, QtWidgets.QLineEdit):
                accounts[row].append(cellPw.text())

            for col in range(4, 7):
                cmbBox2 = self.tableAccount.cellWidget(row, col)
                if isinstance(cmbBox2, QtWidgets.QComboBox):
                    accounts[row].append(cmbBox2.currentIndex())

            for col in range(7, 10):
                value = 'None'
                if self.tableAccount.item(row, col):
                    value = self.tableAccount.item(row, col).text()
                accounts[row].append(value)

        return accounts

    def getHashtagData(self):
        if os.path.isfile('tbH.p'):
            with open('tbH.p', 'rb') as file:
                hashtags = pickle.load(file)
        else:
            hashtags = None

        return hashtags

    def getCommentData(self):
        if os.path.isfile('tbC.p'):
            with open('tbC.p', 'rb') as file:
                comments = pickle.load(file)
        else:
            comments = None

        return comments

    def getFilterData(self):
        if os.path.isfile('tbF.p'):
            with open('tbF.p', 'rb') as file:
                filters = pickle.load(file)
        else:
            filters = None

        return filters


if __name__ == "__main__":
    import sys
    app = QtWidgets.QApplication(sys.argv)
    MainWindow = QtWidgets.QMainWindow()
    ui = Ui_MainWindow()
    ui.setupUi(MainWindow)
    MainWindow.show()
    sys.exit(app.exec_())

