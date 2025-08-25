#!/usr/bin/python
# Created on 2025. 08. 25
# @Author  : 강성훈(ssogaree@gmail.com)
# @File    : sgframework/utils/file_util.py
# @version : 1.00.00
# Copyright (c) 1999-2025 KSFAMS Co., Ltd. All Rights Reserved.

import os


def createFolder(directory):
    try:
        if not os.path.exists(directory):
            os.makedirs(directory)
    except OSError:
        print('Error: Creating directory. ' + directory)