# Energy monitor: Algorithm + visualizer for energy disaggregation of home appliances
###### Yulin Chen, Denis Krylov, Aliaksei Kovzel, Aryan Khawani

Energy model is a tool for the analysis of energy readings from a home environment, and visualizing energy disaggregation of appliances, for the purpose of advising its users about how to use energy in a sustainable way.

This project uses data from the Belkin Energy Disaggregation Competition 2013 \
https://www.kaggle.com/c/belkin-energy-disaggregation-competition
## Getting started

Clone the repository in Pycharm using HTTPS
Download the dataset from Kaggle\
https://www.kaggle.com/competitions/belkin-energy-disaggregation-competition/data

Download the dataset as a zip file （e.g H1.zip)

Unzip the file, copy the files with names containing "Tagged" and copy them into one of the folders within
```bash
static/data/tagged/
```
This is either h1, h2, h3 or h4. If the dataset is H1.zip, then, make sure the data is in the folder /h1

Then, copy the files with names containing "Testing" and copy them into one of the folders within
```bash
static/data/testing/
```
This is either h1, h2, h3 or h4. If the dataset is H1.zip, then, also make sure the data is in the folder /h1

To start the server, open terminal in Pycharm and execute the following:
```bash
python -m flask run
```
Please make sure python and flask are both installed. It may be possible that some dependencies are missing, run
```bash
pip install {missing_dependency_name}
```
to resolve the issue.

Once the server starts successfully, open the following on a browser:
``` bash
http://127.0.0.1:5000
```

## Usage

To use the tool, click on 'choose file', navigate to the project repository, select one of the .mat files from static/data/testing. If you have only downloaded the dataset for house 1 (h1.zip), then select a file from static/data/testing/h1.

Once the file has been selected, simply click on 'Analyse', and wait patiently. It can take a few minutes depending on your hardware's performance.

Then you should be able to see a detailed analysis of the energy data you have selected, including the disaggregation of appliances.

