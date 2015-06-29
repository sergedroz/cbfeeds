__author__ = 'bwolfson'

import sys
import optparse
import detonation_api

def build_cli_parser():
    parser = optparse.OptionParser(usage="%prog [options]", description="Submit a file for detonation to the server")

    # for each supported output type, add an option
    #
    parser.add_option("-c", "--cburl", action="store", default=None, dest="server_url",
                      help="CB server's URL.  e.g., http://127.0.0.1 ")
    parser.add_option("-f", "--filename", action = "store", default = None, dest = "filename",
                      help = "Name of the file to be uploaded")
    parser.add_option("-o", "--orig_samp_size", action = "store", default = None, dest = "orig_samp_size",
                      help = "Original Sample Size for the sample")
    parser.add_option("-s", "--sample", action = "store", default = None, dest = "sample",
                      help = "the sample")
    parser.add_option("-t", "--timebox", action = "store", default = None, dest = "timebox",
                      help = "time box" )
    parser.add_option("--status", action = "store", default = None, dest = "status",
                      help = "status of the detonation")
    return parser

def main(argv):
    parser = build_cli_parser()
    opts, args = parser.parse_args(argv)
    if not opts.server_url or not opts.filename or not opts.orig_samp_size or not opts.sample or not opts.timebox or not opts.status:
        print "Missing required param; run with --help for usage"
        sys.exit(-1)

    # build a detonation api object
    #
    det = detonation_api.DetApi(opts.server_url)

    file_data = det.submit_file_data(opts.filename, opts.orig_samp_size, opts.sample, opts.timebox, opts.status)
    print file_data

if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
