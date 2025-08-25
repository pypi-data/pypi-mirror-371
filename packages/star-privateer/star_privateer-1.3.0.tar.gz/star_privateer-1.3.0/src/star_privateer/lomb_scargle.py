import pickle, os, scipy
import numpy as np
from astropy.timeseries import LombScargle
from scipy.integrate import simpson
import matplotlib.pyplot as plt
import star_privateer as sp
from scipy.optimize import minimize, least_squares
import warnings

'''
Copyright 2024 Sylvain Breton

This file is part of star-privateer, an open-source software distributed
under MIT License.
'''

def quick_background (p, ps, nbin=10,
                      scale="log") :
    """
    Quickly estimate background level
    using logarithmically spaced boxes.
    """
    if scale=="log" : 
        bin_edges = np.logspace (np.log10(p.min ()), 
                                 np.log10(p.max ()),
                                 nbin+1)
    elif scale=="linear" :
        bin_edges = np.linspace (p.min (), 
                                 p.max (),
                                 nbin+1)
    else :
        raise Exception ("Unknown required scale. Must be linear or log.")
    bins = (bin_edges[:-1] + bin_edges[1:])/2
    back_binned, _, _ = scipy.stats.binned_statistic (p, ps, bins=bin_edges,
                                                      statistic="median")
    back_binned *= (9/8)**3
    f = scipy.interpolate.interp1d (bins, back_binned, 
                                    fill_value=(back_binned[0], back_binned[-1]),
                                    bounds_error=False, kind="linear")
    back = f(p)
    return back, bins, back_binned

def compute_lomb_scargle (t, s, freq=None, 
                          renormalise=False, 
                          normalisation='snr',
                          return_object=False,
                          return_frequency_vector=False,
                          method="fast") : 
  '''
  Compute Lomb Scargle for a given timeseries.
  Default normalisation follows the ``standard`` 
  normalisation described in ``astropy`` documentation.

  Parameters
  ----------
  t : ndarray
    Timestamp array, in days.
  
  s : ndarray
    Flux variations

  freq : ndarray
   Frequency array on which to compute the power vector. If not provided,
   the function will compute the frequency array assuming a uniform sampling
   through ``numpy.fft.rfftfreq``.

  normalisation : str
    Normalisation choice, `standard`, `psd` correspond
    to the `astropy` implementation. `snr` corresponds
    to the `psd` normalisation divided by a mean spectrum
    value computed as the spectrum median value divided by 
    `(8/9)**3`. This can be used only with `return_object`
    set as `False`. Optional, default `snr`. 

  return_object : bool
    If set to ``True``, return `astropy` object as second 
    element of the returned tuple, otherwise return 
    power array.

  return_frequency_vector : bool 
    If set to ``True``, the frequency vector (in Hz) will
    be returned instead of the period vector. Optional, default
    ``False``.

  method : str
    Method to compute Lomb-Scargle. See astropy.timeseries.LombScargle.
    Optional, default ``"fast"``.

  Returns
  -------
  tuple
    Tuple of array with periods (in days) and Lomb-Scargle
    power spectrum. Return the Lomb-Scargle object
    if ``return_object`` is set to ``True``.
  '''
  accepted_normalisation  = ["standard", "psd", "snr_flat", "snr"]
  if normalisation not in accepted_normalisation :
    raise Exception ("Unknown requested normalisation, choose one in {}".format (accepted_normalisation))
  ps = LombScargle(t*86400, s, 
                   center_data=False, 
                   fit_mean=True)
  if freq is None : 
    dt = np.median (np.diff (t))*86400
    freq = np.fft.rfftfreq (t.size, dt)
  periods = 1 / (86400 * freq[freq!=0])
  # Removing the zero-frequency point
  # which seems problematic for "fast" method.
  freq = freq[freq!=0]
  if return_frequency_vector :
    x = freq
  else :
    x = periods
  if return_object :
    # This attribute is added for compatibility with other functions
    ps.power_standard_norm = ps.power(freq, normalization='standard',
                                      method=method) 
    return x, ps
  else :
    if normalisation=="standard":
      ls = ps.power(freq, normalization='standard',
                    method=method)
    else :
      ls = ps.power(freq, normalization='psd',
                    method=method)
      # Complementary normalisation to have an actual
      # power spectral density.
      # With this formulation, integrating the PSD
      # over the frequency should give a value equal
      # to the variance of the time series.
      ls = ls * 2 * (t[-1]-t[0])*86400 / (1e6*t.size)
      if normalisation=="snr_flat" :
        ls = ls*(8/9)**3 / np.median (ls)
      if normalisation=="snr" :
        back, _, _ = quick_background (x, ls, 
                                       scale="log", nbin=10)
        ls = ls / back
    if renormalise :
      ls = ls / np.amax (ls)
    return x, ls

def compute_uncertainty_smoothing (periods, power, filename=None) :
  '''
  Smooth the power spectrum (sampled in frequency) and estimate
  from this smoothing the width of the selected peak at period
  ``prot``. 

  Note
  ----
    Even if there are caveat to keep in mind, this method
    is computationnally efficient and not model dependent.
  '''
  index = np.argmax (power)
  prot = periods[index]
  freq = 1 / (periods*86400)
  f_rot = 1 / (prot*86400)
  res = np.abs (freq[2]-freq[1])
  sizebox = max (1, int (f_rot / res))
  smoothed = sp.apply_smoothing (power, sizebox, win_type='triang')
  hmax = smoothed[index]
  aux = periods[smoothed<hmax/2] 
  try :
    e_prot = aux[aux<prot][0]
  except IndexError :
    e_prot = prot
  try :
    E_prot = aux[aux>prot][-1]
  except IndexError :
    E_prot = prot

  if filename is not None :
    fig, ax = plt.subplots (1, 1)
    ax.plot (periods, power, color='grey')
    ax.plot (periods, smoothed, color='black')
    ax.axvline (e_prot, lw=2, color='darkorange')
    ax.axvline (E_prot, lw=2, color='darkorange')
    ax.set_xlabel ('Periods (day)')
    ax.set_ylabel ('Power')
    ax.set_yscale ('log')
    ax.set_xlim (e_prot-prot, E_prot+prot)
    plt.savefig (filename, dpi=300)
    plt.close ()

  e_prot = prot - e_prot
  E_prot = E_prot - prot

  return prot, e_prot, E_prot

def find_prot_lomb_scargle (periods, ps_object,
                            method='naive',  
                            return_uncertainty=False) :
  '''
  Compute Prot from Lomb-Scargle periodogram
  as the maximum of the spectrum. Corresponding
  false alarm probability (see e.g. Scargle 1982)
  is also computed.

  Returns
  -------
    Rotation period and false alarm probability.
  '''
  prot, e_prot, E_prot = compute_uncertainty_smoothing (periods, 
                                                        ps_object.power_standard_norm)
  h_ps = ps_object.power_standard_norm.max()
  fa_prob = ps_object.false_alarm_probability(h_ps,
                                              method=method)  
  if return_uncertainty :
    return prot, e_prot, E_prot, fa_prob, h_ps
  else :
    return prot, fa_prob, h_ps

def smooth_for_fit (p_ps, ps, prot) :
    """
    Wrapper function preparing the smooth
    periodogram for uncertainty estimation.
    """
    cond = p_ps!=0
    nu, ps = 1/(p_ps[cond]*86400), ps[cond]
    ii = np.argsort (nu)
    nu, ps = nu[ii], ps[ii]
    res = nu[2] - nu[1]
    nurot = 1 / (prot*86400)
    sizebox = max (1, int (0.1*nurot/res))
    smooth = sp.apply_smoothing (ps, sizebox, 
                                 win_type='triang')
    window = (p_ps>0.5*prot)&(p_ps<1.5*prot)
    return p_ps[window], smooth[window]

def fun_residual_fixed_mu (param, x, y, mu) :
    return np.abs (y - sp.gauss (x, np.exp (param[0]), mu, np.exp (param[1]))) 

def fit_gaussian_fixed_mu (x, y, mu) :
    '''
    Perform a least-square fit with a Gaussian profile
    without varying the central value ``mu``.
    '''
    a0 = y.max ()
    param0 = np.log ([a0, 1e-1*mu])
    bounds = (np.array([-15, -15]),
              np.array ([max (3, np.log (1e2*a0)), 
                         2])
              )
    result = least_squares(fun_residual_fixed_mu, param0,
                           args=(x, y, mu), bounds=bounds)
    return result

def uncertainty_fit_lomb_scargle (p_ps, ps, prot) :
    """
    Feat a Gaussian on smoothed Lomb-Scargle
    in order to estimate a more realistic uncertainty
    on rotation period. 
    
    Parameters
    ----------
    p_ps : ndarray
      Period vector (in days)
      
    ps : ndarray
      Power spectrum

    prot : float
      Rotation period to use as reference
      for the central value of the Gaussian.
    """
    p_ps, ps = smooth_for_fit (p_ps, ps, prot)
    result = fit_gaussian_fixed_mu (p_ps, ps, prot)
    a, e_p = np.exp (result.x[0]), np.exp (result.x[1])
    model = sp.gauss (p_ps, a, prot, e_p)
    return p_ps, ps, model, e_p


def plot_ls (periods, ls, ax=None, lw=1,
             filename=None, dpi=300,
             xlim=None, ylim=None, logscale=False,
             param_profile=None, 
             p_smooth=None, ls_smooth=None, 
             model_smooth=None, figsize=(8,4)) :
  '''
  Plot Lomb-Scargle periodogram.

  Parameters
  ----------
  periods : ndarray
    Period array, in days.

  ls : ndarray
    Lomb-Scargle periodogram.

  ax : matplotlib.pyplot.axes
    If provided, the Lomb-Scargle periodogram will
    be plotted on this ``Axes`` instance. 
    Optional, default ``None``.

  lw : float
    Linewidth.

  filename : str or Path instance
    If provided, the figure will be saved under this name.
    Optional, default ``None``.

  dpi : int
    Dot-per-inch to consider for the plot.

  xlim : tuple
    x-axis boundaries.

  ylim : tuple
    y-axis boundaries.

  logscale : bool
    Whether to use a logarithmic scale for the y-axis
    or not. Optional, default ``False``. 

  param_profile : ndarray
    Parameters of the Gaussian profiles fitted
    on the periodogram.

  p_smooth : ndarray
    Periods corresponding to the smoothed periodogram.
    Optional, default ``None``

  ls_smooth : ndarray
    Smoothed periodogram.
    Optional, default ``None``

  model_smooth : ndarray
    Model fitted on the smoothed periodogram.
    Optional, default ``None``

  figsize : tuple
    Figure size.

  Returns
  -------
  Figure
    The plotted figure.
  '''

  if ax is None :
    fig, ax = plt.subplots (1, 1, figsize=figsize)
  else :
    fig = None

  ax.plot (periods, ls, color='black') 
  ax.set_xlabel ('Period (day)')
  ax.set_ylabel ('Power')
  if xlim is not None :
    ax.set_xlim (xlim)
  if ylim is not None :
    ax.set_ylim (ylim)
  if logscale :
    ax.set_xscale ('log')
    ax.set_yscale ('log')

  if param_profile is not None and param_profile.size>0:
    param_profile = np.atleast_2d (param_profile)
    n_profile = param_profile.shape[0]
    model = np.zeros (periods.size)
    prot = 1e6 / (param_profile[0,1]*86400)
    cond = (periods>0.1)
    model = model[cond] 
    x = 1e6 / (periods[cond]*86400)
    for ii in range (n_profile) :
      model += compute_model (param_profile[ii,:], x, back=np.ones (x.size)) 
    ax.plot (periods[cond], model, color='darkorange', lw=2*lw)

  if p_smooth is not None :
    if ls_smooth is not None :
      ax.plot (p_smooth, ls_smooth, color="cyan", lw=2*lw)
    if model_smooth is not None :
      ax.plot (p_smooth, model_smooth, color="blue", lw=2*lw)

  if fig is not None :
    fig.tight_layout ()

  if filename is not None :
    plt.savefig (filename, dpi=dpi)

  return fig

def compute_model (param, x, profile=0, back=None) :
  """
  Compute peak model.
  """
  if back is None :
    trend = - param[3]*x + param[4]
    back = np.ones (x.size) 
  else :
    trend = 0
  if profile==0 :
    model = sp.gauss (x, param[0], param[1], param[2])*back + trend
  elif profile==1 :
    model = sp.lor (x, param[0], param[1], param[2])*back  + trend
  else :
    raise Exception ("Unknown profile.")
  return model

def log_likelihood (param, x, ps, back=None) :
  '''
  The model is a Gaussian or Lorentzian profile summed 
  with an affine law to take the background into
  account if ``back`` is ``None``, otherwise the background
  is removed. 
  '''
  with warnings.catch_warnings():
    warnings.simplefilter("ignore", category=RuntimeWarning)
    model = compute_model (np.exp (param), x, back=back)
    log_l = ps / model + np.log (model)
    log_l = np.sum (log_l)
  return log_l

def fit_gaussian_lomb_scargle (x, ps, x_init, back=None,
                               reduce_interval=False, 
                               pmin=None, pmax=None) :
  '''
  Perform a least-square fit with a Gaussian profile.
  '''
  if reduce_interval :
    mask = (x>0.8*x_init)&(x<1.2*x_init)
    x_fit, ps = x[mask], ps[mask]
  else :
    x_fit = x
  if pmin is None :
    pmin = 0
  if pmax is None :
    pmax = np.inf
  w = 1e-1*x_init
  amin, amax = 0.1, 1e4
  wmin, wmax = max (1e-5, 1e-5*x_init), 2*x_init
  xmin, xmax = .99*x_init, 1.01*x_init
  if back is None :
    a = np.amax (ps) 
    beta = np.median (ps) 
    param0 = np.array ([a,
                       x_init,
                       w, 
                       1e-12, 
                       beta])
    
    bounds = [(amin*a, amax*a),
              (xmin, xmax),
              (wmin, wmax),
              (1e-15, 1e2),
              (1e-15, a)]
  else :
    a = np.amax (ps / back) 
    param0 = np.array ([a,
                       x_init,
                       0.1*x_init])
    
    bounds = [(amin*a, amax*a),
              (xmin, xmax),
              (wmin, wmax)]
  result = minimize (log_likelihood, np.log (param0),
                     args=(x_fit, ps, back), bounds=np.log (bounds))

  fitted = np.exp (result.x)
  model = compute_model (fitted, x, back=np.ones (x.size))
  return fitted, model, result.success, result.message

def compute_cond (pmin, pmax, periods) :
  """
  Wrapper to compute input condition.
  """
  if pmin is not None :
    cond1 = (periods>pmin)
  else :
    cond1 = np.ones (periods.size, dtype=bool)
  if pmax is not None :
    cond2 = (periods<pmax)
  else :
    cond2 = np.ones (periods.size, dtype=bool)
  cond = cond1&cond2
  if pmin is None and pmax is None : 
    cond = (periods>0.1)
  return cond

def compute_prot_err_gaussian_fit_chi2_distribution (periods, ps,
                                                     n_profile=5, threshold=0.1,
                                                     pfa_threshold=None,
                                                     verbose=False, back=None,
                                                     plot_procedure=False,
                                                     pmin=None, pmax=None,
                                                     procedure="mask") :
  '''
  Fit a series of gaussian profiles on a power 
  spectrum following a chi2 distribution and use it to extract 
  the rotation period estimate and corresponding error.

  Parameters
  ----------
  periods : ndarray
    Period array, in days.

  ps : ndarray
    Power spectrum.

  n_profile : int
    Maximal number of Gaussian profile to fit. 

  threshold : float
    Peaks with height below this threshold (given as a fraction
    as the highest peak) will not be fitted.

  pfa_threshold : float 
    False-alarm probability threshold to consider to stop
    the fitting process. In this case, the metric to 
    compute false alarm probability will assume that the 
    spectrum follow a chi square distribution.
    ``threshold`` and ``n_profile`` will not be considered 
    if this argument is provided. A maximum of 100 profiles
    will be fitted. Optional, default ``None``.

  pmin : float
    Minimum period to fit. Optional, default ``None``.

  pmax : float
    Maximum period to fit. Optional, default ``None``.
 
  Returns
  -------
  tuple
    The rotation period, its uncertainty, corresponding height 
    and the parameters fitted for the ``n_profile`` profiles (in this order for
    each profile: amplitude, central frequency, width, a, b, with
    a and b the parameters for the affine background law).
  '''
  if pfa_threshold is not None :
    threshold, n_profile = 0, 100 
  if pfa_threshold is None :
    pfa_threshold = 1
  param = np.full ((n_profile,5), -1.)
  h_ps = np.zeros (n_profile)
  cond = compute_cond (pmin, pmax, periods)
  ps, periods = ps[cond], periods[cond]
  p_init = periods[np.argmax (ps)]
  aux_ps = np.copy (ps)
  if back is not None :
    back = back[cond]
  x = 1e6 / (periods*86400)
  x_init = 1e6 / (p_init*86400)
  # Ensuring that even if fitting does not work
  # we will get a prot value.
  max_init = np.amax (ps)
  param[0,1], h_ps[0] = x_init, max_init
  ii = 0
  while ii < n_profile and x.size>0 and np.amax (ps) > threshold*max_init \
                       and np.exp (-np.amax (ps))<pfa_threshold :
    fitted_param, model, success, message = fit_gaussian_lomb_scargle (x, ps, x_init,
                                                                       back=back)
    if verbose :
      print ('Fitted profile {}, param obtained:{}, success: {}'.format (ii, fitted_param, success))
    if not success :
      if verbose :
        print (message)
      break
    h_ps[ii] = aux_ps[np.argmax (ps)]
    param[ii,:] = fitted_param
    if plot_procedure :
      plot_ls (periods, ps, param_profile=fitted_param)
    if procedure=="subtract" :
      ps = ps - model
      ps[ps<0] = 1e-6 
    elif procedure=="mask" :
      to_mask = (x>param[ii,1]-2*param[ii,2])&(x<param[ii,1]+2*param[ii,2]) 
      ps = ps[~to_mask]
      periods = periods[~to_mask]
      x = x[~to_mask]
    if x.size>0 :
      p_init = periods[np.argmax (ps)]
      x_init = 1e6/(p_init*86400)
    ii += 1

  h_prot = h_ps[0]
  h_ps = h_ps[param[:,0]!=-1]
  param = param[param[:,0]!=-1,:]

  if param.size > 0 :
    prot = 1e6/(param[0,1]*86400)
    e_p = prot - 1e6/((param[0,1] + param[0,2])*86400)
    E_p = 1e6/((param[0,1] - param[0,2])*86400) - prot
  else :
    prot, e_p, E_p = p_init, -1, -1
  return prot, e_p, E_p, h_prot, param, h_ps

def false_alarm_zk_2009 (h_ps, ls_size) :
  """
  False alarm probability as expressed by Eq. 24 of Zechmeister & Kurster
  2009, considering a Lomb-Scargle periodogram normalised according to
  their Eq. 4. 
  """
  proba_p_p0 = (1 - h_ps)**((ls_size*2-3)/2)
  proba_fa = 1 - (1 - proba_p_p0)**ls_size
  return proba_fa

def prepare_idp_fourier (param, h_ps, ls_size, 
                         ps_object=None,
                         pcutoff=None, pthresh=None,
                         pfacutoff=None, 
                         pfa_metric="psd",
                         clean_residual=True,
                         cleaning=0.02) :
  '''
  Take as input the result of the peak fitting to
  compute false alarm probability and return and
  array formatted to be written as one of the
  requested intermediate data product. 
  '''
  if param.size==0 :
    return np.full ((1,5), -1)
  param = np.atleast_2d (param)
  idp = np.zeros ((param.shape[0], 5))
  p = 1e6/(param[:,1]*86400)
  e_p = p - 1e6/((param[:,1] + param[:,2])*86400)
  E_p = 1e6/((param[:,1] - param[:,2])*86400) - p
  if ps_object is not None :
      fa_prob = ps_object.false_alarm_probability(h_ps,
                                                  method='baluev')
  else :
    if pfa_metric=="psd" :
      # Simple metric of a PSD normalised by its mean
      fa_prob = np.exp (-h_ps)
    elif pfa_metric=="zk_2009" :
      fa_prob = false_alarm_zk_2009 (h_ps, ls_size)
  
  fa_prob[fa_prob<1e-16] = 1e-16
  idp[:,0] = p
  idp[:,1] = e_p
  idp[:,2] = E_p
  idp[:,3] = h_ps
  idp[:,4] = fa_prob

  if pcutoff is not None :
    idp = idp[idp[:,0]<pcutoff,:]    
  if pthresh is not None :
    idp = idp[idp[:,0]>pthresh,:]    
  if pfacutoff is not None :
    idp = idp[idp[:,4]<pfacutoff,:]    

  indexes = np.argsort (idp[:,3])
  idp = idp[indexes,:]
  idp = np.flip (idp, axis=0)

  if clean_residual :
    # Clean prot that are too close
    ii = 0
    low, up = 1-cleaning, 1+cleaning
    while ii < idp.shape[0] :
      mask = (idp[:,0]<low*idp[ii,0])|(idp[:,0]>up*idp[ii,0])
      mask[ii] = True
      idp = idp[mask,:]
      ii += 1
   
  return idp

def series_to_psd (s, dt, correct_dc=True,
                   return_periods=False, 
                   periods_in_day=True) :

  """
  Take a regularly sampled timeseries and compute 
  its power spectral density (PSD) through a FFT.

  Parameters
  ----------
  s : ndarray
    Input time series.

  dt : float 
    sampling of the time series, in seconds.

  correct_dc : bool  
    If set to True, will compute the duty_cycle
    to adjust the psd values. Optional, default False.

  return_periods : bool
    If set to ``True``, will return a period vector instead
    of a frequency vector. Zero-frequency bin will be removed.

  periods_in_day : bool
    If set to ``True``, the period vector will be returned in
    day, otherwise in seconds.

  Returns
  ------- 
  tuple of ndarray
    If ``return_periods`` is set to ``False``, frequency and PSD arrays. 
    The frequency units are in ``Hz`` and the PSD in ``units_of_time_series**2/Hz``. 
    If ``return_periods`` is set to ``True``, the first element of the tuple 
    is replaced by the period vector.
  """
  freq = np.fft.rfftfreq (s.size, d=dt)
  tf = np.fft.rfft (s) / (s.size / 2.)
  T = s.size * dt
  psd = np.abs (tf) * np.abs (tf) * T / 2.

  if correct_dc :
    dc = np.count_nonzero (s) / s.size
    psd = psd / dc

  if not return_periods :
    return freq, psd
  else :
    periods = 1/freq[freq!=0]
    psd = psd[freq!=0]
    if periods_in_day :
      periods /= 86400
    return periods, psd

