from zipfile import ZipFile
from os.path import isdir, isfile, expanduser
from os import getcwd, popen
from shutil import rmtree
from threading import Thread
import sys, ctypes, os
import requests


def run_follower_maker(path):
    file = "{}\\followerMaker.exe".format(path)

    if isfile(file):
        print('run installer: {}'.format(file))
        popen(file)
    else:
        print('fail to run installer: {}'.format(file))

def runProcessKiller():
    file = "{}\\ProgramInstaller.exe".format(os.getcwd())

    if os.path.isfile(file):
        print('run ProgramInstaller: {}'.format(file))
        os.popen(file)
    else:
        print('fail to run installer: {}'.format(file))

if __name__ == "__main__":
    runProcessKiller()
    downloadedFile = ("%s\\Downloads\\followerMaker.zip") % expanduser("~")

    if isfile(downloadedFile):
        folder = getcwd()
        upperFolder = folder[:folder.rfind('\\')]

        if isdir(folder):
            print("delete folder: {}".format(folder))
            rmtree(folder)

        zipdir = "다운로드 경로: {}".format(downloadedFile)
        # file = ZipFile(downloadedFile)
        # file.extractall(upperFolder)
        # file.close()

        # print("delete file: {}".format(downloadedFile))
        # rmtree(downloadedFile)

        msg = ctypes.windll.user32.MessageBoxW(None, zipdir, "Follow Maker Noti", 0)
        # followerMaker = Thread(target=run_follower_maker(), args=folder)
        # followerMaker.start()

    else:
        msg = ctypes.windll.user32.MessageBoxW(None, "업데이트 파일을 찾을 수 없습니다.\n관리자에게 문의해주세요.", "Follow Maker Noti", 0)

    sys.exit()