import unittest
from unittest import TestCase
from autoconfig import AppVersion
from math import ceil
from random import random

class TestAppVersion(TestCase):
    def test_gt(self):
        assert AppVersion([73, 75, 78]) > AppVersion([40, 36, 78])

    def test_lt(self):
        assert AppVersion([24, 51, 53]) < AppVersion([35, 100, 95])

    def test_random(self):
        for i in range(10000):
            version1 = AppVersion(self.genRandom())
            version2 = AppVersion(self.genRandom())
            v1 = version1.pack()
            v2 = version2.pack()
            if version1 > version2:
                assert (v1[0] > v2[0] or v1[1] > v2[1] or v1[2] > v2[2]), f"v.{v1} is not greater than v.{v2} (iteration {i})"
            elif version2 > version1:
                assert (v1[0] < v2[0] or v1[1] < v2[1] or v1[2] < v2[2]), f"v.{v1} is not smaller than v.{v2} (iteration {i})"
            else:
                assert v1 == v2, f"{v1} != {v2}"

    def genRandom(self) -> list[int, int, int]:
        lst = []
        for i in range(3):
            lst.append(ceil(random() * 1000))
        return lst

if __name__ == "__main__":
    unittest.main()