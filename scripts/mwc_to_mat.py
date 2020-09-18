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

    verify = args.verify

    packet_counts = {}

    mat_out = {
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

        mwc_packets = K.Index.loc[lambda df: df['MessageType'] == "#MWC", : ]
        if args.head > 0:
            mwc_packets = mwc_packets.head( args.head )

        ## Step through MWC packets
        for packet in mwc_packets.itertuples():
            logging.info("Reading MWC packet at offset %d" % packet.ByteOffset)

            K.FID.seek(packet.ByteOffset,0)
            mwc = K.read_EMdgmMWC()


            def make_json_beam( beamData ):

                ## Somewhat ugly due to the dict of lists structure
                return [{
                    'beamPointAngReVertical_deg': beamData['beamPointAngReVertical_deg'][i],
                    'sampleAmplitude05dB_p' : beamData['sampleAmplitude05dB_p'][i],
                    'rxBeamPhase_deg': beamData['rxBeamPhase_deg'][i]
                } for i in range(len(beamData['sampleAmplitude05dB_p'])) ]


            mwc_json = {
                "beams": make_json_beam(mwc['beamData'])
            }

            mat_out['MWC'].append(mwc_json)

            #logging.info(mwc)



    if args.output:

        sio.savemat( args.output, mat_out, long_field_names=True,
                        do_compression=args.compress,
                        oned_as='column' )

        # ## Do packet verification if requested.
        # pingcheckdata = []
        # navcheckdata = []
        # if verify:
        #     K.report_packet_types()
        #     pingcheckdata.append([x for x in K.check_ping_count()])
        #
        #     K.extract_attitude()
        #     # Report gaps in attitude data.
        #     dt_att = np.diff([x.timestamp() for x in K.att["datetime"]])
        #     navcheckdata.append([np.min(np.abs(dt_att)),
        #                          np.max(dt_att),
        #                          np.mean(dt_att),
        #                          1.0 / np.mean(dt_att),
        #                          sum(dt_att >= 1.0)])
        #     # print("Navigation Gaps min: %0.3f, max: %0.3f, mean: %0.3f (%0.3fHz)" %
        #     #      (np.min(np.abs(dt_att)),np.max(dt_att),np.mean(dt_att),1.0/np.mean(dt_att)))
        #     # print("Navigation Gaps >= 1s: %d" % sum(dt_att >= 1.0))
        #     logging.info("Packet statistics:")
        #
        #     # Print column headers
        #     # print('%s' % "\t".join(['File','Npings','NpingsMissing','NMissingMRZ'] +
        #     #                         ['Nav Min Time Gap','Nav Max Time Gap', 'Nav Mean Time Gap','Nav Mean Freq','Nav N Gaps >1s']))
        #
        #     # Print columns
        #     # for x,y in zip(pingcheckdata,navcheckdata):
        #     #    row = x+y
        #     #    #print(row)
        #     #    print("\t".join([str(x) for x in row]))
        #
        #     # Create DataFrame to make printing easier.
        #     DataCheck = pd.DataFrame([x + y for x, y in zip(pingcheckdata, navcheckdata)], columns=
        #     ['File', 'Npings', 'NpingsMissing', 'NMissingMRZ'] +
        #     ['NavMinTimeGap', 'NavMaxTimeGap', 'NavMeanTimeGap', 'NavMeanFreq', 'NavNGaps>1s'])
        #     # K.navDataCheck = pd.DataFrame(navcheckdata,columns=['Min Time Gap','Max Time Gap', 'Mean Time Gap','Mean Freq','N Gaps >1s'])
        #     pd.set_option('display.max_columns', 30)
        #     pd.set_option('display.expand_frame_repr', False)
        #     logging.info(DataCheck)

        #
        # ## Do compression if desired, at the desired level.
        # if compress:
        #
        #     if compressionLevel == 0:
        #
        #         print("Compressing soundings and imagery.")
        #         compressedFilename = K.filename + ".0z"
        #
        #         # Modify filename if the file already exists
        #         idx = 1
        #         while os.path.exists(compressedFilename):
        #             compressedFilename = ((K.filename + "_" + "%02d.0z") % idx)
        #             idx += 1
        #
        #         T = kmall(compressedFilename)
        #         K.index_file()
        #         T.OpenFiletoWrite()
        #
        #         for offset, size, mtype in zip(K.Index['ByteOffset'],
        #                                        K.Index['MessageSize'],
        #                                        K.Index['MessageType']):
        #             K.FID.seek(offset,0)
        #             if mtype == "b'#MRZ'":
        #                 dg = K.read_EMdgmMRZ()
        #                 T.write_EMdgmCZ0(dg)
        #             else:
        #                 buffer = K.FID.read(size)
        #                 T.FID.write(buffer)
        #
        #         K.closeFile()
        #         T.closeFile()
        #
        #     if compressionLevel == 1:
        #
        #         print("Compressing soundings, omitting imagery.")
        #         compressedFilename = K.filename + ".1z"
        #
        #         # Modify filename if the file already exists
        #         idx = 1
        #         while os.path.exists(compressedFilename):
        #             compressedFilename = compressedFilename + "_" + str(idx)
        #
        #         T = kmall(compressedFilename)
        #         K.index_file()
        #         T.OpenFiletoWrite()
        #
        #         for offset, size, mtype in zip(K.Index['ByteOffset'],
        #                                        K.Index['MessageSize'],
        #                                        K.Index['MessageType']):
        #             K.FID.seek(offset,0)
        #             if mtype == "b'#MRZ'":
        #                 dg = K.read_EMdgmMRZ()
        #                 T.write_EMdgmCZ1(dg)
        #             else:
        #                 buffer = K.FID.read(size)
        #                 T.FID.write(buffer)
        #
        #         K.closeFile()
        #         T.closeFile()
        #
        # # Decompress the file is requested.
        # if decompress:
        #
        #     # Discern the compression level and base filename.
        #     regexp = '(?P<basename>.*\.kmall)\.(?P<level>\d+)z'
        #     tokens = re.search(regexp,K.filename)
        #     if tokens is None:
        #         print("Could not discern compression level.")
        #         print("Expecting xxxxx.kmall.\d+.z, where \d+ is 1 or more")
        #         print("integers indicating the compression level.")
        #         sys.exit()
        #
        #     fileBasename = tokens['basename']
        #     compressionLevel = tokens['level']
        #
        #     # Give some status.
        #     if compressionLevel == "0":
        #         print("Decompressing soundings and imagery.(Level: 0)")
        #     elif compressionLevel == "1":
        #         print("Decompessing soundings, imagery was omitted in this format. (Level: 1)")
        #
        #     decompressedFilename = fileBasename
        #     # Check to see if decompressed filename exists and modify if necessary.
        #     idx = 1
        #     while os.path.exists(decompressedFilename):
        #         decompressedFilename = ((fileBasename[:-6] +
        #                                 "_" + "%02d" + '.kmall') % idx)
        #         idx += 1
        #
        #     if verbose >= 1:
        #         print("Decompressing to: %s" % decompressedFilename)
        #         print("Decompressing from Level: %s" % compressionLevel)
        #
        #     # Create kmall object for decompressed file and open it.
        #     T = kmall(filename=decompressedFilename)
        #     T.OpenFiletoWrite()
        #
        #     # Loop through the file, decompressing datagrams
        #     # when necessary and just writing them when not.
        #     for offset, size, mtype in zip(K.Index['ByteOffset'],
        #                                     K.Index['MessageSize'],
        #                                     K.Index['MessageType']):
        #         K.FID.seek(offset,0)
        #         if compressionLevel == "0":
        #
        #             if mtype == "b'#CZ0'":
        #                 dg = K.read_EMdgmCZ0()
        #                 T.write_EMdgmMRZ(dg)
        #             else:
        #                 buffer = K.FID.read(size)
        #                 T.FID.write(buffer)
        #
        #         if compressionLevel == "1":
        #
        #             if mtype == "b'#CZ1'":
        #                 dg = K.read_EMdgmCZ1()
        #                 T.write_EMdgmMRZ(dg)
        #             else:
        #                 buffer = K.FID.read(size)
        #                 T.FID.write(buffer)
        #
        #     T.closeFile()
        #     K.closeFile()
