from flask import Flask, render_template, request, Response, session, flash, redirect
from gpiozero import LED
from signal import pause
import datetime, os, signal
import gevent
import gevent.monkey
import subprocess as sp
import mysql.connector
import check_card 
from gevent.pywsgi import WSGIServer

images = os.path.join('static', 'images')

app = Flask(__name__, template_folder='templates')
app.config['image_folder'] = images

ledRed = LED(21)
ledGreen = LED(20)

@app.route("/", methods=['POST', 'GET'])
def login():
	session['user'] = None
	u, pw,h,db = 'root', 'dmitiot', 'localhost', 'FaceReko'
	con = mysql.connector.connect(user=u,password=pw,host=h,database=db)
	print("Database successfully connected")
	cur = con.cursor()
	query = "SELECT Username, Password FROM Login"
	cur.execute(query)
	if request.method == 'POST':
		for (Username, Password) in cur:
			if request.form['user'] == Username and request.form['pass']==Password:
				session['user'] = request.form['user']
				return redirect('/home')

	return render_template('login.html')

@app.route("/logout")
def logout():
	session.clear()
	return redirect('/')


@app.route("/createacc", methods=['POST','GET'])
def createAcc():
	u, pw,h,db = 'root', 'dmitiot', 'localhost', 'FaceReko'
	con = mysql.connector.connect(user=u,password=pw,host=h,database=db)
	print("Database successfully connected")
	cur = con.cursor()
	flash('Place your RFID card on reader before proceeding!')
	
	
	if request.method == 'POST':
		sql = "INSERT into Login (Username, Password, cardUID) VALUES (%s, %s, %s)"
		cur.execute(sql, (request.form['user'], request.form['pass'], check_card.read()))
		con.commit()
		cur.close()
		con.close()
		print("Success")
		return redirect('/')

	return render_template('createAcc.html')	

@app.route("/home")
def check():
	if session.get('user') is None:
		return redirect('/')
	else:
		return chart()

def chart():
	u, pw,h,db = 'root', 'dmitiot', 'localhost', 'FaceReko'
	data = []
	data2 = []
	con = mysql.connector.connect(user=u,password=pw,host=h,database=db)
	con2 = mysql.connector.connect(user=u,password=pw,host=h,database=db)
	print("Database successfully connected")
	cur = con.cursor()
	cur2 = con2.cursor()
	query = "SELECT Time, Name, Similarity, Confidence, Image FROM AccessLog ORDER BY Time"
	query2 = "SELECT Name,COUNT(*) as count FROM AccessLog GROUP BY Name ORDER BY count DESC"
	cur.execute(query)
	cur2.execute(query2)
	for (Time, Name, Similarity, Confidence, Image) in cur:
		d = []
		d.append("{:%d-%m-%Y %H:%M:%S}".format(Time))
		d.append(Name)
		d.append(Similarity)
		d.append(Confidence)
		d.append(Image)
		data.append(d)    
	#print(data)
	data_reversed = data[::-1]

	for (Name, count) in cur2:
		e = []
		e.append(Name)
		e.append(int(count))
		print(Name, count)
		data2.append(e)
	print(data2)
	
	stat = session.get('status', 'Offline')
	templateData ={'status': stat}

	return render_template('index.html', data=data_reversed, data2=data2, **templateData)
	#print('Rendered')

@app.route("/activate/")
def check2():
	if session.get('user') is None:
		return redirect('/')
	else:
		return activate()

def activate():
	extProc = sp.Popen(['python', 'rfid.py'])
	pid = extProc.pid
	session['proc'] = pid
	session['status'] = 'Active'
	return redirect('/home')

@app.route("/deactivate/")
def check3():
	if session.get('user') is None:
		return redirect('/')
	else:
		return deactivate()

def deactivate():
	pid = session.get('proc', None)
	
	if pid is None:
		return redirect('/home')

	session['status'] = 'Offline'
	os.kill(pid, signal.SIGKILL)
	ledRed.off()
	ledGreen.off()
	
	return redirect('/home')

@app.route("/<img>")
def check4(img):
	if session.get('user') is None:
		return redirect('/')
	else:
		return display_image(img)

def display_image(img):
	full_filename = os.path.join(app.config['image_folder'], img)
	return render_template('image.html', img = full_filename)

if __name__ == '__main__':
	app.secret_key = os.urandom(30)
	app.run(debug=True,host='0.0.0.0')

