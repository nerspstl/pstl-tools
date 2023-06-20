from typing import Optional, Union, Tuple, Any, List

import numpy as np
import numpy.typing as npt


def verify_iterables(iter1: npt.ArrayLike, iter2: npt.ArrayLike) -> None:
    iter1 = np.array(iter1)
    iter2 = np.array(iter2)
    arr1_shape = np.shape(iter1) if hasattr(
        iter1, "__len__") else np.shape(np.array(iter1))
    arr2_shape = np.shape(iter2) if hasattr(
        iter2, "__len__") else np.shape(np.array(iter2))

    if arr1_shape != arr2_shape:
        raise ValueError('Iterables must have the same shape')
    elif len(iter1) != len(iter2):
        raise ValueError('Iterables must have the same length')


def verify_polarity(x: Union[int, float], polarity: str = "positive") -> None:
    if polarity == "positive":
        if x >= 0:
            pass
        else:
            raise ValueError(
                "Argument is negative but should be positve: %s" % (str(x)))
    if polarity == "negative":
        if x <= 0:
            pass
        else:
            raise ValueError(
                "Argument is positive but should be negative: %s" % (str(x)))


def verify_array_polarity(xdata: npt.ArrayLike, polarity: Union[str, List[str]] = "positive") -> None:
    xdata = np.array(xdata)
    if isinstance(polarity, str):
        polarity = [polarity]*len(xdata)
    verify_type(polarity, list)
    for k in range(0, len(xdata), 1):
        val = xdata[k]
        pol = polarity[k]
        verify_polarity(val, polarity=pol)


def verify_1D_array(array: npt.ArrayLike) -> None:
    np_arr = np.array(array)
    if np_arr.ndim != 1:
        raise ValueError("array is not 1D: %sD" % (str(np_arr.ndim)))


def verify_type(x: npt.ArrayLike, var_type: Any, var_str: Optional[str] = None, none_type: bool = False) -> None:
    """
    Verifys that the input 'x' is of type 'var_type'. Raises error if not a match. 
    If 'var_str' is defined, the print function will say:

    '<var_str>' is not type '<var_type>': <x>

    Parameters
    ----------
    x : any
        Variable to test if matches 'var_type'
    var_type : variable type, or tuple of types (cannot be None)
        Variable type to see if matches 'x'
    var_str : str, optional
        String of variable name to dispaly if Raise TypeError occurs
    none_type :  bool, optional
        If True, will also allow variable type to be None

    Returns
    -------
    None

    Rasies
    ------
    TypeError
        If 'x' does not match type of 'var_type'
    """
    if var_str is None:
        if isinstance(x, var_type) is False:
            if none_type and x is None:
                pass
            elif none_type:
                raise TypeError("Argument is not %s or None: %s" %
                                (str(var_type), str(type(x))+": " + str(x)))
            else:
                raise TypeError("Argument is not %s: %s" %
                                (str(var_type), str(type(x))+": " + str(x)))
    elif isinstance(var_str, str):
        if isinstance(x, var_type) is False:
            if none_type and x is None:
                pass
            elif none_type:
                raise TypeError("'%s' is not %s or None: %s" %
                                (var_str, str(var_type), str(type(x))+": " + str(x)))
            else:
                raise TypeError("'%s' is not %s: %s" %
                                (var_str, str(var_type), str(type(x))+": " + str(x)))
    elif not isinstance(var_str, str):
        raise TypeError("'var_str' is not %s: %s" %
                        (str(str), str(x)))
    else:
        raise Exception("Something went wrong in verify_type()")


def verify_pair_of_1D_arrays_type_and_shape(
        # Union[npt.NDArray, Sequence[Union[int, float]]],
        xdata: npt.ArrayLike,
        ydata: npt.ArrayLike  # Union[npt.NDArray, Sequence[Union[int, float]]]
    # ) -> Tuple[Union[npt.NDArray, Sequence[Union[int, float]]], Union[npt.NDArray, Sequence[Union[int, float]]]]:
) -> Tuple[npt.ArrayLike, npt.ArrayLike]:
    """
    Verifys that the two arrays are equal 1D shape and correct orientation (#,). Raises ValueError if not.

    Parameters
    ----------
    xdata : arraylike
        experimental data to check if shape is equilvelent to ydata
    ydata : arraylike
        experimental data to check if shape is  equilvelent to xdata

    Returns
    ----------
    (xdata : np.ndarray, ydata : np.ndarray)
        If input arguments are not numpy arrays, they will be converted to np.ndarray. Otherwise, the original arrays are returned.


    Raises
    ------
    ValueError
        If xdata and ydata are not the same shape
    """
    # check if xdata and ydata are np.ndarray, if not convert them to
    if isinstance(xdata, np.ndarray) is False:
        try:
            xdata = np.array(xdata, dtype=np.float64)
            if xdata.ndim != 1:
                raise TypeError("'xdata' is not 1D array")
        except ValueError as errmsg:
            raise ValueError(str(errmsg)+" in 'xdata'")
    if isinstance(ydata, np.ndarray) is False:
        try:
            ydata = np.array(ydata, dtype=np.float64)
            if ydata.ndim != 1:
                raise TypeError("'ydata' is not 1D array")
        except ValueError as errmsg:
            raise ValueError(str(errmsg)+" in 'ydata'")
    return xdata, ydata


def verify_pair_of_1D_arrays_lengths(xdata: npt.ArrayLike, ydata: npt.ArrayLike):
    """
    Verifys that the two arrays are equal length. Raises ValueError if not.

    Parameters
    ----------
    xdata : arraylike
        experimental data to check if lengths are equilvelent to ydata
    ydata : arraylike
        experimental data to chekc if length is  equilvelent to xdata

    Returns
    ----------
    None

    Raises
    ------
    ValueError
        If xdata and ydata are not the same length
    """
    # convert to numpy arrays s.t. that lengths can be determined
    ydata = np.array(ydata)
    xdata = np.array(xdata)
    # get lengths of data and verify they are the same lengths.
    len_ydata = len(ydata)
    len_xdata = len(xdata)
    if len_xdata != len_ydata:
        raise ValueError("xdata and ydata arrays must have the same length.")


def verify_pair_of_1D_arrays(xdata: npt.ArrayLike, ydata: npt.ArrayLike) -> Tuple[npt.ArrayLike, npt.ArrayLike]:
    """
    Verifys that the two arrays are equal 1D shape (length) and correct orientation (#,). 
    Raises ValueError if not.

    Parameters
    ----------
    xdata : arraylike
        experimental data to check if equilvelent to ydata
    ydata : arraylike
        experimental data to check if equilvelent to xdata

    Returns
    ----------
    (xdata : np.ndarray, ydata : np.ndarray)
        If input arguments are not numpy arrays, they will be converted to np.ndarray. Otherwise, the original arrays are returned.


    Raises
    ------
    ValueError
        If xdata and ydata are not the same shape
    """
    # verify shape and orientation is 1D
    xdata, ydata = verify_pair_of_1D_arrays_type_and_shape(xdata, ydata)
    # verify resulting 1D arrays are same length
    verify_pair_of_1D_arrays_lengths(xdata, ydata)
    return xdata, ydata
