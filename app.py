import glob

from flask import Flask, render_template, json, url_for, request
from flask_wtf import FlaskForm
from wtforms import SubmitField, HiddenField
from werkzeug.utils import secure_filename, redirect

from static.src import data_loader
from static.src.visuals import plot_powers_pie, plot_powers_stack
from static.src.data_loader import *
from static.src.energy_model import EnergyModel


app = Flask(__name__)
app.config['SECRET_KEY'] = '2AC579BD5E34C'
app.config['UPLOAD_FOLDER'] = 'static/files'


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
    old_stackplot = glob.glob('static/plots/stackplot/*')
    old_pie = glob.glob('static/plots/pie/*')
    tagged_files = {}
    test_files = {}

    data_dir_tagged = os.path.abspath('static/data')
    data_dir_test = os.path.abspath('static/files')

    for h in os.listdir(data_dir_tagged):
        files = os.listdir(f'{data_dir_tagged}/{h}')
        tagged_files[h] = sorted([f for f in files if f.startswith('Tagged')])

    for h in os.listdir(data_dir_test):
        files = os.listdir(f'{data_dir_test}/{h}')
        test_files[h] = sorted([f for f in files if f.startswith('Testing')])

    for plot in old_stackplot:
        os.remove(plot)

    for plot in old_pie:
        os.remove(plot)

    tagged_data = data_loader.load_all_tagged('h1')
    model = EnergyModel(tagged_data)
    test_data = data_loader.load_test('h1', test_files['h1'].index(filename))
    times, powers, labels = model.disaggregate(test_data)
    plotpath_stack = plot_powers_stack(times, powers, labels, filename, smooth=False)
    plotpath_pie = plot_powers_pie(powers, labels, filename)

    data = {
        "file": filename,
        "plotpath_stack": plotpath_stack,
        "plotpath_pie": plotpath_pie
    }
    return render_template('analysis.html', data=json.dumps(data))


if __name__ == '__main__':
    app.run(debug=True)
