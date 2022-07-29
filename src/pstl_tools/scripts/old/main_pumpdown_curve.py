import argparse
import matplotlib.pyplot as plt

import numpy as np


parser = argparse.ArgumentParser()
parser.add_argument("-f","--fname",\
        help="path/to/filename ie dir/out.csv",type=str)
args = parser.parse_args()

if args.fname is None:
    fname = input("please add fname>>")
else:
    fname = args.fname

def readDataIn(fname):
    with open(fname) as f:
        data = np.loadtxt(f,delimiter=',',skiprows=1)
    return data

def plotData(data):
    t = data[1:,0]
    p = data[1:,-1]
    plt.semilogy(t,p)
    plt.show()
    plt.close()


def main():
    data = readDataIn(fname)
    plotData(data)


if __name__ == "__main__":
    main()
