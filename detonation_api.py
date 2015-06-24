__author__ = 'bwolfson'

#initial effort to stub out feed detonation
#

import json
import requests
import shutil

class DetApi(object):
    def __init__(self, server, ssl_verify=True, client_validation_enabled=True):
        """
        Requires:
            server -    URL to the server
            ssl_verify - verify server SSL certificate
        """
        if not server.startswith("http"):
            raise TypeError("Server must be URL: e.g, http://cb.example.com")
        self.server = server.rstrip("/")
        self.ssl_verify = ssl_verify
        self.client_validation_enabled = client_validation_enabled

    def submit_md5(self, md5, original_sample_size, sample, timebox):
        '''
        submits or resubmits the binary sample for detonation
        :param md5: the md5 of the entire sample
        :param original_sample_size: original sample size, in bytes
        :param sample: the sample
        :param timebox: time, in seconds, for which sample should be detonated
        :return:
        '''

        #form file to post from md5 file
        #

        files = {
            'file' : open(md5, 'rb'),
        }

        fields = {
            'original_sample_size' : original_sample_size,
            'sample' : sample,
            'timebox' : timebox
        }

        #post request to server
        #
        url = "http://127.0.0.1:9999/submit"
        self.submit_md5_helper(fields)
        r = requests.post(url, files = files)
        r.raise_for_status()
        return r.json()

    def submit_md5_helper(self, dict):
        #add this line for multipart data (JSON and file)
        #
        headers = {'Content-type': 'multipart/form-data'}
        url = "http://127.0.0.1:9999/submit"
        r = requests.post(url, data = json.dumps(dict), headers = headers)
        r.raise_for_status()
        return r.json()
