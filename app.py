import base64
import glob
import html
import random
from datetime import datetime, timedelta
from io import BytesIO

from flask import Flask, render_template, json, url_for, request
from flask_wtf import FlaskForm
from matplotlib import pyplot as plt
from wtforms import SubmitField, HiddenField
from werkzeug.utils import secure_filename, redirect
import os
from wtforms.validators import InputRequired

from static.src import data_loader
from static.src.visuals import plot_powers_pie, plot_powers_stack
from static.src.data_loader import load_all_tagged, load_tagged, load_test
from static.src.energy_model import EnergyModel
from matplotlib.figure import Figure
import pandas as pd


app = Flask(__name__)
app.config['SECRET_KEY'] = '2AC579BD5E34C'
app.config['UPLOAD_FOLDER'] = 'static/data/h1'


class UploadFileForm(FlaskForm):
    filename = HiddenField("filename")
    submit = SubmitField("Upload File")


@app.route('/', methods=['GET', 'POST'])
def home():  # put application's code here
    if request.method == 'POST':
        data = request.form
        filename = data['filename'].split('\\')[-1]
        filepath = os.path.join(os.path.abspath(os.path.dirname(__file__)), app.config['UPLOAD_FOLDER'], secure_filename(filename))
        return redirect(url_for('.processor', filepath=filepath))
    return render_template('home.html')


# todo integrate algorithm to produce x, y values and colors
@app.route('/analysis')
def processor():
    filepath = request.args['filepath']
    filename = filepath.split('\\')[-1]
    tagged_files = data_loader.tagged_files['h1']
    old_plots = glob.glob('static/plots/*')
    for plot in old_plots:
        os.remove(plot)

    tagged_data = data_loader.load_all_tagged('h1')
    model = EnergyModel(tagged_data)
    plot_data(model, tagged_data[tagged_files.index(filename)])

    plotpath = f'static/plots/{filename}'
    plt.savefig(plotpath)

    data = {
        "file": filename,
        "plotpath": plotpath,
    }
    return render_template('analysis.html', data=json.dumps(data))


def plot_data(model, data):
    times, powers, labels = model.disaggregate(data)
    plot_powers_stack(times, powers, labels)
    plot_powers_pie(powers, labels)


if __name__ == '__main__':
    app.run(debug=True)
