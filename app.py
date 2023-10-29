import base64
import glob
import html
import random
from datetime import datetime, timedelta
from io import BytesIO

from flask import Flask, render_template, json, url_for, request
from flask_wtf import FlaskForm
from matplotlib import pyplot as plt
from wtforms import FileField, SubmitField
from werkzeug.utils import secure_filename, redirect
import os
from wtforms.validators import InputRequired
from matplotlib.figure import Figure
import pandas as pd


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
        return redirect(url_for('.processor', filepath=filepath))
    return render_template('home.html', form=form)


# todo integrate algorithm to produce x, y values and colors
@app.route('/analysis')
def processor():
    filepath = request.args['filepath']
    old_plots = glob.glob('static/plots/*')
    for plot in old_plots:
        os.remove(plot)

    filename = filepath.split('\\')[-1]
    labels = ['Other', 'Trash Compactor', 'Garage Lights']
    data1 = [random.randint(380,510) for i in range(100)]
    data2 = [random.randint(120,310) for i in range(100)]
    data3 = [random.randint(50,110) for i in range(100)]
    powers = [data1, data2, data3]
    start_time = datetime(2023, 10, 29, 0, 0, 0)  # Start at midnight
    end_time = datetime(2023, 10, 29, 23, 59, 59)  # End just before midnight the next day

    # Calculate the time interval between each timestamp
    time_interval = (end_time - start_time) / 99  # We want 100 timestamps, so divide by 99

    # Generate the list of timestamps
    times = [start_time + timedelta(seconds=i * time_interval.total_seconds()) for i in range(100)]

    plt.figure(figsize=(10, 4))
    plt.stackplot(times, powers, labels=labels, alpha=0.6)
    plt.legend(loc='upper left')
    plt.xlabel('Time')
    plt.ylabel('Energy Consumption (Wh)')
    plt.title('Energy Disaggregation')
    plt.grid(True)
    plt.tight_layout()

    plotpath = f'static/plots/{filename}'
    plt.savefig(plotpath)

    data = {
        "file": filename,
        "plotpath": plotpath
    }
    return render_template('analysis.html', data=json.dumps(data))


if __name__ == '__main__':
    app.run(debug=True)
