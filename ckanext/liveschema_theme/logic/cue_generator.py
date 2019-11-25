# Import libraries
import pandas as pd
import os
import requests

import ckan.plugins.toolkit as toolkit

import ckan.lib.helpers as helpers


# Function that generate the Cue file
def generateCue(data_dict):
    # Create the dataframe from the CSV file
    matrix = pd.read_csv(data_dict["dataset_link"])

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
    cue = pd.DataFrame(columns=["Class","Cue1", "Cue2", "Cue3", "Cue4", "Cue5", "Cue6"])

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
            cue5 = cue4 / data[column].sum()
            cue6 = 1 - cue5
            # Save the metrics of that Class
            cue.at[column[10:-5], 'Class'] = column[10:-5]
            cue.at[column[10:-5], 'Cue4'] = cue4
            cue.at[column[10:-5], 'Cue5'] = cue5
            cue.at[column[10:-5], 'Cue6'] = cue6

            # Create the new column for the Cues in the input DataFrame, and copy the values for every Element 
            index = data.columns.get_loc(column)
            className = column[0:-4] 
            tempColumn = data[column]
            data.insert(index, className + "_123", tempColumn)

    # Calculate the Knowledge metrics of the input
    cue4 = cue["Cue4"].sum()
    cue5 = cue4 / data["total_456"].sum()
    cue6 = 1 - cue5
    # Save the Knowledge metrics of the input
    cue.at["KNOWLEDGE", 'Class'] = "KNOWLEDGE"
    cue.at["KNOWLEDGE", 'Cue4'] = cue4
    cue.at["KNOWLEDGE", 'Cue5'] = cue5
    cue.at["KNOWLEDGE", 'Cue6'] = cue6

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
            cue2 = cue1 / data[column].sum()
            cue3 = 1 - cue2
            # Save the metrics of that Class
            cue.at[column[10:-5], 'Cue1'] = cue1
            cue.at[column[10:-5], 'Cue2'] = cue2
            cue.at[column[10:-5], 'Cue3'] = cue3

    # Calculate the Knowledge metrics of the input
    cue1 = cue["Cue1"].sum()
    cue2 = cue1 / data["total_123"].sum()
    cue3 = 1 - cue2
    # Save the Knowledge metrics of the input
    cue.at["KNOWLEDGE", 'Cue1'] = cue1
    cue.at["KNOWLEDGE", 'Cue2'] = cue2
    cue.at["KNOWLEDGE", 'Cue3'] = cue3
    
    # Parse the Cue data into the csv file
    cue.to_csv(os.path.normpath(os.path.expanduser("src/ckanext-liveschema_theme/ckanext/liveschema_theme/public/" + data_dict["dataset_name"]+"_Cue.csv")))

    # Get the link of LiveSchema
    CKAN = helpers.get_site_protocol_and_host()
    CKAN_URL = CKAN[0]+"://" + CKAN[1]

    # Set the admin key of LiveSchema
    CKAN_KEY = data_dict["apikey"]

    dataset = toolkit.get_action('package_show')(
        data_dict={"id": data_dict["dataset_name"]})

    # Iterate over every resource of the dataset
    for res in dataset["resources"]:
        # Check if they have the relative Cue matrix file
        if("resource_type" in res.keys() and res["resource_type"] == "Cue"):
            # Delete the current Cue matrix
            dataset = toolkit.get_action('resource_delete')(
                data_dict={"id": res["id"]})
            break

    # Add the description of the Cue metrics of the dataset
    description = "Cue metrics of the dataset"

    # Upload the csv file to LiveSchema
    requests.post(CKAN_URL+"/api/3/action/resource_create",
                data={"package_id": data_dict["dataset_name"], "format": "CUE", "name": data_dict["dataset_name"]+"_Cue.csv", "description": description, "resource_type": "Cue"},
                headers={"X-CKAN-API-Key": CKAN_KEY},
                files=[("upload", file("src/ckanext-liveschema_theme/ckanext/liveschema_theme/public/" + data_dict["dataset_name"]+"_Cue.csv"))])

    # Remove the temporary csv file from the server
    os.remove("src/ckanext-liveschema_theme/ckanext/liveschema_theme/public/" + data_dict["dataset_name"]+"_Cue.csv")