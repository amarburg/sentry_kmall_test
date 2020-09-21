#!/usr/bin/env python

# Simple parser which shows information about a .kmall file
#
# Copied shamelessly from command line interface found in kmall.py

import argparse
import logging
import kmall
import json
from pathlib import Path

if __name__ == '__main__':
    # Handle input arguments
    parser = argparse.ArgumentParser(description="A python script (and class) "
                                                 "for parsing Kongsberg KMALL "
                                                 "data files.")

    ## Input filename as positional
    parser.add_argument('inputfile', action='store', nargs='*', type=Path,
                        help="The path and filename to parse.")

    # parser.add_argument('-d', action='store', type=Path, dest ='kmall_directory',
    #                     help="A directory containing kmall data files to parse.")

    parser.add_argument('--verify','-V', action='store_true', dest ='verify',
                        default=False, help="Perform series of checks to verify the kmall file.")

    parser.add_argument("--output", '-o', type=Path,
                        help="Save data to JSON")

    parser.add_argument("--head", metavar="N", type=int,
                        help="Only process first N entries")

    parser.add_argument('-v', action='count', dest='verbose', default=0,
                        help="Increasingly verbose output (e.g. -v -vv),"
                             "for debugging use -vv")

    args = parser.parse_args()

    defaultLogLevel = 1  # warning is default
    logLevels = [logging.ERROR, logging.WARNING, logging.INFO, logging.DEBUG]
    loglevel = logLevels[ max(0,min(len(logLevels), args.verbose+defaultLogLevel)) ]
    logging.basicConfig(format='%(message)s', level=loglevel)

    verify = args.verify

    packet_counts = {}

    json_out = {
        "MWC": []
    }

    for filename in args.inputfile:
        logging.warning("Processing: %s" % filename)

        # Create the class instance.
        K = kmall.KmallReader(filename)

        # Index file (check for index)
        K.index_file()

        logging.warning("File has %d packets" % len(K.Index) )

        ## Collect counts of each packet type
        grouped = K.Index.groupby('MessageType')

        duration = K.Index.index.max() - K.Index.index.min()
        logging.info("File duration %s" % duration)

        mt = grouped.sum()
        mt['Count'] = K.Index.groupby('MessageType').count()['MessageSize']
        mt.drop('ByteOffset', axis=1, inplace=True )

        logging.info(mt)

        # packet_types = K.Index['MessageType'].value_counts()
        # for type,count in packet_types.iteritems():
        #     logging.info("%10s : %5d" % (type, count))

        #mwc_packets = K.Index.loc[lambda df: df['MessageType'] == "#MWC", : ]

        if args.head:
            index = K.Index.head(args.head)
        else:
            index = K.Index

        ## Step through MWC packets
        for packet in index.itertuples():
            #logging.info("Reading MWC packet at offset %d" % packet.ByteOffset)

            mwc = K.read_datagram( packet )
