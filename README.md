# seeing-double
Identifying binary stars using their light curves only

To generate a training and testing set, clone this repository and cd into it.
This code produces light curves for 'single' stars and 'double' stars, where
the double stars are two single star light curves added together.

The function assemble_data in 'make_training_set.py' will generate synthetic
light curves and save them to a directory of your choice (default is current
directory). Example usage:

```python
lc_dir = "/Users/ruthangus/.kplr/data/lightcurves"  # The directory where
.kplr save light curves
assemble_data(10, lc_dir, ftrain=.8, fdouble=.5, ndays=70, path=".", saveplot=True)
```

Dependencies:
numpy, kplr, pandas and matplotlib.

All these dependencies can be downloaded with pip install.


Docstring for the 'assemble_data' function:
```python
    """
    Code for downloading a training set for Kepler binary project.
    params:
    -------
    N: (int)
        The total number of stars light curves to download. This will be
        adjusted up to give integer fractions of star numbers.
    lc_dir: (str)
        The path to the place where .kplr downloads light curves.
        On my machine this is "~/.kplr/data/lightcurves"
    ftrain: (float)
        The fraction of stars to train on.
        (1-ftrain) is the fraction of test stars. default is 0.8.
        Must be between 0 and 1.
    fdouble: (float)
        The fraction of "double" stars you want.
        (Warning: some of these might be triples or quadruples!)
        Must be between 0 and 1. Default is 0.5 and must be 0.5 for now.
        fsingle = 1-fdouble.
    ndays: (int)
        The number of days of light curves to download. Default is 70.
    path: str
        The path to the directory you'd like the train and test light curves
        and plots to be saved in. Default is current directory.
        Two subdirectories will be created containing test and train light
        curves.
    saveplot: (boolean)
        If true, plots of the light curves will be saved to the train and test
        directories.
    """
```
