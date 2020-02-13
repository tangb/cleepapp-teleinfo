import unittest
import logging
import sys
sys.path.append('../')
from backend.teleinfo import Teleinfo
from raspiot.utils import InvalidParameter, MissingParameter, CommandError, Unauthorized
from raspiot.libs.tests import session
import os
import time
from mock import Mock


class TestTeleinfo(unittest.TestCase):

    def setUp(self):
        self.session = session.TestSession(logging.CRITICAL)
        self.module = self.session.setup(Teleinfo)

    def tearDown(self):
        self.session.clean()


if __name__ == "__main__":
    #coverage run --omit="/usr/local/lib/python2.7/*","test_*" --concurrency=thread test_teleinfo.py; coverage report -m
    unittest.main()
    
