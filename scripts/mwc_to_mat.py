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
        #mwc_packets = K.Index.loc[lambda df: df['MessageType'] == "#MWC", : ]

        if args.head:
            lines_to_process = K.Index.head( args.head )
        else:
            lines_to_process = K.Index

        ## Step through MWC packets
        for packet in lines_to_process.itertuples():

            exclude_packet_types = [ ]

            if packet.MessageType in exclude_packet_types:
                logging.debug("Offset %d:  Skipping message of type %s" %(packet.ByteOffset, packet.MessageType))
                continue

            logging.info("Reading %s packet at offset %d" % (packet.MessageType,packet.ByteOffset) )

            datagram = K.read_datagram( packet )

            if not datagram:
                logging.debug("Offset %d:  Type %s, kmall.py returns no datagram, skipping..." % (packet.ByteOffset, packet.MessageType ) )
                continue

            as_json={}
            for key,item in datagram.items():

                if key is 'header':
                    header = datagram['header']
                    header['dgdatetime'] = str(header['dgdatetime'])
                    as_json[key] = header

                ## SVP has a datetime at the top level
                elif key is 'datetime':
                    as_json[key] = str(item)

                ## 'sensorData' in SPO has an embedded date
                elif key is "sensorData":
                    sensorData = datagram['sensorData']
                    if 'datetime' in sensorData:
                        sensorData['datetime'] = str(sensorData['datetime'])
                        as_json[key] = sensorData
                    else:
                        as_json[key] = item

                elif packet.MessageType=="#MWC" and key is 'beamData':
                    as_json[key] = dictoflists2listofdicts(datagram['beamData'])

                elif packet.MessageType is "#SKM" and key is 'sample':
                    item['KMdefault']['datetime'] = [str(dt) for dt in item['KMdefault']['datetime']]
                    item['delayedHeave']['datetime'] = [str(dt) for dt in item['delayedHeave']['datetime']]

                    as_json[key] = item

                else:
                    as_json[key] = item


            key = packet.MessageType[1:]
            if key not in mat_out:
                mat_out[key] = []

            mat_out[ packet.MessageType[1:] ].append(as_json)


    if args.output:

        sio.savemat( args.output, mat_out, long_field_names=True,
                        do_compression=args.compress,
                        oned_as='column' )
