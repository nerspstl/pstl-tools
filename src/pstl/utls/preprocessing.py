from collections.abc import Sequence
import tkinter as tk
import numpy as np
import pandas as pd
from matplotlib.figure import Figure
from matplotlib.lines import Line2D
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg, NavigationToolbar2Tk  # type: ignore
from scipy.signal import find_peaks, savgol_filter
from scipy.optimize import curve_fit

from pstl.utls.verify import verify_pair_of_1D_arrays, verify_type
from pstl.utls.helpers import normalize
from pstl.utls.helpers import _fit_exponential_func, _fit_linear_func, _fit_polynomial_func
from pstl.utls.helpers_savgol import set_savgol_filter_defaults


def smooth_filter(data, polyorder=1, window_length=1, *args, **kwargs):
    voltage = data.voltage
    current = data.current

    # perform preprocessing filter
    current = savgol_filter(
        current, polyorder=polyorder, window_length=window_length, *args, **kwargs)

    smoothed_data = pd.DataFrame({"voltage": voltage, "current": current})

    return smoothed_data


def preprocess_filter(data, *args, delete=True, **kwargs):
    voltage = data.voltage
    current = data.current

    # perform preprocessing filter
    voltage, current, pts_deleted = preprocessing_filter(
        voltage, current, delete=delete, interactive=False,
    )
    #print(pts_deleted)

    filtered_data = pd.DataFrame({"voltage": voltage, "current": current})
    deleted_data = pd.DataFrame(
        {
            "voltage": pts_deleted[:, 0], "current": pts_deleted[:, 1]
        }
    )
    return filtered_data, deleted_data


def preprocessing_filter(xdata: np.ndarray, ydata: np.ndarray,
                         delete: bool = True, replace: bool = False, interp: str = 'linear',
                         interactive: bool = False,
                         *args, **kwargs) -> tuple[np.ndarray, np.ndarray, np.ndarray | None]:
    """
    Preprocesses xdata and ydata by applying Savitzky-Golay filter for smoothing the curve, 
    detecting erroneous points using find_peaks, and optionally replacing erroneous points with 
    interpolated values. 

    Parameters:
    -----------
    xdata: np.ndarray
        Array containing x-coordinates of the data.
    ydata: np.ndarray
        Array containing y-coordinates of the data.
    delete: bool, default True
        Boolean indicating whether to delete the erroneous points or not. If True, deletes the points.
    replace: bool, default False
        Boolean indicating whether to replace the erroneous points with interpolated values or not.
    interp: str, default 'linear'
        String indicating the interpolation scheme for replacing the erroneous points. 
        Must be one of 'linear', 'exponential', 'polynomial'.
    interactive: bool, default False
        Boolean indicating whether to show interactive matplotlib to get better filtering.
    **kwargs:
        Additional keyword arguments that can be passed to savgol_filter or find_peaks functions.
        The keyword arguments **kwargs are used to specify additional options for the Savitzky-Golay filter and the find_peaks function. The possible keyword arguments are:
        - savgol_filter_kw: A dictionary of keyword arguments for the Savitzky-Golay filter. The default value is {}.
            - window_length: int, optional
                Length of the filter window. If None, it is calculated as 0.08 * len(ydata). Default is None.
            - polyorder: int, optional
                Order of the polynomial used to fit the samples. Default is 1.
        - find_peaks_kw: A dictionary of keyword arguments for the find_peaks function. The default value is {}.
            - prominence: float, optional
                Minimum prominence of peaks. Normalized between [0, 1]. Default is 0.5.
            - threshold: float, optional
                Minimum height of peaks. Normalized between [0, 1]. Default is 0.2.

    Returns:
    --------
    Tuple[np.ndarray, np.ndarray, np.ndarray | None]
        Tuple containing the preprocessed xdata and ydata and x,y points modified.

        If delete=True and replace=False: A tuple of two numpy arrays (xdata, ydata) with erroneous points removed.
        If delete=False and replace=True: A tuple of two numpy arrays (xdata, ydata) with erroneous points replaced by interpolated values.
        If delete=True and replace=True: A tuple of two numpy arrays (xdata, ydata) with erroneous points removed and then replaced by interpolated values.
    """
    # Verify Arrays
    # check if xdata and ydata are np.ndarray, if not convert them to np.ndarray
    # and get shape/lengths of data and verify they are the same.
    xdata, ydata = verify_pair_of_1D_arrays(xdata, ydata)  # type: ignore
    len_data = len(xdata)

    # Get Defaults from keywords for savgol filter and findpeaks
    # retrive savgol_filter and find_peaks keyword arguments from kwargs
    savgol_filter_kw = kwargs.get('savgol_filter_kw', {})
    find_peaks_kw = kwargs.get('find_peaks_kw', {})

    # Savgol_filter for smoothing curve to find difference to identify
    # errounous (spikes) in data

    # Set defaults for savgol_filter
    window_length, polyorder, savgol_filter_kw = set_savgol_filter_defaults(
        ydata, savgol_filter_kwargs=savgol_filter_kw)

    # apply savgol fiter to ydata
    ydata_filtered = savgol_filter(
        ydata, window_length, polyorder, **savgol_filter_kw)

    # Determine where errounous points (spikes in data) occur using find_peaks
    # find difference of ydata and savgol_filtered data, then absolute value and
    # normalize
    ydata_abs_diff = np.abs(np.subtract(ydata, ydata_filtered))
    ydata_normalized = normalize(ydata_abs_diff)

    # get defaults for find_peaks if none are given
    find_peaks_kw['prominence'] = find_peaks_kw.get('prominence', 0.5)
    find_peaks_kw['threshold'] = find_peaks_kw.get('threshold', 0.2)

    # verify is either float, integer or None, raise error if they are not
    if isinstance(find_peaks_kw['prominence'], (int, float)) is False:
        if find_peaks_kw['prominence'] is not None:
            raise TypeError("'prominence' is not an integer or float: %s" % (
                str(find_peaks_kw['prominence'])))
    if isinstance(find_peaks_kw['threshold'], (int, float)) is False:
        if find_peaks_kw['prominence'] is not None:
            raise TypeError("'threshold' is not an integer or float: %s" % (
                str(find_peaks_kw['threshold'])))
    # verify the values are less then one as these are normalized peaks
    if find_peaks_kw['prominence'] > 1:
        if find_peaks_kw['prominence'] is not None:
            raise ValueError("peaks are normalized, 'prominence' must be a value less than 1 or None: %s" % (
                str(find_peaks_kw['prominence'])))
    if find_peaks_kw['threshold'] > 1:
        if find_peaks_kw['threshold'] is not None:
            raise ValueError("peaks are normalized, 'threshold' must be a value less than 1 or None: %s" % (
                str(find_peaks_kw['threshold'])))

    # solve and identify peaks
    peaks, props = find_peaks(ydata_normalized, **find_peaks_kw)

    # if interp is 'linear', 'exponetial', 'polynomial.
    interp_strings = ['linear', 'exponential', 'polynomial']
    if (replace is True) and (interp in interp_strings):
        if interp in ['linear']:
            fit_func = _fit_linear_func
        elif interp in ['exponential']:
            fit_func = _fit_exponential_func
        elif interp in ['polynomial']:
            fit_func = _fit_polynomial_func
        else:
            raise ValueError("wrong interpolation scheme")
        xdata_points_to_replace = xdata[peaks]
        ydata_points_to_replace = ydata[peaks]
        # loop through indeces to replace
        ydata_modified = ydata.copy()
        xdata_modified = xdata.copy()
        for ipeak in peaks:
            if ipeak != 0 and ipeak != len_data:
                ilower = ipeak-1
                ihigher = ipeak+1
            elif ipeak == 0:
                ilower = ipeak+1
                ihigher = ipeak+2
            elif ipeak == len_data:
                ilower = ipeak-2
                ihigher = ipeak+1
            else:
                raise ValueError(
                    "Something went wrong with indecies during replacing points")
            popt, pcov = curve_fit(fit_func,
                                   xdata_points_to_replace[ilower, ihigher],
                                   ydata_points_to_replace[ilower, ihigher],
                                   )
            ydata_fitted = fit_func(xdata_points_to_replace,
                                    *tuple(popt))
            ydata_modified[ipeak] = ydata_fitted
        points_modified = np.array([xdata[peaks], ydata[peaks]]).transpose()
    # if delete is True
    elif delete is True:
        xdata_modified = np.delete(xdata, peaks)
        ydata_modified = np.delete(ydata, peaks)
        points_modified = np.array([xdata[peaks], ydata[peaks]]).transpose()
    # if replace but wrong interp
    elif (replace is False) and (interp not in interp_strings):
        raise ValueError("Error in 'replace is %s and 'interp' is %s" %
                         (str(replace), str(interp)))
    else:
        xdata_modified = xdata.copy()
        ydata_modified = ydata.copy()
        points_modified = np.array([[],[]]).transpose()

    # if interactive plot, makes plots
    if interactive:
        # create root tkinter window to house the plots
        root = tk.Tk()
        # create frames to store figure canvas (draw on)
        frame_figure = tk.Frame(root)
        # and the create frame for control panel packed next to canvas
        frame_control_panel = tk.Frame(root)
        # create control panels for filter and peaks
        frame_cp_filter = tk.Frame(frame_control_panel)
        frame_cp_peaks = tk.Frame(frame_control_panel)
        # create figure to be added to the window
        fig = Figure(figsize=(8, 6), dpi=100)
        # autoadjust the layout to tight
        fig.set_tight_layout(True)
        # initialize figure
        # A tk.DrawingArea.
        canvas = FigureCanvasTkAgg(fig, master=frame_figure)
        canvas.draw()
        wgt_canvas = canvas.get_tk_widget()

        # pack_toolbar=False will make it easier to use a layout manager later on.
        wgt_toolbar = NavigationToolbar2Tk(
            canvas, frame_figure, pack_toolbar=False)
        wgt_toolbar.update()

        # get the axes object
        ax_filter = fig.add_subplot(211)  # type: ignore
        ax_peaks = fig.add_subplot(212, sharex=ax_filter)  # type: ignore
        # set title
        # fig.title("Filtering Erronous Points")
        # add raw data plot
        raw_data_kwargs = kwargs.get('raw_data_kwargs', {})
        raw_data_kwargs.setdefault('color', 'C0')
        raw_data_kwargs.setdefault('alpha', 0.3)
        raw_data_kwargs.setdefault('markerfacecolor', 'none')
        raw_data_kwargs.setdefault('label', 'Prefiltered Data')
        raw_data_kwargs.setdefault('linestyle', '-')
        raw_data_kwargs.setdefault('marker', '*')
        line_raw_data, = ax_filter.plot(  # type: ignore
            xdata, ydata, **raw_data_kwargs)  # type: ignore

        # add filterd data plot
        filtered_data_kwargs = kwargs.get('filtered_data_kwargs', {})
        filtered_data_kwargs.setdefault('color', 'C1')
        filtered_data_kwargs.setdefault('alpha', 0.5)
        filtered_data_kwargs.setdefault('markerfacecolor', 'none')
        filtered_data_kwargs.setdefault('label', 'Filtered Data')
        filtered_data_kwargs.setdefault('linestyle', '-')
        filtered_data_kwargs.setdefault('marker', '^')
        line_filtered_data, = ax_filter.plot(  # type: ignore
            xdata, ydata_filtered, **filtered_data_kwargs)

        # add modified returning data
        modified_data_kwargs = kwargs.get('modified_data_kwargs', {})
        modified_data_kwargs.setdefault('color', 'C2')
        modified_data_kwargs.setdefault('alpha', 1)
        modified_data_kwargs.setdefault('markerfacecolor', 'none')
        modified_data_kwargs.setdefault('label', 'Modified Data')
        modified_data_kwargs.setdefault('linestyle', '-')
        modified_data_kwargs.setdefault('marker', 'v')
        line_modified_data, = ax_filter.plot(  # type: ignore
            xdata_modified, ydata_modified, **modified_data_kwargs)

        # points deleted
        deleted_data_kwargs = kwargs.get('deleted_data_kwargs', {})
        deleted_data_kwargs.setdefault('color', 'C3')
        deleted_data_kwargs.setdefault('alpha', 1)
        # deleted_data_kwargs.setdefault('markerfacecolor', 'None')
        deleted_data_kwargs.setdefault('label', 'Erroneous Spikes')
        deleted_data_kwargs.setdefault('linestyle', 'None')
        deleted_data_kwargs.setdefault('marker', 'X')
        line_peaks, = ax_filter.plot(
            xdata[peaks], ydata[peaks], **deleted_data_kwargs
        )

        # add nomralized, abs residual and identified peaks
        residual_plot_kwargs = kwargs.get('residual_plot_kwargs', {})
        residual_plot_kwargs.setdefault('color', 'C2')
        residual_plot_kwargs.setdefault('alpha', 1)
        residual_plot_kwargs.setdefault('markerfacecolor', 'none')
        residual_plot_kwargs.setdefault(
            'label', 'Normalized Absolute Resdiual')
        residual_plot_kwargs.setdefault('linestyle', '-')
        residual_plot_kwargs.setdefault('marker', 'o')
        line_residual, = ax_peaks.plot(
            xdata, ydata_normalized, **residual_plot_kwargs
        )

        # add nomralized, abs residual and identified peaks
        peaks_plot_kwargs = kwargs.get('peaks_plot_kwargs', {})
        peaks_plot_kwargs.setdefault('color', 'C3')
        peaks_plot_kwargs.setdefault('alpha', 1)
        # peaks_plot_kwargs.setdefault('markerfacecolor', 'None')
        peaks_plot_kwargs.setdefault('label', 'Erroneous Spikes')
        peaks_plot_kwargs.setdefault('linestyle', 'None')
        peaks_plot_kwargs.setdefault('marker', 'X')
        line_peaks, = ax_peaks.plot(
            xdata[peaks], ydata_normalized[peaks], **peaks_plot_kwargs
        )

        # turn legends on
        ax_filter.legend()
        ax_peaks.legend()

        # Declare the variabels for tkinter widgets
        var_window_length = tk.IntVar()
        var_polyorder = tk.IntVar()
        # set default values
        var_window_length.set(window_length)
        var_polyorder.set(polyorder)

        def update_filter(window_length: int, polyorder: int, ydata: Sequence[float],
                          line_filtered_data: Line2D, **savgol_filter_kw) -> None:
            # apply filter with updated parameters
            ydata_filtered = savgol_filter(
                ydata, window_length, polyorder, **savgol_filter_kw)

            # set the filtered data to the updated values
            line_filtered_data.set_ydata(ydata_filtered)
            canvas.draw()

        # Make a horizontal slider to control the frequency.
        window_length_slider = tk.Scale(
            frame_cp_filter, variable=var_window_length,  # type: ignore
            from_=2, to=len_data, label="Window length",
            command=lambda val: update_filter(var_window_length.get(),
                                              var_polyorder.get(),
                                              line_raw_data.get_ydata(),
                                              line_filtered_data,
                                              **savgol_filter_kw)
        )

        # Make a vertically oriented slider to control the amplitude
        polyorder_slider = tk.Scale(
            frame_cp_filter, variable=var_polyorder,  # type: ignore
            from_=1, to=len_data-1, label="Polyorder",
            command=lambda val: update_filter(
                var_window_length.get(),
                var_polyorder.get(),
                line_raw_data.get_ydata(),
                line_filtered_data,
                **savgol_filter_kw)
        )

        # Create a `matplotlib.widgets.Button` to reset the sliders to initial values.
        def reset_filter(window_length: int, polyorder: int, ydata: Sequence[float],
                         line_filtered_data: Line2D, **savgol_filter_kw) -> None:
            window_length_slider.set(window_length)
            polyorder_slider.set(polyorder)
            update_filter(
                int(window_length_slider.get()),
                int(polyorder_slider.get()),
                ydata,
                line_filtered_data,
                **savgol_filter_kw
            )
        btn_filter_reset = tk.Button(
            frame_cp_filter, text="Reset",  # type: ignore
            command=lambda: reset_filter(
                window_length,
                polyorder,
                line_raw_data.get_ydata(),
                line_filtered_data,
                **savgol_filter_kw)
        )

        # packing filter widgets
        window_length_slider.grid(  # type: ignore
            row=0, column=0, sticky="NWSE")
        polyorder_slider.grid(  # type: ignore
            row=0, column=1, sticky="NWSE")
        btn_filter_reset.grid(  # type: ignore
            row=1, column=0, columnspan=2, sticky="NWSE")

        # pack in canvas and toolbar widgets
        # wgt_canvas.grid(  # type: ignore
        # row=0, column=0, sticky="NSWE")
        # wgt_toolbar.grid(  # type: ignore
        # row=1, column=0, sticky="NSWE")
        wgt_toolbar.pack(side=tk.BOTTOM, fill=tk.X)  # type: ignore
        wgt_canvas.pack(side=tk.TOP, fill=tk.BOTH, expand=True)  # type: ignore

        # pack in sub control panel frames to main control panel frame
        frame_cp_filter.grid(  # type:ignore
            row=0, column=0, sticky="NWSE")
        frame_cp_peaks.grid(  # type:ignore
            row=1, column=0, sticky="NWSE")

        # pack in control panel to left of canvas
        frame_control_panel.grid(  # type: ignore
            row=0, column=0, sticky="NEWS")
        frame_figure.grid(  # type: ignore
            row=0, column=1, sticky="NEWS")

        # run mainloop
        root.mainloop()  # type: ignore
    elif interactive is False:
        pass
    else:
        raise ValueError("'interactive' only accepts bool: '%s' and '%s'" % (
            str(interactive)))

    # return tulpe of modified xdata
    return xdata_modified, ydata_modified, points_modified
