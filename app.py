from distutils.log import error
import os
import uuid
import numpy as np
import urllib
import tensorflow as tf
from tensorflow import keras
from tensorflow.keras.models import load_model
from models import Model1, postgres,User
from tensorflow.keras.models import load_model
from tensorflow.keras.preprocessing import image
from flask import Flask, redirect, render_template, request, url_for, session

app = Flask(__name__)
app.secret_key='borto2ana'
app.config['SQLALCHEMY_DATABASE_URI']='postgres://vwqbwmjktbznpk:74d427d22d3c18c234a58c92a46aa903dcac7466db77026ec7dd05aaf9e8fdcb@ec2-44-198-82-71.compute-1.amazonaws.com:5432/d56f0c9tsir81v'

HOST= "localhost"
DATABASE="eatsafe"
USER="postgres"
PASSWORD="psql"

db=postgres()
db.connect(HOST,DATABASE,USER,PASSWORD)


@app.route('/')
def home():
    if not 'user' in session:
        return redirect(url_for('login'))
    else:
        return render_template("Homepage.html")

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method=='GET':
        if not 'user' in session:
            return render_template("login.html")
        else:
            return redirect(url_for('home'))
    if request.method=='POST':
        username=request.form.get('username')
        password=request.form.get('password')
        if not username or not password:
            return render_template("login.html", error="Please fill required feilds")
        else:
            user=User.get_user_by_username(User,db,username)
            if not user:
                return render_template("login.html", error="Incorrect username or password")
            else:
                user_password=user[4]
                if password != user_password:
                    return render_template("login.html", error="Incorrect username or password")
                else:
                    session['user']=user
                    return redirect(url_for('home'))
                
@app.route('/logout',  methods = ['GET', 'POST'])
def logout():
    if request.method == 'GET':
        session.pop('user', None)
        return redirect(url_for('login'))

@app.route('/dashboard')
def dashboard():
    return render_template("dashboard.html")
        
        
@app.route('/signup', methods=['GET', 'POST'])
def signup():
    if request.method=='GET':
        return render_template("signup.html")
    elif request.method=='POST':
        if request.args.get('users')=='signup':
            usertype_id=request.form.get('usertype_id')
            username=request.form.get('username')
            email=request.form.get('email')
            password=request.form.get('password')
            confirm_password=request.form.get('confirm_password')
            phone=request.form.get('phone')
            name=request.form.get('name')
            params=[username,usertype_id,email,password,name,phone,'NOW','NOW',False]
            if password != confirm_password:
                return render_template("signup.html",error="Password Do Not Match")
            else:
                User().add_user(db,params)
                return render_template("login.html")

@app.route('/model2')
def model2():
    return render_template("model2.html")                

@app.route('/model1')
def model1():
    return render_template("model1.html")

@app.route('/success2' , methods = ['GET' , 'POST'])
def success2():
    model = load_model('xception_model.h5')
    model.make_predict_function()
    dic2 = {0 : 'Imported', 1 : 'Local'}
    BASE_DIR = os.path.dirname(os.path.abspath(__file__))
    model = load_model(os.path.join(BASE_DIR , 'xception_model.h5'))
    ALLOWED_EXT = set(['jpg' , 'jpeg' , 'png' , 'jfif'])
    def allowed_file(filename):
        return '.' in filename and \
            filename.rsplit('.', 1)[1] in ALLOWED_EXT
    classes = ['Imported', 'Local']
    def predict(filename , model):
        img = tf.io.read_file(filename)
        img = tf.image.decode_jpeg(img, channels = 3)
        img = tf.image.resize(img, [320, 240])
        img = tf.expand_dims(img, axis=0)
        predict_y=model.predict(img) 
        result=np.argmax(predict_y,axis=1)
        result=dic2[result[0]]
        return result
    error = ''
    target_img = os.path.join(os.getcwd() , 'static/images')
    if request.method == 'POST':
        if(request.form):
            link = request.form.get('link')
            try :
                resource = urllib.request.urlopen(link)
                unique_filename = str(uuid.uuid4())
                filename = unique_filename+".jpg"
                img_path = os.path.join(target_img , filename)
                output = open(img_path , "wb")
                output.write(resource.read())
                output.close()
                img = filename
                class_result , prob_result = predict(img_path , model)
                predictions = {
                          "class1":class_result[0],
                        "class2":class_result[1],
                        "class3":class_result[2],
                        "prob1": prob_result[0],
                        "prob2": prob_result[1],
                        "prob3": prob_result[2],
                }
            except Exception as e : 
                print(str(e))
                error = 'This image from this site is not accesible or inappropriate input'
            if(len(error) == 0):
                return  render_template('success2.html' , img  = img , predictions = predictions)
            else:
                return render_template('model2.html' , error = error) 
        elif (request.files):
            file = request.files['file']
            if file and allowed_file(file.filename):
                file_ext=file.filename.split('.').pop()
                unique_filename=str(uuid.uuid4())
                file.filename=unique_filename+"."+file_ext
                file.save(os.path.join(target_img , file.filename))
                img_path = os.path.join(target_img , file.filename)
                img = file.filename
                result = predict(img_path , model)
                classification_id=Model1().get_classification_id(db,result)
                params=[session['user'][0],classification_id,img,"Now"]
                Model1().add_session(db,params)
                return  render_template('success.html' , img  = img , result = result, classification_id=classification_id)
                #  predictions = {
                    #        "class1":class_result[0],
                #          "class2":class_result[1],
                #          "class3":class_result[2],
                #          "prob1": prob_result[0],
                #          "prob2": prob_result[1],
                #          "prob3": prob_result[2],
                #  }
            else:
                error = "Please upload images of jpg , jpeg and png extension only"
            if(len(error) == 0):
                return  render_template('success2.html' , img  = img , predictions = predictions)
            else:
                return render_template('model2.html' , error = error)
    else:
        return render_template('model2.html')

@app.route('/success' , methods = ['GET' , 'POST'])
def success():
    model = load_model('effecientnetB01.h5')
    model.make_predict_function()
    dic = {0 : 'Beef chuck', 1 : 'Beef fillet', 2 : 'Beef flank', 3 : 'Beef round', 4 : 'Liver', 5 : 'Roast beef', 6 : 'Strip-lion'}
    BASE_DIR = os.path.dirname(os.path.abspath(__file__))
    model = load_model(os.path.join(BASE_DIR , 'effecientnetB01.h5'))
    ALLOWED_EXT = set(['jpg' , 'jpeg' , 'png' , 'jfif'])
    def allowed_file(filename):
        return '.' in filename and \
            filename.rsplit('.', 1)[1] in ALLOWED_EXT
    classes = ['Beef chuck', 'Beef fillet', 'Beef flank', 'Beef round', 'Liver', 'Roast beef', 'Strip-lion']
    def predict(filename , model):
        img = tf.io.read_file(filename)
        img = tf.image.decode_jpeg(img, channels = 3)
        img = tf.image.resize(img, [224,224])
        img = tf.expand_dims(img, axis=0)
        predict_x=model.predict(img) 
        result=np.argmax(predict_x,axis=1)
        result=dic[result[0]]
        return result
    error = ''
    target_img = os.path.join(os.getcwd() , 'static/images')
    if request.method == 'POST':
        if(request.form):
            link = request.form.get('link')
            try :
                resource = urllib.request.urlopen(link)
                unique_filename = str(uuid.uuid4())
                filename = unique_filename+".jpg"
                img_path = os.path.join(target_img , filename)
                output = open(img_path , "wb")
                output.write(resource.read())
                output.close()
                img = filename
                class_result , prob_result = predict(img_path , model)
                predictions = {
                      "class1":class_result[0],
                        "class2":class_result[1],
                        "class3":class_result[2],
                        "prob1": prob_result[0],
                        "prob2": prob_result[1],
                        "prob3": prob_result[2],
                }
            except Exception as e : 
                print(str(e))
                error = 'This image from this site is not accesible or inappropriate input'
            if(len(error) == 0):
                return  render_template('success.html' , img  = img , predictions = predictions)
            else:
                return render_template('model1.html' , error = error) 
        elif (request.files):
            file = request.files['file']
            if file and allowed_file(file.filename):
                file_ext=file.filename.split('.').pop()
                unique_filename=str(uuid.uuid4())
                file.filename=unique_filename+"."+file_ext
                file.save(os.path.join(target_img , file.filename))
                img_path = os.path.join(target_img , file.filename)
                img = file.filename
                result = predict(img_path , model)
                classification_id=Model1().get_classification_id(db,result)
                params=[session['user'][0],classification_id,img,"Now"]
                Model1().add_session(db,params)
                return  render_template('success.html' , img  = img , result = result)
                predictions = {
                          "class1":class_result[0],
                          "class2":class_result[1],
                          "class3":class_result[2],
                          "prob1": prob_result[0],
                          "prob2": prob_result[1],
                          "prob3": prob_result[2],
                  }
            else:
                error = "Please upload images of jpg , jpeg and png extension only"
            if(len(error) == 0):
                return  render_template('success.html' , img  = img , predictions = predictions)
            else:
                return render_template('model1.html' , error = error)
    else:
        return render_template('model1.html')

if __name__ == "__main__":
    app.run(debug = True)