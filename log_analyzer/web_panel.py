from flask import Flask, render_template, jsonify, request, redirect, url_for
from log_analyzer.log_db import LogDB
from log_analyzer.llm_analysis import analyze_log


app = Flask(__name__)


@app.route('/')
def index():
    return redirect(url_for('logs_page'))


@app.route('/logs')
def logs_page():
    page = int(request.args.get('page', 1))
    severity = request.args.get('severity')
    program = request.args.get('program')
    db = LogDB()
    logs = list(db.fetch_logs(limit=100, page=page, severity=severity, program=program))
    db.close()
    severity_colors = {'INFO': 'text-info', 'WARNING': 'text-warning', 'ERROR': 'text-danger'}
    return render_template(
        'logs.html',
        logs=logs,
        severity_colors=severity_colors,
        page=page,
        severity=severity,
        program=program,
        menu='logs'
    )


@app.route('/analyzed')
def analyzed_page():
    return render_template(
        'analyzed.html',
        menu='analyzed'
    )


@app.route('/api/analyzed')
def api_analyzed():
    limit = int(request.args.get('limit', 100))
    page = int(request.args.get('page', 1))
    db = LogDB()
    logs = list(db.fetch_analyzed_logs(limit=limit, page=page))
    db.close()
    return jsonify({'logs': logs})


@app.route('/api/logs')
def api_logs():
    limit = int(request.args.get('limit', 100))
    page = int(request.args.get('page', 1))
    severity = request.args.get('severity')
    host = request.args.get('host')
    program = request.args.get('program')
    search = request.args.get('search')
    db = LogDB()
    logs = list(
        db.fetch_logs(
            limit=limit,
            page=page,
            severity=severity,
            host=host,
            program=program,
            search=search,
        )
    )
    db.close()
    return jsonify({'logs': logs})


@app.route('/api/analyze/<int:log_id>')
def api_analyze(log_id: int):
    result = analyze_log(log_id)
    return jsonify({'result': result})

if __name__ == '__main__':
    app.run(debug=True)
