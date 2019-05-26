from selenium import webdriver
from selenium.common.exceptions import WebDriverException
from bs4 import BeautifulSoup
import os, sys
import time
import re

ERROR_NONE = 0
ERROR_DRIVER = 1
ERROR_UNIDENTIFIED_USER = 2
ERROR_OLD_VERSION = 3

USERCODE_PW = '2813'
UPDATE_PW = '1231'
APPLY_PW = '1824'
NOTY_PW = '1175'

def check_version(macId, curVer, driverPath):
    bResult = True
    errCode = ERROR_NONE
    errMsg = ''
    # 크롬창을 띄우지 않는 옵션을 넣는다
    options = get_chrome_options()
    try:
        driver = webdriver.Chrome(driverPath, options=options)

    except WebDriverException as exc:
        bResult = False
        errCode = 1
        errMsg = 'ensure chromedriver is installed at {}'.format(driverPath)
        return bResult, errCode, errMsg

    driver.implicitly_wait(3)
    url_usercode = 'https://antistereotypes.tistory.com/24'
    driver.get(url_usercode)
    time.sleep(3)

    # div class: input - group
    driver.find_element_by_xpath('//*[@id="entry24password"]').send_keys(USERCODE_PW)
    driver.find_element_by_xpath('//*[@id="content"]/div[1]/div[2]/form/fieldset/button').click()

    html_usercode = driver.page_source
    soup_usercode = BeautifulSoup(html_usercode, 'html.parser')

    classDivs_usercode = soup_usercode.find('div', {'class': 'entry-content'})
    # strUserCodeIniList = classDivs_usercode.find_all('p')

    bIncluded = False
    for ini in classDivs_usercode:
        strIni = re.sub('<.+?>', '', str(ini))
        strCode = strIni[strIni.find('=') + 1:]
        if strCode.find(macId) != -1:
            bIncluded = True
            errMsg = 'Welcome! {} :)'.format(strIni[:strIni.find('=')])
            break

    if bIncluded:
        url_update = 'https://antistereotypes.tistory.com/23'
        driver.get(url_update)
        time.sleep(3)

        # div class: input - group
        driver.find_element_by_xpath('//*[@id="entry23password"]').send_keys(UPDATE_PW)
        driver.find_element_by_xpath('//*[@id="content"]/div[1]/div[2]/form/fieldset/button').click()

        html = driver.page_source
        soup = BeautifulSoup(html, 'html.parser')

        strIniList = soup.find('div', {'class': 'entry-content'})

        for ini in strIniList:
            strIni = re.sub('<.+?>', '', str(ini))
            if not strIni.find('PGM_VERSION') == -1:
                strVer = strIni[strIni.find('=')+1:]
                if curVer < float(strVer):
                    bResult = False
                    errCode = ERROR_OLD_VERSION
                    errMsg = 'Need to program update to Follow Maker v{}'.format(strVer)
    else:
        bResult = False
        errCode = ERROR_UNIDENTIFIED_USER
        errMsg = '등록되지 않은 사용자 확인'

    driver.quit()
    return bResult, errCode, errMsg

def apply_use(macId, driverPath):
    bResult = True
    errCode = ERROR_NONE
    errMsg = '프로그램 사용 신청 완료'
    # 크롬창을 띄우지 않는 옵션을 넣는다
    options = get_chrome_options()
    try:
        driver = webdriver.Chrome(driverPath, options=options)

    except WebDriverException as exc:
        bResult = False
        errCode = 1
        errMsg = 'ensure chromedriver is installed at {}'.format(driverPath)
        return bResult, errCode, errMsg

    driver.implicitly_wait(3)
    url_apply = 'https://antistereotypes.tistory.com/25'
    driver.get(url_apply)
    time.sleep(3)

    # div class: input - group
    driver.find_element_by_xpath('//*[@id="entry25password"]').send_keys(APPLY_PW)
    driver.find_element_by_xpath('//*[@id="content"]/div[1]/div[2]/form/fieldset/button').click()
    driver.implicitly_wait(3)

    now = time.localtime()
    pw_now = "pw%02d%02d%02d" % (now.tm_hour, now.tm_min, now.tm_sec)
    comment_now = "[%04d-%02d-%02d %02d:%02d:%02d] %s 등록 완료" % (now.tm_year, now.tm_mon, now.tm_mday,
                                                                now.tm_hour, now.tm_min, now.tm_sec, macId)
    driver.find_element_by_xpath('//*[@id="entry25Comment"]/div/form/div/div[1]/input[1]').send_keys('신청 댓글')
    driver.find_element_by_xpath('//*[@id="entry25Comment"]/div/form/div/div[1]/input[2]').send_keys(pw_now)
    driver.find_element_by_xpath('//*[@id="entry25Comment"]/div/form/div/div[1]/div/label').click()
    driver.implicitly_wait(3)
    driver.find_element_by_xpath('//*[@id="entry25Comment"]/div/form/div/textarea').send_keys(comment_now)
    driver.find_element_by_xpath('//*[@id="entry25Comment"]/div/form/div/div/button').click()
    time.sleep(3)
    driver.quit()

    return bResult, errCode, errMsg

def get_notification(driverPath):
    bResult = True
    errCode = ERROR_NONE
    errMsg = 'None'
    # 크롬창을 띄우지 않는 옵션을 넣는다
    options = get_chrome_options()

    try:
        driver = webdriver.Chrome(driverPath, options=options)

    except WebDriverException as exc:
        bResult = False
        errCode = 1
        errMsg = 'ensure chromedriver is installed at {}'.format(driverPath)
        return bResult, errCode, errMsg

    driver.implicitly_wait(3)
    url_apply = 'https://antistereotypes.tistory.com/26'
    driver.get(url_apply)
    time.sleep(3)

    # div class: input - group
    driver.find_element_by_xpath('//*[@id="entry26password"]').send_keys(NOTY_PW)
    driver.find_element_by_xpath('//*[@id="content"]/div[1]/div[2]/form/fieldset/button').click()
    driver.implicitly_wait(3)

    html = driver.page_source
    soup = BeautifulSoup(html, 'html.parser')

    strNotiDiv = soup.find('div', {'class': 'entry-content'})
    strNoti = ''
    for noti in strNotiDiv:
        strNoti += re.sub('<.+?>', '', str(noti))
        strNoti += '\n'

    if bResult and strNoti != '':
        errMsg = strNoti

    time.sleep(3)
    driver.quit()

    return bResult, errCode, errMsg

def get_chrome_options():
    options = webdriver.ChromeOptions()
    options.add_argument('--mute-audio')
    options.add_argument('--dns-prefetch-disable')
    options.add_argument('--lang=en-US')
    options.add_argument('--disable-setuid-sandbox')
    options.add_argument('--headless')
    options.add_argument('--disable-gpu')

    return options

''' Python에서 맥주소를 가져오기! '''
def get_mac_address():
    arrinfo = {}
    isdevice = 0
    mk = 0
    if sys.platform=='win32':
        for line in os.popen("ipconfig /all"):
            if line.lstrip().startswith('호스트'):
                host = line.split(':')[1].strip()
                arrinfo["host"] = host
            else:
                if line.lstrip().startswith('터널'):
                    isdevice = 0
                if line.lstrip().startswith('이더넷'):
                    isdevice = 1
                if line.lstrip().startswith('무선'):
                    isdevice = 1
                if isdevice == 1:
                    if line.lstrip().startswith('미디어 상태'):
                        desc = line.split(':')[1].strip()
                        if desc == '미디어 연결 끊김':
                            isdevice = 0
                    if line.lstrip().startswith('설명'):
                        desc = line.split(':')[1].strip()
                        if desc.lstrip().startswith('Bluetooth'):
                            isdevice = 0
                    if line.lstrip().startswith('물리적'):
                            #mac = line.split(':')[1].strip().replace('-',':')
                            mac = line.split(':')[1].strip()
                            arrinfo[mk] = mac
                            isdevice = 0
                            mk+=1
    else:
        for line in os.popen("/sbin/ifconfig"):
            if line.find('Ether') >-1:
                mac=line.split()[4]
                arrinfo[mk] = mac
                isdevice = 0
                mk+=1
    return arrinfo