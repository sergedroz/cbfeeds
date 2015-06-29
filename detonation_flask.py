import os
import cjson
import simplejson
from flask import Flask, request, redirect, url_for, send_from_directory, make_response, render_template, json
#from werkzeug import secure_filename
import file_data_storage


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

@app.route('/submit/<filename>/data', methods = ['PUT', 'GET'])
def file_data(filename):
    '''
    stores a file's data or retrieves the data and displays it
    :param filename: name of the file
    :return:
    '''
    files = file_data_storage.files
    if request.method == 'PUT':
        data = request.data
        files.append(json.loads(data))
        response = make_response_json(data)
        return response
    else:
        if files is not None:
            file_exists = False
            for file in files:
                print file['filename'].lower()
                print filename.lower()
                if file['filename'].lower() == filename.lower():
                    file_exists = True
                    file = file
                    break
                else:
                    continue
            if file_exists:
                return render_template('specific.html', file = file)
            else:
                return "file does not exist"
        else:
            return "No Files currently submitted"

@app.route('/status/<filename>', methods=['GET'])
def file_status(filename):
    '''
    displays a stored file's status, if the status is complete, results are displayed
    :param filename: name of the file whose status to display
    :return:
    '''
    files = file_data_storage.files
    print files
    if files is not None:
        file_exists = False
        for file in files:
            if file['filename'].lower() == filename.lower():
                file_exists = True
                file = file
                status = file['detonation_results']['status']
            else:
                continue
        if file_exists:
            return render_template('status.html', file = file, status = status)
        else:
            return "file does not exist"
    else:
        return "No files currently submitted"


@app.route('/submit', methods=['POST', 'GET'])
def upload_file():
    if request.method == 'POST':
        file = request.files['file']
        if file and allowed_file(file.filename):
            #filename = secure_filename(file.filename)
            filename = file.filename
            file.save(os.path.join(app.config['UPLOAD_FOLDER'], filename))

            return redirect(url_for('uploaded_file', filename=filename))
    else:
        files = file_data_storage.files
        return render_template('format.html', files = files)



@app.route("/report/<md5>", methods=['GET'])
def report_md5():
    return


@app.route("/status/global", methods=['GET'])
def status_global():
    return


@app.route('/submit/<filename>')
def uploaded_file(filename):
    return send_from_directory(app.config['UPLOAD_FOLDER'],
                               filename)


def allowed_file(filename):
    return '.' in filename and \
           filename.rsplit('.', 1)[1] in ALLOWED_EXTENSIONS


# wrapper around the flask make_response method that includes encoding to json
def make_response_json(data, *args, **kwargs):
    if args or kwargs:
        response = make_response(simplejson.dumps(data, *args, **kwargs))
    else:
        response = make_response(cjson.encode(data))
    response.headers['Content-Type'] = "application/json; charset=utf-8"
    return response


if __name__ == "__main__":
    app.run(port=9999, debug=True)
