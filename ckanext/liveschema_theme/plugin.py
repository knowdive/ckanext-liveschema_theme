# encoding: utf-8
# Import libraries
import ckan.plugins as plugins

import ckan.plugins.toolkit as toolkit

from ckan.plugins import IRoutes, implements, SingletonPlugin
from ckan.config.routing import SubMapper

# Import the package for the update function from the logic folder
import ckanext.liveschema_theme.logic.updater
import ckanext.liveschema_theme.logic.auth
import ckanext.liveschema_theme.logic.action

# Get the biggest catalogs ordered by the number of contained datasets
def most_popular_catalogs():
    '''Return a sorted list of the catalogs with the most datasets.'''

    # Get a list of all the site's catalogs from CKAN, sorted by number of
    # datasets.
    catalogs = toolkit.get_action('organization_list')(
        data_dict={'sort': 'package_count desc', 'all_fields': True})

    # Truncate the list to the 5 most popular catalogs only.
    catalogs = catalogs[:5]

    # Return the list of catalogs
    return catalogs

# For the given dataset, get the link of the resource of the given format 
def format_selection(dataset, format):
    '''Return the link of the resource of the given format for the given dataset '''
    # Create the dummy variable that will eventually contain the link 
    resLink = ""

    datasetDict = toolkit.get_action('package_show')(
        data_dict={"id": dataset})
    # Iterate over every resource of the dataset
    for res in datasetDict["resources"]:
        # Check if they have the given format
        if(res["format"] == format):
            # Delete the older FCA matrix
            resLink = res["url"]

    # Return the list of datasets that have the relative csv file to return
    return resLink

# Get the list of datasets
def dataset_selection(resource_type):
    '''Return a list of the datasets with their requested resource_type.'''
    
    # Create the list of datasets
    dataSetSelection = list()
    # Use searchLimit and index in order to get all the datasets, overcoming the limit of 1000 rows
    searchLimit = True
    index = 0
    while(searchLimit):
        searchLimit = False
        # Get a list of 1000 datasets
        datasets = toolkit.get_action('package_search')(
            data_dict={"include_private": True, "start": index*1000, "rows": 1000})
        # Reset the index if the number of results reach the limit of rows
        if(len(datasets["results"]) == 1000):
            searchLimit = True
            index = index + 1
        # Iterate over every datasets
        for dataset in datasets["results"]:
            linkResource = ""
            # Iterate over every resource of the dataset
            for res in dataset["resources"]:
                # Check if they have the relative resource type
                if("resource_type" in res.keys() and res["resource_type"] == resource_type and "format" in res.keys() and res["format"] != "temp"): # [TODO] To be commented the temp part, after the switch to id 
                    # Get the link of the desired resouce type
                    linkResource = res["url"]
            # [TODO] Use id of resource to get also the temp that are going to get generated 
            # Append the dataset to the selection
            dataSetSelection.append({"name": dataset["name"], "link": linkResource, "title": dataset["title"] + " [" + dataset["organization"]["title"] + "]"})

    # Order the datasets
    dataSetSelection.sort(key = lambda i: (i['title']))
    # Return the list of datasets that have the relative csv file to return
    return dataSetSelection


# Get the list of catalogs with their relative title
def catalog_selection():
    '''Return a list of the catalogs with their relative title.'''

    # Get a list of all the catalogs
    catalogs = toolkit.get_action('organization_list')(
        data_dict={})

    # Create the list of catalogs with their relative title
    catalogsSelection = list()

    # Iterate over every catalogs
    for name in catalogs:
        # Get the information about every catalogs
        catalog = toolkit.get_action('organization_show')(
            data_dict={"id": name})
        # Store the catalog with its title
        catalogsSelection.append({"name": name, "title": catalog["title"]})

    # Return the list of catalogs with their relative title
    return catalogsSelection


class LiveSchemaThemePlugin(plugins.SingletonPlugin):
    '''LiveSchemaThemePlugin'''
    # Declare that this class implements IConfigurer.
    plugins.implements(plugins.IConfigurer)

    def update_config(self, config):

        # Add this plugin's templates dir to CKAN's extra_template_paths, so
        # that CKAN will use this plugin's custom templates.
        # 'templates' is the path to the templates dir, relative to this
        # plugin.py file.
        toolkit.add_template_directory(config, 'templates')

        # Add this plugin's public dir to CKAN's extra_public_paths, so
        # that CKAN will use this plugin's custom static files.
        toolkit.add_public_directory(config, 'public')

        # Register this plugin's fanstatic directory with CKAN.
        # Here, 'fanstatic' is the path to the fanstatic directory
        # (relative to this plugin.py file), and 'liveschema_theme' is the name
        # that we'll use to refer to this fanstatic directory from CKAN
        # templates.
        toolkit.add_resource('fanstatic', 'liveschema_theme')

    # Declare that this plugin will implement ITemplateHelpers.
    plugins.implements(plugins.ITemplateHelpers)

    def get_helpers(self):
        '''Register the most_popular_catalogs() function above as a template
        helper function.'''
        # Template helper function names should begin with the name of the
        # extension they belong to, to avoid clashing with functions from
        # other extensions.
        return {'liveschema_theme_most_popular_catalogs': most_popular_catalogs, 
            'liveschema_theme_format_selection': format_selection, 
            'liveschema_theme_dataset_selection': dataset_selection, 
            'liveschema_theme_catalog_selection': catalog_selection }   

    # Edit the Routes of CKAN to add custom ones for the services
    implements(IRoutes, inherit=True)

    def before_map(self, map):

        # These named routes are used for custom dataset forms which will use
        # the names below based on the dataset.type ('dataset' is the default type)

        # Define the custom Controller for the routes of ckanext_LiveSchema_theme
        LiveSchemaController = 'ckanext.liveschema_theme.controller:LiveSchemaController'

        # Define the list of new routes to be added
        map.connect('ckanext_liveschema_theme_services', '/service', controller=LiveSchemaController, action='services')
        map.connect('ckanext_liveschema_theme_fca_generator', '/service/fca_generator', controller=LiveSchemaController, action='fca_generator')
        map.connect('ckanext_liveschema_theme_cue_generator', '/service/cue_generator', controller=LiveSchemaController, action='cue_generator')
        map.connect('ckanext_liveschema_theme_visualization_generator', '/service/visualization_generator', controller=LiveSchemaController, action='visualization_generator')
        map.connect('ckanext_liveschema_theme_query_catalog', '/service/query_catalog', controller=LiveSchemaController, action='query_catalog')
        map.connect('ckanext_liveschema_theme_fca_generator_id', '/service/fca_generator/{id}', controller=LiveSchemaController, action='fca_generator')
        map.connect('ckanext_liveschema_theme_cue_generator_id', '/service/cue_generator/{id}', controller=LiveSchemaController, action='cue_generator')
        map.connect('ckanext_liveschema_theme_visualization_generator_id', '/service/visualization_generator/{id}', controller=LiveSchemaController, action='visualization_generator')
        map.connect('ckanext_liveschema_theme_updater', '/service/updater', controller=LiveSchemaController, action='updater')
        map.connect('ckanext_liveschema_theme_uploader', '/service/uploader', controller=LiveSchemaController, action='uploader')
        map.connect('ckanext_liveschema_theme_fca', '/dataset/fca/{id}', controller=LiveSchemaController, action='fca', ckan_icon='table')
        map.connect('ckanext_liveschema_theme_cue', '/dataset/cue/{id}', controller=LiveSchemaController, action='cue', ckan_icon='info')
        map.connect('ckanext_liveschema_theme_visualization', '/dataset/visualization/{id}', controller=LiveSchemaController, action='visualization', ckan_icon='image')
        map.connect('ckanext_liveschema_theme_graph', '/dataset/graph/{id}', controller=LiveSchemaController, action='graph', ckan_icon='arrows-alt')
        map.connect('ckanext_liveschema_theme_query', '/dataset/query/{id}', controller=LiveSchemaController, action='query', ckan_icon='search')
        map.connect('ckanext_liveschema_theme_reset', '/dataset/reset/{id}', controller=LiveSchemaController, action='reset')
        map.connect('ckanext_liveschema_theme_contact', '/contact', controller=LiveSchemaController, action='contact')

        # Return the new configuration to the default handler of the routers
        return map

    # Add authorization functions for the services
    plugins.implements(plugins.IAuthFunctions)

    def get_auth_functions(self):
        return {
            'ckanext_liveschema_theme_services': ckanext.liveschema_theme.logic.auth.services,
            'ckanext_liveschema_theme_fca_generator': ckanext.liveschema_theme.logic.auth.fca_generator,
            'ckanext_liveschema_theme_cue_generator': ckanext.liveschema_theme.logic.auth.cue_generator,
            'ckanext_liveschema_theme_visualization_generator': ckanext.liveschema_theme.logic.auth.visualization_generator,
            'ckanext_liveschema_theme_updater': ckanext.liveschema_theme.logic.auth.updater,
            'ckanext_liveschema_theme_uploader': ckanext.liveschema_theme.logic.auth.uploader,
            'ckanext_liveschema_theme_reset': ckanext.liveschema_theme.logic.auth.reset
        }

    # Add functions for the services
    plugins.implements(plugins.IActions)

    def get_actions(self):
        action_functions = {
            'ckanext_liveschema_theme_fca_generator':
                ckanext.liveschema_theme.logic.action.fca_generator,
            'ckanext_liveschema_theme_cue_generator':
                ckanext.liveschema_theme.logic.action.cue_generator,
            'ckanext_liveschema_theme_visualization_generator':
                ckanext.liveschema_theme.logic.action.visualization_generator,
            'ckanext_liveschema_theme_updater':
                ckanext.liveschema_theme.logic.action.updater,
            'ckanext_liveschema_theme_uploader':
                ckanext.liveschema_theme.logic.action.uploader,
            'ckanext_liveschema_theme_query':
                ckanext.liveschema_theme.logic.action.query,
            'ckanext_liveschema_theme_visualization_lotus':
                ckanext.liveschema_theme.logic.action.visualization_lotus,
            'ckanext_liveschema_theme_reset':
                ckanext.liveschema_theme.logic.action.reset
        }
        return action_functions
