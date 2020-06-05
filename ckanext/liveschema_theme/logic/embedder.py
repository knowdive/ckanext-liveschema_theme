# Import libraries
import pandas as pd
import os
import shutil
import json

import ckan.plugins.toolkit as toolkit

import cgi

# Function that generates the Knowledge Embeddings
def embedKnowledge(data_dict):

    # [TODO] Get Dataset CSV Resource url from id of resource

	# Name of folder for intermediate results
    path = "src/ckanext-liveschema_theme/ckanext/liveschema_theme/public/resources/" + data_dict["dataset_name"] + "/"
    # Create Directory if not already present
    if not os.path.isdir(path):
		os.makedirs(path)

    # Create the dataframe from the CSV file
    triples = pd.read_csv(data_dict["dataset_link"])

	# Name of the training file
    parsedTSV = path + "/" + data_dict["dataset_name"] + ".tsv"

    with open(parsedTSV, "w+") as train:
		# Iterate over every triples row
		for index, row in triples.iterrows():
			train.write(str(row["Subject"])+"\t"+str(row["Predicate"])+"\t"+str(row["Object"])+"\n") 	

	# Remove temp resource
    toolkit.get_action('resource_delete')(context = {'ignore_auth': True}, data_dict = {'id': data_dict["res_id"]})

    # Remove intermediate results
    try:
        shutil.rmtree(path)
    except OSError as e:
        print("Error: %s : %s" % (path, e.strerror))