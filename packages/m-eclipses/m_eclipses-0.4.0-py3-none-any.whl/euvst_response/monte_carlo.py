"""
Monte Carlo simulation functions for instrument response analysis.
"""

from __future__ import annotations
from typing import Tuple
import numpy as np
import astropy.units as u
from ndcube import NDCube
from tqdm import tqdm
from .radiometric import (
    apply_exposure_and_poisson, intensity_to_photons, add_telescope_throughput, 
    photons_to_pixel_counts, apply_focusing_optics_psf, to_electrons, add_visible_stray_light, to_dn,
    add_pinhole_visible_light
)
from .pinhole_diffraction import apply_euv_pinhole_diffraction
from .fitting import fit_cube_gauss
from .utils import angle_to_distance


def simulate_once(I_cube: NDCube, t_exp: u.Quantity, det, tel, sim) -> Tuple[NDCube, ...]:
    """
    Run a single Monte Carlo simulation of the instrument response.
    
    Parameters
    ----------
    I_cube : NDCube
        Input intensity cube
    t_exp : u.Quantity
        Exposure time
    det : Detector_SWC or Detector_EIS
        Detector configuration
    tel : Telescope_EUVST or Telescope_EIS
        Telescope configuration
    sim : Simulation
        Simulation configuration
        
    Returns
    -------
    tuple of NDCube
        Signal cubes at each step of the radiometric pipeline:
        (intensity_exp, photons_total, photons_throughput, photons_pixels, 
         photons_focused, photons_euv_pinholes, electrons, electrons_stray, 
         electrons_pinholes, dn)
    """
    # Apply exposure time and Poisson noise
    intensity_exp = apply_exposure_and_poisson(I_cube, t_exp)
    
    # Convert to total photons
    photons_total = intensity_to_photons(intensity_exp)
    
    # Apply telescope optical throughput
    photons_throughput = add_telescope_throughput(photons_total, tel)
    
    # Convert to pixel counts
    photons_pixels = photons_to_pixel_counts(photons_throughput, det.wvl_res, det.plate_scale_length, angle_to_distance(sim.slit_width))

    # Apply focusing optics PSF (primary mirror + diffraction grating)
    if sim.psf:
        photons_focused = apply_focusing_optics_psf(photons_pixels, tel)
    else:
        photons_focused = photons_pixels
    
    # Apply EUV pinhole diffraction effects (after focusing optics, if enabled)
    if sim.enable_pinholes and len(sim.pinhole_sizes) > 0:
        photons_euv_pinholes = apply_euv_pinhole_diffraction(photons_focused, det, sim, tel)
    else:
        photons_euv_pinholes = photons_focused
    
    # Convert to electrons
    electrons = to_electrons(photons_euv_pinholes, t_exp, det)
    
    # Add visible stray light (with filter throughput)
    electrons_stray = add_visible_stray_light(electrons, t_exp, det, sim, tel)
    
    # Add visible light pinhole effects (if enabled)
    if sim.enable_pinholes and len(sim.pinhole_sizes) > 0:
        electrons_pinholes = add_pinhole_visible_light(electrons_stray, t_exp, det, sim, tel)
    else:
        electrons_pinholes = electrons_stray
    
    # Convert to digital numbers
    dn = to_dn(electrons_pinholes, det)

    return (intensity_exp, photons_total, photons_throughput, photons_pixels, 
            photons_focused, photons_euv_pinholes, electrons, electrons_stray, 
            electrons_pinholes, dn)


def monte_carlo(I_cube: NDCube, t_exp: u.Quantity, det, tel, sim, n_iter: int = 5) -> Tuple[NDCube, dict, NDCube, dict]:
    """
    Run Monte Carlo simulations and fit results.
    
    Parameters
    ----------
    I_cube : NDCube
        Input intensity cube
    t_exp : u.Quantity
        Exposure time
    det : Detector_SWC or Detector_EIS
        Detector configuration
    tel : Telescope_EUVST or Telescope_EIS
        Telescope configuration
    sim : Simulation
        Simulation configuration
    n_iter : int
        Number of Monte Carlo iterations
        
    Returns
    -------
    tuple
        (first_dn_signal, dn_fit_results, first_photon_signal, photon_fit_results)
        - first_dn_signal: First iteration DN signal (NDCube)
        - dn_fit_results: Dict with fit data and units stored separately
        - first_photon_signal: First iteration photon signal (NDCube)  
        - photon_fit_results: Dict with fit data and units stored separately
    """
    first_dn_signal, first_photon_signal = None, None
    dn_fit_values_list, photon_fit_values_list = [], []
    
    for i in tqdm(range(n_iter), desc="Monte-Carlo", unit="iter", leave=False):
        # Simulate one run
        (intensity_exp, photons_total, photons_throughput, photons_pixels, 
         photons_focused, photons_euv_pinholes, electrons, electrons_stray, 
         electrons_pinholes, dn) = simulate_once(I_cube, t_exp, det, tel, sim)
        
        # Store first iteration signals only
        if i == 0:
            first_dn_signal = dn
            first_photon_signal = photons_euv_pinholes
        
        # Fit DN signal
        dn_fit_values, dn_fit_units = fit_cube_gauss(dn, n_jobs=sim.ncpu)
        dn_fit_values_list.append(dn_fit_values)
        
        # Fit photon signal
        photon_fit_values, photon_fit_units = fit_cube_gauss(photons_euv_pinholes, n_jobs=sim.ncpu)
        photon_fit_values_list.append(photon_fit_values)
        
    # Stack fit results
    dn_fits_values = np.stack(dn_fit_values_list)
    photon_fits_values = np.stack(photon_fit_values_list)
    
    # Compute statistics on stripped data
    dn_fit_results = {
        "first_fit_data": dn_fits_values[0],
        "mean_data": dn_fits_values.mean(axis=0),
        "std_data": dn_fits_values.std(axis=0),
        "units": dn_fit_units,
    }
    
    photon_fit_results = {
        "first_fit_data": photon_fits_values[0],
        "mean_data": photon_fits_values.mean(axis=0),
        "std_data": photon_fits_values.std(axis=0),
        "units": photon_fit_units,
    }
    
    return first_dn_signal, dn_fit_results, first_photon_signal, photon_fit_results
