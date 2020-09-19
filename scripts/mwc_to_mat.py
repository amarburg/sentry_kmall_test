#!/usr/bin/env python

# Simple parser which shows information about a .kmall file
#
# Copied shamelessly from command line interface found in kmall.py

import argparse
import logging
import kmall
import json
from pathlib import Path

from numpy.core.records import fromarrays

import scipy.io as sio

def dictoflists2listofdicts( dl ):
    return [dict(zip(dl,t)) for t in zip(*dl.values())]


if __name__ == '__main__':
    # Handle input arguments
    parser = argparse.ArgumentParser(description="A python script (and class) "
                                                 "for parsing Kongsberg KMALL "
                                                 "data files.")

    ## Input filename as positional
    parser.add_argument('inputfile', action='store', nargs='*', type=Path,
                        help="The path and filename to parse.")

    parser.add_argument("--output", '-o', type=Path,
                        help="Output Mat file")

    parser.add_argument("--head", metavar="N", type=int,
                        help="Only process first N entries")

    parser.add_argument('-z', action='store_true', dest = 'compress',
                       default = False, help="Create a compressed (somewhat lossy) version of the file. See -l")

    parser.add_argument('-v', action='count', dest='verbose', default=0,
                        help="Increasingly verbose output (e.g. -v -vv),"
                             "for debugging use -vv")

    args = parser.parse_args()

    defaultLogLevel = 1  # warning is default
    logLevels = [logging.ERROR, logging.WARNING, logging.INFO, logging.DEBUG]
    loglevel = logLevels[ max(0,min(len(logLevels), args.verbose+defaultLogLevel)) ]
    logging.basicConfig(format='%(message)s', level=loglevel)

    mat_out = {
        "MWC": []
    }

    for filename in args.inputfile:
        logging.warning("Processing: %s" % filename)

        # Create the class instance.
        K = kmall.KmallReader(filename)
        K.index_file()

        logging.warning("File has %d packets" % len(K.Index) )

        duration = K.Index.index.max() - K.Index.index.min()
        logging.info("File duration %s" % duration)

        ## Collect counts of each packet type
        grouped = K.Index.groupby('MessageType')
        mt = grouped.sum()
        mt['Count'] = K.Index.groupby('MessageType').count()['MessageSize']
        mt.drop('ByteOffset', axis=1, inplace=True )

        logging.info(mt)

        ## Find all of the MWC packets
        mwc_packets = K.Index.loc[lambda df: df['MessageType'] == "#MWC", : ]
        if args.head:
            mwc_packets = mwc_packets.head( args.head )

        ## Step through MWC packets
        for packet in mwc_packets.itertuples():

            logging.info("Reading MWC packet at offset %d" % packet.ByteOffset)

            K.FID.seek(packet.ByteOffset,0)
            mwc = K.read_EMdgmMWC()

            mwc_json={}
            for key,item in mwc.items():

                if key is 'header':
                    header = mwc['header']
                    header['dgdatetime'] = str(header['dgdatetime'])
                    mwc_json[key] = header

                elif key is 'beamData':
                    mwc_json[key] = dictoflists2listofdicts(mwc['beamData'])

                else:
                    mwc_json[key] = item


            mat_out['MWC'].append(mwc_json)


    if args.output:

        sio.savemat( args.output, mat_out, long_field_names=True,
                        do_compression=args.compress,
                        oned_as='column' )
