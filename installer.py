from zipfile import ZipFile
from os.path import isdir, isfile, expanduser
from os import getcwd, popen
from shutil import rmtree
from threading import Thread
import sys, ctypes

def run_follower_maker(path):
    file = "{}\\followerMaker.exe".format(path)

    if isfile(file):
        print('run installer: {}'.format(file))
        popen(file)
    else:
        print('fail to run installer: {}'.format(file))

if __name__ == "__main__":
    downloadedFile = ("%s\\Downloads\\followerMaker.zip") % expanduser("~")
    if isfile(downloadedFile):
        folder = getcwd()
        upperFolder = folder[:folder.rfind('\\')]

        if isdir(folder):
            print("delete folder: {}".format(folder))
            rmtree(folder)

        print("extract file: {}".format(downloadedFile))
        file = ZipFile(downloadedFile)
        file.extractall(upperFolder)
        file.close()

        print("delete file: {}".format(downloadedFile))
        rmtree(downloadedFile)

        msg = ctypes.windll.user32.MessageBoxW(None, "업데이트가 완료되어 프로그램을 재실행합니다.", "Follow Maker Noti", 0)
        followerMaker = Thread(target=run_follower_maker(), args=folder)
        followerMaker.start()

    else:
        msg = ctypes.windll.user32.MessageBoxW(None, "업데이트 파일을 찾을 수 없습니다.\n관리자에게 문의해주세요.", "Follow Maker Noti", 0)

    sys.exit()