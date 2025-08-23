import unittest
from anomalies import anomaly


class TestColav_anomaly(unittest.TestCase):
    def test__working(self):
        self.assertEqual(list(anomaly.free([-1, 1], [4, -2])),
                         [3, 3, 3, -12, -12, 15], True)


if __name__ == '__main__':
    unittest.main()
