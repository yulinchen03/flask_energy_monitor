import html

from flask import Flask, render_template, json
from flask_wtf import FlaskForm
from wtforms import FileField, SubmitField
from werkzeug.utils import secure_filename
import os
from wtforms.validators import InputRequired

app = Flask(__name__)
app.config['SECRET_KEY'] = '2AC579BD5E34C'
app.config['UPLOAD_FOLDER'] = 'static/files'


class UploadFileForm(FlaskForm):
    file = FileField("File", validators=[InputRequired()])
    submit = SubmitField("Upload File")


@app.route('/', methods=['GET', 'POST'])
def home():  # put application's code here
    form = UploadFileForm()
    if form.validate_on_submit():
        file = form.file.data
        filepath = os.path.join(os.path.abspath(os.path.dirname(__file__)), app.config['UPLOAD_FOLDER'], secure_filename(file.filename))
        file.save(filepath)
        data = processor(filepath)
        return render_template("analysis.html", data=html.unescape(json.dumps(data)))
    return render_template('home.html', form=form)


# todo integrate algorithm to produce x, y values and colors
# filepath to dataset is the argument
def processor(filepath):
    filename = filepath.split('\\')[-1]
    data = {
        "file": filename,
        "xValues1": [1, 2, 3, 4, 5, 6, 7, 8],
        "xValues2": [1, 2, 3, 4, 5, 6, 7, 8],
        "yValues1": [7, 8, 8, 9, 9, 9, 10, 11],
        "yValues2": [5, 7, 6, 5, 2, 6, 5, 8]
    }
    return data


if __name__ == '__main__':
    app.run(debug=True)
