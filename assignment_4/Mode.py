__author__ = 'Owner'


local = 1
planetLab = 2
testing = 3


def print_mode(x):
    # print ">>>>>"  + str(x)
    if x == local:
        return "local"
    elif x == planetLab:
        return "planetLab"
    elif x == testing:
        return "testing"
    else:
        return "Something wrong happened!!!!!!!!!!!!"