from datetime import datetime
from os import environ as env
from sys import argv

from flask import Flask, request, render_template, jsonify
from flask.ext.sqlalchemy import SQLAlchemy
from pytz import timezone
from twilio.rest import TwilioRestClient


app = Flask(__name__)
app.debug = True
app.config['SQLALCHEMY_DATABASE_URI'] = env['DB_URL']
db = SQLAlchemy(app)
client = TwilioRestClient(env['ACCOUNT_SID'], env['AUTH_TOKEN'])


class Call(db.Model):
    id = db.Column(db.String(255), primary_key=True)
    recording_url = db.Column(db.String(4096))
    transcript = db.Column(db.Text())
    date = db.Column(db.DateTime(timezone=True))

    def __init__(self, id, recording_url, transcript, date=None):
        self.id = id
        self.recording_url = recording_url
        self.transcript = transcript
        if date is None:
            date = datetime.utcnow()
        self.date = date

    def __repr__(self):
        return '<Call %r>' % self.id

    @property
    def status(self):
        if 'open' in self.transcript and 'close' in self.transcript:
            if self.transcript.index('open') < self.transcript.index('open'):
                return 'open'
            else:
                return 'closed'
        elif 'open' in self.transcript:
            return 'open'
        elif 'close' in self.transcript:
            return 'closed'
        else:
            return 'unknown'


@app.route('/')
def index():
    return render_template(
        'index.html',
        call=Call.query.order_by(Call.date.desc()).first(),
        timezone=timezone('US/Eastern'))


@app.route('/json')
def json():
    return jsonify({'data': [{
        k: getattr(call, k) for k in
        ['date', 'status', 'id', 'recording_url', 'transcript']
    } for call in Call.query.order_by('date').all()]})


@app.route('/twilio/callback', methods=['POST'])
def callback():
    return """
<Response>
    <Record timeout="60" transcribeCallback="{}"/>
</Response>
""".format(env['SERVER_URL'] + '/twilio/transcription-callback')


@app.route('/twilio/transcription-callback', methods=['POST'])
def transcription_callback():
    db.session.add(Call(id=request.form['CallSid'],
                        recording_url=request.form['RecordingUrl'],
                        transcript=request.form['TranscriptionText']))
    db.session.commit()
    return ''

if len(argv) >= 2:
    if argv[1] == 'server':
        print('run with gunicorn: `gunicorn fountainheadstatus:app`')
    elif argv[1] == 'createdb':
        db.create_all()
    elif argv[1] == 'update':
        call = client.calls.create(
            url=env['SERVER_URL'] + '/twilio/callback',
            to='+17032509124',
            from_=env['FROM'],
            send_digits='w1',
            record=True,
        )
        print(call.sid)
