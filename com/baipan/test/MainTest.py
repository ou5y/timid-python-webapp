# !C:\Python27\python.exe
# -*- coding: UTF-8 -*-

import unittest
import time
from com.baipan.util.DictUtil import *
import com.baipan.db.jdbc

print com.baipan.db.jdbc.port
print com.baipan.db.jdbc.password()


if __name__ == '__main__':
    print
    # unittest.main()


class TestClass(unittest.TestCase):
    def setUp(self):
        print "BEGIN****************"

    def tearDown(self):
        print "DONE*****************"

    def test_dict(self):
        print Dict(a=1)
