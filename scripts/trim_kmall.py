#!/usr/bin/env python

# Simple parser which shows information about a .kmall file
#
# Copied shamelessly from command line interface found in kmall.py

import argparse
import logging
import kmall
import json
from pathlib import Path

import sys
import time
import signal
import subprocess


if __name__ == '__main__':
    # Handle input arguments
    parser = argparse.ArgumentParser(description="A python script (and class) "
                                                 "for parsing Kongsberg KMALL "
                                                 "data files.")

    ## Input filename as positional
    parser.add_argument('infile', type=Path,
                        help="The .kmall filename to parse.")

    parser.add_argument("outfile", type=Path,
                        help="Output Mat file")

    parser.add_argument("--size", metavar="N", type=int,
                        help="Desired output file size in MB")

    parser.add_argument('-v', action='count', dest='verbose', default=0,
                        help="Increasingly verbose output (e.g. -v -vv),"
                             "for debugging use -vv")

    args = parser.parse_args()

    defaultLogLevel = 1  # warning is default
    logLevels = [logging.ERROR, logging.WARNING, logging.INFO, logging.DEBUG]
    loglevel = logLevels[ max(0,min(len(logLevels), args.verbose+defaultLogLevel)) ]
    logging.basicConfig(format='%(message)s', level=loglevel)

    logging.warning("Processing: %s" % args.infile)
    size_bytes = args.size * 1024*1024

    # Create the class instance.
    K = kmall.KmallReader(args.infile)
    K.index_file()

    logging.warning("File has %d packets" % len(K.Index) )

    inset = K.Index.loc[lambda df: df['ByteOffset'] < size_bytes, : ]

    last_packet = inset.tail(1)

    logging.debug(last_packet)
    num_bytes = last_packet.ByteOffset + last_packet.MessageSize

    logging.debug("Copying %d bytes" % num_bytes)

    cmd = ['dd', "if=%s" % args.infile, "of=%s" % args.outfile, "bs=1", "count=%d" % num_bytes]
    p = subprocess.run( cmd )
