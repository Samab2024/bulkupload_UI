from flask import Flask, render_template, request, redirect, flash, jsonify, session, Response # type: ignore
from werkzeug.utils import secure_filename # type: ignore
import os, threading, uuid, traceback
from veracode_api_signing.plugin_requests import RequestsAuthPluginVeracodeHMAC as VeracodeHMAC
from new_api import veracode_api_call as api_call
from csv_in import csvIn

UPLOAD_FOLDER = './uploads'
ALLOWED_EXTENSIONS = {'csv'}
JOB_STORE = {}

app = Flask(__name__)
app.secret_key = 'supersecretkey'
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER
os.makedirs(UPLOAD_FOLDER, exist_ok=True)

def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

# Logger object per session
class SessionLogger:
    def __init__(self):
        self.logs = []

    def info(self, msg):
        self.logs.append({'msg': msg, 'type': 'info'})

    def error(self, msg):
        self.logs.append({'msg': msg, 'type': 'error'})

# Background CSV processor
def process_csv(region, api_id, api_secret, filepath, session_id):
    logger = JOB_STORE.get(session_id)
    if not logger:
        return
    try:
        creds = VeracodeHMAC(api_id, api_secret)
        myCSV = csvIn.fromFile(filepath)

        # Credentials test
        try:
            params = {'rownum': 'CredentialsTest'}
            api_call(region=region, endpoint='getmaintenancescheduleinfo', creds=creds, logger=logger, params=params)
        except Exception as e:
            logger.error(f"Bad credentials: {e}")
            return

        # Process CSV rows
        lineinfo = myCSV.next()
        while lineinfo:
            if 'apiaction' in lineinfo:
                try:
                    endpoint = lineinfo.pop('apiaction')
                    api_call(region=region, endpoint=endpoint, creds=creds, logger=logger, params=lineinfo)
                except Exception as e:
                    logger.error(f"Error on row {lineinfo.get('rownum')}: {e}")
                    traceback.print_exc()
            lineinfo = myCSV.next()

        logger.info("CSV completed successfully!")

    except Exception as e:
        logger.error(f"Unexpected error: {e}")
        traceback.print_exc()

@app.route('/')
def root():
    return redirect('/dashboard')

# Dashboard UI
@app.route('/dashboard', methods=['GET'])
def dashboard():
    return render_template('dashboard.html')


# Handle upload (API-style endpoint)
@app.route('/upload', methods=['POST'])
def upload():
    if request.method == 'POST':
        region = request.form.get('region', '').strip()
        api_id = request.form.get('api_id', '').strip()
        api_secret = request.form.get('api_secret', '').strip()
        file = request.files.get('csv_file')

        if not all([region, api_id, api_secret, file]):
            flash('All fields are required!', 'error')
            return redirect(request.url)
        if not allowed_file(file.filename):
            flash('Invalid file type. Only CSV allowed.', 'error')
            return redirect(request.url)

        filename = secure_filename(file.filename)
        filepath = os.path.join(app.config['UPLOAD_FOLDER'], filename)
        file.save(filepath)

        # Session and logger
        session_id = str(uuid.uuid4())
        JOB_STORE[session_id] = SessionLogger()

        # Start processing in background thread
        threading.Thread(target=process_csv, args=(region, api_id, api_secret, filepath, session_id), daemon=True).start()

        return jsonify({"session_id": session_id})

    return render_template('dashboard.html')

@app.route('/get_logs/<session_id>')
def get_logs(session_id):
    logger = JOB_STORE.get(session_id)
    if logger:
        return jsonify(logger.logs)
    return jsonify([])

@app.route('/download_logs/<session_id>')
def download_logs(session_id):
    logger = JOB_STORE.get(session_id)
    if logger:
        log_text = '\n'.join(
            f"{l['type'].upper()}: {l['msg']}" for l in logger.logs
        )
        return Response(
            log_text,
            mimetype='text/plain',
            headers={"Content-Disposition": "attachment;filename=upload_log.txt"}
        )
    return "No logs found", 404

if __name__ == '__main__':
    # Run internally on 0.0.0.0 so team can access
    app.run(host='0.0.0.0', port=2000, debug=True)
