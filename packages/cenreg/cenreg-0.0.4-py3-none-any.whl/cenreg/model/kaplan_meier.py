import numpy as np
import scipy

from cenreg.distribution.linear import LinearCDF, LinearQuantileFunction


def createCdfLinear(
    observed_times: np.ndarray,
    uncensored: np.ndarray,
    bins: np.ndarray,
):
    """
    Create CdfLinear object from Kaplan-Meier estimator.

    Parameters
    ----------
    observed_times : ndarray (float)
        One-dimensional ndarray containing observed times.

    uncensored : ndarray (bool)
        One-dimensional ndarray containing censored (False)
        or uncensored (True).

    bins : ndarray (float)
        One-dimensional sorted ndarray containing time bins.
        The first element must be 0.0.
        The last element must be larger than maximum time of observed_times.

    Returns
    -------
    CdfLinear object
    """

    km = KaplanMeierDistribution()
    km.fit(observed_times, uncensored)
    cdf = km.cdf(bins)

    # interpolate between km.bins[-1] and bins[-1]
    diff = bins[-1] - km.bins[-1]
    if diff <= 0.0:
        raise ValueError(
            "bins must be larger than maximum time of observed_times."
        )
    mask = bins > km.bins[-1]
    r = (bins[mask] - km.bins[-1]) / diff
    cdf[mask] = 1.0 - km.cure_rate + km.cure_rate * r
    return LinearCDF(bins, cdf, apply_cumsum=False)


def createQuantilesLinear(
    observed_times: np.ndarray,
    uncensored: np.ndarray,
    qk_levels: np.ndarray,
    max_time: float,
):
    """
    Create QuantilesLinear object from Kaplan-Meier estimator.

    Parameters
    ----------
    observed_times : ndarray (float)
        One-dimensional ndarray containing observed times.

    uncensored : ndarray (bool)
        One-dimensional ndarray containing censored (False)
        or uncensored (True).

    qk_levels : ndarray (float)
        One-dimensional ndarray containing quantile levels.

    max_time : float
        max_time must be larger than maximum time of observed_times.

    Returns
    -------
    QuantilesLinear object
    """

    km = KaplanMeierDistribution()
    km.fit(observed_times, uncensored)
    if max_time <= km.bins[-1]:
        raise ValueError("max_time must be larger than maximum time of observed_times.")
    times = km.icdf(qk_levels)

    # interpolate between km.max_observed_time and max_time
    diff = max_time - km.bins[-1]
    mask = 1.0 - qk_levels < km.cure_rate
    r = (1.0 - qk_levels[mask]) / km.cure_rate
    times[mask] = km.bins[-1] + diff * (1.0 - r)
    return LinearQuantileFunction(qk_levels, times, apply_cumsum=False)


class KaplanMeierDistribution:
    """
    Distribution class of Kaplan-Meier estimator.
    This class does not use any interpolation.

    Notes:
        At least one data point must be uncensored.
        CDF values can be strictly less than 1.0 after the last uncensored data point.
        Survival rates can be strictly greater than 0.0 after the last uncensored data point.
        Inverse CDF values may not be correct for large quantiles (due to the above notes).
        While the original Kaplan-Meier estimator is defined for non-negative times,
        this implementation can handle negative times.
    """

    def _compute_variance(
        self,
        alpha: float,
    ):
        """
        Compute variance of survival rates using the exponential Greenwood formula.

        Parameters
        ----------
        alpha : float
            Significance level for confidence intervals: [alpha/2.0, 1.0-alpha/2.0].
        """

        last_rate_is_zero = self.survival_rates[-1] == 0.0
        if last_rate_is_zero:
            survival_rates = self.survival_rates[:-1]
            num_alive = self._num_alive[:-1]
            num_death = self._num_death[:-1]
        else:
            survival_rates = self.survival_rates
            num_alive = self._num_alive
            num_death = self._num_death

        s = np.log(survival_rates)
        z = np.log(-s)

        rate = num_death / (num_alive * (num_alive - num_death))
        std = np.sqrt(np.cumsum(rate) / (s * s))
        std *= scipy.stats.norm.ppf(alpha / 2.0)
        self.survival_rates_lb = np.exp(-np.exp(z - std))
        self.survival_rates_ub = np.exp(-np.exp(z + std))

        if last_rate_is_zero:
            self.survival_rates_lb = np.append(self.survival_rates_lb, 0.0)
            self.survival_rates_ub = np.append(self.survival_rates_ub, 0.0)

    def fit(
        self,
        observed_times: np.ndarray,
        uncensored: np.ndarray,
        weights: np.ndarray | None = None,
        alpha: float | None = None,
    ):
        if weights is None:
            weights = np.ones_like(observed_times)

        # sort based on uncensored and observed_times
        uncensored = uncensored.astype(int)
        if np.sum(uncensored) == 0:
            raise ValueError("At least one data point must be uncensored.")
        temp = np.concatenate(
            [
                observed_times.reshape(-1, 1),
                uncensored.reshape(-1, 1),
                weights.reshape(-1, 1),
            ],
            axis=1,
        )
        temp = temp[np.argsort(temp[:, 1])[::-1]]
        temp = temp[np.argsort(temp[:, 0])]

        # count alive and dead
        num_alive = np.sum(temp[:, 2]) - np.cumsum(temp[:, 2]) + temp[:, 2]
        temp = np.concatenate([temp, num_alive.reshape(-1, 1)], axis=1)
        dead = temp[temp[:, 1] == 1]
        cumsum_death = np.concatenate([[0.0], np.cumsum(dead[:, 2])])
        cut_index = np.concatenate(
            ([True], dead[1:, 0] != dead[:-1, 0], [True])
        ).nonzero()[0]
        self._num_death = cumsum_death[cut_index[1:]] - cumsum_death[cut_index[:-1]]
        self._num_alive = dead[cut_index[:-1], 3]
        self._time_points = dead[cut_index[:-1], 0]

        # compute survival rates
        rate = 1.0 - self._num_death / self._num_alive
        self.survival_rates = np.cumprod(rate)

        # compute variance
        if alpha is not None:
            if alpha < 0.0 or alpha > 0.5:
                raise ValueError("alpha must be in [0.0, 0.5].")
            self._compute_variance(alpha)

        # store statistics
        self.last_uncensored_time = self._time_points[-1]
        self.cure_rate = self.survival_rates[-1]

        # add the survival rate 1.0 at the start time
        start_time = np.min(observed_times)
        if start_time >= 0.0:
            start_time = 0.0
        else:
            print("WARNING: minimum observed time is negative {}".format(start_time))
        if start_time < self._time_points[0]:
            self.bins = np.append(start_time, self._time_points)
            self.survival_rates = np.append(1.0, self.survival_rates)
            if alpha is not None:
                self.survival_rates_lb = np.append(1.0, self.survival_rates_lb)
                self.survival_rates_ub = np.append(1.0, self.survival_rates_ub)
        else:
            self.bins = self._time_points

        # add the survival rate 0.0 at the last observed time
        if self.cure_rate > 0.0:
            self.bins = np.append(self.bins, np.max(observed_times))
            self.survival_rates = np.append(self.survival_rates, self.cure_rate)
            if alpha is not None:
                self.survival_rates_lb = np.append(
                    self.survival_rates_lb, self.cure_rate
                )
                self.survival_rates_ub = np.append(
                    self.survival_rates_ub, self.cure_rate
                )

    def average_cdf(self, t: np.ndarray):
        """
        Compute average cumulative distribution function.

        Parameters
        ----------
        t : ndarray (float)
            ndarray of shape [batch_size] containing time points.

        Returns
        -------
        average cumulative probability : ndarray (float)
            ndarray of shape [batch_size] containing average cumulative probability of event occurrence.
        """

        return self.cdf(t)

    def cdf(self, t: np.ndarray, add_edges: bool = False):
        """
        Compute cumulative distribution function.

        Parameters
        ----------
        t : ndarray (float)
            ndarray of shape [num_bins] containing time points.

        add_edges : bool
            If True, add 0.0 at the start time and 1.0 at the last observed time.

        Returns
        -------
        cumulative probability : ndarray (float)
            ndarray of shape [num_bins] containing cumulative probability of event occurrence.
        """
        ret = 1.0 - self.survival_function(t)
        if add_edges:
            s = np.array(ret.shape)
            s[-1] = 1
            zeros = np.zeros(s)
            ones = np.ones(s)
            ret = np.concatenate([zeros, ret, ones], -1)
        return ret

    def icdf(self, quantiles: np.ndarray):
        """
        Compute cumulative distribution function.

        Parameters
        ----------
        quantiles : ndarray (float)
            ndarray of shape [batch_size] containing quantiles.

        Returns
        -------
        cumulative probability : ndarray (float)
            ndarray of shape [batch_size] containing cumulative probability of event occurrence.
        """

        p = 1.0 - self.survival_rates
        idx = np.searchsorted(p, quantiles, side="left")
        idx = np.clip(idx, 0, len(self.bins) - 1)
        return self.bins[idx]

    def survival_function(self, t: np.ndarray):
        """
        Compute survival function.

        Parameters
        ----------
        t : ndarray (float)
            Survival rates are computed for values t.
            t must be one or two-dimensional ndarray.

        Returns
        -------
        survival_rates : ndarray (float)
            ndarray of the same shape as t containing survival rates.
        """
        # TODO reimplement this function
        idx = np.searchsorted(self.bins, t, side="right") - 1

        sr = np.zeros_like(t)
        sr[idx < 0] = 1.0
        mask = (idx >= 0) & (idx < len(self.survival_rates))
        sr[mask] = self.survival_rates[idx[mask]]
        return sr
