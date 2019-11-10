# Import libraries
import ckan.plugins.toolkit as toolkit

# Import the package for the update function from the logic folder
import ckanext.liveschema_theme.logic.updater
import ckanext.liveschema_theme.logic.fca_generator

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