from flask import Flask, render_template, url_for, request, redirect
from flask.wrappers import Request
from parser import get_parsed_data
from celery import Celery
from celery.result import AsyncResult

app = Flask(__name__)
cel_app = Celery('parse', broker='redis://127.0.0.1:6379', backend='db+sqlite:///db.sqlite3')


@cel_app.task
def parse(url: str):
    return get_parsed_data(url)


@app.route('/', methods=['GET', 'POST'])
def index():
    status = ""
    task_id = ""
    if request.method == "POST":
        url = request.form.get('parse_url')
        result = parse.delay(url)
        status = result.status
        task_id = result.task_id
    return render_template('index.html', context=status, id=task_id)


@app.route('/get_status', methods=['GET'])
def get_status(pid: str):
    res = AsyncResult(pid)
    if res.successful():
        return res.result


if __name__ == '__main__':
    app.run(debug=True)
