from flask import Flask
from application import report_f1

app = Flask(__name__)
app.register_blueprint(report_f1.report_f1, url_prefix="")


if __name__ == '__main__':
    app.run(debug=True)