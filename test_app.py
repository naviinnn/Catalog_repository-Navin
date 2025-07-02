from flask import Flask

app = Flask(__name__)
@app.route('/Hello')
def home():
    return "Hello Flask , How you doin ? :)"  
if __name__ == '__main__':
    app.run(debug=True,)