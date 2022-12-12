import argparse as arg

from pstl.tools.animate import monitor

from pstl.scripts.monitor.bakeout.defaults import set_defaults


# create parser class
parser=arg.ArgumentParser()

# add parser arguments
parser.add_argument("-f","--filename",
        help="Path to date file to use",
        type=str,default=None)
parser.add_argument("-s","--savename",
        help="Save plot and new csv with this name",
        type=str,dafault=None),
parser.add_argument("-d","--delimiter",
        help="Deliminator for csv file (default is ',')",
        type=str,default=",")
# collect arguments
args = parser.parse_args()

# define variables based on passed in arguments
fname = args.filename
sname = args.savename


def main():
    if fname is None:
        defaults=set_defaults()
    else:
        # will read in dict to use OR setup python script
        pass # delet once implemented
    bakeout=monitor.Figure(3,3,**defaults)
    bakeout.monitor()

if __name__ == "__main__":
    main()
