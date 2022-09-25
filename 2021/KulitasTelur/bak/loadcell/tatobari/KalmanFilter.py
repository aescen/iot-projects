# SimpleKalmanFilter - a Kalman Filter implementation for single variable models.
# Created by Denys Sene, January, 1, 2017.
# Released under MIT License - see LICENSE file for details. 


class SimpleKalmanFilter:
    def __init__(self, mea_e, est_e, q):
        self._err_measure = mea_e
        self._err_estimate = est_e
        self._q = q
        self._current_estimate = 0
        self._last_estimate = 0
        self._kalman_gain = 0

    def updateEstimate(self, mea):
        self._kalman_gain = self._err_estimate / (self._err_estimate + self._err_measure)
        self._current_estimate = self._last_estimate + self._kalman_gain * (mea - self._last_estimate)
        self._err_estimate =  (1.0 - self._kalman_gain) * self._err_estimate + abs(self._last_estimate - self._current_estimate) * self._q
        self._last_estimate = self._current_estimate

        return self._current_estimate

    def setMeasurementError(self, ea_e):
        self._err_measure = mea_e

    def setEstimateError(self, est_e):
        self._err_estimate = est_e


    def setProcessNoise(self, q):
        self._q = q

    def getKalmanGain(self):
        return self._kalman_gain

