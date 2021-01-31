from flask import Flask, render_template, request, redirect, url_for
from parser import get_parsed_data
from celery import Celery

app = Flask(__name__)
cel_app = Celery('main', broker='redis://127.0.0.1:6379', backend='db+sqlite:///db.sqlite3')


@cel_app.task
def parse(url: str):
    return get_parsed_data(url)


@app.route('/', methods=['GET', 'POST'])
def index():
    status = ""
    task_id = ""
    task_result = None
    if request.method == "GET":
        task_result = request.args.get('task_result')

    if request.method == "POST":
        url = request.form.get('parse_url')
        result = parse.delay(url)

        status = result.status
        task_id = result.task_id

    return render_template('index.html', context=status, id=task_id, task_result=task_result)


@app.route('/get_status', methods=['POST'])
def get_status():
    res = cel_app.AsyncResult(request.form.get('pid'))
    if res.successful():
        return redirect(url_for('index', task_result=res.result))
    else:
        return redirect('/', task_result='Still processing, please reload')


if __name__ == '__main__':
    app.run(debug=True)
