from zipfile import ZipFile
from os.path import isdir, isfile, expanduser
from os import getcwd, popen
from shutil import rmtree
from threading import Thread
import sys

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

        file = ZipFile(downloadedFile)
        file.extractall(upperFolder)

        followerMaker = Thread(target=run_follower_maker(), args=folder)
        followerMaker.start()

    sys.exit()