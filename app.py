import os, flask, io, datetime
from werkzeug.utils import secure_filename 
import tensorflow as tf
import numpy as np
from PIL import Image
from flask import request
from model import Network
import db

CKPT_DIR = 'ckpt'                                                # 定义模型存储的位置

app = flask.Flask(__name__)
app.config['UPLOAD_FOLDER'] = 'static/uploads/'                  #上传的图片存放在服务器端的static/uploads目录下
#app.config['ALLOWED_EXTENSIONS'] = set(['png', 'jpg', 'jpeg'])   #允许的图片格式

# Load Pre-trained TensorFlow MNIST Model
def loadmodel():
    global net
    net = Network()
    global sess
    sess = tf.Session()
    sess.run(tf.global_variables_initializer())
    # tf.train.Saver是用来保存训练结果的。
    saver = tf.train.Saver()
    # 开始训练前，检查ckpt文件夹，看是否有checkpoint文件存在。
    # 如果存在，则读取checkpoint文件指向的模型，restore到sess中。
    ckpt = tf.train.get_checkpoint_state(CKPT_DIR)
    if ckpt and ckpt.model_checkpoint_path:
        saver.restore(sess, ckpt.model_checkpoint_path)
    else:
        raise FileNotFoundError("Unable to find saved model")

# Make Prediction
def predict(image_path):
    # 读图片并转为黑白的
    img = Image.open(image_path).convert('L')  
    flatten_img = np.reshape(img, 784)
    x = np.array([1 - flatten_img])
    # 因为x只传入了一张图片，取y[0]即可
    # np.argmax()取得one-hot编码最大值的下标，即代表的数字
    y = sess.run(net.y, feed_dict={net.x: x})
    result = np.argmax(y[0])
    return result

# For a given file, return whether it's an allowed type or not
'''def allowed_file(filename):  
    return '.' in filename and \
           filename.rsplit('.', 1)[1] in app.config['ALLOWED_EXTENSIONS']
'''

def parseName(name, time):
    temp = []
    temp.append(str(time))
    temp.append('_')
    temp.append(name)
    name = ''.join(temp)
    return name

# Flask Router
@app.route("/")
def index():
    return  '''
    <!doctype html>
    <title>Upload new File</title>
    <body>
    <h1>选择图片进行识别</h1>
    <form action='http://0.0.0.0:8000/mnist' method='post' enctype='multipart/form-data'>
        <input type='file' name='file'>
    <input type='submit' value='预测'>
    </form>'''
  
@app.route("/mnist", methods=["POST"])
def mnist():
    req_time = datetime.datetime.now()#记录请求时间
    if flask.request.method == "POST":
        #if flask.request.files.get("image"):
        upload_file = flask.request.files["file"] 
        upload_filename = secure_filename(upload_file.filename)#上传文件文件名的安全获取，文件名不要用中文
        
        save_filename = parseName(upload_filename,req_time)
        save_filepath = os.path.join(app.root_path, app.config['UPLOAD_FOLDER'], save_filename)#对文件路径进行拼接
        upload_file.save(save_filepath)#将upload_file保存在服务器的文件系统中
        mnist_result = str(predict(save_filepath))
        db.insertData(request.remote_addr, req_time, save_filepath, mnist_result)
        req_time = str(req_time)
        return upload_filename + ' ' + req_time + ' ' + mnist_result
           # return ("%s%s%s%s%s%s%s%s%s" % ("Upload File Name: ", upload_filename, "\n", 
           #                   "Upload Time: ", req_time, "\n",
           #                   "Prediction: ",mnist_result, "\n"))

if __name__ == '__main__':
    if not os.path.exists(app.config['UPLOAD_FOLDER']):
        os.makedirs(app.config['UPLOAD_FOLDER'])

    db.createKeySpace()
    loadmodel()
    app.run(debug=True, use_reloader=False, host='0.0.0.0')