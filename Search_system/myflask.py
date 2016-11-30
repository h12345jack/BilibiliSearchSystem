#coding=utf8
from flask import render_template
from flask import Flask

app = Flask(__name__)

@app.route('/')
@app.route('/index')
def hello(name=None):
    return render_template('index.html', name=name)


if __name__ == '__main__':
    app.run()