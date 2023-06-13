import numpy as np

from pstl.utls.verify import verify_1D_array, verify_type, verify_polarity


def verify_key_exist(key, dictionary):
    if key in dictionary:
        return True
    else:
        return False


def set_savgol_filter_defaults(ydata: np.ndarray,
                               window_length: int | None = None,
                               polyorder: int | None = None,
                               savgol_filter_kwargs: dict = {},
                               **kwargs):
    # Verify 1D array and get length of ydata
    verify_1D_array(ydata)
    len_ydata = len(ydata)

    if window_length is None:
        default_window_length = int(0.08*len_ydata)
        default_window_length = default_window_length if default_window_length % 2 != 0 else default_window_length+1
        window_length = savgol_filter_kwargs.pop(
            'window_length', default_window_length)
    else:
        _ = savgol_filter_kwargs.pop('window_length', None)

    if polyorder is None:
        polyorder = savgol_filter_kwargs.pop('polyorder', 1)
    else:
        _ = savgol_filter_kwargs.pop('polyorder', None)

    # verify int and verify if positive
    verify_type(window_length, int, 'window_length')
    verify_type(polyorder, int, 'polyorder')
    verify_polarity(window_length)
    verify_polarity(polyorder)

    return window_length, polyorder, savgol_filter_kwargs
