# Import libraries
import pandas as pd
import os
import math
import requests

import ckan.plugins.toolkit as toolkit

import ckan.lib.helpers as helpers

import csv
from itertools import izip_longest


# Function that generate the Cue file
def generateVisualization(data_dict):
    # Create the dataframe from the CSV file
    matrix = pd.read_csv(data_dict["dataset_link"])
    
    # Create the DataFrame used to save the occurrences of the Names present on the Element row
    DF = pd.DataFrame(columns=["Element", "Names"])

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
        
        # Save the correlation between Element and Names
        SDF = DF.append({"Element": str(row["TypeTerm"]), "Names": propertiesTokens}, ignore_index=True)

        #Add the term to the list with its tokens
        typeLists.append((str(row["TypeTerm"]) + " " +  " ".join(propertiesTokens)).split())

    # Create the vennFile from the typeList used to generate the Venn diagram
    with open(os.path.normpath(os.path.expanduser("src/ckanext-liveschema_theme/ckanext/liveschema_theme/public/" + data_dict["dataset_name"]+"_Visualization.csv")),"w+") as f:
        writer = csv.writer(f)
        for values in izip_longest(*typeLists):
            writer.writerow(values)

    # Get the link of LiveSchema
    CKAN = helpers.get_site_protocol_and_host()
    CKAN_URL = CKAN[0]+"://" + CKAN[1]

    # Set the admin key of LiveSchema
    CKAN_KEY = data_dict["apikey"]
    
    # Upload the csv file to LiveSchema
    requests.post(CKAN_URL+"/api/3/action/resource_patch",
                data={"id": data_dict["res_id"], "format": "VIS"},
                headers={"X-CKAN-API-Key": CKAN_KEY},
                files=[("upload", file("src/ckanext-liveschema_theme/ckanext/liveschema_theme/public/" + data_dict["dataset_name"]+"_Visualization.csv"))])


    # Create the DataFrame used to save the table used to identify common Elements between Names
    DTF = pd.DataFrame(columns=["total", "Names", "number", "Elements"])
    # Create the set used to check if new Names has to be added or if existing Names has to be updated
    set_ = set()
    # Iterate for every row present on DF, for every Element and the relative Names
    for index_, row in DF.iterrows():
        # Check if new Names has to be added or if existing Names has to be updated
        a = len(set_)
        set_.add(str(row["Names"]))
        if(a < len(set_)):
            # Create a new row on the DataFrame for that Names
            DTF.at[str(row["Names"]), "total"] = len(row["Names"])
            DTF.at[str(row["Names"]), "Names"] = row["Names"]
            DTF.at[str(row["Names"]), "Elements"] = str(row["Element"])
            DTF.at[str(row["Names"]), "number"] = 1
        else:
            # Update the row for that Names, adding the new Element
            elements = str(DTF.at[str(row["Names"]), "Elements"])
            number = DTF.at[str(row["Names"]), "number"]
            DTF.at[str(row["Names"]), "Elements"] = elements + " , " + str(row["Element"])
            DTF.at[str(row["Names"]), "number"] = number + 1



    colSelection = list()

    DTF = DTF.sort_values("number")

    DTF.to_csv("corss.csv")

    # [TODO] To think about a more complex selection
    for index_, row in DTF.iterrows():
        if(row["total"] == 4):
            colSelection = row["Names"]

            ##loading data
            data = pd.read_csv("src/ckanext-liveschema_theme/ckanext/liveschema_theme/public/" + data_dict["dataset_name"]+"_Visualization.csv", dtype='unicode')
            #Make a direction to the temporary file(which is created for generating plots)
            dir_ = "src/ckanext-liveschema_theme/ckanext/liveschema_theme/public/resources/"


            for column in data:
                if( column not in colSelection):
                    data.drop(column, axis=1, inplace=True)


            file_name = sep_file(dir_,data)
            plot_Venn(file_name)

            #del_file(dir_,data)

            break

            

    # Remove the temporary csv file from the server
    os.remove("src/ckanext-liveschema_theme/ckanext/liveschema_theme/public/" + data_dict["dataset_name"]+"_Visualization.csv")

    # Get the final version of the package
    CKANpackage = toolkit.get_action('package_show')(
            data_dict={"id": data_dict["dataset_name"]})
    # Iterate over all the resources
    for resource in CKANpackage["resources"]:
        # Remove eventual temp resources left in case of error
        if resource["format"] == "temp" and (resource["resource_type"] == "Visualization"):
            toolkit.get_action("resource_delete")(data_dict={"id":resource["id"]})


#Separate a csv file into target input files
def sep_file(dir_, data):
    file_name =[]
    for column in data:
        file_content = data[column].dropna(axis=0,how='all')
        file_n = dir_ + column+".csv"
        file_content.to_csv(os.path.normpath(os.path.expanduser(file_n)))
        file_name.append(file_n)
    return file_name

#Delete the temporary inputs
def del_file(dir_,data):
    for column in data:
        file_n = dir_ + column + ".csv"
        if (os.path.exists(file_n)):
            os.remove(file_n)

#The Venn plot function
def plot_Venn(file_name):
    if 2<=len(file_name)<=6:
        a = os.system(r"intervene venn -i "+str(dir)+"*.csv --output ~/results --type list --figtype png")

#The UpSet plot function
def plot_UpSet(file_name):
    if 2 <= len(file_name) <= 6:
        a = os.system(r"intervene upset -i data1/*.csv --output Results --type list --figtype png")

#The Pairwise plot function
def plot_Pairwise(file_name):
    if 2 <= len(file_name) <= 20:
        os.system(r"intervene pairwise -i data1/*.csv --output Results --type list --figtype png")


