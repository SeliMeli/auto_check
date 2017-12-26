#!/usr/bin/env python
# -*- coding: utf-8 -*-
from apscheduler.schedulers.blocking import BlockingScheduler
import logging
from cccheck import auto_check

if __name__ == '__main__':
    logging.basicConfig(level=logging.INFO, format='%(asctime)s'+': '+'%(levelname)s'+': '+'%(message)s')
    scheduler = BlockingScheduler(timezone='Asia/Shanghai')
    scheduler.add_job(auto_check.check_in, 'interval', days=1, start_date=auto_check.check_in_date)
    scheduler.add_job(auto_check.check_out, 'interval', days=1, start_date=auto_check.check_out_date)
    scheduler.start()
