from flask import Flask, request, jsonify
from flask_cors import CORS

import pickle
import numpy as np
import pandas as pd

from tensorflow.keras.preprocessing.text import Tokenizer
from tensorflow.keras.preprocessing.sequence import pad_sequences
from tensorflow import keras

import os 
import re
from urllib.parse import urlparse
import tldextract
from tld import get_tld, is_tld
################################
def abnormal_url(url):
    hostname=urlparse(url).hostname
    hostname=str(hostname)
    match=re.search(hostname,url)
    if match:
        return 1
    else:
        return 0
def http_secure(url):
    http=urlparse(url).scheme
    match=str(http)
    if match=='https':
        return 1
    else:
        return 0
def digit_count(url):
    digits=0
    for c in url:
        if c.isnumeric():
            digits+=1
    return digits
def letter_count(url):
    letters=0
    for c in url:
        if c.isalpha():
            letters+=1
    return letters
def find_shortening_service(url):
    match=re.search('bit\.ly|goo\.gl|shorte\.st|go2l\.ink|x\.co|ow\.ly|t\.co|tinyurl|tr\.im|is\.gd|cli\.gs|'
                      'yfrog\.com|migre\.me|ff\.im|tiny\.cc|url4\.eu|twit\.ac|su\.pr|twurl\.nl|snipurl\.com|'
                      'short\.to|BudURL\.com|ping\.fm|post\.ly|Just\.as|bkite\.com|snipr\.com|fic\.kr|loopt\.us|'
                      'doiop\.com|short\.ie|kl\.am|wp\.me|rubyurl\.com|om\.ly|to\.ly|bit\.do|t\.co|lnkd\.in|'
                      'db\.tt|qr\.ae|adf\.ly|goo\.gl|bitly\.com|cur\.lv|tinyurl\.com|ow\.ly|bit\.ly|ity\.im|'
                      'q\.gs|is\.gd|po\.st|bc\.vc|twitthis\.com|u\.to|j\.mp|buzurl\.com|cutt\.us|u\.bb|yourls\.org|'
                      'x\.co|prettylinkpro\.com|scrnch\.me|filoops\.info|vzturl\.com|qr\.net|1url\.com|tweez\.me|v\.gd|'
                      'tr\.im|link\.zip\.net', url)
    if match:
        return 1
    else:
        return 0
def contain_ip_address(url):
    match=re.search('(([01]?\\d\\d?|2[0-4]\\d|25[0-5])\\.([01]?\\d\\d?|2[0-4]\\d|25[0-5])\\.([01]?\\d\\d?|2[0-4]\\d|25[0-5])\\.'
        '([01]?\\d\\d?|2[0-4]\\d|25[0-5])\\/)|'  # IPv4
        '(([01]?\\d\\d?|2[0-4]\\d|25[0-5])\\.([01]?\\d\\d?|2[0-4]\\d|25[0-5])\\.([01]?\\d\\d?|2[0-4]\\d|25[0-5])\\.'
        '([01]?\\d\\d?|2[0-4]\\d|25[0-5])\\/)|'  # IPv4 with port
        '((0x[0-9a-fA-F]{1,2})\\.(0x[0-9a-fA-F]{1,2})\\.(0x[0-9a-fA-F]{1,2})\\.(0x[0-9a-fA-F]{1,2})\\/)' # IPv4 in hexadecimal
        '(?:[a-fA-F0-9]{1,4}:){7}[a-fA-F0-9]{1,4}|'
        '([0-9]+(?:\.[0-9]+){3}:[0-9]+)|'
        '((?:(?:\d|[01]?\d\d|2[0-4]\d|25[0-5])\.){3}(?:25[0-5]|2[0-4]\d|[01]?\d\d|\d)(?:\/\d{1,2})?)', url)
    if match:
        return 1
    else:
        return 0
####################################
def protocol(url):
    result=urlparse(url)
    return result.scheme
def sub_domain(url):
    domain=tldextract.extract(url)
    return domain.subdomain
def domain(url):
    domain=tldextract.extract(url)
    return domain.domain
def suffix(url):
    domain=tldextract.extract(url)
    return domain.suffix
def path(url):
    result=urlparse(url)
    return result.path
#################################

app = Flask(__name__)
CORS(app)

maxlen=300
label=['benign', 'defacement', 'malware', 'phishing', 'spam']

def nn_predict(data):
    try:
        link=[str(data['url'])]
        link=pd.DataFrame(link,columns=['url'])
        link['url_len']=link['url'].apply(lambda x: len(str(x)))
        chars=['@','?','-','=','.','#','%','+','$','!','*',',','//']
        for char in chars:
            link[char]=link['url'].apply(lambda x: x.count(char))
        link['abnormal_url']=link['url'].apply(lambda x: abnormal_url(x))
        link['https']=link['url'].apply(lambda x: http_secure(x))
        link['digits']=link['url'].apply(lambda x: digit_count(x))
        link['letters']=link['url'].apply(lambda x: letter_count(x))
        link['shortening_service']=link['url'].apply(lambda x: find_shortening_service(x))
        link['contain_ip_address']=link['url'].apply(lambda x: contain_ip_address(x))
        link=link.drop(columns=['url'],axis=1)
        model=keras.models.load_model(r'D:\PythonWorkspace\PythonMain\IoT\Flask\model\20feature.h5')
        y_pred=model.predict(link)
        return y_pred[0][0]
    except Exception as e:
        print(e)
        return None

def get_feature(data,tokenizer,model):
  temp_data = tokenizer.texts_to_sequences(data)
  temp_data = pad_sequences(temp_data, maxlen=maxlen, padding='post',truncating='post')
  feature=model.predict(temp_data)

  del(temp_data)
  return feature

def cnn_predict(data):
    try:
        with open(r'D:\PythonWorkspace\PythonMain\IoT\Flask\model\tokenizer_char_urls4_17k.pkl','rb') as handle:
            tokenizer=pickle.load(handle)
        print('Tokenizer: Ok')
        model= keras.models.load_model(r'D:\PythonWorkspace\PythonMain\IoT\Flask\model\feature_character.h5')
        print('Feature character: Ok')
        model_test=keras.models.load_model(r'D:\PythonWorkspace\PythonMain\IoT\Flask\model\p2_cnn_lstm_epoch_18_val_acc_0.99.h5')
        print('CNN: Ok')
        link=[str(data['url'])]
        link=pd.DataFrame(link,columns=['url'])
        link['protocol_url']=link['url'].apply(lambda x: protocol(x))
        link['sub_domain_url']=link['url'].apply(lambda x: sub_domain(x))
        link['domain_url']=link['url'].apply(lambda x: domain(x))
        link['suffix_domain_url']=link['url'].apply(lambda x: suffix(x))
        link['path_url']=link['url'].apply(lambda x: path(x))
        feature=get_feature(link['protocol_url'],tokenizer,model)
        feature2=get_feature(link['sub_domain_url'],tokenizer,model)
        feature3=get_feature(link['domain_url'],tokenizer,model)
        feature4=get_feature(link['suffix_domain_url'],tokenizer,model)
        feature5=get_feature(link['path_url'],tokenizer,model)
        feature=np.concatenate((feature,feature2,feature3,feature4,feature5),axis=1)
        del(feature2)
        del(feature3)
        del(feature4)
        del(feature5)
        feature=pd.DataFrame(feature,columns=['f'+str(x)for x in range(1,feature.shape[1]+1)])
        y_pred=np.argmax(model_test.predict(feature),axis=1)
        return y_pred[0]
    except Exception as e:
        print(e)
    return None

def predict(data):
    try:       
        score=nn_predict(data)
        print('Score: ',score)
        if score < 0.5:
            return 0
        return cnn_predict(data)
    except Exception as e:
        print(e)
        return e
@app.route('/process_data', methods=['POST'])
def process_data():
    data = request.get_json()
    # Xử lý dữ liệu ở đây (ví dụ: in ra console)
    print("Received data:", data)
    # data1={'url':'http://hotel-luna.ch/doc1977/document.php'}#url độc hại
    y_pred=predict(data)
    if y_pred is not None:
        print("Predict label: ",label[y_pred])
        # Trả về kết quả cho client (ví dụ: chuỗi "Processed!")
        return jsonify({"result": label[y_pred]})
    print("Predict label: Error!!!")
    return jsonify({"result": "Error predict!"})
if __name__ == '__main__':
    app.run(debug=True)