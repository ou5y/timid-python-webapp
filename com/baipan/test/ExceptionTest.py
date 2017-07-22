# !C:\Python27\python.exe
# -*- coding: UTF-8 -*-
from com.baipan.exception.ErrorException import *

e = ErrorException(-1, '挂了')
print "错误代码：%d \t 错误描述：%s" % (e.errorCode, e.errorMsg)

e.errorCode = 1
e.errorMsg = '活了'

print "错误代码：%d \t\t\t 错误描述：%s" % (e.errorCode, e.errorMsg)

print "zher er"

print e
