import unittest

from craftai import Time

class TestTime(unittest.TestCase):

  def test_timezone_format(self):
    self.assertEqual(Time(timezone="+01:00").timezone, "+01:00")
    self.assertEqual(Time(timezone="CET").timezone, "+01:00")
    self.assertEqual(Time(timezone="+0100").timezone, "+01:00")
    self.assertEqual(Time(timezone="+01").timezone, "+01:00")
    self.assertEqual(Time(timezone="CST").timezone, "-06:00")
