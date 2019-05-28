from zipfile import ZipFile
from os.path import isdir, isfile, expanduser
from os import getcwd, popen
from shutil import rmtree
from threading import Thread
import sys, ctypes
import requests


def run_follower_maker(path):
    file = "{}\\followerMaker.exe".format(path)

    if isfile(file):
        print('run installer: {}'.format(file))
        popen(file)
    else:
        print('fail to run installer: {}'.format(file))

def download_file_from_google_drive(id, destination):
    URL = "https://docs.google.com/uc?export=download"

    session = requests.Session()

    response = session.get(URL, params = { 'id' : id }, stream = True)
    token = get_confirm_token(response)

    if token:
        params = { 'id' : id, 'confirm' : token }
        response = session.get(URL, params = params, stream = True)

    save_response_content(response, destination)

def get_confirm_token(response):
    for key, value in response.cookies.items():
        if key.startswith('download_warning'):
            return value

    return None

def save_response_content(response, destination):
    CHUNK_SIZE = 32768

    with open(destination, "wb") as f:
        for chunk in response.iter_content(CHUNK_SIZE):
            if chunk: # filter out keep-alive new chunks
                f.write(chunk)

if __name__ == "__main__":
    file_id = '11rxdMFAU_jf5WD8hvrgbNrYF3UWFRoAG'
    downloadedFile = ("%s\\Downloads\\followerMaker.zip") % expanduser("~")
    download_file_from_google_drive(file_id, downloadedFile)

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