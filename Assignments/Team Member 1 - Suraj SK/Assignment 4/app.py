from flask import Flask, render_template

app = Flask(__name__)
app.config['SECRET_KEY'] = 'UreGeQ93_trDU-QMqANIhrdL63qecZa_AZnvKBXrN0R_'

@app.route("/")
def home():
    return render_template("index.html")

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=True)
