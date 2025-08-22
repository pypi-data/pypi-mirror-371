# -*- coding: utf-8 -*-

from __future__ import annotations

import warnings
from pathlib import Path
from typing import Optional, Sequence, Tuple, Union, cast

import matplotlib.dates as mdates
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
from matplotlib.axes import Axes
from matplotlib.colorbar import Colorbar
from matplotlib.colors import LogNorm, Normalize
from matplotlib.figure import Figure
from tabulate import tabulate

from .aerosol1d import Aerosol1D

params = {
    "legend.fontsize": 15,
    "axes.labelsize": 20,
    "axes.titlesize": 20,
    "xtick.labelsize": 13,
    "ytick.labelsize": 13,
    "figure.figsize": (19, 10),
}
plt.rcParams.update(params)


class Aerosol2D(Aerosol1D):
    """
    A class for managing time-resolved, size-distributed aerosol data.

    This class extends `Aerosol1D` to handle datasets that contain particle
    size distributions (e.g., number, mass, or surface area concentration
    across particle size bins). It supports transformation between physical
    representations (dN, dS, dV, dW), visualization, activity segmentation,
    and summary statistics including PM values and particle size metrics.

    Parameters
    ----------
    dataframe : pandas.DataFrame
        A DataFrame containing the data to load. The first column should
        contain time stamps or be the DataFrame index. The second column should
        be the total concentration. All remaining columns must represent
        concentration values in size bins with bin midpoints as column headers.

    Notes
    -----
    All data handling is done with `pandas`. Input DataFrames are expected to
    have particle size bin midpoints as column headers, and the class assumes
    these are numeric and represent diameters in nanometers.
    """

    def __init__(self, dataframe):
        super().__init__(dataframe)

    @property
    def bin_edges(self):
        """
        List of bin edges in nm

        Returns
        -------
        float
            bin edges ( "nm" ).
        """
        value = self._meta.get("bin_edges")
        if value is None:
            raise ValueError("bin_edges are not set.")
        return value

    @property
    def bin_mids(self):
        """
        List of bin mids in nm

        Returns
        -------
        float
            bin mids ( "nm" ).
        """
        bin_mids = self._meta.get("bin_mids")
        if bin_mids is None:
            raise ValueError("bin_mids are not set. Please set bin_mids.")
        return bin_mids

    @property
    def density(self) -> float:
        """
        Unit of the measurements.

        Returns
        -------
        float
            Particle density in "g/cm³".
        """
        density = self._meta.get("density")
        if not isinstance(density, (int, float)):
            # covers None or any other wrong type
            raise ValueError("Density is not set. Please set density.")
        return float(density)

    @property
    def metadata(self):
        """
        Meta data as extracted upon loading the data

        Returns
        -------
        dict
            Meta data related to the loaded data.

        """
        return self._meta

    @property
    def size_data(self):
        """
        Sizebin data

        Returns
        -------
        pandas.DataFrame
            Concentration data from all sizebins in the dataset.

        """
        return self.data[self._sizebin_headers]

    @property
    def _sizebin_headers(self):
        """
        Headers of the sizebin concentration columns within main DataFrame

        Returns
        -------
        list
            Headers to access sizebin columns.

        Raises
        ------
        ValueError
            If bin mids are not present.
        """
        if self.bin_mids is None:
            raise ValueError("bin_mids are not set. Please set bin_mids.")
        return [str(x) for x in self.bin_mids]

    ###########################################################################
    """############################# Functions #############################"""
    ###########################################################################

    def convert_to_mass_concentration(self, *, inplace: bool = True) -> "Aerosol2D":
        """
        Convert particle size distribution data to mass concentration (ug/m³) based on current data type.

        Parameters
        ----------
        inplace : bool, optional
            If True (default), modifies the current instance in-place.
            If False, returns a new instance with converted mass concentration data.

        Returns
        -------
        self or aerosolxd
            Updated instance with mass concentration data, either in-place or as a copy.
        """
        if "dW" in self.dtype:
            print("Data is already in mass concentration (ug/m³).")
            return self if inplace else self.copy_self()

        if self.bin_mids is None:
            raise ValueError(
                "bin_mids are not set. Please set bin_mids before converting to mass concentration."
            )
        bin_radii = self.bin_mids / 2.0  # convert diameter to radius in nm

        if "dS" in self.dtype:
            # Convert from surface area to number, then to volume, then to mass
            surface_area_per_particle = 4 * np.pi * bin_radii**2
            number_distribution = self.size_data.copy() / surface_area_per_particle
            volume_per_particle = (4 / 3) * np.pi * bin_radii**3
            volume_distribution = number_distribution * volume_per_particle
            mass_distribution = (
                volume_distribution * self.density * 1e-9
            )  # convert nm³ to ug

        elif "dV" in self.dtype:
            # Convert from volume to mass directly
            mass_distribution = self.size_data.copy() * self.density * 1e-9

        elif "dN" in self.dtype:
            # Convert from number to volume, then to mass
            volume_per_particle = (4 / 3) * np.pi * bin_radii**3
            volume_distribution = self.size_data.copy() * volume_per_particle
            mass_distribution = volume_distribution * self.density * 1e-9

        else:
            raise ValueError("Unknown data type for conversion.")

        # Apply the results
        target_instance = self if inplace else self.copy_self()
        target_instance._data[self._sizebin_headers] = mass_distribution
        target_instance._meta["unit"] = "ug/m³"
        target_instance._meta["dtype"] = "dW"

        # Update total concentration
        # Ensure unnormalized data before summing
        if "/dlogDp" in target_instance.dtype:
            unnormalized = target_instance.unnormalize_logdp(inplace=False)
            sum_data = unnormalized.size_data.sum(axis=1)
        else:
            sum_data = mass_distribution.sum(axis=1)

        target_instance._data["Total Concentration"] = sum_data

        return target_instance

    ###########################################################################

    def convert_to_number_concentration(self, *, inplace: bool = True) -> "Aerosol2D":
        """
        Convert particle size distribution data to number concentration (cm⁻³)
        from the current data type.

        Parameters
        ----------
        inplace : bool, optional
            If True (default), modifies the current instance in-place.
            If False, returns a new instance with number concentration data.

        Returns
        -------
        self or aerosolxd
            Updated instance with number concentration data, either in-place or as a copy.
        """
        if "dN" in self.dtype:
            print("Data is already in number concentration (cm⁻³).")
            return self if inplace else self.copy_self()

        bin_radii = self.bin_mids / 2.0  # nm

        if "dV" in self.dtype:
            # Convert from volume to number
            volume_per_particle = (4 / 3) * np.pi * bin_radii**3  # nm³
            number_distribution = self.size_data.copy() / volume_per_particle

        elif "dW" in self.dtype:
            # Convert from mass to volume, then to number
            volume_distribution = self.size_data.copy() / self.density * 1e9  # nm³
            volume_per_particle = (4 / 3) * np.pi * bin_radii**3
            number_distribution = volume_distribution / volume_per_particle

        elif "dS" in self.dtype:
            # Convert from surface area to number
            surface_area_per_particle = 4 * np.pi * bin_radii**2
            number_distribution = self.size_data.copy() / surface_area_per_particle

        else:
            raise ValueError("Unknown data type for conversion.")

        # Apply the results
        target_instance = self if inplace else self.copy_self()
        target_instance._data[self._sizebin_headers] = number_distribution
        target_instance._meta["unit"] = "cm⁻³"
        target_instance._meta["dtype"] = "dN"

        # Update total concentration
        # Ensure unnormalized data before summing
        if "/dlogDp" in target_instance.dtype:
            unnormalized = target_instance.unnormalize_logdp(inplace=False)
            sum_data = unnormalized.size_data.sum(axis=1)
        else:
            sum_data = number_distribution.sum(axis=1)

        target_instance._data["Total Concentration"] = sum_data

        return target_instance

    ###########################################################################

    def convert_to_surface_concentration(self, inplace: bool = True):
        """
        Convert particle size distribution data to surface area concentration (nm²/cm³)
        based on the current data type.

        Parameters
        ----------
        inplace : bool, optional
            If True (default), modifies the current instance in-place.
            If False, returns a new instance with surface area concentration data.

        Returns
        -------
        self or aerosolxd
            Updated instance with surface area concentration data, either in-place or as a copy.
        """
        if "dS" in self.dtype:
            print("Data is already in surface area concentration (nm²/cm³).")
            return self if inplace else self.copy_self()

        bin_radii = self.bin_mids / 2.0  # in nm
        surface_area_per_particle = 4 * np.pi * bin_radii**2
        volume_per_particle = (4 / 3) * np.pi * bin_radii**3

        if "dV" in self.dtype:
            # Volume -> Number -> Surface Area
            number_distribution = self.size_data.copy() / volume_per_particle
            surface_area_distribution = number_distribution * surface_area_per_particle

        elif "dW" in self.dtype:
            # Mass -> Volume -> Number -> Surface Area
            volume_distribution = self.size_data.copy() / self.density * 1e9  # nm³/cm³
            number_distribution = volume_distribution / volume_per_particle
            surface_area_distribution = number_distribution * surface_area_per_particle

        elif "dN" in self.dtype:
            # Number -> Surface Area
            surface_area_distribution = (
                self.size_data.copy() * surface_area_per_particle
            )

        else:
            print("Unknown data type for conversion.")
            return None

        # Apply the results
        target_instance = self if inplace else self.copy_self()
        target_instance._data[self._sizebin_headers] = surface_area_distribution
        target_instance._meta["unit"] = "nm²/cm³"
        target_instance._meta["dtype"] = "dS"

        # Update total concentration
        # Ensure unnormalized data before summing
        if "/dlogDp" in target_instance.dtype:
            unnormalized = target_instance.unnormalize_logdp(inplace=False)
            sum_data = unnormalized.size_data.sum(axis=1)
        else:
            sum_data = surface_area_distribution.sum(axis=1)
        target_instance._data["Total Concentration"] = sum_data

        return target_instance

    ###########################################################################

    def convert_to_volume_concentration(self, inplace: bool = True):
        """
        Convert particle size distribution data to volume concentration (nm³/cm³)
        based on the current data type.

        Parameters
        ----------
        inplace : bool, optional
            If True (default), modifies the current instance in-place.
            If False, returns a new instance with volume concentration data.

        Returns
        -------
        self or aerosolxd
            Updated instance with volume concentration data, either in-place or as a copy.
        """
        if "dV" in self.dtype:
            print("Data is already in volume concentration (nm³/cm³).")
            return self if inplace else self.copy_self()

        bin_radii = self.bin_mids / 2.0  # in nm
        volume_per_particle = (4 / 3) * np.pi * bin_radii**3
        surface_area_per_particle = 4 * np.pi * bin_radii**2

        if "dS" in self.dtype:
            # Surface Area -> Number -> Volume
            number_distribution = self.size_data.copy() / surface_area_per_particle
            volume_distribution = number_distribution * volume_per_particle

        elif "dW" in self.dtype:
            # Mass -> Volume
            volume_distribution = self.size_data.copy() / self.density * 1e9  # nm³/cm³

        elif "dN" in self.dtype:
            # Number -> Volume
            volume_distribution = self.size_data.copy() * volume_per_particle

        else:
            print("Unknown data type for conversion.")
            return None

        # Apply the results
        target_instance = self if inplace else self.copy_self()
        target_instance._data[self._sizebin_headers] = volume_distribution
        target_instance._meta["unit"] = "nm³/cm³"
        target_instance._meta["dtype"] = "dV"

        # Update total concentration
        # Ensure unnormalized data before summing
        if "/dlogDp" in target_instance.dtype:
            unnormalized = target_instance.unnormalize_logdp(inplace=False)
            sum_data = unnormalized.size_data.sum(axis=1)
        else:
            sum_data = volume_distribution.sum(axis=1)
        target_instance._data["Total Concentration"] = sum_data

        return target_instance

    ###########################################################################

    def set_density(self, density: Union[float, int] = 1.0):
        """
        Set density of the aerosol particles in g/cm3

        Parameters
        ----------
        density : float
            Density of the aerosol particles.

        Returns
        -------
        class: Aerosol2D
            The updated density data. If the data was already mass-based then the
            updated density is applied immidiatly.
        """
        if "dW" in self.dtype:
            unit_density_data = self.size_data.copy() / self.density
            new_density_data = unit_density_data * density
            self._data[self._sizebin_headers] = new_density_data

        self._meta["density"] = density
        return self

    ###########################################################################

    def normalize_logdp(self, inplace: bool = True):
        """
        Normalize the size distribution data by dlogDp to obtain, e.g., dN/dlogDp.

        Parameters
        ----------
        inplace : bool, optional
            If True, modifies current instance in-place.
            If False, returns a new instance with normalized data.

        Returns
        -------
        self or aerosolxd
            Instance with normalized size distribution data.
        """
        log_bin_edges = np.log10(self.bin_edges)
        dlog_dp = np.diff(log_bin_edges)

        bin_columns = self._sizebin_headers

        if len(dlog_dp) != len(bin_columns):
            raise ValueError("Mismatch between number of bins and dlogDp array.")

        normalized_data = self._data[bin_columns].copy().div(dlog_dp, axis=1)

        target = self if inplace else self.copy_self()
        target._data[bin_columns] = normalized_data

        if "/dlogDp" not in self.dtype:
            target._meta["dtype"] = f"{self.dtype}/dlogDp"

        return target

    ###########################################################################

    def unnormalize_logdp(self, inplace: bool = True):
        """
        Reverse dlogDp normalization (e.g., convert dN/dlogDp to dN).

        Parameters
        ----------
        inplace : bool, optional
            If True, modifies current instance in-place.
            If False, returns a new instance with unnormalized data.

        Returns
        -------
        self or aerosolxd
            Instance with unnormalized size distribution data.
        """
        log_bin_edges = np.log10(self.bin_edges)
        dlog_dp = np.diff(log_bin_edges)

        bin_columns = self._sizebin_headers

        if len(dlog_dp) != len(bin_columns):
            raise ValueError("Mismatch between number of bins and dlogDp array.")

        unnormalized_data = self._data[bin_columns].copy().mul(dlog_dp, axis=1)

        target = self if inplace else self.copy_self()
        target._data[bin_columns] = unnormalized_data

        if "/dlogDp" in self.dtype:
            target._meta["dtype"] = self.dtype.replace("/dlogDp", "")
        else:
            print("Warning: dtype does not contain '/dlogDp'; nothing was changed.")

        return target

    ###########################################################################

    def plot_psd(
        self, activities: Optional[list[str]] = None, normalize: bool = True, ax=None
    ):
        """
        Plot the average particle size distribution (PSD) for the entire dataset and optionally selected activities.

        Parameters
        ----------
        activities : list of str, optional
            List of activity names to include. If None, all defined activities are plotted.
        normalize : bool, optional
            Whether to normalize PSD to dlogDp before plotting. If data is already normalized, will respect that.
        ax : matplotlib.axes.Axes, optional
            Optional matplotlib Axes object to plot on.

        Returns
        -------
        fig : matplotlib.figure.Figure
            The matplotlib Figure object.
        ax : matplotlib.axes.Axes
            The matplotlib Axes object.
        """
        new_fig_created = False
        if ax is None:
            fig, ax = plt.subplots(figsize=(8, 5))
            new_fig_created = True
        else:
            fig = ax.figure

        # Determine normalization state
        is_already_normalized = "/dlogDp" in self.dtype
        bin_columns = self._sizebin_headers
        bin_mids = self.bin_mids
        log_bin_edges = np.log10(self.bin_edges)
        dlog_dp = np.diff(log_bin_edges)
        factor_series = pd.Series(dlog_dp, index=bin_columns)

        # Determine label based on normalization intent
        if normalize and not is_already_normalized:
            y_label_dtype = f"{self.dtype}/dlogDp"
        elif not normalize and is_already_normalized:
            y_label_dtype = self.dtype.replace("/dlogDp", "")
        else:
            y_label_dtype = self.dtype
        ax.set_ylabel(f"{y_label_dtype}, {self.unit}")

        # Colormap for activities
        all_activities = sorted(self._activity_periods.keys())
        color_map = plt.colormaps.get_cmap("gist_ncar")
        activity_colors = {
            activity: color_map(i / max(1, len(all_activities)))
            for i, activity in enumerate(all_activities)
        }

        # Plot selected or all activities
        selected_activities = activities if activities is not None else self.activities

        for activity in selected_activities:
            if activity not in self.activities:
                print(f"Activity '{activity}' not found. Skipping.")
                continue

            subset = self.data[self.data[activity]]
            if subset.empty:
                continue

            if normalize:
                if not is_already_normalized:
                    act_data = subset[bin_columns].copy().div(factor_series, axis=1)
                else:
                    act_data = subset[bin_columns].copy()
            else:
                if is_already_normalized:
                    act_data = subset[bin_columns].copy().mul(factor_series, axis=1)
                else:
                    act_data = subset[bin_columns].copy()

            avg_act = act_data.mean()
            std_act = act_data.std()
            color = activity_colors.get(activity, None)

            ax.plot(bin_mids, avg_act, label=activity, color=color or "black")
            ax.fill_between(
                bin_mids,
                avg_act - std_act,
                avg_act + std_act,
                color=color or "black",
                alpha=0.3,
            )
        ax.set_xscale("log")
        ax.set_xlabel("Particle diameter (nm)")
        ax.grid(True, which="both", linestyle="--", linewidth=0.5)
        ax.legend()
        if new_fig_created:
            fig.tight_layout()

        return fig, ax

    ###########################################################################

    def correct_diffusion_losses(
        self,
        D_tube: float,
        L: float,
        Q: float,
        T: float = 293,
        P: float = 101300,
        inplace: bool = True,
    ):
        """
        Correct for diffusion losses in a sampling tube based on tubing geometry,
        flow conditions, and particle sizes.

        Parameters
        ----------
        D_tube : float
            Diameter of the tubing (in meters).
        L : float
            Length of the tubing (in meters).
        Q : float
            Volumetric flow through the tubing (in L/min).
        T : float, optional
            Temperature in Kelvin. Default is 293 K.
        P : float, optional
            Pressure in Pascals. Default is 101300 Pa.
        inplace : bool, optional
            Whether to modify the current instance or return a new one. Default is True.

        Returns
        -------
        Aerosol2D
            Instance with diffusion-corrected sizebin data.
        """
        # Constants
        k = 1.380649e-23  # Boltzmann constant
        Dp = np.array(self.bin_mids) * 1e-9  # Convert nm to meters
        Q_m3s = Q / (1000 * 60)  # Convert L/min to m³/s
        A = 0.25 * np.pi * D_tube**2
        V = Q_m3s / A  # Flow velocity (m/s)

        # Mean free path (adjusted for P, T)
        mfp_std = 66.5e-9  # m
        mfp = (
            mfp_std * (101e3 / P) * (T / 293.15) * ((1 + 110 / 293.15) / (1 + 110 / T))
        )

        # Gas properties
        eta_std = 1.708e-5
        eta = (
            eta_std * (T / 273.15) ** 1.5 * (393.396 / (T + 120.246))
        )  # dynamic viscosity
        rho = 1.293 * (273.15 / T) * (P / 101300)  # gas density

        # Knudsen number and slip correction
        Kn = 2 * mfp / Dp
        Cc = 1 + Kn * (1.142 + 0.558 * np.exp(-0.999 / Kn))

        # Reynolds number
        Re = rho * V * D_tube / eta

        # Diffusion coefficient
        Dc = k * T * Cc / (3 * np.pi * eta * Dp)
        Sc = eta / (rho * Dc)
        xi = np.pi * Dc * L / Q_m3s

        # Sherwood number
        if Re < 2000:
            Sh = 3.66 + 0.2672 / (xi + 0.10079 * xi ** (1 / 3))
        else:
            Sh = 0.0118 * Re ** (7 / 8) * Sc ** (1 / 3)

        # Diffusion efficiency
        eff = np.exp(-Sh * xi)

        # Apply correction
        corrected = self.copy_self() if not inplace else self
        size_cols = corrected._sizebin_headers
        corrected._data[size_cols] = corrected._data[size_cols].div(eff, axis=1)
        corrected._data["Total Concentration"] = corrected._data[size_cols].sum(axis=1)

        # Store efficiency in metadata for reference
        corrected._meta["diffusion_efficiency"] = eff.tolist()
        corrected._meta["diffusion_loss_corrected"] = True

        return corrected

    ###########################################################################

    def plot_timeseries(
        self,
        y_tot: Tuple[float, float] = (0.0, 0.0),
        y_3d: Tuple[float, float] = (1.0, 0.0),
        log: bool = True,
        ax1: Optional[Axes] = None,
        ax2: Optional[Axes] = None,
        mark_activities: bool | Sequence[str] = False,
    ) -> tuple[Figure, Axes, Axes, Colorbar]:
        """
        Plot total concentration (top) and a size-resolved time series (bottom).

        Parameters
        ----------
        y_tot : (ymin, ymax)
            Y-limits for total concentration. (0, 0) => auto.
        y_3d : (zmin, zmax)
            Color scale limits for the mesh. (1, 0) => auto (special sentinel).
            If zmin != 1, values are clamped to >= zmin.
            If zmax == 0, zmax is taken from the data maximum after clamping.
        log : bool
            If True, try logarithmic color scaling. Falls back to linear when
            no positive finite values exist in the plotted data.
        ax1, ax2 : Axes
            Provide both or neither. If neither, new figure/axes are created.
        mark_activities : bool | list[str]
            Passed to `plot_total_conc()`.

        Returns
        -------
        fig, ax1, ax2, cbar
        """
        if (ax1 is None) != (ax2 is None):
            raise ValueError("You must provide both ax1 and ax2, or neither.")

        # ---- Create new axes if needed ----
        if ax1 is None and ax2 is None:
            newplot = True
            fig, (ax1, ax2) = plt.subplots(nrows=2, sharex=True, figsize=(10, 6))
        else:
            assert ax1 is not None and ax2 is not None
            fig = cast(Figure, ax1.figure)
            newplot = False

        # ----- Data shortcuts -----
        time = self.time  # 1D DatetimeIndex/array
        total = self.total_concentration  # 1D array-like
        data = self.size_data  # 2D array-like (time x size)
        bin_edges = self.bin_edges  # 1D array-like (size edges)

        # ---- Top panel: total concentration ----
        _, ax1_new = self.plot_total_conc(ax=ax1, mark_activities=mark_activities)
        ax1 = ax1_new

        # Y-limits for the total concentration plot
        if y_tot != (0.0, 0.0):
            ymin = y_tot[0] if y_tot[0] != 0 else float(np.nanmin(total) * 0.98)
            ymax = y_tot[1] if y_tot[1] != 0 else float(np.nanmax(total) * 1.02)
            if np.isfinite([ymin, ymax]).all() and ymax > ymin:
                ax1.set_ylim(ymin, ymax)

        # ---- Mesh grid in time/size ----
        if len(time) > 1:
            dt = (time[1] - time[0]) / 2
        else:
            # Fallback delta (1 minute) if only a single timestamp exists
            dt = pd.Timedelta(minutes=1)

        time_edges = pd.DatetimeIndex(np.append(time - dt, [time[-1] + dt]))
        x_grid, y_grid = np.meshgrid(time_edges, bin_edges, indexing="ij")

        # ---- Prepare Z and handle bounds ----
        Z = np.asarray(
            data, dtype=float
        )  # shape (len(time), len(size_bins)-1) typically
        finite = np.isfinite(Z)

        # Interpret y_3d semantics
        auto_scale = y_3d == (1.0, 0.0)
        if not auto_scale:
            zmin_in, zmax_in = y_3d
            # Clamp lower bound if explicitly set (zmin != 1 sentinel)
            if zmin_in != 1.0:
                Z = np.maximum(Z, zmin_in)
            # If zmax is 0, pick from data after clamping
            if zmax_in == 0.0:
                zmax_in = float(np.nanmax(Z)) if np.any(np.isfinite(Z)) else 1.0
            zmin_auto = float(np.nanmin(Z)) if np.any(np.isfinite(Z)) else 0.0
            zmax_auto = float(np.nanmax(Z)) if np.any(np.isfinite(Z)) else 1.0
            zmin = float(zmin_in if zmin_in != 1.0 else zmin_auto)
            zmax = float(zmax_in if zmax_in != 0.0 else zmax_auto)
        else:
            # Pure auto limits from the data (we’ll refine for log below)
            if np.any(finite):
                zmin = float(np.nanmin(Z))
                zmax = float(np.nanmax(Z))
            else:
                zmin, zmax = 0.0, 1.0

        # ---- Choose scaling (log with graceful fallback) ----
        use_log = bool(log)

        if use_log:
            # LogNorm demands strictly positive finite bounds
            positive = np.isfinite(Z) & (Z > 0)
            if not np.any(positive):
                warnings.warn(
                    "plot_timeseries: no positive finite values for log scale; "
                    "falling back to linear.",
                    RuntimeWarning,
                )
                use_log = False
            else:
                # For log autoscale or if user gave non-positive zmin, pick smallest positive
                vmin_pos = float(np.nanmin(Z[positive]))
                vmax_pos = float(np.nanmax(Z[positive]))
                # Ensure vmin/vmax are valid and ordered
                vmin = (
                    vmin_pos
                    if (auto_scale or zmin <= 0 or not np.isfinite(zmin))
                    else max(zmin, np.nextafter(0.0, 1.0))
                )
                vmax = vmax_pos if (auto_scale or not np.isfinite(zmax)) else zmax
                # Guard against degeneracy
                if (
                    not np.isfinite(vmin)
                    or not np.isfinite(vmax)
                    or vmin <= 0
                    or vmax <= vmin
                ):
                    # Last-resort sane defaults
                    vmin = max(np.nextafter(0.0, 1.0), 1e-12)
                    vmax = vmin * 10.0
                norm = LogNorm(vmin=vmin, vmax=vmax)
        if not use_log:
            # Linear Normalize; allow zeros/negatives
            vmin = zmin
            vmax = zmax
            # If bounds are invalid/degenerate, choose safe defaults
            if (not np.isfinite(vmin)) or (not np.isfinite(vmax)) or (vmax <= vmin):
                if np.any(finite):
                    vmin = float(np.nanmin(Z[finite]))
                    vmax = float(np.nanmax(Z[finite]))
                else:
                    vmin, vmax = 0.0, 1.0
                if not np.isfinite(vmin) or not np.isfinite(vmax) or vmax <= vmin:
                    vmin, vmax = 0.0, 1.0
            norm = Normalize(vmin=vmin, vmax=vmax)

        # ---- Mesh plot ----
        assert ax2 is not None
        mesh = ax2.pcolormesh(
            x_grid,
            y_grid,
            Z,
            cmap="jet",  # keep your existing colormap
            norm=norm,
            shading="flat",  # keep your choice; 'auto' also OK
        )

        # Y axis (size) log-scaling and labels
        ax2.set_yscale("log")
        ax2.set_ylabel("Dp, nm")
        ax2.set_xlabel("Time")
        if newplot:
            ax1.set_xlabel("")

        # Date formatting
        ax2.xaxis.set_major_formatter(
            mdates.ConciseDateFormatter(mdates.AutoDateLocator())
        )

        # Colorbar
        cbar: Colorbar = fig.colorbar(mesh, ax=[ax1, ax2])
        cbar.set_label(f"{self.dtype}, {self.unit}")

        # Styling
        ax1.tick_params(axis="y", which="both", direction="out", length=6, width=2)
        ax2.tick_params(axis="y", which="both", direction="out", length=6, width=2)

        return fig, ax1, ax2, cbar

    ###########################################################################

    def summarize(self, filename: Optional[str | Path] = None) -> pd.DataFrame:
        """
        Summarize aerosol characteristics for each activity period.

        Metrics included for each segment:
        - PNC (cm⁻³): Particle number concentration (sum across number bins)
        - PM1, PM2.5, PM4 (respirable), PM10 (inhalable) in µg/m³, calculated using partial bin inclusion
        - Total mass concentration (µg/m³)
        - Mode diameter (nm): Bin midpoint with max number conc per timestep
        - Median diameter (nm): 50% of cumulative number distribution
        - GMD (nm): Geometric mean diameter (log-space, number-weighted)

        All metrics include standard deviation across the segment.

        Parameters
        ----------
        filename : str, optional
            If provided, saves the summary to Excel.

        Returns
        -------
        pd.DataFrame
            Summary statistics for all defined activities.
        """

        def partial_mass_sum(mass_df, bin_edges, bin_mids, cutoff):
            result = pd.Series(0.0, index=mass_df.index)
            for i, mid in enumerate(bin_mids):
                d_lo, d_hi = bin_edges[i], bin_edges[i + 1]
                col = str(mid)
                if d_hi <= cutoff:
                    result += mass_df[col]
                elif d_lo < cutoff < d_hi:
                    frac = (cutoff - d_lo) / (d_hi - d_lo)
                    result += mass_df[col] * frac
            return result

        number_data = self.convert_to_number_concentration(inplace=False)
        mass_data = self.convert_to_mass_concentration(inplace=False)
        bin_edges = np.array(self.bin_edges)
        bin_mids = np.array(self.bin_mids)

        rows = []

        for activity in self.activities:
            mask = self.data[activity]
            if mask.sum() == 0:
                continue

            num_df = number_data.size_data.loc[mask]
            mass_df = mass_data.size_data.loc[mask]

            # PNC
            pnc_series = num_df.sum(axis=1)
            pnc = pnc_series.mean()
            pnc_std = pnc_series.std()

            # PM fractions (with partial bins)
            pm1_series = partial_mass_sum(mass_df, bin_edges, bin_mids, 1000)
            pm2_5_series = partial_mass_sum(mass_df, bin_edges, bin_mids, 2500)
            pm4_series = partial_mass_sum(mass_df, bin_edges, bin_mids, 4000)
            pm10_series = partial_mass_sum(mass_df, bin_edges, bin_mids, 10000)

            pm1, pm1_std = pm1_series.mean(), pm1_series.std()
            pm2_5, pm2_5_std = pm2_5_series.mean(), pm2_5_series.std()
            pm4, pm4_std = pm4_series.mean(), pm4_series.std()
            pm10, pm10_std = pm10_series.mean(), pm10_series.std()

            # Total mass
            total_mass_series = mass_df.sum(axis=1)
            total_mass = total_mass_series.mean()
            total_mass_std = total_mass_series.std()

            # Per-time-step size metrics
            mode_d_list = []
            median_d_list = []
            gmd_list = []

            for _, row in num_df.iterrows():
                dist = row.values
                total = dist.sum()
                if total == 0:
                    continue

                # Mode diameter
                mode_d = bin_mids[np.argmax(dist)]
                mode_d_list.append(mode_d)

                # Median diameter
                cum = np.cumsum(dist)
                cum /= cum[-1]
                median_idx = np.searchsorted(cum, 0.5)
                median_d = bin_mids[median_idx]
                median_d_list.append(median_d)

                # GMD
                gmd = np.exp(np.sum(np.log(bin_mids) * dist) / total)
                gmd_list.append(gmd)

            # Final size stats
            mode_d = np.mean(mode_d_list)
            mode_d_std = np.std(mode_d_list)
            median_d = np.mean(median_d_list)
            median_d_std = np.std(median_d_list)
            gmd = np.mean(gmd_list)
            gmd_std = np.std(gmd_list)

            # Store row
            rows.append(
                [
                    activity,
                    round(pnc, 2),
                    round(pnc_std, 2),
                    round(pm1, 2),
                    round(pm1_std, 2),
                    round(pm2_5, 2),
                    round(pm2_5_std, 2),
                    round(pm4, 2),
                    round(pm4_std, 2),
                    round(pm10, 2),
                    round(pm10_std, 2),
                    round(total_mass, 2),
                    round(total_mass_std, 2),
                    round(mode_d, 1),
                    round(mode_d_std, 1),
                    round(median_d, 1),
                    round(median_d_std, 1),
                    round(gmd, 1),
                    round(gmd_std, 1),
                ]
            )

        summary = pd.DataFrame(
            rows,
            columns=[
                "Segment",
                "PNC (cm⁻³)",
                "PNC std (cm⁻³)",
                "PM1 (µg/m³)",
                "PM1 std (µg/m³)",
                "PM2.5 (µg/m³)",
                "PM2.5 std (µg/m³)",
                "PM4 (µg/m³)",
                "PM4 std (µg/m³)",
                "PM10 (µg/m³)",
                "PM10 std (µg/m³)",
                "Total Mass (µg/m³)",
                "Total Mass std (µg/m³)",
                "Mode Dp (nm)",
                "Mode Dp std (nm)",
                "Median Dp (nm)",
                "Median Dp std (nm)",
                "GMD (nm)",
                "GMD std (nm)",
            ],
        )

        if filename:
            summary.to_excel(filename, index=False)
            print(f"Summary saved to: {filename}")

        summary_t = summary.set_index("Segment").T
        idx_reset = summary_t.reset_index()
        print("\nSummary of aerosol properties (transposed):\n")
        print(
            tabulate(
                idx_reset.values,  # rows → ndarray of iterables
                headers=idx_reset.columns.tolist(),  # ← convert Index → list[str]
                tablefmt="pretty",
                floatfmt=".3f",
            )
        )

        return summary
