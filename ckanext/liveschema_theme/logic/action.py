# Import libraries
import ckan.plugins.toolkit as toolkit

# Import the package for the update function from the logic folder
import ckanext.liveschema_theme.logic.updater

# Get the function from toolkit
enqueue_job = toolkit.enqueue_job

# Define the action of update of LiveSchema
def update(context, data_dict):
    # Enqueue the script to be executed by the background worker
    enqueue_job(ckanext.liveschema_theme.logic.updater.updateLiveSchema, args=[], title="LiveSchemaUpdater", queue=u'default', timeout=-1)