import os
from flask import Flask, render_template, url_for, redirect, request
from flask.ext.dropbox import Dropbox, DropboxBlueprint
from werkzeug import secure_filename

app = Flask(__name__)

# set up Dropbox
import settings
app.config.from_object(settings)
dropbox = Dropbox(app)
dropbox.register_blueprint(url_prefix='/dropbox')

@app.route('/login')
def login():
    if not dropbox.is_authenticated:
        return u'Click <a href="%s">here</a> to login with Dropbox.' % \
            dropbox.login_url
    return redirect(url_for('home', text=md))

@app.route('/', methods=('GET', 'POST'))
def home():
    if dropbox.is_authenticated:
        loggedin = True
    else:
        loggedin = False
    # to save current file in Dropbox
    if request and request.method == 'POST':
        md = request.form['markdown']
        if md:
            name = ''
            for c in md:
                if c == '\n':
                    name += '.md'
                    break
                if c.isalnum():
                    name += c
            if md:
                client = dropbox.client
                filename = secure_filename(name)
                result = client.put_file('/' + filename, md)
                path = result['path'].lstrip('/')
                return render_template('index.html', text=md, uploaded=filename, loggedin=loggedin)

    if request and request.method == 'GET' and request.query_string:
        return render_template('index.html', text=request.args.get('text'), loggedin=loggedin)

    return render_template('index.html', loggedin=loggedin)

@app.route('/upload', methods=('GET', 'POST'))
def upload():
    if not dropbox.is_authenticated:
        return redirect(url_for('home'))

    if request and request.method == 'POST':
        file_obj = request.files['file']
        if file_obj:
            md = file_obj.read()
            return redirect(url_for('home', text=md))
    
    return render_template('upload.html')

if __name__ == '__main__':
    # Bind to PORT if defined, otherwise default to 5000.
    app.debug = True
    port = int(os.environ.get('PORT', 5000))
    app.run(host='0.0.0.0', port=port)