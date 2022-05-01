# MethodNameGeneration

Authors:
- Zane Varner
- Cerag Oguztuzun
- Feng Long

## Gathering the Data

The data used for this assignment comes from the [code2seq repository from Alon et al](https://github.com/tech-srl/code2seq/blob/master/README.md#datasets). The java-small dataset was used for the experiments and the paper, but the java-med and java-large datasets are also in the correct format.

## Parsing the Data Files

Edit the main function in `parse_main.py` to point to the correct data file paths for your machine.  Run this file in order to generate the text file of all of the processed data.

## Reducing the Data

Use the Jupyter notebook `dist.ipynb` in order to plot the distribution of the processed data as well as to reduce the size of the data based on a percentile of the lengths of the input or output sequences.

## Running the Models

Upload the processed (and reduced) data file to a folder in Google Drive.

Each model is implemented in Google Colab in order to take advantage of the GPUs. The notebooks for the [RNN](https://colab.research.google.com/drive/1ZpfScdhgQpx-HmC7oTb5ucJpW1dfw5Kx?usp=sharing) and [Transformer](https://colab.research.google.com/drive/1bJjMXyNl0PPK1q5DdR4pv9yk2dmhwZB4?usp=sharing) models are linked.

Within the notebooks, edit the paths to point to where you have uploaded the data files. Also, update the results folder path to indicate where you would like the results to be produced.

You may then run the entire notebook in order to run an experiment.  Make sure to specify which contexts should be used in the data preparation cells as well as the name of the experiment.

## Producing the Metrics

After running the experiments in Google Colab, download the `predictions.txt` file from Google Drive. Then, use the `results.py` Python file to produce the metrics using the predictions. Note that the path to the predictions file will have to be manually updated in the `results.py` script.
