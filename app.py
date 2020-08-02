
#this is my change 

import os,json
from flask import Flask, render_template, request, redirect, url_for, abort, session, jsonify
from SOAPpy import SOAPProxy
import servicenow_rest.api as sn
import requests

username, password, instance = 'satya.yadavalli', 'Satya%40123', 'wiprodemo'
#s = sn.Client(instance,username,password) #'wiprodev1', 'satya.yadavalli', 'Satya@123')
#s.table = 'incident'

tmpl_dir = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'web/templates')
stat_dir = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'web/static')
print tmpl_dir
app = Flask(__name__)
app.config['SECRET_KEY'] = 'F34TF$($e34D';

@app.route('/')
def home():
	return kural();
	
@app.route('/kural', methods=['GET'])
def kural():
	 print 'New Ticket called'
	 return render_template('kural.html')

@app.route('/signin', methods=['POST'])
def signin():
	if request.method == 'POST':
	 session['username'] = request.form['username']
	 session['password'] = request.form['password']
	 session['logged_in'] = True
	 return newticket();
	 
@app.route('/newticket', methods=['GET'])
def newticket():
	 print 'New Ticket called'
	 return render_template('newticket.html')

@app.route('/listtickets', methods=['GET'])
def listtickets():
	 print 'List Tickets called'
	 return render_template('listtickets.html')


@app.route('/signout', methods=['GET'])
def signout():
 	 session['logged_in'] = False
	 session.clear()
	 return render_template('index.html')


@app.route('/createtkt', methods=['POST'])
def createtkt():
	try:
		tkDesc =request.form['tktdesc']
		tkPrio =request.form['tktprty']
		tkCat =request.form['optCategory']
		
		shtDesc = tkDesc
		catg = tkCat
		subCat='General'
		print tkDesc
		print catg
		createTickets(catg,subCat,shtDesc,tkDesc,tkPrio)
		print 'Ticket Created'
	except sn.UnexpectedResponse as e:  # Unexpected server response (i.e. authentication error)
		print(e)
 	return listtickets();

@app.route('/gettkts', methods=['GET'])
def gettkts():
	username, password, instance = session['username'], session['password'], 'wiprodemo'
	s = sn.Client(instance,username,password) 
	s.table="incident" 
	try:
		res = s.get({"sys_created_by": username, "sysparm_limit":"5"}) 
		print str(res)
		return json.dumps(res)
	except sn.UnexpectedResponse as e:  # Unexpected server response (i.e. authentication error)
		print(e)


@app.route('/gettkts2', methods=['GET'])
def gettkts2():
 username, password, instance = session['username'], session['password'], 'wiprodemo'
 # Set the request parameters
 url = 'https://'+instance+'.service-now.com/api/now/table/incident?sysparm_limit=10&sysparm_query=active=true^ORDERBYDESCnumber'
 
 # Set proper headers
 headers = {"Accept":"application/json"}
 
 # Do the HTTP request
 response = requests.get(url, auth=(username, password), headers=headers )
 
 # Check for HTTP codes other than 200
 if response.status_code != 200: 
  print('Status:', response.status_code, 'Headers:', response.headers, 'Error Response:',response.json())
  
 return json.dumps(response.json())


@app.route('/getcats', methods=['POST'])
def getcats():
	mjson = request.json
	mjson = json.dumps(mjson)
	print mjson
	pheaders = {"content-type" : "application/json"}
	r = requests.post("http://ec2-52-7-252-23.compute-1.amazonaws.com:8022/classificationApp/verifyBot",headers=pheaders,data=mjson)
	print r.text
	return json.dumps(r.text)
	


def createTickets(categ, subcategory,shortdec,comments,priority):
	username, password, instance = session['username'], session['password'], 'wiprodemo'
	s = sn.Client(instance,username,password)
	s.table = 'incident'
	#strJSON = {"category":double_quote(categ),"sub_category":double_quote(subcategory),"short_description":double_quote(shortdec),"comments":double_quote(comments)}"
	strJSON={}
	strJSON['category']=categ
	strJSON['sub_category']=subcategory
	strJSON['short_description']=shortdec
	strJSON['comments']=comments
	strJSON['contact_type']='Self-service'
	strJSON['urgency']=priority
	strJSON['state']=1
	print strJSON

	try:
		
		res = s.insert(strJSON)
		print(res)
	except sn.UnexpectedResponse as e:  # Unexpected server response (i.e. authentication error)
		print(e)


def double_quote(word):
    double_q = '"' # double quote
    return double_q + word + double_q
     

@app.route('/message')
def message():
    if not 'username' in session:
        return abort(403)
    return render_template('message.html', username=session['username'], 
                                           message=session['message'])

if __name__ == '__main__':
    app.run('0.0.0.0', 8084)