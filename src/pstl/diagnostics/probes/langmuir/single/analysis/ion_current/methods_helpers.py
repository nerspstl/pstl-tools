default_fit_thin_kwargs = {
    'deg': 1, 'power': 1, 'polarity': 1,
    'reverse': False, 'return_best': True, 'fit_type': "linear",
    'min_points': 5, 'istart': None, 'iend': None, 'invalid': "ignore",
    'fstep': None, 'fstep_type': None, 'fstep_adjust': True, 'fitmax': None,
    'bstep': None, 'bstep_type': None, 'bstep_adjust': True, 'bitmax': None,
    'threshold_residual': None, 'threshold_rmse': 0.30,
    'threshold_rsq': 0.95, 'threshold_method': None,
    'convergence_residual_percent': 1.0, 'convergence_rmse_percent': 1.0,
    'convergence_rsq_percent': 1.0, 'convergence_method': None,
    'strict': False, 'full': True, 'printlog': False,
}


default_fit_power_kwargs = {
    'deg': 1, 'power': None, 'polarity': -1,  # power needs to be defined
    'reverse': False, 'return_best': True, 'fit_type': "power",
    'min_points': 5, 'istart': None, 'iend': None, 'invalid': "ignore",
    'fstep': None, 'fstep_type': None, 'fstep_adjust': True, 'fitmax': None,
    'bstep': None, 'bstep_type': None, 'bstep_adjust': True, 'bitmax': None,
    'threshold_residual': None, 'threshold_rmse': 0.50,
    'threshold_rsq': 0.95, 'threshold_method': None,
    'convergence_residual_percent': 1.0, 'convergence_rmse_percent': 10.0,
    'convergence_rsq_percent': 1.0, 'convergence_method': None,
    'strict': False, 'full': True, 'printlog': False,
}

default_fit_kwargs = {
    "thin"  :   default_fit_thin_kwargs,
    "thick" :   default_fit_power_kwargs,
}