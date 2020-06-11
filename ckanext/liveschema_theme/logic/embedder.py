# Import libraries
import pandas as pd
import os
import shutil
import json
import numpy as np

import xlsxwriter

import subprocess32

# Library to sort the entities & relations
import locale
locale.setlocale(locale.LC_ALL, '')

import ckan.plugins.toolkit as toolkit

import cgi

# Function that generates the Knowledge Embeddings
def embedKnowledge(data_dict):

    # [TODO] Get Dataset CSV Resource url from id of resource

    # Set visibility of loading gear
    loading='src/ckanext-liveschema_theme/ckanext/liveschema_theme/fanstatic/loading.css' 
    loadingFile = open(loading, 'w')
    loadingFile.write(data_dict["loading"])
    loadingFile.close()

	# Name of folder for intermediate results
    path = "src/ckanext-liveschema_theme/ckanext/liveschema_theme/public/resources/" + data_dict["dataset_name"] + "/"
    # Create Directory if not already present
    if not os.path.isdir(path):
		os.makedirs(path)

    # Create the dataframe from the CSV file
    triples = pd.read_csv(data_dict["dataset_link"])

	# Name of the training file
    parsedTSV = path + data_dict["dataset_name"] + ".tsv"

    with open(parsedTSV, "w+") as train:
		# Iterate over every triples row
		for index, row in triples.iterrows():
			subj = str(row["Subject"])
			pred = str(row["Predicate"])
			obj = str(row["Object"]).replace('\r\n','\n').replace('\n', ' | ')
			train.write(subj + "\t" + pred + "\t" + obj + "\n") 	

    # Call function with python3 to execute real embedder
    out = subprocess32.call("python3 src/ckanext-liveschema_theme/ckanext/liveschema_theme/logic/knowledgeEmbedder.py " + data_dict["dataset_name"] + 
     " !" + data_dict["options"]["strModel"] + " !" + data_dict["options"]["embedding_dim"] + " !" + data_dict["options"]["normalization_of_entities"] + 
     " !" + data_dict["options"]["scoring_function"] + " !" + data_dict["options"]["margin_loss"] + " !" + data_dict["options"]["random_seed"] + 
     " !" + data_dict["options"]["num_epochs"] + " !" + data_dict["options"]["learning_rate"] + " !" + data_dict["options"]["batch_size"] + 
     " !" + data_dict["options"]["test_set_ratio"] + " !" + data_dict["options"]["filter_negative_triples"] + " !" + data_dict["options"]["maximum_number_of_hpo_iters"], shell=True)

    # Check if execution went well
    if(not out):
        # Name of the embedding Model
        embeddingModel = "trained_model.pkl"

        # Upload trained model
        upload = cgi.FieldStorage()
        upload.filename = embeddingModel
        upload.file = file(os.path.normpath(os.path.expanduser(path + embeddingModel)))
        data = {
            "id": data_dict["res_id_model"], 
            "format": "EMB",
            'url': embeddingModel, #'will-be-overwritten-automatically',
            'upload': upload
        }
        toolkit.get_action('resource_patch')(context = {'ignore_auth': True}, data_dict=data)

        # Name of the embedding
        embeddingName = data_dict["dataset_name"] + "_Emb_"+ data_dict["options"]["strModel"] +".xlsx"
        
        # Create a the excel file for the embedding
        embeddings = xlsxwriter.Workbook(path + embeddingName)
        # Add bold cell format
        bold = embeddings.add_format({'bold': True})


        # Retrieve Entities Embedding from json file
        with open(path + 'entities_to_embeddings.json') as entitiesE:
            entitiesEJSON = json.load(entitiesE)
        
        # Get all entities names from embeddings, sorted
        entitiesNames = sorted(entitiesEJSON.keys(), cmp=locale.strcoll)    

        # Create the sheet for the Entities embeddings
        entityEmb = embeddings.add_worksheet("Entities")
        # Create the sheet for the EntitiesToEntities relations
        entities = embeddings.add_worksheet("Entities To Entities")
        entities.write(0, 0, 'Entity|Entity', bold)  # Cell is bold
        index = 1
        # Iterate over the data and write it out row by row.
        for entity in entitiesNames:
            # Save Entity Embeddings
            entityEmb.write(0, index-1, entity, bold)
            entityEmb.write_column(1, index-1, list(entitiesEJSON[list(entitiesNames)[index-1]]))
            # Initialise Entities to Entities relations
            entities.write(index, 0, entity)
            entities.write(0, index, entity)
            index += 1

        # Iterate over every cell of the DataFrame
        for i in range(0, index-1):
            for j in range(i, index-1):
                # Work only with elements not on the diagonal and not already checked 
                if(i != j):
                    # Transform the embeddings into a numpy array
                    arrayI = np.array(entitiesEJSON[list(entitiesNames)[i]])
                    arrayJ = np.array(entitiesEJSON[list(entitiesNames)[j]])
                    # Compute the Euclidean norm between these 2 arrays
                    norm = np.linalg.norm(arrayI - arrayJ)
                    # Update both the combinations with the norm
                    entities.write(i+1, j+1, norm)
                    entities.write(j+1, i+1, norm)
                else:
                    entities.write(i+1, i+1, 0)


        # Retrieve Relations Embedding from json file
        with open(path + 'relations_to_embeddings.json') as relationsE:
            relationsEJSON = json.load(relationsE)
        
        # Get all relations names from embeddings, sorted
        relationsNames = sorted(relationsEJSON.keys(), cmp=locale.strcoll)

        # Create the sheet for the Relations embeddings
        relationEmb = embeddings.add_worksheet("Relations")
        # Create the sheet for the RelationsToRelations 
        relations = embeddings.add_worksheet("Relations to Relations")
        relations.write(0, 0, 'Relation|Relation', bold)  # Cell is bold
        index = 1
        # Iterate over the data and write it out row by row.
        for relation in relationsNames:
            # Save Relations Embeddings
            relationEmb.write(0, index-1, relation, bold)
            relationEmb.write_column(1, index-1, list(relationsEJSON[list(relationsNames)[index-1]]))
            # Initialise Relations to Relations relations
            relations.write(index, 0, relation)
            relations.write(0, index, relation)
            index += 1
            
        # Iterate over every cell of the DataFrame
        for i in range(0, index-1):
            for j in range(i, index-1):
                # Work only with elements not on the diagonal and not already checked
                if(i != j):
                    # Transform the embeddings into a numpy array
                    arrayI = np.array(relationsEJSON[list(relationsNames)[i]])
                    arrayJ = np.array(relationsEJSON[list(relationsNames)[j]])
                    # Compute the Euclidean norm between these 2 arrays
                    norm = np.linalg.norm(arrayI - arrayJ)
                    # Update both the combination with the norm
                    relations.write(i+1,j+1,norm)
                    relations.write(j+1,i+1,norm)
                else:
                    relations.write(i+1, i+1, 0)

        # Close the embeddings Excel file
        embeddings.close()
        
        # Upload the csv file to LiveSchema
        upload = cgi.FieldStorage()
        upload.filename = embeddingName
        upload.file = file(os.path.normpath(os.path.expanduser(path + embeddingName)))
        data = {
            "id": data_dict["res_id"], 
            "format": "EMB",
            'url': embeddingName, #'will-be-overwritten-automatically',
            'upload': upload
        }
        toolkit.get_action('resource_patch')(context = {'ignore_auth': True}, data_dict=data)

        # Add file to DataStore using DataPusher
        import ckanext.datapusher.logic.action as dpaction
        dpaction.datapusher_submit(context = {'ignore_auth': True}, data_dict={'resource_id': str(data_dict["res_id"])})

        # Create a Data Explorer view of the resource
        toolkit.get_action('resource_view_create')(context = {'ignore_auth': True}, data_dict={'resource_id': str(data_dict["res_id"]), 'title': "Data Explorer", 'view_type': "recline_view"})

    else: # If there has been a problem with the execution
	    # Remove temp resources
        toolkit.get_action('resource_delete')(context = {'ignore_auth': True}, data_dict = {'id': data_dict["res_id"]})
        toolkit.get_action('resource_delete')(context = {'ignore_auth': True}, data_dict = {'id': data_dict["res_id_model"]})
    
    # Get the final version of the package
    CKANpackage = toolkit.get_action('package_show')(
            data_dict={"id": data_dict["dataset_name"]})
    # Iterate over all the resources
    for resource in CKANpackage["resources"]:
        # Remove eventual temp resources left in case of error
        if resource["format"] == "temp" and (resource["resource_type"] == "Emb"):
            toolkit.get_action("resource_delete")(context={"ignore_auth": True},data_dict={"id":resource["id"]})

    # Remove intermediate results
    try:
        shutil.rmtree(path)
    except OSError as e:
        print("Error: %s : %s" % (path, e.strerror))

    # Remove visibility of loading gear
    if(os.path.isfile(loading)):
        os.remove(loading)