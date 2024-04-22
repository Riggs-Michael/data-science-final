# University of Arkansas at Little Rock - IFSC 7370: Data Science and Technologies - Michael Riggs

## About

This is the code repository for the research paper "_Comparative Analysis of Relative Toxicity Levels Across
Skill Brackets in Dota 2_," which is the final project for the spring 2024 semester of IFSC 7370 by Michael Riggs.

## Setup

It's recommended to use a virtual environment with a Python 3.8 interpreter for this project, so as to not clutter
your development machine with Python packages. To install the requirements for the scripts, after activating your
virtual environment, simply run `pip install -r requirements.txt` to install all necessary Python packages.
Additionally, it will be necessary to create a local .env file for configuration. The scripts are written with
default values included, however the defaults will be much more restrictive than if you configure a .env file.

### Environment variables
The following environment variables should be set in the .env file:
- OPEN_DOTA_API_KEY
  - This is the key for use with the OpenDota Web API, and will allow data fetching to go at a much higher rate
- MAX_CALLS_PER_RUN
  - The maximum number of total calls to the OpenDota Web API that the fetch script will make in a single run
- MAX_PARSED_ID_CALLS_PER_RUN
  - The maximum number of calls to fetch new parsed match ids that the fetch script will make in a single run
- OPENAI_API_KEY
  - This is the key for use with OpenAI's Web API. It is required to run the Toxicity Labeler script

## Data

The results of my running the DataFetcher and ToxicityLabeler script are uploaded to this repo as a means to
reproduce the analysis portion of this project. There is a compressed folder (parsed_match_ids.zip) that contains
a csv of match ids that correspond to matches OpenDota has already parsed. Extracting this csv to the root of
the project directory is advised if you would like to fetch different matches for analysis, as reconstructing
this will take a significant number of calls to the OpenDota api.

Additionally, there are several csvs titled as <skill bracket name>_match_transcripts.csv which contain the raw
match chat logs fetched from OpenDota. These have been fed to OpenAI's gpt-4-turbo model for labeling, and the
results saved in csvs titled as labeled_<skill bracket name>_match_transcripts.csv

## Analysis outputs

Lastly, the outputs of the DataProcessor script have been uploaded as well. They include pngs titled as
<skill bracket name>_toxicity_distribution.png and give a graphical representation of the distribution
of toxicity levels in the corresponding skill bracket, as labeled by OpenAI's gpt-4-turbo model. There is also
a boxplot titled toxicity_boxplot.png which contains a boxplot of each bracket together for visual comparison.
Finally, there is a csv titled toxicity_stats.csv which includes the mean, standard deviation, and median
toxicity levels for each bracket, as well as the number of matches which were dropped due to the model's
inability to label them, and the number of matches which were adjusted from being unlabeled to manually
labeled as No Toxicity because they had no chat logs.