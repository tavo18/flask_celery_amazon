# project/server/main/views.py


from datetime import datetime
from flask import render_template, Blueprint, jsonify, request, redirect, url_for
from project.server.tasks import create_task
from project.server.tasks import scrape_amazon
from celery.result import AsyncResult
import sqlite3
from celery import current_app 



main_blueprint = Blueprint("main", __name__,)


@main_blueprint.route("/", methods=["GET"])
def home():
    # Get past tasks
    conn = sqlite3.connect('celery.db')
    c = conn.cursor()

    c.execute('SELECT * FROM celery_taskmeta')

    finished = c.fetchall()
    all_tasks = [{'task_id': item[1], 'status': item[2], 'date_done': item[4]} for item in finished]

    c.close()
    conn.close()

    # Get current tasks    
    i = current_app.control.inspect()
    tasks = i.active()
    for key in tasks.keys():
        for task in tasks[key]:
            task_result = AsyncResult(task['id'])
            date = datetime.fromtimestamp(task['time_start']).isoformat(' ')
            all_tasks.append({'task_id': task['id'], 'status': task_result.status, 'date_done': date})
    
    all_tasks.sort(key=lambda item:item['date_done'], reverse=True)
    
    return render_template("main/home.html", tasks = all_tasks)


@main_blueprint.route("/tasks", methods=["POST"])
def run_task():
    content = request.json
    task_type = content["type"]
    task = create_task.delay(int(task_type))
    return jsonify({"task_id": task.id}), 202


@main_blueprint.route("/scrape_amazon", methods=["POST"])
def run_scrape_amazon():
    text = request.form['amazon_links']
    task = scrape_amazon.delay(text)
    return redirect(url_for('main.home'), code = 302)
    # return jsonify({"task_id": task.id}), 202


@main_blueprint.route("/tasks/<task_id>", methods=["GET"])
def get_status(task_id):
    task_result = AsyncResult(task_id)
    result = {
        "task_id": task_id,
        "task_status": task_result.status,
        "task_result": task_result.result
    }
    return jsonify(result), 200
