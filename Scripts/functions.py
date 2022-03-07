import rpy2.robjects.packages as rpackages
import rpy2.robjects as ro

import rpy2.robjects.conversion as conversion
from rpy2.robjects.lib import grdevices

from PIL import Image as image
from IPython.display import Image, display
import logging
import traceback
import pandas as pd
import tempfile
# from rpy2.robjects import pandas2ri
# imports for debugging differnce between py2rpy_pandasdataframe & rpy2.robjects.DataFrame.from_csvfile
# from pandas.core.frame import DataFrame as PandasDataFrame
# from collections import OrderedDict
# import warnings
# from rpy2.robjects.vectors import StrVector, DataFrame
# import rpy2.rinterface as rinterface

py2rpy = conversion.Converter('original pandas conversion').py2rpy


def _checks(data, layout, cut, image_name):
    """ just to check if parameters are acceptable.
    It is designed this way such that all errors will be reported to user before exiting.
    Note: except Exception doesn't catch keyboardInterrupt and SystemExits
    """
    try:
        if type(data) != pd.DataFrame:
            raise ValueError("Please use a pandas DataFrame.")
    except Exception:
        logging.error(traceback.format_exc())
    try:
        if layout not in ["spring", "circle", "groups"]:
            raise ValueError("Please use 'spring', 'circle' or 'groups'")
    except Exception:
        logging.error(traceback.format_exc())
    try:
        if not isinstance(layout, str):
            raise ValueError("layout must be a str")
    except Exception:
        logging.error(traceback.format_exc())
    try:
        if not isinstance(cut, float):
            cut = float(cut)
        if not isinstance(cut, (float, int)):
            raise ValueError("Cut must be an integer or float")
    except Exception:
        logging.error(traceback.format_exc())
    try:
        if not isinstance(image_name, str):
            raise ValueError("image_name must be a str preferably suffixed with .png")
    except Exception:
        logging.error(traceback.format_exc())


def ising_plot(data=None, layout="spring", cut=0.8, image_name="network.png", display_image=True, save=True):
    """
    IsingFit wrapper for python usage
    Note: Not all qgraph functionality is present. WIP/ upon request.

    Parameters
    ----------
    data : pandas.DataFrame, optional
        A Dataframe of binary data (non Binary data will be exempted from the final network), by default None
    layout : str, optional
        for R's qgraph:
        "circle" places all nodes in a single circle
        "groups" gives a circular layout in which each group is put in separate circles
        "spring" gives a force embedded layout
        , by default "spring"
    cut : float, optional
        A value to make all edges above the cut very thick and visible, by default 0.8
    image_name : str, optional
        A name for your png image, by default "network.png"
    display_image: bool, optional
        Display image when in notebook mode, by default True
    save: bool, optional
        Saves the image, by default True

    Returns
    -------
    rpy2.robjects.vectors.ListVector
        an 'IsingFit' object that contains the following items:
    weiadj:        The weighted adjacency matrix.
    thresholds:    Thresholds of the variables.
    q:             The object that is returned by qgraph (class 'qgraph'). It is the equivalent to weiadj but at 2 d.p.
    gamma:         The value of hyperparameter gamma.
    AND:           A logical indicating whether the AND-rule is used or not. If not, the OR-rule is used.
    time:          The time it took to estimate the network.
    asymm.weights: The (asymmetrical) weighted adjacency matrix before applying the AND/OR rule.
    lambda.values: The values of the tuning parameter per node that ensured the best fitting set of neighbors.
    """
    # Checks
    _checks(data, layout, cut, image_name)

    # imports
    ising_fit_r = rpackages.importr("IsingFit")
    qgraph_r = rpackages.importr("qgraph")

    # # py2rpy_pandasdataframe requires debugging!
    # data.set_index(pd.Index(range(1, len(data) + 1)))
    # pandas2ri.activate()             # automatic conversion of numpy objects into rpy2 objects
    # data_r = pandas2ri.py2rpy_pandasdataframe(data)  # convert pandas df to r df

    with tempfile.NamedTemporaryFile(mode='r+') as temp:
        data.to_csv(temp.name, index=False)
        data_r = ro.DataFrame.from_csvfile(temp.name)
        ising = ising_fit_r.IsingFit(data_r)

        # get the regular version with $weiadj
        with grdevices.render_to_bytesio(grdevices.jpeg, width=512, height=448, res=140) as img:
            qgraph_r.qgraph(ising.rx2("weiadj"), layout=layout, cut=cut)

        if save is True:
            # Save file
            with open(image_name, "wb") as png:
                png.write(img.getvalue())

        # if display is wanted
        if display_image is True:
            # if we want to display the image in a ipynb environment
            display(Image(data=img.getvalue(), format='jpeg', embed=True))

            # if we saved the file, we can open it up (this is more relevant for running as a script)
            if "png" in locals():
                # Image will open in a pop up
                picture = image.open(image_name)
                picture.show()
        return ising
