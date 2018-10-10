import numpy as np
import kplr
client = kplr.API()
import pandas as pd
import os
from kepler_data import load_kepler_data
import matplotlib.pyplot as plt


def assemble_data(N, lc_dir, ftrain=.8, fdouble=.5, ndays=70, path=".",
                  saveplot=False):
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
    while (N * ftrain) % 3 and (N * (1 - ftrain)) % 3:
        N += 1
    print("actually using {} stars".format(N))

    df = pd.read_csv("../data/KICs.csv")
    kids = df.KIC.values
    np.random.shuffle(kids)
    kids = kids[:N]

    ntrain = int(N*ftrain)
    print(N, "stars in total")
    print(ntrain, "for training, ", N - ntrain, "for testing")
    print(ntrain/3, "training singles, ", (ntrain/3)*2, "training doubles, ",
          (N - ntrain)/3, "testing singles, ", 2*((N - ntrain)/3),
          "testing doubles")

    # Create the directories for saving data
    dirname = "{0}/train/".format(path)
    if not os.path.exists(dirname):
        os.mkdir(dirname)
        print("Directory " , dirname ,  " Created ")

    dirname = "{0}/test/".format(path)
    if not os.path.exists(dirname):
        os.mkdir(dirname)
        print("Directory " , dirname ,  " Created ")

    # Allocate indices for splitting train and test.
    inds = np.arange(N)
    np.random.seed(42)
    np.random.shuffle(inds)
    training_inds = inds[:ntrain]
    testing_inds = inds[ntrain:]

    training_ids = df.KIC.iloc[training_inds]
    make_singles_and_doubles(training_ids.values, "train", ndays, path=path,
                             lc_dir=lc_dir, saveplot=saveplot)

    testing_ids = df.KIC.iloc[testing_inds]
    make_singles_and_doubles(testing_ids.values, "test", ndays, path=path,
                             lc_dir=lc_dir, saveplot=saveplot)


def make_singles_and_doubles(ids, train_or_test, ndays, lc_dir, fdouble=.5,
                             path=".", saveplot=False):
    """
    params:
    -------
    ids: list or array
        The KIC ids to create light curves from.
    train_or_test: str
        The directory in which to save the resulting light curves.
    """
    ntrain = len(ids)
    ndouble = int((ntrain/3) * 2)

    double_ids = ids[:ndouble]
    single_ids = ids[ndouble:]
    print(train_or_test, "set: ", ndouble/2, "doubles, made with {} light"
          "curves and ".format(ndouble), len(single_ids), "singles \n")

    for j, i in enumerate(np.arange(0, len(double_ids), 2)):
        id0, id1, id2 = str(double_ids[i]).zfill(9), \
            str(double_ids[i + 1]).zfill(9), str(single_ids[j]).zfill(9)
        print("double 1 id = ", id0, "double 2 id = ", id1, "single id = ",
              id2)

        # Download the light curves to add together
        fname = "{0}/{1}".format(lc_dir, id0)
        if not os.path.exists(fname):
            download_light_curve(double_ids[i])
        fname = "{0}/{1}".format(lc_dir, id1)
        if not os.path.exists(fname):
            download_light_curve(double_ids[i + 1])

        # Download the single star light curve.
        fname = "{0}/{1}".format(lc_dir, id2)
        if not os.path.exists(fname):
            download_light_curve(single_ids[j])

        # Load the light curves into memory
        p0 = "{0}/{1}".format(lc_dir, id0)
        x0, y0, yerr0, cadence0 = load_kepler_data(p0)
        p1 = "{0}/{1}".format(lc_dir, id1)
        x1, y1, yerr1, cadence1 = load_kepler_data(p1)
        p2 = "{0}/{1}".format(lc_dir, id2)
        x2, y2, yerr2, cadence2 = load_kepler_data(p2)

        # Add the light curves together according to their cadences.
        x, y0, yerrdouble, x1, y1, yerr1, ydouble, \
            xsingle, ysingle, yerrsingle, cadence = \
                add_lcs_together(x0, y0, yerr0, cadence0,
                                x1, y1, yerr1, cadence1,
                                x2, y2, yerr2, cadence2)

        # Choose a random segment of the light curve that is ndays long and
        # make sure it's not empty!
        tmin, tmax = 0, max(x) - ndays
        for k in range(100):
            t = np.random.uniform(tmin, tmax)
            m = (t < x) * (x < t + ndays)
            if len(x[m]):
                break
        x, y0, yerrdouble, x1, y1, yerr1, ydouble, xsingle, ysingle, \
            yerrsingle, cadence = x[m], y0[m], yerrdouble[m], x1[m], y1[m], \
            yerr1[m], ydouble[m], xsingle[m], ysingle[m], yerrsingle[m], \
            cadence[m]

        if saveplot:
            plt.figure(figsize=(16, 9))
            plt.plot(x, y0, ".", label="star 1")
            plt.plot(x1, y1 + .01, ".", label="star 2")
            plt.plot(x, ydouble + .02, ".", label="double star")
            plt.plot(xsingle, ysingle + .03, "k.", label="single star")
            plt.legend()
            figname = "{0}/{1}/{2}_{3}_{4}_plot".format(path, train_or_test,
                                                        id0, id1, id2)
            print("saving figure as ", figname)
            plt.savefig(figname)

        # Save the light curves.
        double_lc = pd.DataFrame(dict({"time": x, "flux": ydouble,
                                       "flux_err": yerrdouble,
                                       "cadence": cadence}))
        fname = "{0}/{1}/{2}_{3}_lc.csv".format(path, train_or_test, id0, id1)
        print("saving double lc to ", fname)
        double_lc.to_csv(fname)

        single_lc = pd.DataFrame(dict({"time": x, "flux": ysingle,
                                       "flux_err": yerrsingle,
                                       "cadence": cadence}))
        fname = "{0}/{1}/{2}_lc.csv".format(path, train_or_test, id2)
        print("saving single lc to ", fname, "\n")
        single_lc.to_csv(fname)


def add_lcs_together(x0, y0, yerr0, cadence0, x1, y1, yerr1, cadence1, x2, y2,
                     yerr2, cadence2):
    df0 = pd.DataFrame(dict({"x0": x0, "y0": y0, "yerr0": yerr0,
                             "cadence": cadence0}))
    df1 = pd.DataFrame(dict({"x1": x1, "y1": y1, "yerr1": yerr1,
                             "cadence": cadence1}))
    df2 = pd.DataFrame(dict({"x2": x2, "y2": y2, "yerr2": yerr2,
                             "cadence": cadence2}))
    _df = pd.merge(df0, df1, on="cadence", how="inner")
    df = pd.merge(_df, df2, on="cadence", how="inner")

    return df.x0.values, df.y0.values, df.yerr0.values, \
           df.x1.values, df.y1.values, df.yerr1.values, \
           df.y0.values+df.y1.values, \
           df.x2.values, df.y2.values, df.yerr2.values, df.cadence.values


def download_light_curve(id):
    """
    Download the Kepler light curves of star (id). Default location is
    ~/.kplr/data/lightcurves/
    """
    star = client.star(id)
    print("downloading light curves for star ", id, "...")
    star.get_light_curves(fetch=True, short_cadence=False)


if __name__ == "__main__":
    lc_dir = "/Users/ruthangus/.kplr/data/lightcurves"
    assemble_data(10, lc_dir, ftrain=.8, fdouble=.5, ndays=70, path=".",
                  saveplot=True)
