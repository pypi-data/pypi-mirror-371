import logging
import unittest

from scipy.stats import false_discovery_control

from nonconform.estimation.weighted_conformal import WeightedConformalDetector
from nonconform.strategy.jackknife import Jackknife
from nonconform.utils.data.load import load_breast
from nonconform.utils.stat.metrics import false_discovery_rate, statistical_power
from pyod.models.iforest import IForest


class TestCaseJackknifeConformal(unittest.TestCase):

    logging.basicConfig(level=logging.INFO)

    def test_jackknife_conformal_breast(self):
        x_train, x_test, y_test = load_breast(setup=True, seed=1)

        ce = WeightedConformalDetector(
            detector=IForest(behaviour="new"), strategy=Jackknife()
        )

        ce.fit(x_train)
        est = ce.predict(x_test)

        decisions = false_discovery_control(est, method="bh") <= 0.2
        self.assertEqual(false_discovery_rate(y=y_test, y_hat=decisions), 0.143)
        self.assertEqual(statistical_power(y=y_test, y_hat=decisions), 0.857)

    def test_jackknife_conformal_plus_breast(self):
        x_train, x_test, y_test = load_breast(setup=True, seed=1)

        ce = WeightedConformalDetector(
            detector=IForest(behaviour="new"), strategy=Jackknife(plus=True)
        )

        ce.fit(x_train)
        est = ce.predict(x_test)

        decisions = false_discovery_control(est, method="bh") <= 0.2
        self.assertEqual(false_discovery_rate(y=y_test, y_hat=decisions), 0.143)
        self.assertEqual(statistical_power(y=y_test, y_hat=decisions), 0.857)


if __name__ == "__main__":
    unittest.main()
