import os
import psycopg
from flask import Flask, request, redirect, render_template_string

app = Flask(__name__)

def connect():
    return psycopg.connect(host=os.getenv('DB_HOST', 'db'), dbname='tasks', user='tasks', password=os.environ['DB_PASSWORD'])

@app.get('/health')
def health():
    try:
        with connect() as db:
            db.execute('SELECT 1')
        return {'status': 'ok', 'database': 'connected'}
    except psycopg.Error:
        return {'status': 'unavailable'}, 503

@app.route('/', methods=['GET', 'POST'])
def index():
    with connect() as db:
        db.execute('CREATE TABLE IF NOT EXISTS tasks (id SERIAL PRIMARY KEY, title VARCHAR(200) NOT NULL, done BOOLEAN NOT NULL DEFAULT FALSE)')
        if request.method == 'POST':
            title = request.form.get('title', '').strip()
            if not title or len(title) > 200:
                return 'Title must contain 1-200 characters', 400
            db.execute('INSERT INTO tasks(title) VALUES (%s)', (title,))
        rows = db.execute('SELECT id,title,done FROM tasks ORDER BY id DESC').fetchall()
    if request.method == 'POST':
        return redirect('/')
    return render_template_string(PAGE, rows=rows)

@app.post('/complete/<int:task_id>')
def complete(task_id):
    with connect() as db:
        db.execute('UPDATE tasks SET done=TRUE WHERE id=%s', (task_id,))
    return redirect('/')

PAGE = '''<!doctype html><html lang="en"><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1"><title>Cloud Tasks</title><style>body{font:18px system-ui;background:#edf2f7;color:#162238;margin:0}main{max-width:760px;margin:60px auto;padding:32px;background:white;border-radius:20px}p,small{color:#536278}form{display:flex;gap:12px}input{flex:1;min-width:0;padding:14px;border:1px solid #aab8cb;border-radius:8px}button{padding:12px;border:0;border-radius:8px;background:#2459c4;color:white;cursor:pointer}li{display:flex;justify-content:space-between;align-items:center;padding:18px 0;border-bottom:1px solid #ddd;gap:16px}ul{padding:0}</style><main><small>DEVOPS / CLOUD COMPUTING</small><h1>Cloud Tasks</h1><p>A persistent task board powered by PostgreSQL.</p><form method="post"><input name="title" maxlength="200" required placeholder="What needs to get done?" aria-label="Task title"><button>Add task</button></form><ul>{% for id,title,done in rows %}<li><span>{{title}}</span>{% if done %}<small>Completed</small>{% else %}<form method="post" action="/complete/{{id}}"><button>Complete</button></form>{% endif %}</li>{% else %}<li>Your task board is ready.</li>{% endfor %}</ul></main></html>'''
