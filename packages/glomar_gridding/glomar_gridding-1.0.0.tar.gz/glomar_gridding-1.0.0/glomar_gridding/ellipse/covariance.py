# Copyright 2025 National Oceanography Centre
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

"""Class to estimate covariance matrix from ellipse parameters and positions."""

import datetime
import logging
import sys
from itertools import combinations
from typing import Any
from warnings import warn

import numpy as np
from scipy.special import gamma
from scipy.special import kv as modified_bessel_2nd

from glomar_gridding.constants import RADIUS_OF_EARTH_KM
from glomar_gridding.types import CovarianceMethod, DeltaXMethod
from glomar_gridding.utils import cov_2_cor, mask_array, sizeof_fmt

if sys.version_info.minor >= 12:
    from itertools import batched
else:
    from glomar_gridding.utils import batched

TWO_PI = 2 * np.pi


class EllipseCovarianceBuilder:
    """
    Compute covariance from Ellipse parameters and positions.

    v = Matern covariance shape parameter

    Lx - an numpy array of horizontal length scales (
    Ly - an numpy array of meridonal length scales
    theta - an numpy array of rotation angles (RADIANS ONLY)

    sdev - standard deviation -- right now it just takes a numeric array
    if you have multiple contribution to sdev (uncertainties derived from
    different sources), you need to put them into one array

    Rules:
    Valid (ocean) point:
    1) cov_ns and cor_ns are computed out to max_dist; out of range = 0.0
    2) Masked points are ignored

    Invalid (masked) points:
    1) Skipped over

    Parameters
    ----------
    Lx, Ly, theta, stdev: numpy.ndarray
        Arrays with non-stationary parameters
    lats, lons : numpy.ndarray
        Arrays containing the latitude and longitude values
    v : float
        Matern shape parameter
    delta_x_method : str
        How are displacements computed between points
    max_dist : float | None
        If the Haversine distance between 2 points exceed max_dist,
        covariance is set to 0. If set to None then an infinite max dist is
        assumed and covariance between all pairs of positions will be computed.
    precision : type
        Floating point precision of the output covariance numpy defaults to
        np.float32.
    covariance_method : CovarianceMethod
        Set the covariance method used:

            - array (default): faster but uses significantly more memory as
              more pre-computation is performed. Values are computed in a
              vectorised method.
            - loop: slower iterative process, computes each value individually
            - batched: combines the above approaches.

        If the number of grid-points exceeds 10_000 and "array" method is used,
        the method will be overwritten to "loop".
    batch_size : int | None
        Size of the batch to use for the "batched" method. Must be set if the
        covariance_method is set to "batched".
    """

    def __init__(
        self,
        Lx: np.ndarray,
        Ly: np.ndarray,
        theta: np.ndarray,
        stdev: np.ndarray,
        lats: np.ndarray,
        lons: np.ndarray,
        v: float,
        delta_x_method: DeltaXMethod | None = "Modified_Met_Office",
        max_dist: float | None = None,
        precision=np.float32,
        covariance_method: CovarianceMethod = "array",
        batch_size: int | None = None,
    ) -> None:
        ove_start_time = datetime.datetime.now()
        logging.info(
            "Overhead processing start: ",
            ove_start_time.strftime("%Y-%m-%d %H:%M:%S"),
        )

        if max_dist is not None and not isinstance(max_dist, (int, float)):
            raise ValueError("max_dist must be a number")

        # Defining the input data
        self.v = v  # Matern covariance shape parameter
        self.precision = precision
        self.Lx = mask_array(Lx.astype(self.precision))
        self.Ly = mask_array(Ly.astype(self.precision))
        self.theta = mask_array(theta.astype(self.precision))
        self.stdev = mask_array(stdev.astype(self.precision))
        self.max_dist = max_dist
        self.delta_x_method: DeltaXMethod | None = delta_x_method
        self.lats = lats.astype(self.precision)
        self.lons = lons.astype(self.precision)
        self.covariance_method: CovarianceMethod = covariance_method
        self.delta_x_method = delta_x_method
        self.batch_size = batch_size

        # The cov and corr matrix will be sq matrix of this
        self.xy_shape = self.Lx.shape
        self.n_elements = np.prod(self.xy_shape)

        self._get_mask()

        ove_end_time = datetime.datetime.now()
        print(
            "Overhead processing ended: ",
            ove_end_time.strftime("%Y-%m-%d %H:%M:%S"),
        )
        print("Time elapsed: ", ove_end_time - ove_start_time)
        self._calculate_covariance()
        # self._calculate_cor()

    def _get_mask(self) -> None:
        self.data_has_mask = np.ma.is_masked(self.Lx)
        if self.data_has_mask:
            logging.info("Masked pixels detected in input files")
            self.data_mask = self.Lx.mask
            self.covar_size = np.sum(np.logical_not(self.data_mask))
        else:
            logging.info("No masked pixels")
            self.data_mask = np.zeros_like(self.Lx, dtype=bool)
            self.covar_size = self.n_elements

        logging.info("Compressing (masked) array to 1D")
        self.Lx_compressed = self.Lx.compressed()
        self.Ly_compressed = self.Ly.compressed()
        self.theta_compressed = self.theta.compressed()
        self.stdev_compressed = self.stdev.compressed()

        self.x_grid, self.y_grid = np.meshgrid(self.lons, self.lats)
        self.x_mask = np.ma.masked_where(self.data_mask, self.x_grid)
        self.y_mask = np.ma.masked_where(self.data_mask, self.y_grid)
        self.lat_grid_compressed = self.y_mask.compressed()
        self.lon_grid_compressed = self.x_mask.compressed()
        self.lat_grid_compressed_rad = np.deg2rad(self.lat_grid_compressed)
        self.lon_grid_compressed_rad = np.deg2rad(self.lon_grid_compressed)

        self.xy_compressed = np.column_stack(
            [self.lon_grid_compressed, self.lat_grid_compressed]
        )
        self.xy_full = np.column_stack(
            [self.x_mask.flatten(), self.y_mask.flatten()]
        )
        return None

    def _get_disp_fn(self) -> None:
        if self.covariance_method == "low_memory":
            match self.delta_x_method:
                case "Modified_Met_Office":
                    self.disp_fn = _mod_mo_disp_single
                case "Met_Office":
                    self.disp_fn = _mo_disp_single
                case _:
                    raise ValueError(
                        f"Unknown 'delta_x_method' value: {self.delta_x_method}"
                    )
            return None
        match self.delta_x_method:
            case "Modified_Met_Office":
                self.disp_fn = _mod_mo_disp_multi
            case "Met_Office":
                self.disp_fn = _mo_disp_multi
            case _:
                raise ValueError(
                    f"Unknown 'delta_x_method' value: {self.delta_x_method}"
                )
        return None

    def _calculate_covariance(self) -> None:
        cov_start_time = datetime.datetime.now()
        if (
            len(self.Lx_compressed) > 10_000
            and self.covariance_method == "array"
        ):
            warn(
                "Number of grid-points > 10_000, setting to low-memory mode "
                + f"(num grid-points = {len(self.Lx_compressed)}"
            )
            self.covariance_method = "low_memory"
        # Precomupte common terms
        # Note, these are 1x4 rather than 2x2 for convenience
        self._get_disp_fn()
        self.sigmas = _sigma_rot_func_multi(
            self.Lx_compressed, self.Ly_compressed, self.theta_compressed
        ).astype(self.precision)
        self.sqrt_dets = np.sqrt(_det_22_multi(self.sigmas))
        self.gamma_v_term = gamma(self.v) * (2 ** (self.v - 1))
        self.sqrt_v_term = np.sqrt(self.v) * 2

        match self.covariance_method:
            case "low_memory":
                self.calculate_covariance_loop()
            case "array":
                self.calculate_covariance_array()
            case "batched":
                self.calculate_covariance_batched()
            case _:
                raise ValueError(
                    f"Unknown covariance_method: {self.covariance_method}"
                )

        cov_end_time = datetime.datetime.now()
        logging.info(
            "Cov processing ended: ", cov_end_time.strftime("%Y-%m-%d %H:%M:%S")
        )
        print("Time elapsed: ", cov_end_time - cov_start_time)
        logging.info(
            "Mem used by cov mat = ", sizeof_fmt(sys.getsizeof(self.cov_ns))
        )
        self.cov_ns += np.diag(self.stdev_compressed**2).astype(self.precision)

        return None

    def calculate_covariance_array(self) -> None:
        """Calculate the covariance matrix from the ellipse parameters"""
        N = len(self.Lx_compressed)

        # Calculate distances & Displacements
        i_s, j_s = np.asarray(list(combinations(range(N), 2))).transpose()
        if self.max_dist is not None:
            dists = _haversine_multi(
                self.lat_grid_compressed_rad[i_s],
                self.lon_grid_compressed_rad[i_s],
                self.lat_grid_compressed_rad[j_s],
                self.lon_grid_compressed_rad[j_s],
            )
            mask = dists > self.max_dist
            del dists
            i_s = i_s.compress(~mask)
            j_s = j_s.compress(~mask)

        # Calculate covariance values
        cij = self.c_ij_anisotropic_array(i_s, j_s)
        # OPTIM: Initialise empty covariance matrix after computing values to
        # save memory.
        self.cov_ns = np.zeros((N, N), dtype=self.precision)
        self.cov_ns[i_s, j_s] = cij
        del cij

        # Add transpose
        self.cov_ns = self.cov_ns + self.cov_ns.T

        return None

    def calculate_covariance_loop(self) -> None:
        """
        Compute the covariance matrix from ellipse parameters, using a loop.
        This approach is more memory safe and appropriate for low-memory
        operations, but is significantly slower than self.calculate_covariance
        which uses a lot of pre-computation and a vectorised approach.

        Each ellipse is defined by values from Lxs, Lys, and thetas, with
        standard deviation in stdevs.

        References
        ----------
        1. Paciorek and Schevrish 2006 [PaciorekSchervish]_ Equation 8
        2. Karspeck et al. 2012 [Karspeck]_ Equation 17
        """
        # Initialise empty matrix
        N = len(self.Lx_compressed)
        self.cov_ns = np.zeros((N, N), dtype=self.precision)

        for i, j in combinations(range(N), 2):
            # Leave as zero if too far away
            if (self.max_dist is not None) and (
                _haversine_single(
                    self.lat_grid_compressed_rad[i],
                    self.lon_grid_compressed_rad[i],
                    self.lat_grid_compressed_rad[j],
                    self.lon_grid_compressed_rad[j],
                )
                > self.max_dist
            ):
                continue

            sigma_bar = 0.5 * (self.sigmas[i] + self.sigmas[j])
            sigma_bar_det = _det_22_single(sigma_bar)
            # Leave as zero if cannot invert the sigma_bar matrix
            if sigma_bar_det == 0:
                continue

            stdev_prod = self.stdev_compressed[i] * self.stdev_compressed[j]
            c_ij = stdev_prod / self.gamma_v_term
            c_ij *= np.sqrt(
                np.divide(
                    (self.sqrt_dets[i] * self.sqrt_dets[j]), sigma_bar_det
                )
            )

            # Get displacements
            delta_y, delta_x = self.disp_fn(
                self.lat_grid_compressed_rad[i],
                self.lon_grid_compressed_rad[i],
                self.lat_grid_compressed_rad[j],
                self.lon_grid_compressed_rad[j],
            )

            tau = np.sqrt(
                (
                    delta_x * (delta_x * sigma_bar[3] - delta_y * sigma_bar[1])
                    + delta_y
                    * (-delta_x * sigma_bar[2] + delta_y * sigma_bar[0])
                )
                / sigma_bar_det
            )

            inner = self.sqrt_v_term * tau
            c_ij *= np.power(inner, self.v)
            c_ij *= modified_bessel_2nd(self.v, inner)
            # if res > stdev_prod:
            #     raise ValueError(
            #         "c_ij must always be smaller than sdev_i * sdev_j"
            #     )
            # Assign and mirror
            self.cov_ns[i, j] = self.cov_ns[j, i] = self.precision(c_ij)

        return None

    def calculate_covariance_batched(self) -> None:
        """
        Compute the covariance matrix from ellipse parameters, using a batched
        approach.
        This approach is more memory safe and appropriate for low-memory
        operations, but is slower than self.calculate_covariance
        which pre-computes values at all upper triangle points. This approach
        performs pre-computation at all points within the current batch.

        Each ellipse is defined by values from Lxs, Lys, and thetas, with
        standard deviation in stdevs.

        Requires a batch_size parameter.

        References
        ----------
        1. Paciorek and Schevrish 2006 [PaciorekSchervish]_ Equation 8
        2. Karspeck et al. 2012 [Karspeck]_ Equation 17
        """
        if self.batch_size is None:
            raise ValueError("batch_size must be set if using 'batched' method")

        # Initialise empty matrix
        N = len(self.Lx_compressed)
        self.cov_ns = np.zeros((N, N), dtype=self.precision)

        for batch in batched(combinations(range(N), 2), self.batch_size):
            i_s, j_s = np.asarray(batch).T

            # Mask large distances
            if self.max_dist is not None:
                dists = _haversine_multi(
                    self.lat_grid_compressed_rad[i_s],
                    self.lon_grid_compressed_rad[i_s],
                    self.lat_grid_compressed_rad[j_s],
                    self.lon_grid_compressed_rad[j_s],
                )
                mask = dists > self.max_dist
                i_s = i_s.compress(~mask)
                j_s = j_s.compress(~mask)
                del dists

            loop_c_ij = self.c_ij_anisotropic_array(i_s, j_s)
            self.cov_ns[i_s, j_s] = loop_c_ij.astype(self.precision)

        self.cov_ns += self.cov_ns.T

        return None

    def c_ij_anisotropic_array(self, i_s, j_s) -> np.ndarray:
        """
        Compute the covariances between pairs of ellipses, at displacements.

        Each ellipse is defined by values from Lxs, Lys, and thetas, with
        standard deviation in stdevs.

        The displacements between each pair of ellipses are x_is and x_js.

        For N ellipses, the number of displacements should be 1/2 * N * (N - 1),
        i.e. the displacement between each pair combination of ellipses. This
        function will return the upper triangular values of the covariance
        matrix (excluding the diagonal).

        `itertools.combinations` is used to handle ordering, so the
        displacements must be ordered in the same way.

        Parameters
        ----------
        i_s : numpy.ndarray
            The row indices for the covariance matrix.
        j_s : numpy.ndarray
            The column indices for the covariance matrix.

        Returns
        -------
        c_ij : numpy.ndarray
            A vector containing the covariance values between each pair of
            ellipses. This will return the components of the upper triangle of
            the covariance matrix as a vector (excluding the diagonal).

        References
        ----------
        1. Paciorek and Schevrish 2006 [PaciorekSchervish]_ Equation 8
        2. Karspeck et al. 2012 [Karspeck]_ Equation 17
        """
        dy, dx = self.disp_fn(
            self.lat_grid_compressed_rad[i_s],
            self.lon_grid_compressed_rad[i_s],
            self.lat_grid_compressed_rad[j_s],
            self.lon_grid_compressed_rad[j_s],
        )
        c_ij = (
            self.stdev_compressed[i_s] * self.stdev_compressed[j_s]
        ) / self.gamma_v_term

        sigma_bars = 0.5 * (self.sigmas[i_s] + self.sigmas[j_s])
        sigma_bar_dets = _det_22_multi(sigma_bars)
        c_ij *= np.sqrt(
            (self.sqrt_dets[i_s] * self.sqrt_dets[j_s]) / sigma_bar_dets
        )
        # NOTE: inner = tau * sqrt(v) * 2
        inner = self.sqrt_v_term * np.sqrt(
            (
                dx * (dx * sigma_bars[:, 3] - dy * sigma_bars[:, 1])
                + dy * (-dx * sigma_bars[:, 2] + dy * sigma_bars[:, 0])
            )
            / sigma_bar_dets
        )
        del sigma_bars, sigma_bar_dets, dy, dx
        c_ij *= np.power(inner, self.v)
        c_ij *= modified_bessel_2nd(self.v, inner)

        return c_ij.astype(self.precision)

    def calculate_cor(self) -> None:
        """Calculate correlation matrix from the covariance matrix"""
        self.cor_ns = cov_2_cor(self.cov_ns)
        return None

    def uncompress_cov(
        self,
        diag_fill_value: Any = np.nan,
        fill_value: Any = np.nan,
    ) -> None:
        """
        Convert the covariance matrix to full grid size.

        Optionally, fill the array with along the diagonal with a
        `diag_fill_value` and off the diagonal with a `fill_value`, which both
        default to `np.nan`.

        Overwrites the `cov_ns` attribute.

        Parameters
        ----------
        diag_fill_value : Any
            Value to assign to diagonal masked values. Defaults to `np.nan`
        fill_value : Any
            Value to assign to off-diagonal masked values. Defaults to `np.nan`
        """
        if not np.sum(~self.data_mask) == self.cov_ns.shape[0]:
            raise ValueError("Data mask and coordinates cannot be aligned")
        fmask = np.logical_or.outer(
            self.data_mask.flatten(), self.data_mask.flatten()
        )
        # Set up uncompressed array
        uncompressed = np.full_like(
            fmask, fill_value=fill_value, dtype=self.precision
        )
        diag_idcs = np.diag_indices_from(uncompressed)
        uncompressed[diag_idcs] = diag_fill_value

        np.place(uncompressed, ~fmask, self.cov_ns)
        self.cov_ns = uncompressed


def _sigma_rot_func_multi(
    Lx: np.ndarray,
    Ly: np.ndarray,
    theta: np.ndarray,
) -> np.ndarray:
    """Flattened Sigma matrices for a list of Lx, Ly, theta triplets."""
    ct = np.cos(theta)
    st = np.sin(theta)
    c2 = np.power(ct, 2)
    s2 = np.power(st, 2)
    cs = np.multiply(ct, st)
    Lx2 = np.power(Lx, 2)
    Ly2 = np.power(Ly, 2)
    del ct, st
    return np.column_stack(
        [
            np.multiply(c2, Lx2) + np.multiply(s2, Ly2),
            np.multiply(cs, Lx2 - Ly2),
            np.multiply(cs, Lx2 - Ly2),
            np.multiply(s2, Lx2) + np.multiply(c2, Ly2),
        ]
    )


def _det_22_single(
    mat: np.ndarray,
) -> np.ndarray:
    """Determinant of a flattened 2 x 2 matrix"""
    return mat[0] * mat[3] - mat[1] * mat[2]


def _det_22_multi(
    mats: np.ndarray,
) -> np.ndarray:
    """Determinants of an array of flattened 2 x 2 matrices"""
    return mats[:, 0] * mats[:, 3] - mats[:, 1] * mats[:, 2]


def _haversine_single(
    lat0: float,
    lon0: float,
    lat1: float,
    lon1: float,
) -> float:
    """Haversine distance between a pair of points"""
    dlon = lon0 - lon1
    dlat = lat0 - lat1

    if abs(dlon) < 1e-6 and abs(dlat) < 1e-6:
        return 0

    a = (
        np.sin(dlat / 2) ** 2
        + np.cos(lat0) * np.cos(lat1) * np.sin(dlon / 2) ** 2
    )
    c = 2 * np.arcsin(np.sqrt(a))

    return RADIUS_OF_EARTH_KM * c


def _haversine_multi(
    lat0: np.ndarray,
    lon0: np.ndarray,
    lat1: np.ndarray,
    lon1: np.ndarray,
) -> np.ndarray:
    """Haversine distance for a list of pairs of points"""
    dlon = lon0 - lon1
    dlat = lat0 - lat1

    a = (
        np.sin(dlat / 2) ** 2
        + np.cos(lat0) * np.cos(lat1) * np.sin(dlon / 2) ** 2
    )
    c = 2 * np.arcsin(np.sqrt(a))

    return RADIUS_OF_EARTH_KM * c


def _mod_mo_disp_single(
    lat0: float,
    lon0: float,
    lat1: float,
    lon1: float,
) -> tuple[float, float]:
    """Modified Met Office displacements between two points"""
    dy = lat0 - lat1
    dx = lon0 - lon1
    dx = dx - TWO_PI if dx > np.pi else dx
    dx = dx + TWO_PI if dx < -np.pi else dx

    y_cos_mean = 0.5 * (np.cos(lat0) + np.cos(lat1))
    dx *= y_cos_mean

    return RADIUS_OF_EARTH_KM * dy, RADIUS_OF_EARTH_KM * dx


def _mo_disp_single(
    lat0: float,
    lon0: float,
    lat1: float,
    lon1: float,
) -> tuple[float, float]:
    """Met Office displacements between two points"""
    dy = lat0 - lat1
    dx = lon0 - lon1
    dx = dx - TWO_PI if dx > np.pi else dx
    dx = dx + TWO_PI if dx < -np.pi else dx

    return RADIUS_OF_EARTH_KM * dy, RADIUS_OF_EARTH_KM * dx


def _mod_mo_disp_multi(
    lat0: np.ndarray,
    lon0: np.ndarray,
    lat1: np.ndarray,
    lon1: np.ndarray,
) -> tuple[np.ndarray, np.ndarray]:
    """Modified Met Office displacements between a list of pairs of points"""
    dy = lat0 - lat1
    dx = lon0 - lon1
    dx[dx > np.pi] -= TWO_PI
    dx[dx < -np.pi] += TWO_PI

    y_cos_mean = 0.5 * (np.cos(lat0) + np.cos(lat1))
    dx *= y_cos_mean

    return RADIUS_OF_EARTH_KM * dy, RADIUS_OF_EARTH_KM * dx


def _mo_disp_multi(
    lat0: np.ndarray,
    lon0: np.ndarray,
    lat1: np.ndarray,
    lon1: np.ndarray,
) -> tuple[np.ndarray, np.ndarray]:
    """Met Office displacements between a list of pairs of points"""
    dy = lat0 - lat1
    dx = lon0 - lon1
    dx[dx > np.pi] -= TWO_PI
    dx[dx < -np.pi] += TWO_PI

    return RADIUS_OF_EARTH_KM * dy, RADIUS_OF_EARTH_KM * dx
