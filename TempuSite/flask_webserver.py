from flask import Flask, render_template, request
from file_handling import JSONFile
import os
import json
import psutil

from random import shuffle

def parse_bytes(bytes):
    kb = 1024
    mb = 1048576
    gb = 1073741824

    if bytes < kb: return {'use': round(bytes,1), 'unit':'B', 'factors': {'B': 1, 'KB': kb, 'MB': mb, 'GB': gb}}
    if kb <= bytes < mb: return {'use': round(bytes/kb,1), 'unit':'KB', 'factors': {'B': 1, 'KB': kb, 'MB': mb, 'GB': gb}}
    if mb <= bytes < gb: return {'use': round(bytes/mb,1), 'unit':'MB', 'factors': {'B': 1, 'KB': kb, 'MB': mb, 'GB': gb}}
    return {'use': round(bytes/gb,1), 'unit':'GB', 'factors': {'B': 1, 'KB': kb, 'MB': mb, 'GB': gb}}

app = Flask(__name__)

log_location = os.getenv('TEMPUBOT_LOG_PATH', '') + '/'

if log_location == '':
    raise FileNotFoundError('TEMPUBOT_LOG_PATH not defined.')

log_file = JSONFile(
    filename='log.json', 
    location=log_location
)

schedule_file = JSONFile(
    filename='schedule.json', 
    location=log_location
)

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/signoffs', methods=['GET', 'PUT'])
def signoffs():
    return render_template('signoffs.html')

@app.route('/signofffile', methods=['GET', 'PUT'])
def signofffile():
    signoffs = schedule_file.get('signoffs')

    if (request.method == 'PUT'):
        i = request.json['index']
        signoff = request.json['signoff']
        if (signoffs[i] == signoff):
            del signoffs[i]
            schedule_file.set('signoffs', signoffs)

        return json.dumps({'success':True}), 200, {'ContentType':'application/json'} 

    return json.dumps(
        signoffs,
        ensure_ascii=False,
        separators=(',', ':')
    )

@app.route('/status')
def status():
    content = log_file.read()

    alive = True
    pid = int(log_file.get('pid'))
    if not psutil.pid_exists(pid): alive = False
    else: 
        process_name = psutil.Process(pid).name()
        if not process_name == log_file.get('process_name'): alive = False
    content['alive'] = alive

    memory_used = 0
    if (alive): memory_used = psutil.Process(pid).memory_info().rss
    memory_dict = parse_bytes(memory_used)
    content['memory'] = memory_dict

    children = '-'
    if (alive): children = str(len(psutil.Process(pid).children(recursive=True)))
    content['children'] = children

    for entry in content['log']:
        if entry['type'] in ['command', 'message']:
            entry['shorthand'] = '{} ({}): {}'.format(entry['author'], entry['channel'], entry['message'])
        else:
            entry['shorthand'] = entry['message']
        
    content['log'].sort(key=lambda x: x['date'] + x['time'], reverse=True)

    return json.dumps(
        content,
        ensure_ascii=False,
        separators=(',', ':')
    )

if __name__ == '__main__':
    app.run(debug=False, port=5000)