# Import libraries
import ckan.plugins.toolkit as toolkit

from rdflib import Graph
from rdflib.util import guess_format

# Import the package for the update function from the logic folder
import ckanext.liveschema_theme.logic.updater
import ckanext.liveschema_theme.logic.fca_generator
import ckanext.liveschema_theme.logic.cue_generator
import ckanext.liveschema_theme.logic.visualization_generator

# Get the function from toolkit
enqueue_job = toolkit.enqueue_job

# Define the action of updater of LiveSchema
def updater(context, data_dict):
    # Enqueue the script to be executed by the background worker
    enqueue_job(ckanext.liveschema_theme.logic.updater.updateLiveSchema, args=[data_dict], title="updateLiveSchema", queue=u'default', timeout=-1)

# Define the action of fca_generator of LiveSchema
def fca_generator(context, data_dict):
    # Enqueue the script to be executed by the background worker
    enqueue_job(ckanext.liveschema_theme.logic.fca_generator.generateFCA, args=[data_dict], title="generateFCA", queue=u'default', timeout=-1)

# Define the action of fca_generator of LiveSchema
def cue_generator(context, data_dict):
    # Enqueue the script to be executed by the background worker
    enqueue_job(ckanext.liveschema_theme.logic.cue_generator.generateCue, args=[data_dict], title="generateCue", queue=u'default', timeout=-1)

# Define the action of fca_generator of LiveSchema
def visualization_generator(context, data_dict):
    # Enqueue the script to be executed by the background worker
    enqueue_job(ckanext.liveschema_theme.logic.visualization_generator.generateVisualization, args=[data_dict], title="generateVisualization", queue=u'default', timeout=-1)

# Define the action of query of LiveSchema
def query(context, data_dict):

    #return "Work in Progress"
    N3Resource = data_dict["N3Resource"]
    query = data_dict["query"]
    # Try to create the graph to analyze the vocabulary
    try:
        g = Graph()
        result = g.parse(N3Resource["url"], format=guess_format("n3"), publicID=N3Resource["name"])

        qres = g.query(query)

        result = ""
        for row in qres:
            result = result + " -_- " + str(row)

        return result
    except Exception as e:  
        return "Exception: " +str(e)
