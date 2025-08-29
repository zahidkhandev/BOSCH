from functions.conversions import ctof
from functions.conversions import ftoc
import argparse

parser = argparse.ArgumentParser(description="program has 2 functions to convert celcius to Far or vice versa")

parser.add_argument('-b','--choice', metavar='choice', required=True)
parser.add_argument('-c', '--celcius', metavar='celcius', required=False)
parser.add_argument('-f','--farenheit', metavar='farenheit', required=False)

args = parser.parse_args()

if(args.choice == 'ftoc'):
    print(ftoc(args.farenheit))
else:
    print(ctof(args.celcius))
    