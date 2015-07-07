__author__ = 'bwolfson'
'''
Flask file for initial effort to stub out extending CBfeeds to detonation
'''
import cjson
import simplejson
from flask import Flask, request, make_response, render_template, json
import base64
import time
import hashlib
import file_data_storage

app = Flask(__name__)

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
    :return: the html template for the /submit page with the submitted files info
    '''

    #the global dictionary of submitted files
    #
    global_dict = file_data_storage.global_dict

    if len(request.form) == 0:
    #Submitting through a cli script (detonation api)

        #get the server response, and decode the file content's bytes
        #
        response = json.loads(request.data)
        md5 = response['md5']
        file = base64.b64decode(response['file'])

        #Update the global dictionary of submitted files keyed my md5
        #
        global_dict[md5] = {
            'original_sample_size' : response['original_sample_size'],
            'timebox' : response['timebox'],
            'file' : file,
            'filename' : response['filename'],
            'time_submitted' : response['time_started'],
            'queue_time' : response['queue_time'],
            'report' : response['report']
        }

    else:
    #submitting through UI

        #extract variable values from HTML form
        #
        filename = request.files['file'].filename
        detonation_time = request.form['timebox']
        queue_time = request.form['queue_time']

        #read the file from cwd into bytes so its contents can be held in the dictionary
        #
        f = open(filename, 'rb')
        bytes = f.read()
        md5 = hashlib.md5(bytes).hexdigest()

        #Update the global dictionary of submitted files keyed by md5
        #
        global_dict[md5] = {
            'original_sample_size' : len(bytes),
            'timebox' : detonation_time,
            'file' : base64.b64encode(bytes),
            'filename' : filename,
            'time_submitted' : time.time(),
            'queue_time' : queue_time,
            'report' : "Example report for a submitted binary sample"
        }

    #Set all the detonation_results fields to initial values
    #
    update_status(md5)

    #return the page with the newly submitted file's info included
    #
    return render_template('format.html', files = file_data_storage.global_dict)

@app.route('/submit/<md5>', methods = ['POST', 'GET'])
def resubmit_md5(md5):
    '''
    Resubmits a file for detonation, updates the global dictionary of submitted file data
    :return: if POST, a string telling that file was resubmitted, if GET, html template to resubmit a file
    '''
    #the global dictionary of submitted files
    #
    global_dict = file_data_storage.global_dict

    #check if file exists
    #
    does_exist = False
    for key in global_dict.keys():
        if key == md5:
            does_exist = True
            break
        else:
            continue

    if does_exist:
        if request.method == 'POST':
            #update the global dictionary of submitted files
            #
            old_data = global_dict[md5]
            global_dict[md5] = {
                'original_sample_size' : old_data['original_sample_size'],
                'timebox' : old_data['timebox'],
                'file' : old_data['file'],
                'filename' : old_data['filename'],
                'time_submitted' : time.time(),
                'queue_time' : old_data['queue_time'],
                'report' : old_data['report']
            }
            return "file resubmitted."

        else:
            #request method is GET, show the html template to resubmit files
            #
            return render_template('resubmit.html', md5 = md5, global_dict = global_dict)
    else:
        return "File does not exist"

@app.route('/status/<md5>', methods = ['GET'])
def status_md5(md5):
    '''
    Output the status for this md5
    :param md5: the md5 of the sample
    :return: html template displaying the status of this file
    '''

    #the global dictionary of submitted binaries
    #
    global_dict = file_data_storage.global_dict

    #check if file exists in global dict
    #
    does_exist = False
    for key in global_dict.keys():
        if key == md5:
            does_exist = True
        else:
            continue

    # if it does, update the global dictionary of submitted files based on current time
    # and output the status info
    #
    if does_exist:
        file_data = global_dict[md5]
        finish_time = file_data['time_submitted'] + float(file_data['queue_time']) + \
                float(file_data['timebox'])
        analysis_start_time = file_data['time_submitted'] + float(file_data['queue_time'])
        now = time.time()
        
        if now > finish_time:
        #status is complete (binary analysis is finished)

            file_data['detonation_results'] = {
                                'status' : 'Complete',
                                'eta_to_analysis' : 0,
                                'eta_to_complete' : 0,
                                'analysis_complete' : 100,
                                'results' : {
                                    'score' : -100,
                                    'analysis_successful': True,
                                    'error_description': "Bogus Error Description",
                                    'analysis_summary': "The TIC did pretty well"
                                }
            }

            return render_template('specific.html', file_data = file_data,
                                   results = file_data['detonation_results']['results'])

        elif analysis_start_time <= now <= finish_time:
        #status is analyzing (binary analysis is currently happening)

            eta_to_complete = finish_time - now
            percent_complete = ((float(file_data['timebox']) - eta_to_complete)/float(file_data['timebox']))*100
            file_data['detonation_results'] = {
                                'status' : 'Analyzing',
                                'eta_to_analysis' : 0,
                                'eta_to_complete' : eta_to_complete,
                                'analysis_complete' : percent_complete
            }

            return render_template('specific.html', file_data = file_data, results = None)

        else:
        #status is queued (binary analysis has not started yet)
            remaining_queue_time = analysis_start_time - now
            file_data['detonation_results'] = {
                                'status' : 'Queued',
                                'eta_to_analysis' : remaining_queue_time,
                                'eta_to_complete' : remaining_queue_time + float(file_data['timebox']),
                                'analysis_complete' : 0
            }

            return render_template('specific.html', file_data = file_data, results = None)

    else:
    #file not found in the global dictionary
        return "File not found"

@app.route('/status/global', methods = ['GET'])
def status_global():
    '''
    display the global status of the feed provider, i.e. all the currently submitted samples
    :return: html template displaying the global status
    '''
    #global dictionary of submitted files
    #
    global_dict = file_data_storage.global_dict

    #lists to be passed to html template
    #
    completed_samples = []
    analyzing_samples = []
    queued_samples = []

    #populate the empty lists based on status
    #
    for md5 in global_dict.keys():
        update_status(md5)
        if global_dict[md5]['detonation_results']['status'].lower() == 'complete':
            completed_samples.append(global_dict[md5])
        elif global_dict[md5]['detonation_results']['status'].lower() == 'analyzing':
            analyzing_samples.append(global_dict[md5])
        else: queued_samples.append(global_dict[md5])

    #send data to html template and display global status
    #
    return render_template('global_status.html', global_dict = global_dict, completed_samples = completed_samples,
                           analyzing_samples = analyzing_samples, queued_samples = queued_samples,
                           count_completed = len(completed_samples), count_analyzing = len(analyzing_samples),
                                                 count_queued = len(queued_samples))

@app.route('/report/<md5>', methods = ['GET'])
def report_md5(md5):
    '''
    Output the detailed report for a sample
    :param md5: the md5 hash of the sample
    :return: the detailed binary analysis report for the sample
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

@app.route('/submit', methods=['GET'])
def submitted_files():
    '''
    display all the currently submitted files for detonation
    :return: html template displaying the files
    '''
    return render_template('format.html', files = file_data_storage.global_dict)

def update_status(md5):
    '''
    update the global dictionary of submitted files' detonation results
    :param md5:
    :return: void
    '''

    #the global dictionary of submitted files
    #
    global_dict = file_data_storage.global_dict

    file_data = global_dict[md5] #this file's data
    finish_time = file_data['time_submitted'] + float(file_data['queue_time']) + \
                float(file_data['timebox'])
    analysis_start_time = file_data['time_submitted'] + float(file_data['queue_time'])
    now = time.time()

    if now > finish_time:
    #status is complete (binary analysis is finished)

        file_data['detonation_results'] = {
                            'status' : 'Complete',
                            'eta_to_analysis' : 0,
                            'eta_to_complete' : 0,
                            'analysis_complete' : 100,
                            'results' : {
                                    'score' : -100,
                                    'analysis_successful': True,
                                    'error_description': "Bogus Error Description",
                                    'analysis_summary': "The TIC did pretty well"
                            }
        }

    elif analysis_start_time <= now <= finish_time:
    #status is analyzing (binary analysis is currently happening)

        eta_to_complete = finish_time - now
        percent_complete = ((float(file_data['timebox']) - eta_to_complete)/float(file_data['timebox']))*100
        file_data['detonation_results'] = {
                                'status' : 'Analyzing',
                                'eta_to_analysis' : 0,
                                'eta_to_complete' : eta_to_complete,
                                'analysis_complete' : percent_complete
        }

    else:
    #status is queued (binary analysis has not started yet)

        remaining_queue_time = analysis_start_time - now
        file_data['detonation_results'] = {
                                'status' : 'Queued',
                                'eta_to_analysis' : remaining_queue_time,
                                'eta_to_complete' : remaining_queue_time + float(file_data['timebox']),
                                'analysis_complete' : 0
        }

if __name__ == "__main__":
    app.run(port=9999, debug=True)
