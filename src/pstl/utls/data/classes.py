import pandas as pd

available_file_types = {
    0   :   [".tab", "table", "tabular"],
    1   :   [".csv","csv"],
    2   :   [".json","json"],
    3   :   [".xls", "xls"],
}

def setup(settings):
    """
    Creates and returns a PSTLDataFrame object based on settings dictionary passed in.
    The settings parameter must have keys 'file' and 'file_type'.
    
    Keys:
        'file'      : str   ->  name of plasma ['cylinderical', 'spherical', or 'planar']
        'file_type' : str   ->  type of data file to read in ['.csv', '.xls', or '.json']
    (optional)
        'name'          : str   ->  name designation for data object
        'description'   : str   ->  description of data object
        'args'          : tuple ->  addional position arguments
        'kwargs'        : dict  ->  addional keyword arguments
    Returns: PSTLDataFrame Object

    Other Notes:
        common kwargs for 'file_type' : ".csv"
            "sep" --or-- "delimiter"    :   str         ->  tabular table delimiter i.e. "," --or-- "\t"
            "header"                    :   int | None  ->  location of header  
                i.e. 
                    if no-header then None
                    if first line header then 0
                    if names is given then header should be 0
            "names"     :   iterable(str,...)           ->  column names i.e. ["voltage", "current"]
            "skiprows"  :   int | list[int,...] | None  ->  # of rows or list of rows to skip
    """
    shape = settings["file_type"].lower()
    if shape in available_file_types[0]:
        get_data_func = pd.read_table
    elif shape in available_file_types[1]:
        get_data_func = pd.read_csv
    elif shape in available_file_types[2]:
        get_data_func = pd.read_json
    elif shape in available_file_types[3]:
        get_data_func = pd.read_excel
    else:
        raise ValueError("'%s' is not a valid option."%(shape))
    negative = settings.get("negative", False)
    name = settings.get("name",None)
    description = settings.get("name",None)
    file = settings["file"]
    args = settings.get("args", (None))
    kwargs = settings.get("kwargs",{})
    dataframe_args = kwargs.get("dataframe_args", [])
    dataframe_kwargs = kwargs.get("dataframe_kwargs",{})
    data = get_data_func(file,*args,**kwargs)
    data.iloc[:,1] = data.iloc[:,1]*-1 if negative is True else data.iloc[:,1] # type: ignore
    pstl_data = PSTLDataFrame(data,*dataframe_args,
                              name=name,description=description,
                              **dataframe_kwargs) # type: ignore
    return pstl_data

class PSTLDataFrame(pd.DataFrame):
    """
    Built on top of a pandas DataFrame, this class adds attributes 'name' and 'description'
    simply for tracking and identifying dataframes more easily
    """
    def __init__(self,*args,name=None,description=None,**kwargs) -> None:
        super().__init__(*args,**kwargs)
        self._name = name
        self._description = description

    @property
    def name(self):
        return self._name
    @name.setter
    def name(self, string):
        if isinstance(string, (str, type(None))):
            self._name = string
        else:
            raise TypeError("'%s' Must be a str or None type, not %s"%(str(string),str(type(string))))
    @property
    def description(self):
        return self._description
    @description.setter
    def description(self, string):
        if isinstance(string, (str, type(None))):
            self._description = string
        else:
            raise TypeError("Description change must be str or None type, not type '%s'"%(str(type(string))))

