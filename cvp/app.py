"""Covid-19 Vaccine Passport Application"""

from flask import Flask
from flask import render_template, request

app = Flask(__name__)


@app.route('/')
def homepage():
    return render_template('homepage.html', title='this is title of homepage', body='option to register and login')


@app.route('/register', methods=["GET", "POST"])
def register_input():
    print(f'in register(), {request.method=}')
    if request.method == "POST":
        return render_template("uploading_of_document.html")


@app.route('/register_confirm', methods=["GET", "POST"])
def register_confirm():
    print(f'in register_confirm(), {request.method=}')
    if request.method == "POST":
        email = request.form.get('email')
        password = request.form.get('password')
        confirm_password = request.form.get('confirm_password')

        # do things with these
        if password == confirm_password:
            return render_template('create_account.html', info=f'Welcome {email=}, {password=}, {confirm_password=} !')
    return render_template("uploading_of_document.html", wrong_pass='Password did not match!')


if __name__ == '__main__':
    app.run(debug=True)
