# Import libraries
import ckan.plugins.toolkit as toolkit
import ckan.logic as logic

import rdflib
from rdflib import Graph
from rdflib.util import guess_format

import pandas as pd
import os
import math
import requests

import ckan.plugins.toolkit as toolkit

import ckan.lib.helpers as helpers

import csv
from itertools import izip_longest

# Import the package for the update function from the logic folder
import ckanext.liveschema_theme.logic.updater
import ckanext.liveschema_theme.logic.embedder
import ckanext.liveschema_theme.logic.fca_generator
import ckanext.liveschema_theme.logic.cue_generator
import ckanext.liveschema_theme.logic.visualization_generator

# Get the function from toolkit
enqueue_job = toolkit.enqueue_job
# Get the function from logic
get_action = logic.get_action

# Define the action of updater of LiveSchema
def updater(context, data_dict):
    # Enqueue the script to be executed by the background worker
    enqueue_job(ckanext.liveschema_theme.logic.updater.updateLiveSchema, args=[data_dict], title="updateLiveSchema", queue=u'default', timeout=-1)

# Define the action of Upload Dataset of LiveSchema
def uploader(context, data_dict):
    # Enqueue the script to be executed by the background worker
    enqueue_job(ckanext.liveschema_theme.logic.updater.uploadDataset, args=[data_dict['id'], data_dict['package'], data_dict['filePath'], data_dict['data']], title="uploadPackage", queue=u'default', timeout=-1)

# Define the action of embedder of LiveSchema
def embedder(context, data_dict):
    # Enqueue the script to be executed by the background worker
    # [TODO] Pass filePath of resource to avoid 404 with private datasets
    enqueue_job(ckanext.liveschema_theme.logic.embedder.embedKnowledge, args=[data_dict], title="embedKnowledge", queue=u'default', timeout=-1)

# Define the action of fca_generator of LiveSchema
def fca_generator(context, data_dict):
    # Enqueue the script to be executed by the background worker
    # [TODO] Pass filePath of resource to avoid 404 with private datasets
    enqueue_job(ckanext.liveschema_theme.logic.fca_generator.generateFCA, args=[data_dict], title="generateFCA", queue=u'default', timeout=-1)

# Define the action of cue_generator of LiveSchema
def cue_generator(context, data_dict):
    # Enqueue the script to be executed by the background worker
    # [TODO] Pass filePath of resource to avoid 404 with private datasets
    enqueue_job(ckanext.liveschema_theme.logic.cue_generator.generateCue, args=[data_dict], title="generateCue", queue=u'default', timeout=-1)

# Define the action of visualization_generator of LiveSchema
def visualization_generator(context, data_dict):
    # Enqueue the script to be executed by the background worker
    # [TODO] Pass filePath of resource to avoid 404 with private datasets
    enqueue_job(ckanext.liveschema_theme.logic.visualization_generator.generateVisualization, args=[data_dict], title="generateVisualization", queue=u'default', timeout=-1)

# Define the action of reset resources of LiveSchema
def reset(context, data_dict):
    # Enqueue the script to be executed by the background worker
    # [TODO] Pass filePath of resource to avoid 404 with private datasets
    enqueue_job(ckanext.liveschema_theme.logic.updater.addResources, args=[data_dict['id'], data_dict['package']], title="resetResources", queue=u'default', timeout=-1)


# Define the action of query of LiveSchema
def query(context, data_dict):
    # Get the resource and query from the form
    TTL_Resource = data_dict["TTL_Resource"]
    query = data_dict["query"]
    try:
        # Try to create the graph to analyze the vocabulary
        g = Graph()
        result = g.parse(TTL_Resource["url"], format=guess_format("ttl"), publicID=TTL_Resource["name"])
        # Query the dataset
        qres = g.query(query)

        # Save the result of the query
        result = list()
        for row in qres:
            rowRes = list()
            for res in row:
                if(res):
                    rowRes.append(res.toPython())
            result.append(rowRes)
        # Return the result of the query
        return result
    except Exception as e:  
        # Return the exception
        return [["Exception: " +str(e)]]


# Define the action of KLotus of LiveSchema
def visualization_lotus(context, data_dict):
    # [TODO] To become a job and add it as a image view resource to LiveSchema
    
    # Create the dataframe from the FCA file
    data = pd.read_csv(data_dict["FCAResource"])

    # Create the DataFrame used to save the occurrences of the Types present on the Token row
    DF = pd.DataFrame(columns=["Token", "Types"])

    # Create the set used to check if new Types has to be added or if existing Types has to be updated
    tokens = set()
    # Iterate over every row of the matrix
    for index, row in data.iterrows():
        # Iterate over overy tokenized column of the matrix
        for column in data.columns[2:]:
            # If the row has a value, then add the token to the list of the TypeTerm
            if(row[column]):
                # Check if new column has to be added or if existing column has to be updated
                a = len(tokens)
                tokens.add(str(column))
                if(a < len(tokens)):
                    DF.at[str(column), "Token"] = column
                    DF.at[str(column), "Types"] = str(row["TypeTerm"])
                else:
                    types = str(DF.at[str(column), "Types"])
                    DF.at[str(column), "Types"] = types + " , " + str(row["TypeTerm"])

    # Create the DataFrame used to save the table used to identify common Tokens between Types
    DTF = pd.DataFrame(columns=["total", "Types", "number", "Tokens"])
    # Create the set used to check if new Types has to be added or if existing Types has to be updated
    set_ = set()
    # Iterate for every row present on DF, for every Token and the relative Types
    for index_, row in DF.iterrows():
        # Check if new Types has to be added or if existing Types has to be updated
        a = len(set_)
        set_.add(str(row["Types"]))
        if(a < len(set_)):
            # Create a new row on the DataFrame for that Types
            DTF.at[str(row["Types"]), "total"] = len(str(row["Types"]).split(","))
            DTF.at[str(row["Types"]), "Types"] = row["Types"]
            DTF.at[str(row["Types"]), "Tokens"] = str(row["Token"])
            DTF.at[str(row["Types"]), "number"] = 1
        else:
            # Update the row for that Types, adding the new Token
            elements = str(DTF.at[str(row["Types"]), "Tokens"])
            number = DTF.at[str(row["Types"]), "number"]
            DTF.at[str(row["Types"]), "Tokens"] = elements + " , " + str(row["Token"])
            DTF.at[str(row["Types"]), "number"] = number + 1

    DTF = DTF.sort_values(by='total', ascending=False)

    DTF = DTF.sort_values(by='number', ascending=False)

    # Select the most intersecting columns
    colSel = list()
    thres = 0
    maxx = 0 
    maxxTypes = ""
    for index_, row in DTF.iterrows():
        if( maxx < row["total"] ):
            maxx = row["total"] 
            maxxTypes = row["Types"]
        if(4 <= row["total"] <= 5 ):
            if(row["total"]*row["number"] > thres): # [TODO] To think about a more complex selection
                thres = row["total"]*row["number"]
                colSel = list()
                for a in  row["Types"].split(","):
                    colSel.append(a.strip())
    if(not len(colSel)):
        colSel = list()
        i = 0
        for a in maxxTypes.split(","):
            colSel.append(a.strip())
            i += 1
            if(i == 5):
                break

    # Load the Visualization data
    data = pd.read_csv(data_dict["visualizationResource"], dtype='unicode')

    # Make a direction to the temporary file (which is created for generating plots)
    dir_ = "src/ckanext-liveschema_theme/ckanext/liveschema_theme/public/"
    
    # Drop the columns not selected from the visualization file
    for column in data:
        if( column.strip() not in colSel):
            data.drop(column, axis=1, inplace=True)

    # Separate the selected columns in multiple target input files
    file_name = sep_file(dir_ + "resources/", data)

    # Generate the Venn Plot
    plot_Venn(dir_, file_name, data_dict["dataset_name"])

    # Delete the temporaty files
    del_file(dir_ + "resources/", data)

    # Boolean used to check if a new view has to be created
    KLotusView = True
    # Get the views related to the visualization resource, and check if the Knowledge Lotus is already present
    views = toolkit.get_action('resource_view_list')(context = {'ignore_auth': True}, data_dict={'id': str(data_dict["visId"])})
    for view in views:
        if(view["title"] == "Knowledge Lotus"):
            KLotusView = False
    # Create a KLotus view of the resource if there were none
    if(KLotusView):
        toolkit.get_action('resource_view_create')(context = {'ignore_auth': True}, data_dict={'resource_id': str(data_dict["visId"]), 'title': "Knowledge Lotus", 'view_type': "image_view", 'image_url': "/KLotus/" + data_dict["dataset_name"] + "_KLotus.png"})

#Separate a csv file into target input files
def sep_file(dir_, data):
    file_name =[]
    headers = data.columns.values.tolist()
    for i in range(len(headers)):
        file_content = data[headers[i]].dropna(axis=0,how='all')
        file_n = dir_ + headers[i]+".csv"
        file_content.to_csv(file_n,index=False)
        file_name.append(file_n)
    return file_name

#Delete the temporary inputs
def del_file(dir_, data):
    headers = data.columns.values.tolist()
    for i in range(len(headers)):
        file_n = dir_ + headers[i] + ".csv"
        if (os.path.exists(file_n)):
            os.remove(file_n)

#The Venn plot function
def plot_Venn(dir_, file_name, dataset_name):
    if 2<=len(file_name)<=5:
        a = os.system(r"intervene venn -i "+str(dir_ + "resources/")+"*.csv --output "+str(dir_ + "KLotus/")+" --type list --figtype png")
        os.rename(str(dir_ + "KLotus/Intervene_venn.png"), str(dir_ + "KLotus/" + dataset_name + "_KLotus.png"))
