# Import libraries
import ckan.plugins.toolkit as toolkit
import ckan.logic as logic

import rdflib
from rdflib import Graph
from rdflib.util import guess_format

# Import the package for the update function from the logic folder
import ckanext.liveschema_theme.logic.updater
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

# Define the action of fca_generator of LiveSchema
def fca_generator(context, data_dict):
    # Enqueue the script to be executed by the background worker
    #resource_patch
    enqueue_job(ckanext.liveschema_theme.logic.fca_generator.generateFCA, args=[data_dict], title="generateFCA", queue=u'default', timeout=-1)

# Define the action of cue_generator of LiveSchema
def cue_generator(context, data_dict):
    # Enqueue the script to be executed by the background worker
    enqueue_job(ckanext.liveschema_theme.logic.cue_generator.generateCue, args=[data_dict], title="generateCue", queue=u'default', timeout=-1)

# Define the action of visualization_generator of LiveSchema
def visualization_generator(context, data_dict):
    # Enqueue the script to be executed by the background worker
    enqueue_job(ckanext.liveschema_theme.logic.visualization_generator.generateVisualization, args=[data_dict], title="generateVisualization", queue=u'default', timeout=-1)

# Define the action of reset resources of LiveSchema
def reset(context, data_dict):
    # Enqueue the script to be executed by the background worker
    enqueue_job(ckanext.liveschema_theme.logic.updater.addResources, args=[data_dict['id'] ,data_dict['apikey'], data_dict['package']], title="resetResources", queue=u'default', timeout=-1)


# Define the action of query of LiveSchema
def query(context, data_dict):
    # Get the resource and query from the form
    N3Resource = data_dict["N3Resource"]
    query = data_dict["query"]
    try:
        # Try to create the graph to analyze the vocabulary
        g = Graph()
        result = g.parse(N3Resource["url"], format=guess_format("n3"), publicID=N3Resource["name"])
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