import os
import cjson
import simplejson
from flask import Flask, request, redirect, url_for, send_from_directory, make_response, render_template, json
#from werkzeug import secure_filename
import file_data_storage
import base64
import time
import hashlib
import detonation_api


UPLOAD_FOLDER = '/home/bwolfson/uploads'
ALLOWED_EXTENSIONS = set(['md5', 'py','pyc' 'txt', 'md5'])

app = Flask(__name__)
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER

# additional detonation_params field to feedinfo section of a feed
#
'''
{
    'host' :
    'resource_base' :
    'max_sample_size' :
    'supported_sample_types' :
    'default_detonation_time' :
}
'''

@app.route('/submit', methods = ['POST'])
def submit_md5():
    '''
    Submits a file for detonation and updates the global dictionary of submitted file data
    :return:
    '''
    global_dict = file_data_storage.global_dict
    if len(request.form) == 0: #True when submitting through script, false when submitting through UI HTML form

        response = json.loads(request.data)

        md5 = response['md5']
        file = base64.b64decode(response['file'])

        global_dict[md5] = {
            'original_sample_size' : response['original_sample_size'],
            'file' : file,
            'filename' : response['filename'],
            'timebox' : response['timebox'],
            'time_started' : response['time_started'],
            'report' : response['report']
        }
        update_status(md5)
        return "File Submitted, md5 hash for file is: %s" % md5

    else: #submitting through UI
        #extract variable values from HTML form
        file = request.files['file']
        filename = request.files['file'].filename
        detonation_time = request.form['timebox']
        print filename, detonation_time

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
        update_status(md5)
        return "File Submitted, md5 hash for file is: %s" % md5


@app.route('/submit/<md5>', methods = ['POST', 'GET'])
def resubmit_md5(md5):
    '''
    Resubmits a file for detonation, updates the global dictionary of sumbitted file data
    :return:
    '''
    global_dict = file_data_storage.global_dict
    print global_dict
    does_exist = False
    for key in global_dict.keys():
        if key == md5:
            does_exist = True
            break
        else:
            continue

    if does_exist:
        if request.method == 'POST':
            old_data = global_dict[md5]
            global_dict[md5] = {
                'original_sample_size' : old_data['original_sample_size'],
                'timebox' : old_data['timebox'],
                'file' : old_data['file'],
                'filename' : old_data['filename'],
                'time_started' : time.time(),
                'report' : old_data['report']
            }
            return "file resubmitted."
        else: return render_template('resubmit.html', md5 = md5, global_dict = global_dict)
    else: return "File does not exist"


@app.route('/status/<md5>', methods = ['GET'])
def status_md5(md5):
    '''
    Output the status for this md5
    :param md5: the md5 of the sample
    :return: the status
    '''
    #the global dictionary of submitted binaries
    global_dict = file_data_storage.global_dict

    #check if file exists in global dict
    does_exist = False
    for key in global_dict.keys():
        if key == md5:
            does_exist = True
        else:
            continue

    # if it does, output the current status of detonation
    if does_exist:
        file_data = global_dict[md5]
        print file_data
        if file_data['time_started'] + float(file_data['timebox']) < time.time():
            file_data['detonation_results'] = {
                                'status' : 'Complete',
                                'eta_to_analysis' : 0,
                                'eta_to_complete' : 0,
                                'analysis_complete' : "100% complete",
                                'results' : {
                                    'score' : -100,
                                    'analysis_successful': True,
                                    'error_description': "Bogus Error Description",
                                    'analysis_summary': "The TIC did pretty well"
                                }
            }

            return render_template('specific.html', file_data = file_data,
                                   results = file_data['detonation_results']['results'])
        else:
            finish_time = file_data['time_started'] + float(file_data['timebox'])
            eta_to_complete = finish_time - time.time()
            percent_complete = ((float(file_data['timebox']) - eta_to_complete)/float(file_data['timebox']))*100
            file_data['detonation_results'] = {
                                'status' : 'Analyzing',
                                'eta_to_analysis' : 0,
                                'eta_to_complete' : finish_time - time.time(),
                                'analysis_complete' : percent_complete
            }

            return render_template('specific.html', file_data = file_data, results = None)

    else:
        return "File not found"

@app.route('/status/global', methods = ['GET'])
def status_global():
    '''
    display the global status of the feed provider, i.e. all the currently submitted samples
    :return:
    '''
    global_dict = file_data_storage.global_dict
    completed_samples = []
    analyzing_samples = []
    queued_samples = []
    print global_dict
    for md5 in global_dict.keys():
        update_status(md5)
        if global_dict[md5]['detonation_results']['status'].lower() == 'complete':
            completed_samples.append(global_dict[md5])
        elif global_dict[md5]['detonation_results']['status'].lower() == 'analyzing':
            analyzing_samples.append(global_dict[md5])
        else: queued_samples.append(global_dict[md5])

    return render_template('global_status.html', global_dict = global_dict, completed_samples = completed_samples,
                           analyzing_samples = analyzing_samples, queued_samples = queued_samples,
                           count_completed = len(completed_samples), count_analyzing = len(analyzing_samples),
                                                 count_queued = len(queued_samples))

@app.route('/report/<md5>', methods = ['GET'])
def report_md5(md5):
    '''
    Output the detailed report for a sample
    :param md5: the md5 hash of the sample
    :return:
    '''

    #the global dictionary of submitted binaries
    global_dict = file_data_storage.global_dict

    #check if file exists in global dict
    does_exist = False
    for key in global_dict.keys():
        if key == md5:
            does_exist = True
        else:
            continue

    # if it does, output the report
    if does_exist:
        return global_dict[md5]['report']
    else:
        return "file not found"

@app.route('/submit', methods=['POST', 'GET'])
def submitted_files():
    return render_template('format.html', files = file_data_storage.global_dict)

# wrapper around the flask make_response method that includes encoding to json
def make_response_json(data, *args, **kwargs):
    if args or kwargs:
        response = make_response(simplejson.dumps(data, *args, **kwargs))
    else:
        response = make_response(cjson.encode(data))
    response.headers['Content-Type'] = "application/json; charset=utf-8"
    return response

def update_status(md5):
    file_data = file_data_storage.global_dict[md5]
    if file_data['time_started'] + float(file_data['timebox']) < time.time():
            file_data['detonation_results'] = {
                                'status' : 'Complete',
                                'eta_to_analysis' : 0,
                                'eta_to_complete' : 0,
                                'analysis_complete' : "100% complete",
                                'results' : {
                                    'score' : -100,
                                    'analysis_successful': True,
                                    'error_description': "Bogus Error Description",
                                    'analysis_summary': "The TIC did pretty well"
                                }
            }

            return render_template('specific.html', file_data = file_data,
                                   results = file_data['detonation_results']['results'])
    else:
            finish_time = file_data['time_started'] + float(file_data['timebox'])
            eta_to_complete = finish_time - time.time()
            percent_complete = ((float(file_data['timebox']) - eta_to_complete)/float(file_data['timebox']))*100
            file_data['detonation_results'] = {
                                'status' : 'Analyzing',
                                'eta_to_analysis' : 0,
                                'eta_to_complete' : finish_time - time.time(),
                                'analysis_complete' : percent_complete
            }


if __name__ == "__main__":
    app.run(port=9999, debug=True)
