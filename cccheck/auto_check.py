#!/usr/bin/env python
# -*- coding: utf-8 -*-
import string
import random
import hashlib
import requests
import logging
from apscheduler.schedulers.blocking import BlockingScheduler
import time


user_name = '15823315964'
password = 'zhou6607'
url = '183.230.102.33:14003'
login_uri = '/app/index/login'
check_in_uri = '/app/checkin/clock'
check_in_device = '2100060101'


def get_random_string():
    return ''.join(random.choice(string.digits+string.ascii_lowercase) for _ in range(16))


def get_encoded_password():
    salt = get_random_string()
    stage_1_password = hashlib.md5(password.encode('utf-8')).hexdigest()
    pre_encoded = stage_1_password + salt
    return hashlib.md5(pre_encoded.encode('utf-8')).hexdigest(), salt


def login():
    encoded_password, salt = get_encoded_password()
    headers = {'Accept': '*/*', 'Accept-Encoding': 'gzip,deflate', 'User-Agent': 'okhttp/3.3.0', 'Content-Type': 'application/json;charset=utf-8'}
    payload = {'cellphoneId': '351952086244222', 'cellphoneInfo': '7.0SM-G9350', 'location': '', 'loginWay': '3', 'versionNum': '2.1.1.0', 'latitude': '0', 'loginName': user_name, 'longitude': '0', 'password': encoded_password, 'salt': salt}
    r = requests.post('http://'+url+login_uri, json=payload, headers=headers)
    r.raise_for_status()
    json_result = r.json()
    returnCode = json_result.get('returnCode')
    if returnCode != 1:
        logging.error('Log in failed')
    details = json_result.get('details')
    user = details.get('user')
    uid = user.get('id')
    token = details.get('token')
    logging.info('login success')
    return uid, token


def check_in(uid, token):
    headers = {'Accept': '*/*', 'Accept-Encoding': 'gzip,deflate', 'User-Agent': 'okhttp/3.3.0',
               'Content-Type': 'application/json;charset=utf-8', 'Access-Token': token}
    payload = {'checkinDeviceSn': check_in_device, 'userId': uid}
    r = requests.post('http://'+url+check_in_uri, headers=headers, json=payload)
    r.raise_for_status()
    r_json = r.json()
    return_code = r_json.get('returnCode')
    if return_code != 200:
        logging.error("check failed")
    logging.info("check success")


def daily_check():
    time.sleep(random.randint(0, 840))
    uid, token = login()
    check_in(uid, token)

if __name__ == '__main__':
    logging.basicConfig(level=logging.INFO,format='%(asctime)s'+': '+'%(levelname)s'+': '+'%(message)s')
    scheduler = BlockingScheduler()
    scheduler.add_job(daily_check, 'interval', days=1, start_date='2017-12-21 17:30:00 CST')
    scheduler.add_job(daily_check, 'interval', days=1, start_date='2017-12-22 08:15:00 CST')
    logging.info("mission started")
    scheduler.start()
