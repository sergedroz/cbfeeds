__author__ = 'bwolfson'

import sys
import optparse
import detonation_api
import file_data_storage


def build_cli_parser():
    parser = optparse.OptionParser(usage="%prog [options]", description="Submit a file for detonation to the server")

    # for each supported output type, add an option
    #
    parser.add_option("-c", "--cburl", action="store", default=None, dest="server_url",
                      help="CB server's URL.  e.g., http://127.0.0.1 ")
    parser.add_option("-f", "--filename", action = "store", default = None, dest = "filename",
                      help = "Name of the file to be uploaded")
    parser.add_option("-t", "--timebox", action = "store", default = None, type = int, dest = "timebox",
                      help = "Detonation time for sample" )
    parser.add_option("-q", "--queue_time", action = "store", default = None, type = int, dest = "queue_time",
                      help = "Queue Time")

    return parser

def main(argv):
    parser = build_cli_parser()
    opts, args = parser.parse_args(argv)
    if not opts.server_url or not opts.filename or not opts.timebox or not opts.queue_time:
        print "Missing required param; run with --help for usage"
        sys.exit(-1)
    '''
    #some way of checking if the given filename actually exists in the filesystem
    lookfor = opts.filename
    file_found = False
    print lookfor
    print os.walk('.')
    for root, dirs, files in os.walk('\''):
        print "searching", root
        if lookfor in files:
            file_found = True
            print "found: %s" % join(root, lookfor)
            break

    if not file_found:
        print "File not found, check spelling/extension"
        sys.exit(-1)
    '''

    # build a detonation api object
    #
    det = detonation_api.DetApi(opts.server_url)

    det.submit_md5(opts.filename, opts.timebox, opts.queue_time)

    print file_data_storage.global_dict

if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))