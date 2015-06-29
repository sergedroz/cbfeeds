__author__ = 'bwolfson'

#initial effort to stub out feed detonation
#

import json
import requests


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

    def submit_file(self, filename):
        '''
        submits a file for detonation
        :param filename: the name of the file
        :return:
        '''

        #form file to post from md5 file
        #

        files = {
            'file' : open(filename, 'rb'),
        }

        #post request to server
        #
        url = "%s/submit" % self.server

        r = requests.post(url, files = files)
        r.raise_for_status()
        return r.json()

    def submit_file_data(self, filename, original_sample_size, sample, timebox, status):
        '''
        submits the data for a given file upload
        :param filename: name of the file
        :param original_sample_size: original sample size, in bytes
        :param sample: complete sample
        :param timebox: time for detonation
        :param status: status of the detonation
        :return:
        '''
        analysis_results = {
            'score' : None,
            'analysis_successful' : None,
            'error_description' : None,
            'analysis_summary' : None
        }

        detonation_results = {
            'status' : status,
            'eta_to_analysis' : None,
            'eta_to_complete' : None,
            'analysis_complete' : None,
            'analysis_results' : analysis_results

        }

        request = {
            'filename' : filename,
            'original_sample_size' : original_sample_size,
            'sample' : sample,
            'timebox' : timebox,
            'detonation_results' : detonation_results
        }

        #add this line for multipart data (JSON and file)
        #
        #headers = {'Content-type': 'multipart/form-data'}
        url = "%s/submit/%s/data" % (self.server, filename)
        r = requests.put(url, data = json.dumps(request))
        r.raise_for_status()
        return r.json()
