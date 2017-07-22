# !C:\Python27\python.exe
# -*- coding: UTF-8 -*-

import logging, time

__author__ = '5y'

'''自定义异常类'''


class ErrorException(BaseException):
    def __init__(self, errorCode=0, errorMsg=None, t = time.strftime("%Y-%m-%d %H:%M:%S", time.localtime())):
        super(ErrorException, self).__init__()
        self.__errorCode = errorCode
        self.__errorMsg = errorMsg
        self.__time = t

    def __str__(self):
        str = "错误代码：%d \t\t 错误描述：%s\t\t%s" % (self.__errorCode, self.__errorMsg, self.__time)
        # print str
        logging.info(str)
        return str

    __repr__ = __str__

    @property
    def errorCode(self):
        return self.__errorCode

    @errorCode.setter
    def errorCode(self, errorCode):
        self.__errorCode = errorCode

    @property
    def errorMsg(self):
        return self.__errorMsg

    @errorMsg.setter
    def errorMsg(self, errorMsg):
        self.__errorMsg = errorMsg
