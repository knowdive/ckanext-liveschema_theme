# Import libraries
import pandas as pd
import os
import math

import ckan.plugins.toolkit as toolkit

import csv
from itertools import izip_longest

import cgi


# Function that generate the Visualization file
def generateVisualization(data_dict):
    # Get the dataset link
    dataset_link = data_dict["dataset_link"]
    # If it is not valid: FCA yet to be created at the time
    if not dataset_link:
        # Get the new link of the FCA
        datasetDict = toolkit.get_action('package_show')(
            data_dict={"id": data_dict["dataset_name"]})
        # Iterate over every resource of the dataset
        for res in datasetDict["resources"]:
            # Check if they have the given format
            if(res["format"] == "FCA"):
                # Delete the older FCA matrix
                dataset_link = res["url"]

    # Create the dataframe from the FCA file
    matrix = pd.read_csv(dataset_link)

    # Use a list to create the visualization file
    typeLists = list()
    # Iterate over every row of the matrix
    for index, row in matrix.iterrows():
        # List of tokens of a TypeTerm
        propertiesTokens = list()
        # Iterate over overy tokenized column of the matrix
        i = 0
        for column in matrix.columns[2:]:
            # If the row has a value, then add the token to the list of the TypeTerm
            if(row[column] and not math.isnan(row[column])):
                for j in range(int(row[column])):
                    propertiesTokens.append(str(column))
            i+=1

        #Add the term to the list with its tokens
        typeLists.append((str(row["TypeTerm"]) + " " +  " ".join(propertiesTokens)).split())

    # Create the vennFile from the typeList used to generate the Venn diagram
    with open(os.path.normpath(os.path.expanduser("src/ckanext-liveschema_theme/ckanext/liveschema_theme/public/" + data_dict["dataset_name"]+"_Visualization.csv")),"w+") as f:
        writer = csv.writer(f)
        for values in izip_longest(*typeLists):
            writer.writerow(values)

    # Upload the csv file to LiveSchema
    upload = cgi.FieldStorage()
    upload.filename = data_dict["dataset_name"]+"_Visualization.csv"
    upload.file = file("src/ckanext-liveschema_theme/ckanext/liveschema_theme/public/" + data_dict["dataset_name"]+"_Visualization.csv")
    data = {
        "id": data_dict["res_id"], 
        "format": "VIS",
        'url': data_dict["dataset_name"]+"_Visualization.csv", #'will-be-overwritten-automatically',
        'upload': upload
    }
    toolkit.get_action('resource_patch')(context = {'ignore_auth': True}, data_dict=data)

    # Add file to DataStore using DataPusher
    import ckanext.datapusher.logic.action as dpaction
    dpaction.datapusher_submit(context = {'ignore_auth': True}, data_dict={'resource_id': str(data_dict["res_id"])})
    
    # Create a Data Explorer view of the resource
    toolkit.get_action('resource_view_create')(context = {'ignore_auth': True}, data_dict={'resource_id': str(data_dict["res_id"]), 'title': "Data Explorer", 'view_type': "recline_view"})

    # Remove the temporary csv file from the server
    os.remove("src/ckanext-liveschema_theme/ckanext/liveschema_theme/public/" + data_dict["dataset_name"]+"_Visualization.csv")

    # Get the final version of the package
    CKANpackage = toolkit.get_action('package_show')(
            data_dict={"id": data_dict["dataset_name"]})
    # Iterate over all the resources
    for resource in CKANpackage["resources"]:
        # Remove eventual temp resources left in case of error
        if resource["format"] == "temp" and (resource["resource_type"] == "Visualization"):
            toolkit.get_action("resource_delete")(context={"ignore_auth": True}, data_dict={"id":resource["id"]})