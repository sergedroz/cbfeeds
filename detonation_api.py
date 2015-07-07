__author__ = 'bwolfson'

'''
CBfeeds Detonation API file, used for testing through example scripts
'''

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

    def submit_md5(self, filename, detonation_time, queue_time):
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

        params['md5'] = md5
        params['original_sample_size'] = len(bytes)
        params['timebox'] = detonation_time
        params['file'] = base64.b64encode(bytes)
        params['filename'] = filename
        params['time_started'] = time.time()
        params['queue_time'] = queue_time,
        params['report'] = "Example report for a submitted binary sample"

        #Update the global dictionary of updated files keyed by md5
        #
        file_data_storage.global_dict[md5] = {
            'original_sample_size' : params['original_sample_size'],
            'timebox' : params['timebox'],
            'file' : params['file'],
            'filename' : params['filename'],
            'time_started' : params['time_started'],
            'queue_time' : params['queue_time'],
            'report' : params['report']
        }

        url = '%s/submit' % self.server
        print params
        print url
        r = requests.post(url, data = json.dumps(params))
        r.raise_for_status()

