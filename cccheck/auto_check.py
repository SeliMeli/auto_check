#!/usr/bin/env python
# -*- coding: utf-8 -*-
import string
import random
import hashlib
from functools import wraps

import requests
import logging
from apscheduler.schedulers.blocking import BlockingScheduler
import time
from cccheck.exceptions import CheckException, LoginException, RetryException
from requests.exceptions import HTTPError
from chinese_calendar import is_holiday
import datetime

user_name = '18723228317'
password = 'lwy19950906'
url = '183.230.102.33:14003'
login_uri = '/app/index/login'
check_in_uri = '/app/checkin/clock'
check_in_device = '2100060101'
check_in_date = datetime.datetime.strptime('2017-12-21 08:15:00 +0800', '%Y-%m-%d %H:%M:%S %z')
check_out_date = datetime.datetime.strptime('2017-12-21 17:30:00 +0800', '%Y-%m-%d %H:%M:%S %z')


def login_cache(func):
    uid_token = {'uid': 'default', 'token': 'default'}
    refresh_times = 0

    @wraps(func)
    def _wrapper(*args):
        if args:
            if refresh_times > 2:
                raise RetryException()
            uid, token = func(args)
            uid_token['uid'] = uid
            uid_token['token'] = token
            ++refresh_times
            return uid, token
        if uid_token.get('token') != 'default':
            return uid_token['uid'], uid_token['token']
    return _wrapper


def get_random_string():
    return ''.join(random.choice(string.digits+string.ascii_lowercase) for _ in range(16))


def get_encoded_password():
    salt = get_random_string()
    stage_1_password = hashlib.md5(password.encode('utf-8')).hexdigest()
    pre_encoded = stage_1_password + salt
    return hashlib.md5(pre_encoded.encode('utf-8')).hexdigest(), salt


@login_cache
def login(force=False):
    encoded_password, salt = get_encoded_password()
    headers = {'Accept': '*/*', 'Accept-Encoding': 'gzip,deflate', 'User-Agent': 'okhttp/3.3.0', 'Content-Type': 'application/json;charset=utf-8'}
    payload = {'cellphoneId': '351952086244222', 'cellphoneInfo': '7.0SM-G9350', 'location': '', 'loginWay': '3', 'versionNum': '2.1.1.0', 'latitude': '0', 'loginName': user_name, 'longitude': '0', 'password': encoded_password, 'salt': salt}
    r = requests.post('http://'+url+login_uri, json=payload, headers=headers)
    r.raise_for_status()
    json_result = r.json()
    returnCode = json_result.get('returnCode')
    if returnCode != 1:
        raise LoginException(user=user_name, password=password, response=json_result)
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
    if return_code != 1:
        raise CheckException(user=user_name, response=r_json)
    logging.info("check success")


def daily_check():
    if is_holiday(datetime.datetime.now(datetime.timezone(datetime.timedelta(hours=8))).date()):
        pass
    else:
        run_after = random.randint(0, 840)
        logging.info('Auto Check in/out start in '+run_after+'secs')
        time.sleep(run_after)

        try:
            uid, token = login()
            check_in(uid, token)
        except LoginException as e:
            logging.exception(e)
        except HTTPError as e:
            logging.exception(e)
        except CheckException as e:
            logging.exception(e)
            login(True)




if __name__ == '__main__':
    logging.basicConfig(level=logging.INFO, format='%(asctime)s'+': '+'%(levelname)s'+': '+'%(message)s')
    scheduler = BlockingScheduler()
    scheduler.add_job(daily_check, 'interval', days=1, start_date=check_in_date)
    scheduler.add_job(daily_check, 'interval', days=1, start_date=check_out_date)
    logging.info("mission started")
    scheduler.start()
