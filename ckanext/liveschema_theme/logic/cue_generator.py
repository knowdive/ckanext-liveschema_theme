# Import libraries
import pandas as pd
import os

import ckan.plugins.toolkit as toolkit

import cgi

# Function that generate the Cue file
def generateCue(data_dict):

    # Set visibility of loading gear
    loading='src/ckanext-liveschema_theme/ckanext/liveschema_theme/fanstatic/loading.css' 
    loadingFile = open(loading, 'w')
    loadingFile.write(data_dict["loading"])
    loadingFile.close()

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

    # Generate the resulting DataFrame having as words the tokenized columns of the matrix, and a total of 0 for every row
    data = pd.DataFrame({"word": matrix.columns[6:], "total": 0})

    # Use a set to avoid creating duplicate Columns
    typeSet = set()
    # Iterate over every row of the matrix
    for index, row in matrix.iterrows():
        # Generate the name of the new column
        colName = "in class (" + str(row["TypeTerm"]) + ")"
        # Check if that column is already present on the DataFrame
        typeSetL = len(typeSet)
        typeSet.add(row["TypeTerm"])
        # If there weren't columns with that name
        if(typeSetL < len(typeSet)):
            # Create a new column of 0 for that name
            data[colName] = 0

        # Iterate over overy tokenized column of the matrix
        i = 0
        for column in matrix.columns[6:]:
            # If the row has a value, then upload the values of the DataFrame
            if(row[column]):
                data.at[i, colName] = data.at[i, colName] + row[column]
                data.at[i, "total"] = data.at[i, "total"] + row[column]
            i+=1

    # Create the DataFrame used to save the Cues
    cue = pd.DataFrame(columns=["eType","Cue_e", "Cue_er", "Cue_ec", "Cue_c", "Cue_cr", "Cue_cc"])

    # Iterate for every column present on data
    for column in data:
        # Rename the columns
        if "word" not in column:
            data.rename(index=str, columns={column: str(column+"_456")}, inplace= True)
            column += "_456"
        # Checks if the column identify a Class
        if("in class" in column):
            # Create the new column for the Cues in the input DataFrame, and calculate the values for every Element 
            index = data.columns.get_loc(column)
            className = "Cue(" + column[10:-5] + ")_456"
            tempColumn = data[column] / data["total_456"]
            data.insert(index, className, tempColumn)
            
            # Calculate the metrics of that Class
            cue4 = data[className].sum()
            cue5 = ( cue4  / data[column].sum()) if data[column].sum() != 0 else 0
            cue6 = 1 - cue5
            # Save the metrics of that Class
            cue.at[column[10:-5], 'eType'] = column[10:-5]
            cue.at[column[10:-5], 'Cue_c'] = cue4
            cue.at[column[10:-5], 'Cue_cr'] = cue5
            cue.at[column[10:-5], 'Cue_cc'] = cue6

            # Create the new column for the Cues in the input DataFrame, and copy the values for every Element 
            index = data.columns.get_loc(column)
            className = column[0:-4] 
            tempColumn = data[column]
            data.insert(index, className + "_123", tempColumn)

    # Calculate the Knowledge metrics of the input
    cue4 = cue["Cue_c"].sum()
    cue5 = (cue4 / data["total_456"].sum()) if data["total_456"].sum() != 0 else 0
    cue6 = 1 - cue5
    # Save the Knowledge metrics of the input
    cue.at["KNOWLEDGE", 'eType'] = "KNOWLEDGE"
    cue.at["KNOWLEDGE", 'Cue_c'] = cue4
    cue.at["KNOWLEDGE", 'Cue_cr'] = cue5
    cue.at["KNOWLEDGE", 'Cue_cc'] = cue6

    # Create the new column for the Cues in the input DataFrame, and copy the values from the original column
    index = data.columns.get_loc("total_456")
    className = "total_123"
    tempColumn = data["total_456"]
    data.insert(index, className, tempColumn)

    # Iterate for every row present on data, for every Element
    for index, row in data.iterrows():
        # For evert column that indicates a Name
        for column in data:
            # Check if the Name is present on that Element/row
            if(("in class" in column and "_456" in column) and row[column]): 
                # Format data for another kind of cue Analysis
                if(row[column] > 1):
                    data.at[index, "total_123"] = row["total_123"] - row[column] + 1 
                    row["total_123"] = row["total_123"] - row[column] + 1
                    data.at[index, column[0:-4] + "_123" ] = 1

    # Iterate for every column present on data
    for column in data:
        # Checks if the column identify a Class
        if(("in class" in column and "_123" in column)):
            # Create the new column for the Cue in the input DataFrame, and calculate the values for every Element 
            index = data.columns.get_loc(column) - 1
            className = "Cue(" + column[10:-5] + ")_123"
            tempColumn = data[column] / data["total_123"]
            data.insert(index, className, tempColumn)
            
            # Calculate the metrics of that Class
            cue1 = data[className].sum()
            cue2 = (cue1 / data[column].sum()) if data[column].sum() != 0 else 0
            cue3 = 1 - cue2
            # Save the metrics of that Class
            cue.at[column[10:-5], 'Cue_e'] = cue1
            cue.at[column[10:-5], 'Cue_er'] = cue2
            cue.at[column[10:-5], 'Cue_ec'] = cue3

    # Calculate the Knowledge metrics of the input
    cue1 = cue["Cue_e"].sum()
    cue2 = (cue1 / data["total_123"].sum()) if data["total_123"].sum() != 0 else 0
    cue3 = 1 - cue2
    # Save the Knowledge metrics of the input
    cue.at["KNOWLEDGE", 'Cue_e'] = cue1
    cue.at["KNOWLEDGE", 'Cue_er'] = cue2
    cue.at["KNOWLEDGE", 'Cue_ec'] = cue3
    
    # Parse the Cue data into the csv file
    cue.to_csv(os.path.normpath(os.path.expanduser("src/ckanext-liveschema_theme/ckanext/liveschema_theme/public/" + data_dict["dataset_name"]+"_Cue.csv")))

    # Upload the csv file to LiveSchema
    upload = cgi.FieldStorage()
    upload.filename = data_dict["dataset_name"]+"_Cue.csv"
    upload.file = file("src/ckanext-liveschema_theme/ckanext/liveschema_theme/public/" + data_dict["dataset_name"]+"_Cue.csv")
    data = {
        "id": data_dict["res_id"], 
        "format": "CUE",
        'url': data_dict["dataset_name"]+"_Cue.csv", #'will-be-overwritten-automatically',
        'upload': upload
    }
    toolkit.get_action('resource_patch')(context = {'ignore_auth': True}, data_dict=data)

    # Add file to DataStore using DataPusher
    import ckanext.datapusher.logic.action as dpaction
    dpaction.datapusher_submit(context = {'ignore_auth': True}, data_dict={'resource_id': str(data_dict["res_id"])})

    # Create a Data Explorer view of the resource
    toolkit.get_action('resource_view_create')(context = {'ignore_auth': True}, data_dict={'resource_id': str(data_dict["res_id"]), 'title': "Data Explorer", 'view_type': "recline_view"})

    # Remove the temporary csv file from the server
    os.remove("src/ckanext-liveschema_theme/ckanext/liveschema_theme/public/" + data_dict["dataset_name"]+"_Cue.csv")

    # Get the final version of the package
    CKANpackage = toolkit.get_action('package_show')(
            data_dict={"id": data_dict["dataset_name"]})
    # Iterate over all the resources
    for resource in CKANpackage["resources"]:
        # Remove eventual temp resources left in case of error
        if resource["format"] == "temp" and (resource["resource_type"] == "Cue"):
            toolkit.get_action("resource_delete")(context={"ignore_auth": True},data_dict={"id":resource["id"]})

    # Remove visibility of loading gear
    if(os.path.isfile(loading)):
        os.remove(loading)