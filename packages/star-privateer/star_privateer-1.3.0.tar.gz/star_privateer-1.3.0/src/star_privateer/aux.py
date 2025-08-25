import star_privateer as sp
from astropy.io import fits
from scipy import signal
import numpy as np
import pandas as pd
import os
from pathlib import Path

'''
Copyright 2024 Sylvain Breton

This file is part of star-privateer, an open-source software distributed
under MIT License.
'''

def closest_odd (a) :
  if a%2==1:
    return a
  else :
    return a-1

def gauss (x, a, mu, hwhm) :
  """
  Gaussian profile. 
  Width is computed as half width as half maximum. 

  Parameters
  ----------
  x : ndarray
    Frequency vector.

  a : float
    Amplitude

  mu : float
    Central frequency.

  hwhm : float
    Half width at half maximum
  """
  return a * np.exp (- 1/2 * (np.sqrt(2*np.log(2))*(x-mu) / hwhm)**2)

def lor (x, a, mu, sigma) :
  return a / (1 + 4 * ((x-mu)**2 / sigma**2))

def rebin (a, nrebin=4) :
    """
    Rebin a vector according to ``nrebin`` factor.
    """
    if a.size%nrebin!= 0 :
        a = a[:-(a.size%nrebin)]
    a = np.nanmean (a.reshape (-1, nrebin), axis=1)
    return a

def apply_fir (t, s, cut=55, numtaps=10001,
               desired=None, bands=None) :
  '''
  Apply high-pass finite impulse response
  filter.

  Parameters
  ----------
  t : float or array-like
    Vector of time stamps (if array) or sampling time (if float).
  '''
  if type (t) in [float, np.float_, np.float64,
                      np.float32] :
    dt = t
  else :
    dt = np.median (np.diff (t))
  numtaps = np.minimum (closest_odd(s.size//3 - 1), numtaps) 
  fs = 1 / (dt*86400)  
  if bands is None :
    f_cut = 1 / (cut*86400)
    bands=[0, f_cut, f_cut, fs/2]
  if desired is None :
    desired=[0,0,1,1] 
  b = signal.firls (numtaps, bands, desired, fs=fs)
  s = signal.filtfilt (b, [1.0], s)
  return s

def preprocess (t, s, cut=55, numtaps=10001,
                bands=None, desired=None) :
  '''
  Preprocess a time series by substracting
  its mean value and applying a FIR filter (see ``scipy.signal.firls``).
  By default the filter will be a high-filter
  with period cutoff specified by ``cut``, and is applied using
  ``scipy.signal.filtfilt``. 

  Parameters
  ----------
  t : float or array-like
    Vector of time stamps (if array) or sampling time (if float).
    Must be provided in days.

  s : array-like
    Time series

  cut : float
    Filter cutoff (in days) in case the default high-pass filter
    is used. Optional, default ``55``.

  numtaps : int
    Number of taps in the filter. Must be odd, default to ``10001``.
    See ``scipy.signal.firls`` documentation.

  bands : array-like 
    Frequency bands (in Hz) for the filter. Override ``cut`` if
    provided. See ``scipy.signal.firls`` documentation.
    Optional, default ``None``.
  
  desired : array-like 
    Corresponding gain for the filter if ``bands`` is provided.
    Optional, default ``None``.

  Returns 
  -------
  ndarray
    The filtered time series.
  '''
  # Setting median to 0.
  s = s - np.mean (s)
  # The low-frequency trend need to be filtered out.
  # Applying a FIR.
  s = apply_fir (t, s, cut=cut, numtaps=numtaps,
                 bands=bands, desired=desired)
  # Setting median to 0.
  s = s - np.mean (s)
  return s

def load_k2_example () :
    '''
    Load K2 light curve example for MSAP4-01
    and MSAP4-02 demonstrators.
    '''
    filename = get_target_filename (sp.timeseries, 
                      'epic211015853', filetype='fits')
    with filename as f :
      hdul = fits.open (f)
      hdu = hdul[1]
      t = np.array (hdu.data['TIME'])
      s = np.array (hdu.data['PDCSAP_FLUX'])
      mask = ~(np.isnan (t) | np.isnan (s))
      t = t[mask]
      s = s[mask]
      dt = np.median (np.diff (t))
      hdul.close ()
    s = s - np.mean (s)
    s[np.isnan (s)] = 0
    return t, s, dt

def get_available_kic () :
    '''
    Returns list of available kics in the module.
    '''
    return [3733735, 8006161, 10644253]

def load_kepler_example (kic=3733735) :
    '''
    Load one of the Kepler example light curves provided
    with the module.

    Parameters
    ----------
    kic : int
      The Kepler identifier of the star to look for. 

    Returns
    -------
    tuple 
      Tuple with timestamps, flux time series and temporal sampling.
    '''
    available = get_available_kic ()
    if kic in available :
      filename = get_target_filename (sp.timeseries, str (kic).zfill (9), filetype='fits')
      t, s, dt = sp.load_resource (filename)
      return t, s, dt
    else :
      raise Exception ("KIC{} is not available. Available KICs are {}".format (str(kic).zfill(9), available))

def load_virgo_timeseries () :
    '''
    Load the 2-hour sampled time series from the solar VIRGO/SPM instruments
    included with the module. 

    Returns
    -------
    tuple
      Tuple with time stamps (in Julian day), and flux time series from
      each VIRGO/SPM channel: blue, green, and red.
    '''
    f_blue = get_target_filename (sp.timeseries, 'virgo_2_hour_blue', filetype='fits')
    f_green = get_target_filename (sp.timeseries, 'virgo_2_hour_green', filetype='fits')
    f_red = get_target_filename (sp.timeseries, 'virgo_2_hour_red', filetype='fits')
    t, lc_blue, _ = sp.load_resource (f_blue)
    _, lc_green, _ = sp.load_resource (f_green)
    _, lc_red, _ = sp.load_resource (f_red)
    return t, lc_blue, lc_green, lc_red

def load_resource (filename) :
    '''
    Load data from a given light_curve.
    Assume that the fits file correspond to 
    KESPEISMIC product and the csv file to
    simulated data provided by Suzanne Aigrain.
    '''
    if type (filename)==str :
      filename = Path (filename)
    with filename as f :
      ext = os.path.splitext (f)[1] 
      if ext=='.fits' or ext=='.fit' :
            hdul = fits.open (f)
            hdu = hdul[0]
            data = np.array (hdu.data).astype (float)
            hdul.close ()
      elif ext=='.csv' :
            df = pd.read_csv (f)
            data= df[['time', 'fcor3']].to_numpy ()
      else :
        raise Exception ("Unkown filename extension.")
    t = data[:,0]
    s = data[:,1]
    if ext=='.csv' :
      s = s - np.mean (s)
      # Normalise the flux variation to ppm
      s = s*1e6
    dt = np.median (np.diff (t))
    return t, s, dt

def get_list_targets (dataset) :
  '''
  Get list of targets for a given dataset.
  '''
  with sp.internal_path (dataset, 'list_target.dat') as f :
      list_targets = np.loadtxt (f, dtype=int)
  return list_targets

def get_target_filename (dataset, str_id, filetype='fits') :
  '''
  Get filename corresponding to a given target
  in the required ``dataset``.
  '''
  if filetype=='fits':
    filename = sp.internal_path (dataset, '{}.{}'.format (str_id, filetype))
  elif filetype=='csv':
    filename = sp.internal_path (dataset, 'plato_brightbinned{}_cor.{}'.format (str_id, filetype))
  else :
    raise Exception ("Unknown requested file extension.")
  return filename

def get_kepler_quarters () :
  '''
  Return a tuple with start and end date of the 
  Kepler quarters.
  '''
  start = np.array([54953.0, 54964.5, 55002.5, 55093.5, 
                    55185.3, 55276.4, 55372.4, 55463.1, 
                    55568.3, 55641.5, 55739.8, 55834.1,
                    55932.3, 56015.6, 56106.6, 56205.9,
                    56306,56391.71]) 
  end = np.array([54963.25, 54997.99, 55091.47, 55182.5, 
                  55275.3, 55371.2, 55462.3, 55552.55,
                  55635.35, 55738.93, 55833.27, 55931.34,
                  56015.031, 56106.1, 56203.8294, 56303.64,
                  56391,56423.5120])
  return start, end
