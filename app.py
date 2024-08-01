from flask import Flask, request, jsonify, render_template, send_from_directory, session, redirect, url_for
from werkzeug.utils import secure_filename
import os
from skimage.io import imread
import cv2
import numpy as np
from pymongo import MongoClient, errors
from bson import ObjectId
from werkzeug.security import generate_password_hash, check_password_hash

# Import your existing image processing functions
from utils import calcMeasurements, preprocess, kMeans_cluster, edgeDetection, getBoundingBox, cropOrig, overlayImage, calcFeetGirth

app = Flask(__name__)
UPLOAD_FOLDER = 'uploads/original'
PROCESSED_FOLDER = 'uploads/processed'
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER
app.config['PROCESSED_FOLDER'] = PROCESSED_FOLDER
app.secret_key = 'your_secret_key_here'  # Change this to a secure random key

# MongoDB connection
client = MongoClient('mongodb://localhost:27017')
db = client['feet_measurement']  # Replace with your database name
dbzappos = client['zappos'] 
dbamazon = client['amazon']
dbflipkart= client['flipkart']
users_collection = db['users']

# Create directories if they don't exist
if not os.path.exists(UPLOAD_FOLDER):
    os.makedirs(UPLOAD_FOLDER)

if not os.path.exists(PROCESSED_FOLDER):
    os.makedirs(PROCESSED_FOLDER)

# Routes

@app.route('/')
def index():
    if 'username' in session:
        return render_template('index.html')
    return redirect(url_for('login'))

@app.route('/upload', methods=['POST'])
def upload():
    if 'username' not in session:
        return redirect(url_for('login'))

    if 'image' not in request.files:
        return jsonify({'error': 'No file part'}), 400
    file = request.files['image']
    if file.filename == '':
        return jsonify({'error': 'No selected file'}), 400
    if file:
        filename = secure_filename(file.filename)
        original_filepath = os.path.join(app.config['UPLOAD_FOLDER'], filename)
        file.save(original_filepath)
        
        # Process the image and calculate measurements
        oimg = imread(original_filepath)
        preprocessedOimg = preprocess(oimg)
        clusteredImg = kMeans_cluster(preprocessedOimg)
        edgedImg = edgeDetection(clusteredImg)
        boundRect, contours, contours_poly, img = getBoundingBox(edgedImg)
        croppedImg, pcropedImg = cropOrig(boundRect[1], clusteredImg)
        newImg = overlayImage(croppedImg, pcropedImg)
        fedged = edgeDetection(newImg)
        fboundRect, fcnt, fcntpoly, fimg = getBoundingBox(fedged)
        foot_length_cm = calcFeetGirth(pcropedImg, fboundRect)
        ball_breadth_cm, bridge_breadth_cm, ball_girth_cm, instep_girth_cm=calcMeasurements(foot_length_cm)
        # Save processed image
        processed_filename = 'processed_' + filename
        processed_filepath = os.path.join(app.config['PROCESSED_FOLDER'], processed_filename)
        cv2.imwrite(processed_filepath, fimg)
        
        # Format values to two decimal points
        foot_length_cm = round(foot_length_cm, 2)
        ball_breadth_cm = round(ball_breadth_cm, 2)
        bridge_breadth_cm = round(bridge_breadth_cm, 2)
        ball_girth_cm = round(ball_girth_cm, 2)
        instep_girth_cm = round(instep_girth_cm, 2)
        
        return render_template('result.html', 
                               original_image=filename, 
                               processed_image=processed_filename,
                               foot_length_cm=foot_length_cm,
                               ball_breadth_cm=ball_breadth_cm,
                               bridge_breadth_cm=bridge_breadth_cm,
                               ball_girth_cm=ball_girth_cm,
                               instep_girth_cm=instep_girth_cm)

@app.route('/uploads/original/<filename>')
def uploaded_file(filename):
    return send_from_directory(app.config['UPLOAD_FOLDER'], filename)

@app.route('/uploads/processed/<filename>')
def processed_file(filename):
    return send_from_directory(app.config['PROCESSED_FOLDER'], filename)

@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        
        if users_collection.find_one({'username': username}):
            return 'User already exists!'
        
        hash_password = generate_password_hash(password)
        try:
            users_collection.insert_one({'username': username, 'password': hash_password})
            return redirect(url_for('login'))
        except errors.DuplicateKeyError:
            return 'User already exists!'

    return render_template('register.html')

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        
        user = users_collection.find_one({'username': username})
        
        if user and check_password_hash(user['password'], password):
            session['username'] = username
            return redirect(url_for('index'))
        
        return 'Invalid username or password'

    return render_template('login.html')

@app.route('/logout')
def logout():
    session.pop('username', None)
    return redirect(url_for('login'))


@app.route('/get-url', methods=['GET'])
def get_url():
    gender = request.args.get('gender')
    feet_length_cm = float(request.args.get('cm'))
    
    collection = dbzappos[gender]  # Choose collection based on gender
    
    # Find the document with the smallest 'cm' value greater than or equal to feet_length_cm
    document = collection.find_one({'cm': {'$gte': feet_length_cm}}, sort=[('cm', 1)])
    
    if document:
        return jsonify({'url': document['url']})
    else:
        return jsonify({'url': None})

@app.route('/get-urlamazon', methods=['GET'])
def get_urlamazon():
    gender = request.args.get('gender')
    feet_length_cm = float(request.args.get('cm'))
    
    collection = dbamazon[gender]  # Choose collection based on gender
    
    # Find the document with the smallest 'cm' value greater than or equal to feet_length_cm
    document = collection.find_one({'cm': {'$gte': feet_length_cm}}, sort=[('cm', 1)])
    
    if document:
        return jsonify({'url': document['url']})
    else:
        return jsonify({'url': None})

@app.route('/get-urlflipkart', methods=['GET']) 
def get_urlflipkart():
    gender = request.args.get('gender')
    feet_length_cm = float(request.args.get('cm'))
    
    collection = dbflipkart[gender]  # Choose collection based on gender
    
    # Find the document with the smallest 'cm' value greater than or equal to feet_length_cm
    document = collection.find_one({'cm': {'$gte': feet_length_cm}}, sort=[('cm', 1)])
    
    if document:
        return jsonify({'url': document['url']})
    else:
        return jsonify({'url': None})

if __name__ == '__main__':
    app.run(debug=True)