#coding=utf8

import json

from flask import render_template
from flask import Flask,request,abort,redirect
from whoosh_index import query,mysql_result_by_cid

app = Flask(__name__)

@app.route('/')
@app.route('/index')
@app.route('/index.html')
def hello(name=None):
    return render_template('index.html', name=name)

@app.route("/search.html")
def search():
    danmu = request.args.get('danmu',"黄婷婷")
    page = request.args.get("page","1")
    query_rs = query(danmu)
    result = query_rs[(int(page)-1)*10:int(page)*10]
    return render_template('search.html',number=len(query_rs),page=page,results=result,query_word=danmu)

@app.route("/result.html")
def result_bilibili():
    cid = request.args.get('cid',"8150643")
    result = mysql_result_by_cid(cid)
    print cid,result
    if not len(result):return abort(404)
    return render_template('result.html',cid=cid,result=result)

@app.route("/tag/<tag_name>")
@app.route("/tag/<tag_name>/")
def tag(tag_name):
    print tag_name
    return redirect("http://search.bilibili.com/all?keyword="+tag_name);

@app.errorhandler(404)
def page_not_found(e):
    return render_template('404.html'), 404


if __name__ == '__main__':
    app.run(debug=True)
