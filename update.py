from uuid import getnode as get_mac
from selenium import webdriver
from selenium.common.exceptions import WebDriverException
from bs4 import BeautifulSoup
import pandas as pd
import time
import re
import csv

ERROR_NONE = 0
ERROR_DRIVER = 1
ERROR_UNIDENTIFIED_USER = 2
ERROR_OLD_VERSION = 3

USERCODE_PW = '2813'
UPDATE_PW = '1231'
APPLY_PW = '1824'

def check_version(macId, curVer, driverPath):
    bResult = True
    errCode = ERROR_NONE
    errMsg = 'None'
    # 크롬창을 띄우지 않는 옵션을 넣는다
    options = webdriver.ChromeOptions()
    options.add_argument('headless')
    options.add_argument('disable-gpu')
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
    strUserCodeIniList = classDivs_usercode.find_all('p')

    bIncluded = False
    for ini in strUserCodeIniList:
        strIni = re.sub('<.+?>', '', str(ini))
        strCode = strIni[strIni.find('=') + 1:]
        if strCode == str(macId):
            bIncluded = True
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

        classDivs = soup.find('div', {'class': 'entry-content'})

        strUpdateIniList = classDivs.find_all('p')
        for ini in strUpdateIniList:
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
        errMsg = 'Unidentified users'

    driver.close()
    return bResult, errCode, errMsg

def apply_use(macId, driverPath):
    bResult = True
    errCode = ERROR_NONE
    errMsg = 'None'
    # 크롬창을 띄우지 않는 옵션을 넣는다
    options = webdriver.ChromeOptions()
    options.add_argument('headless')
    options.add_argument('disable-gpu')
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
    comment_now = "[%04d-%02d-%02d %02d:%02d:%02d] %d 등록 완료" % (now.tm_year, now.tm_mon, now.tm_mday,
                                                                now.tm_hour, now.tm_min, now.tm_sec, macId)
    driver.find_element_by_xpath('//*[@id="entry25Comment"]/div/form/div/div[1]/input[1]').send_keys('신청 댓글')
    driver.find_element_by_xpath('//*[@id="entry25Comment"]/div/form/div/div[1]/input[2]').send_keys(pw_now)
    driver.find_element_by_xpath('//*[@id="entry25Comment"]/div/form/div/div[1]/div/label').click()
    driver.implicitly_wait(3)
    driver.find_element_by_xpath('//*[@id="entry25Comment"]/div/form/div/textarea').send_keys(comment_now)
    driver.find_element_by_xpath('//*[@id="entry25Comment"]/div/form/div/div/button').click()
    time.sleep(3)
    driver.close()

    return bResult, errCode, errMsg
