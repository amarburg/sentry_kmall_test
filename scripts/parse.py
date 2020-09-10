#!/usr/bin/env python

# Copied shamelessly from command line interface found in kmall.py

import argparse
import logging
from kmall import KmallReader
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

    parser.add_argument('-z', action='store_true', dest = 'compress',
                       default = False, help="Create a compressed (somewhat lossy) version of the file. See -l")

    parser.add_argument('-l', action='store', type = int, dest = 'compressionLevel',
                       default = 0, help=("Set the compression level (Default: 0).\n" +
                       "\t 0: Somewhat lossy compression of soundings and imagery data.(Default)\n" +
                       "\t 1: Somewhat lossy compression of soundings with imagery omitted."))

    parser.add_argument('-Z', action='store_true', dest = 'decompress',
                       default = False, help=("Decompress a file compressed with this library. " +
                                             "Files must end in .Lz, where L is an integer indicating " +
                                             "the compression level (set by -l when compresssing)"))


    parser.add_argument('-v', action='count', dest='verbose', default=0,
                        help="Increasingly verbose output (e.g. -v -vv -vvv),"
                             "for debugging use -vvv")
    args = parser.parse_args()

    loglevel = logging.WARNING - (10*args.verbose) if args.verbose > 0 else logging.WARNING
    logging.basicConfig(format='%(levelname)s: %(message)s', level=loglevel)

    #kmall_filename = args.kmall_filename
    #kmall_directory = args.kmall_directory

    verify = args.verify

    # suffix = "kmall"
    # if decompress:
    #     suffix

    # if kmall_directory:
    #     filestoprocess = []
    #
    #     if verbose >= 3:
    #         print("directory: " + directory)
    #
    #     # Recursively work through the directory looking for kmall files.
    #     for root, subFolders, files in os.walk(kmall_directory):
    #         for fileval in files:
    #             if fileval[-suffix.__len__():] == suffix:
    #                 filestoprocess.append(os.path.join(root, fileval))
    # else:
    #     filestoprocess = [kmall_filename]

    # if filestoprocess.__len__() == 0:
    #     print("No files found to process.")
    #     sys.exit()

    for filename in args.inputfile:
        logging.info("")
        logging.info("Processing: %s" % filename)

        # Create the class instance.
        K = KmallReader(filename, logger=logging.getLogger() )
        K.verbose = args.verbose
        logging.debug("Processing file: %s" % K.filename)

        # Index file (check for index)
        K.index_file()

        ## Do packet verification if requested.
        pingcheckdata = []
        navcheckdata = []
        if verify:
            K.report_packet_types()
            pingcheckdata.append([x for x in K.check_ping_count()])

            K.extract_attitude()
            # Report gaps in attitude data.
            dt_att = np.diff([x.timestamp() for x in K.att["datetime"]])
            navcheckdata.append([np.min(np.abs(dt_att)),
                                 np.max(dt_att),
                                 np.mean(dt_att),
                                 1.0 / np.mean(dt_att),
                                 sum(dt_att >= 1.0)])
            # print("Navigation Gaps min: %0.3f, max: %0.3f, mean: %0.3f (%0.3fHz)" %
            #      (np.min(np.abs(dt_att)),np.max(dt_att),np.mean(dt_att),1.0/np.mean(dt_att)))
            # print("Navigation Gaps >= 1s: %d" % sum(dt_att >= 1.0))
            logging.info("Packet statistics:")

            # Print column headers
            # print('%s' % "\t".join(['File','Npings','NpingsMissing','NMissingMRZ'] +
            #                         ['Nav Min Time Gap','Nav Max Time Gap', 'Nav Mean Time Gap','Nav Mean Freq','Nav N Gaps >1s']))

            # Print columns
            # for x,y in zip(pingcheckdata,navcheckdata):
            #    row = x+y
            #    #print(row)
            #    print("\t".join([str(x) for x in row]))

            # Create DataFrame to make printing easier.
            DataCheck = pd.DataFrame([x + y for x, y in zip(pingcheckdata, navcheckdata)], columns=
            ['File', 'Npings', 'NpingsMissing', 'NMissingMRZ'] +
            ['NavMinTimeGap', 'NavMaxTimeGap', 'NavMeanTimeGap', 'NavMeanFreq', 'NavNGaps>1s'])
            # K.navDataCheck = pd.DataFrame(navcheckdata,columns=['Min Time Gap','Max Time Gap', 'Mean Time Gap','Mean Freq','N Gaps >1s'])
            pd.set_option('display.max_columns', 30)
            pd.set_option('display.expand_frame_repr', False)
            logging.info(DataCheck)

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
