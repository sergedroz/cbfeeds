__author__ = 'bwolfson'

import sys
import optparse

# append DetApi
sys.path.append("../cbfeeds")
print sys.path
from cbfeeds import detonation_api



def build_cli_parser():
    parser = optparse.OptionParser(usage="%prog [options]", description="Submit an md5 for detonation")

    # for each supported output type, add an option
    #
    parser.add_option("-c", "--cburl", action="store", default=None, dest="server_url",
                      help="CB server's URL.  e.g., http://127.0.0.1 ")
    parser.add_option("-n", "--no-ssl-verify", action="store_false", default=True, dest="ssl_verify",
                      help="Do not verify server SSL certificate.")
    parser.add_option("-m", "--md5", action="store", default = None, dest = "md5",
                      help = "md5 of entire sample")

    return parser


def main(argv):
    parser = build_cli_parser()
    opts, args = parser.parse_args(argv)
    if not opts.server_url or not opts.no_ssl_verify or not opts.md5:
        print "Missing required parameter, try again with -h for help"
        sys.exit(-1)

    detapi = detonation_api.DetApi(opts.server_url, opts.no_ssl_verify)
    print detapi.test()


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))