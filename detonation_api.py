__author__ = 'bwolfson'

#initial effort to stub out feed detonation
#

import json
import requests
import base64
import hashlib
import file_data_storage
import time

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

    def submit_md5(self, filename, detonation_time):
        '''
        submits or resubmits a file for detonation
        :param filename: the name of the file
        :param detonation_time: the suspected time for detonation
        :return:
        '''

        params = {}

        f = open(filename, 'rb')
        bytes = f.read()
        md5 = hashlib.md5(bytes).hexdigest()
        print md5
        print time.time()

        params['file'] = base64.b64encode(bytes)
        params['filename'] = filename
        params['md5'] = md5
        params['original_sample_size'] = len(bytes)
        params['timebox'] = detonation_time
        params['time_started'] = time.time()
        params['report'] = "Example report for a submitted binary sample"

        #Update the global dictionary of updated files keyed by md5
        #
        file_data_storage.global_dict[md5] = {
            'original_sample_size' : params['original_sample_size'],
            'timebox' : params['timebox'],
            'file' : params['file'],
            'filename' : params['filename'],
            'time_started' : params['time_started'],
            'report' : params['report']
        }

        url = '%s/submit' % self.server
        print params
        print url
        r = requests.post(url, data = json.dumps(params))
        r.raise_for_status()


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
