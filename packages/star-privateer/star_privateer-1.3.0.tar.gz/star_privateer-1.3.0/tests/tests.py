import os, pytest
import warnings
import importlib.resources
import star_privateer as sp
from scipy.signal import correlate
from astropy.io import fits
import numpy as np

@pytest.fixture(scope="session")
def tmp_dir (tmp_path_factory) :
  tmp = tmp_path_factory.mktemp ("test_outputs")
  return tmp

class TestLoadingData :

  def test_load_k2 (self) :
    sp.load_k2_example ()

  def test_load_kepler (self) :
    sp.load_kepler_example (kic=3733735)
    sp.load_kepler_example (kic=8006161)
    sp.load_kepler_example (kic=10644253)
    with pytest.raises(Exception):
      # Trying to get an inexistent KIC
      sp.load_kepler_example (kic=0)

  def test_virgo (self) :
    sp.load_virgo_timeseries ()

class TestAnalysisMethods :
 
  @pytest.fixture(scope="class")
  def data (self) :
    filename = sp.get_target_filename (sp.timeseries, '003733735')
    d = sp.load_resource (filename)
    return d

  @pytest.fixture(scope="class")
  def t (self, data) :
     return data[0]

  @pytest.fixture(scope="class")
  def s (self, data) :
     return data[1]

  @pytest.fixture(scope="class")
  def dt (self, t) :
     return np.median (np.diff (t))

  def testParseval (self, t, s) :
    freq, psd = sp.compute_lomb_scargle (t, s, return_frequency_vector=True,
                                         normalisation="psd")
    df = np.median (np.diff (freq*1e6))
    sigma_f = np.sqrt (np.sum (psd) * df)
    sigma_t = np.std (s)
    assert np.abs (sigma_f / sigma_t - 1) < 1e-3

  def testLombScargleNoFit (self, t, s, dt, tmp_dir) :
    p_ps, ps_object = sp.compute_lomb_scargle (t, s, return_object=True)
    ls = ps_object.power_standard_norm
    prot, fa_prob, h_ps = sp.find_prot_lomb_scargle (p_ps, ps_object)
    filename = os.path.join (tmp_dir, "smoothing_uncertainty.png")
    prot, e_prot, E_prot = sp.compute_uncertainty_smoothing (p_ps, ls,
                                                          filename=filename)
    prot, e_prot, E_prot, fa_prob, h_ps = sp.find_prot_lomb_scargle (p_ps, ps_object, 
                                                                     return_uncertainty=True)
    assert e_prot>0
    assert E_prot>0

  def testLombScargleFit (self, t, s, dt, tmp_dir) :
    p_ps, ls = sp.compute_lomb_scargle (t, s)
    pcutoff = 60
    cond = p_ps < pcutoff
    (prot, e_p, 
     E_p, h_ps, 
     param, list_h_ps) = sp.compute_prot_err_gaussian_fit_chi2_distribution (p_ps[cond], ls[cond],
                                                                             n_profile=5, threshold=0.1,
                                                                             verbose=True)
    assert e_p>0
    assert E_p>0
    (p_smooth, ls_smooth, 
     model_smooth, e_p) = sp.uncertainty_fit_lomb_scargle (p_ps, ls, prot)
    assert e_p>0
    filename = os.path.join (tmp_dir, "lomb_scargle.png")
    sp.plot_ls (p_ps, ls, filename=filename, 
                param_profile=param, logscale=True,
                p_smooth=p_smooth, ls_smooth=ls_smooth,
                model_smooth=model_smooth)

  def testLombScargleFitPFAThreshold (self, t, s, dt, tmp_dir) :
    p_ps, ls = sp.compute_lomb_scargle (t, s)
    pcutoff = 60
    cond = p_ps < pcutoff
    (prot, e_p, 
     E_p, h_ps, 
     param, list_h_ps) = sp.compute_prot_err_gaussian_fit_chi2_distribution (p_ps[cond], ls[cond],
                                                                             pfa_threshold=1e-6,
                                                                             verbose=True)
    assert e_p>0
    assert E_p>0
    filename = os.path.join (tmp_dir, "lomb_scargle.png")
    sp.plot_ls (p_ps, ls, filename=filename, 
                param_profile=param, logscale=True)

  def testCCF (self) :
    y1 = np.array ([0, 1, 3, 4])
    y2 = np.array ([1, 2, 0, 1])
    lags = np.arange (y1.size)
    ccf = sp.compute_ccf (y1, y2, lags)
    assert np.all (ccf==np.array ([6, 3, 1, 0]))

  def testACF (self, t, s, dt) :
    p_in = np.linspace (0, 9, 10)
    p_out, acf_1 = sp.compute_acf (s, dt, p_in, normalise=True,
                                      use_scipy_correlate=False)
    p_out, acf_2 = sp.compute_acf (s, dt, p_in, normalise=True,
                                      use_scipy_correlate=True)
    assert np.all (np.abs (acf_1 - acf_2) < 1e-6)

  def testFindPeriodACF(self, t, s, dt, tmp_dir) :
    p_in = np.linspace (0, 100, 5000)
    p_acf, acf = sp.compute_acf (s, dt, p_in, normalise=True,
                                    use_scipy_correlate=True, smooth=False)
    _, acf_a1 = sp.compute_acf (s, dt, p_in, normalise=True,
                                    use_scipy_correlate=True, smooth=True)
    _, acf_a2 = sp.compute_acf (s, dt, p_in, normalise=True,
                                   use_scipy_correlate=True, smooth=True,
                                   win_type='triang')
    _, acf_a3 = sp.compute_acf (s, dt, p_in, normalise=True,
                                   use_scipy_correlate=True, smooth=True,
                                   smooth_period=30)
    (prot, hacf, gacf, 
     index_prot_acf, prots, hacfs, gacfs) = sp.find_period_acf (p_acf, acf)
    a_min, a_max = sp.find_local_extrema (acf)
    sph, e_sph = sp.compute_sph (t, s, prot)
    sph, t_sph, sph_series = sp.compute_sph (t, s, prot,
                                             return_timeseries=True)
    filename = os.path.join (tmp_dir, "acf.png")
    sp.plot_acf (p_acf, acf, prot=prot, acf_additional=[acf_a1, acf_a2, acf_a3],
                 color_additional=['darkorange', 'blue', 'red'], 
                 filename=filename)

  def testCSImplementation(self, tmp_dir) :
    t_cs = np.linspace (0, 365, 36500)  
    dt_cs = np.median (np.diff (t_cs))
    s_cs = np.sin (2*np.pi*t_cs)
    p_ps, ls = sp.compute_lomb_scargle (t_cs, s_cs, return_object=False)
    p_acf, acf = sp.compute_acf (s_cs, dt_cs, normalise=True,
                                 use_scipy_correlate=True, smooth=True)
    cs = sp.compute_cs (ls, acf, p_ps=p_ps, p_acf=p_acf)
    prot, h_cs = sp.find_prot_cs (p_acf, cs)
    prot, E_p, param = sp.compute_prot_err_gaussian_fit (p_acf, cs, verbose=False,
                                                         n_profile=5, threshold=0.1)
    feature, feature_names = sp.create_feature_from_fitted_param (param, method='CS')
    assert feature_names[0]=='CS_0_1'
    assert np.all(np.abs (feature[feature_names=='CS_0_2']-prot)<1e-6)
    filename = os.path.join (tmp_dir, "cs_implementation.png")
    sp.plot_cs (p_acf, cs, filename=filename, param_gauss=param, xlim=(0,10))

  def testCSLightCurve(self, t, s, dt, tmp_dir) :
    p_ps, ls = sp.compute_lomb_scargle (t, s, return_object=False)
    p_in = np.linspace (0, 100, 5000)
    p_acf, acf = sp.compute_acf (s, dt, p_in, normalise=True,
                                    use_scipy_correlate=True, smooth=True)
    cs = sp.compute_cs (ls, acf, p_ps=p_ps, p_acf=p_acf)
    prot, h_cs = sp.find_prot_cs (p_acf, cs)
    prot, E_p, param = sp.compute_prot_err_gaussian_fit (p_acf, cs, verbose=True,
                                                         n_profile=5, threshold=0.1)
    filename = os.path.join (tmp_dir, "cs.png")
    sp.plot_cs (p_acf, cs, filename=filename, param_gauss=param)

  def testComputeDeltaProt (self) :
    prot = 5
    dr_candidates = np.array([1, 4, 6, 5.3, 12, 28])
    dr_err = np.array([0.1, 0.4, 0.5, 0.53, 1.2, 2.8])
    dr_err = np.array([0.1, 0.4, 0.5, 0.53, 1.2, 2.8])
    dr, dr_err, _, _ = sp.compute_delta_prot (prot, dr_candidates, dr_err,
                                              dr_err, delta_min=1/3, delta_max=5/3)
    state = np.full (dr.size, -1)
    IDP_123_DELTA_PROT_NOSPOT = np.c_[dr, dr_err, state]
    expected = np.array([[ 4.  ,  0.4  , -1 ],
                         [ 6.  ,  0.5  , -1 ],
                         [ 5.3 ,  0.53 , -1 ]])
    assert np.all (IDP_123_DELTA_PROT_NOSPOT - expected < 1e-6)

  def testEstimatePhotonNoise (self, t, s) :
    noise = sp.estimate_photon_noise (t, s, noise_band=None)

  def testComputeSphShortNoiseCorrection (self, t, s) :
    prot = 2.5
    noise = sp.estimate_photon_noise (t, s, noise_band=None)
    sph, e_sph = sp.compute_sph (t, s, prot,
                                 correct_noise=True)
    assert noise < sph

  def testComputeSphShort (self, t, s) :
    prot = 2 * (t[-1] - t[0])
    sph, e_sph = sp.compute_sph (t, s, prot)
    assert np.abs (sph - np.std (s)) < 1e-6
    assert e_sph==0

  def testComputeSphShortNoiseCorrection (self, t, s) :
    prot = 2 * (t[-1] - t[0])
    sph, e_sph = sp.compute_sph (t, s, prot,
                                 correct_noise=True)
    assert e_sph==0

  def testComputeSphMissingProt (self, t, s) :
    sph, e_sph = sp.compute_sph (t, s, -1)
    assert sph==-1
    assert e_sph==-1


  def testAnalysisPipeline (self, t, s, dt, tmp_dir) :
    filename = os.path.join (tmp_dir, "pipeline.png")
    (p_ps, p_acf, ps, acf, cs, 
    features, feature_names, fig) = sp.analysis_pipeline (t, s, periods_in=None,
                                                          wavelet_analysis=False, plot=True,
                                                          filename=filename, 
                                                          lw=1, dpi=300, smooth_acf=True)
    df = sp.save_features (os.path.join (tmp_dir, "3733735_features.csv"), 
                           3733735, features, feature_names)
    assert p_ps.shape==ps.shape
    assert p_acf.shape==acf.shape
    assert p_acf.shape==cs.shape
    assert len (feature_names)==features.size

  def testAnalysisPipelinePFAThreshold (self, t, s, dt, tmp_dir) :
    filename = os.path.join (tmp_dir, "pipeline.png")
    (p_ps, p_acf, ps, acf, cs, 
    features, feature_names, fig) = sp.analysis_pipeline (t, s, periods_in=None,
                                                          wavelet_analysis=False, plot=True,
                                                          filename=filename, pfa_threshold=1e-6,  
                                                          lw=1, dpi=300, smooth_acf=True)
    df = sp.save_features (os.path.join (tmp_dir, "3733735_features.csv"), 
                           3733735, features, feature_names)
    assert p_ps.shape==ps.shape
    assert p_acf.shape==acf.shape
    assert p_acf.shape==cs.shape
    assert len (feature_names)==features.size

  def testAnalysisPipelineSmoothLS (self, t, s, dt, tmp_dir) :
    filename = os.path.join (tmp_dir, "pipeline.png")
    (p_ps, p_acf, ps, acf, cs, 
    features, feature_names, fig) = sp.analysis_pipeline (t, s, periods_in=None,
                                                          wavelet_analysis=False, plot=True,
                                                          filename=filename, ls_err_smooth=True,  
                                                          lw=1, dpi=300, smooth_acf=True)
    df = sp.save_features (os.path.join (tmp_dir, "3733735_features.csv"), 
                           3733735, features, feature_names)
    assert p_ps.shape==ps.shape
    assert p_acf.shape==acf.shape
    assert p_acf.shape==cs.shape
    assert len (feature_names)==features.size

  def testWavelet (self, s, t, dt, tmp_dir) :
    nrebin = 8
    dt *= nrebin
    t, s = sp.rebin (t, nrebin=nrebin), sp.rebin (s, nrebin=nrebin)
    p_in, wps, gwps, coi, scales = sp.compute_wps (s, dt*86400, periods=None,
                                                   normalise=True, mother=None)
    prot, E_p, param = sp.compute_prot_err_gaussian_fit (p_in, gwps, verbose=False,
                                                         n_profile=5, threshold=0.1)
    filename = os.path.join (tmp_dir, "wavelet.png")
    sp.plot_wps (t, p_in, wps, gwps, coi=coi,
              cmap='Blues', shading='auto', 
              filename=filename,
              color_coi='black', ylogscale=False, param_gauss=param,
              ax1=None, ax2=None, lw=1, normscale='linear',
              vmin=None, vmax=None, dpi=200)

  def testWaveletPywavelets (self, s, t, dt, tmp_dir) :
    nrebin = 8
    dt *= nrebin
    t, s = sp.rebin (t, nrebin=nrebin), sp.rebin (s, nrebin=nrebin)
    p_in, wps, gwps, coi, scales = sp.compute_wps (s, dt*86400, backend="pywavelets")
    prot, E_p, param = sp.compute_prot_err_gaussian_fit (p_in, gwps, verbose=False,
                                                         n_profile=5, threshold=0.1)
    filename = os.path.join (tmp_dir, "wavelet_pywt.png")
    sp.plot_wps (t, p_in, wps, gwps, coi=coi,
              cmap='Blues', shading='auto', 
              filename=filename,
              color_coi='black', ylogscale=False, param_gauss=param,
              ax1=None, ax2=None, lw=1, normscale='linear',
              vmin=None, vmax=None, dpi=200)

  def testAnalysisPipelineWavelet (self, s, t, dt, tmp_dir) :
    nrebin = 8
    t, s = sp.rebin (t, nrebin=nrebin), sp.rebin (s, nrebin=nrebin)
    filename = os.path.join (tmp_dir, "pipeline_wavelet.png")
    (p_ps, p_acf, gwps, wps, 
     acf, cs, coi, features, 
     feature_names, fig) = sp.analysis_pipeline (t, s, periods_in=None,
                          wavelet_analysis=True, plot=True,
                          filename=filename, lw=1, dpi=200)
    assert p_ps.shape==gwps.shape
    assert p_ps.shape[0]==wps.shape[0]
    assert p_acf.shape==acf.shape
    assert p_acf.shape==cs.shape
    assert len (feature_names)==features.size

class TestRooster :

  def testLoadReference (self) :
    df = sp.load_reference_catalog (catalog='santos-19-21')
    assert df.columns==['prot']

  def testAttributeClass (self) :
    target_id = [3733735, 1245803]
    df = sp.attribute_rot_class (target_id, catalog='santos-19-21')
    assert df.loc[3733735, 'target_class']=='rot'
    assert df.loc[1245803, 'target_class']=='no_rot'

    p_candidates = np.array ([[2.6, 2.4, 5.1], [2, 2, 2]])
    df = sp.attribute_period_sel (target_id, p_candidates,
                                     catalog='santos-19-21')
    assert df.loc[3733735, 'target_class']==0

    p_candidates = np.array ([[5.6, 2.4, 5.1], [2, 2, 2]])
    df = sp.attribute_period_sel (target_id, p_candidates,
                                     catalog='santos-19-21')
    assert df.loc[3733735, 'target_class']== 1

    p_candidates = np.array ([[5, 5, 2.5], [2, 2, 2]])
    df = sp.attribute_period_sel (target_id, p_candidates,
                                     catalog='santos-19-21')
    assert df.loc[3733735, 'target_class']==2

  def testTrainRoosterInstanceOnTheFly (self) :
    chicken = sp.load_rooster_instance (verbose=True)
    chicken.getTrainingRotClassInfo ()
    chicken.getTestRotClassInfo ()
    chicken.getTrainingPeriodSelInfo ()
    chicken.getTestPeriodSelInfo ()
    chicken.getLastAnalysisInfo ()

  def testTrainRoosterInstanceOnTheFlyMethods (self) :
    c0 = sp.load_rooster_instance (verbose=True, methods=None)
    c1 = sp.load_rooster_instance (verbose=True, methods=["GLS", "ACF", "CS"])
    c2 = sp.load_rooster_instance (verbose=True, methods=["WPS", "GLS", "ACF", "CS"])
    c3 = sp.load_rooster_instance (verbose=True, methods=["WPS", "ACF", "CS"])
    f0 = c0.getFeatureNames()
    f0.sort()
    f1 = c2.getFeatureNames()
    f1.sort () 
    f2 = c2.getFeatureNames()
    f2.sort () 
    f3 = c2.getFeatureNames()
    f3.sort () 
    assert f0==f2
    assert f1==f2

  def testCreateRoosterInstance (self, tmp_dir) :
    # Initialising ROOSTER without specifying any random forest option
    chicken = sp.ROOSTER ()
    # Specifying number of estimators
    chicken = sp.ROOSTER (n_estimators=50, max_leaf_nodes=10)
    assert chicken.RotClass.n_estimators==50
    assert chicken.isTrained () is False
    assert chicken.isTested () is False
    filename = os.path.join (tmp_dir, "rooster_instance")
    chicken.save (filename)
    chicken = sp.load_rooster_instance (filename=filename)
    # Check that we can correctly access the loaded instance properties
    assert chicken.RotClass.n_estimators==50

  def testCreateRoosterInstanceDict (self, tmp_dir) :
    chicken = sp.ROOSTER (rotclass_kwargs={"n_estimators":50},
                          periodsel_kwargs={"n_estimators":75},
                          n_estimators=100)
    assert chicken.RotClass.n_estimators==50
    assert chicken.PeriodSel.n_estimators==75
