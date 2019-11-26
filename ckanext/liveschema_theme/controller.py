# Import libraries
from pylons import config

import ckan.lib.base as base
from ckan.lib.base import BaseController

from ckan.plugins import toolkit
import ckan.model as model
import ckan.lib.helpers as helpers
import ckan.logic as logic

import pandas as pd

# Get the variables and functions from toolkit
c = toolkit.c
_ = toolkit._
request = toolkit.request
redirect_to = toolkit.redirect_to
enqueue_job = toolkit.enqueue_job
abort = toolkit.abort
# Get the function from base
render = base.render
# Get the functions from logic
check_access = logic.check_access
get_action = logic.get_action
# Get the error from logic
NotAuthorized = logic.NotAuthorized
NotFound = logic.NotFound
ValidationError = logic.ValidationError


# Base Controller to handle the new routes for the services of LiveSchema
class LiveSchemaController(BaseController):

    # Define the behaviour of the index of services
    def index(self):
        # Build the context using the information obtained by session and user
        context = {'model': model, 'session': model.Session,
                   'user': c.user or c.author}
        # Check if the user has the access to this page
        try:
            check_access('ckanext_liveschema_theme_services', context, {})
        # Otherwise abort with NotAuthorized message
        except NotAuthorized:
            abort(401, _('User not authorized to view page'))
        # Render the page desired
        return render('service/services.html')

    # Define the behaviour of the fca generator
    def fca_generator(self, id = ""):
        # If the page has to handle the form resulting from the service
        if request.method == 'POST' and "dataset" in request.params.keys():
            # Get the selected dataset
            dataset = request.params['dataset'].split(",")
            dataset_name = dataset[0]
            dataset_link = dataset[1]
            
            # If the dataset does not have the required resource
            if not dataset_link:
                # Redirect to the dataset main page
                return redirect_to(controller='package', action='read',
                    id=dataset_name)

            strPredicates = request.params.get('strPredicates', " ")

            # Build the context using the information obtained by session and user
            context = {'model': model, 'session': model.Session,
                       'user': c.user or c.author}

            # Check if the user has the access to this page
            try:
                check_access('ckanext_liveschema_theme_fca_generator', context, data_dict={})
            # Otherwise abort with NotAuthorized message
            except NotAuthorized:
                abort(401, _('User not authorized to view page'))

            # Execute the update action
            get_action('ckanext_liveschema_theme_fca_generator')(context, data_dict={"dataset_name": dataset_name ,"dataset_link": dataset_link, "strPredicates": strPredicates, 'apikey': c.userobj.apikey})

            # Go to the dataset page
            LiveSchemaController = 'ckanext.liveschema_theme.controller:LiveSchemaController'
            return redirect_to(controller=LiveSchemaController, action='fca',
                    id=dataset_name)

        # Render the page of the service
        return render('service/fca_generator.html',
                      {'id': id})

    # Define the behaviour of the cue generator
    def cue_generator(self, id = ""):
        # If the page has to handle the form resulting from the service
        if request.method == 'POST' and "dataset" in request.params.keys():
            # Get the selected dataset
            dataset = request.params['dataset'].split(",")
            dataset_name = dataset[0]
            dataset_link = dataset[1]

            # If the dataset does not have the required resource
            if not dataset_link:
                # Redirect to the page for the generation of that resurce
                LiveSchemaController = 'ckanext.liveschema_theme.controller:LiveSchemaController'
                return redirect_to(controller=LiveSchemaController, action='fca_generator',
                    id=dataset_name)

            # Build the context using the information obtained by session and user
            context = {'model': model, 'session': model.Session,
                       'user': c.user or c.author}

            # Check if the user has the access to this page
            try:
                check_access('ckanext_liveschema_theme_cue_generator', context, data_dict={})
            # Otherwise abort with NotAuthorized message
            except NotAuthorized:
                abort(401, _('User not authorized to view page'))

            # Execute the update action
            get_action('ckanext_liveschema_theme_cue_generator')(context, data_dict={"dataset_name": dataset_name ,"dataset_link": dataset_link, 'apikey': c.userobj.apikey})

            # Go to the dataset page
            LiveSchemaController = 'ckanext.liveschema_theme.controller:LiveSchemaController'
            return redirect_to(controller=LiveSchemaController, action='cue',
                    id=dataset_name)

        # Render the page of the service
        return render('service/cue_generator.html',
                      {'id': id})


    # Define the behaviour of the visualization generator
    def visualization_generator(self, id = ""):
        # If the page has to handle the form resulting from the service
        if request.method == 'POST' and "dataset" in request.params.keys():
            # Get the selected dataset
            dataset = request.params['dataset'].split(",")
            dataset_name = dataset[0]
            dataset_link = dataset[1]

            # If the dataset does not have the required resource
            if not dataset_link:
                # Redirect to the page for the generation of that resurce
                LiveSchemaController = 'ckanext.liveschema_theme.controller:LiveSchemaController'
                return redirect_to(controller=LiveSchemaController, action='fca_generator',
                    id=dataset_name)

            # Build the context using the information obtained by session and user
            context = {'model': model, 'session': model.Session,
                       'user': c.user or c.author}

            # Check if the user has the access to this page
            try:
                check_access('ckanext_liveschema_theme_visualization_generator', context, data_dict={})
            # Otherwise abort with NotAuthorized message
            except NotAuthorized:
                abort(401, _('User not authorized to view page'))

            # Execute the update action
            get_action('ckanext_liveschema_theme_visualization_generator')(context, data_dict={"dataset_name": dataset_name ,"dataset_link": dataset_link, 'apikey': c.userobj.apikey})

            # Go to the dataset page
            LiveSchemaController = 'ckanext.liveschema_theme.controller:LiveSchemaController'
            return redirect_to(controller=LiveSchemaController, action='visualization',
                    id=dataset_name)

        # Render the page of the service
        return render('service/visualization_generator.html',
                      {'id': id})

    # Define the behaviour of the updater service
    def updater(self):
        # Build the context using the information obtained by session and user
        context = {'model': model, 'session': model.Session,
                   'user': c.user or c.author}

        # If the page has to handle the form resulting from the service
        if request.method == 'POST':
            # Check if the user has the access to this page
            try:
                check_access('ckanext_liveschema_theme_fca_generator', context, data_dict={})
            # Otherwise abort with NotAuthorized message
            except NotAuthorized:
                abort(401, _('User not authorized to view page'))

            # List of catalogs to update
            catalogsSelection = list()
            # Add the chosen catalogs obtained by the form
            if "catalogs" in request.params.keys():
                for key, value in request.params.iteritems():
                    catalogsSelection.append(value)
            
            # Execute the update action
            get_action('ckanext_liveschema_theme_updater')(context, data_dict={"catalogsSelection": catalogsSelection, 'apikey': c.userobj.apikey})

            # Redirect to the index
            return redirect_to("../")

        # Check if the user has the access to this page
        try:
            check_access('ckanext_liveschema_theme_updater', context, {})
        # Otherwise abort with NotAuthorized message
        except NotAuthorized:
            abort(401, _('User not authorized to view page'))

        # Render the page of the service
        return render('service/updater.html')
    
    # Define the behaviour of the graph visualization tool
    def graph(self, id):
        # Build the context using the information obtained by session and user
        context = {'model': model, 'session': model.Session,
                   'user': c.user, 'for_view': True,
                   'auth_user_obj': c.userobj}

        # Declare link variable to be obtained 
        link = ''

        # Try to access the information
        try:
            # Define the data_dict to pass to the package_show action
            data_dict = {'id': id}
            # get the information about the desired package
            c.pkg_dict = get_action('package_show')(context, data_dict)

            # Get the dataset type of the dataset
            dataset_type = c.pkg_dict['type'] or 'dataset'

            # Set the link for the information
            #[TODO] Once deployed, link should have the url of the LiveSchema's relative resource instead of the url
            link = c.pkg_dict['url']
        # Otherwise return the relative error codes
        except NotFound:
            abort(404, _('Dataset not found'))
        except NotAuthorized:
            abort(403, _('Unauthorized to read dataset %s') % id)

        # Render the page of the service
        return render('package/graph.html',
                      {'dataset_type': dataset_type, 'link': link})
   
    # Define the behaviour of the graph visualization tool
    def fca(self, id):
        # Build the context using the information obtained by session and user
        context = {'model': model, 'session': model.Session,
                   'user': c.user, 'for_view': True,
                   'auth_user_obj': c.userobj}

        FCAList = list()
        # Try to access the information
        try:
            # Define the data_dict to pass to the package_show action
            data_dict = {'id': id, 'include_tracking': True}
            # get the information about the desired package
            c.pkg_dict = get_action('package_show')(context, data_dict)

            # Get the dataset type of the dataset
            dataset_type = c.pkg_dict['type'] or 'dataset'

            for res in c.pkg_dict['resources']:
                if "resource_type" in res.keys() and res["resource_type"] == "FCA":
                    FCAList.append(res)

        # Otherwise return the relative error codes
        except NotFound:
            abort(404, _('Dataset not found'))
        except NotAuthorized:
            abort(403, _('Unauthorized to read dataset %s') % id)

        # Render the page of the service
        return render('package/fca.html',
                      {'dataset_type': dataset_type, 'FCAList': FCAList, 'pkg' : c.pkg_dict}) 


    # Define the behaviour of the graph visualization tool
    def cue(self, id):
        # Build the context using the information obtained by session and user
        context = {'model': model, 'session': model.Session,
                   'user': c.user, 'for_view': True,
                   'auth_user_obj': c.userobj}

        # Resource to eventually show on the web page
        cueResource = ""
        termList = list()
        Cue1List = list() 
        Cue2List = list() 
        Cue3List = list() 
        Cue4List = list() 
        Cue5List = list() 
        Cue6List = list() 
        # Try to access the information
        try:
            # Define the data_dict to pass to the package_show action
            data_dict = {'id': id, 'include_tracking': True}
            # get the information about the desired package
            c.pkg_dict = get_action('package_show')(context, data_dict)

            # Get the dataset type of the dataset
            dataset_type = c.pkg_dict['type'] or 'dataset'

            for res in c.pkg_dict['resources']:
                if "resource_type" in res.keys() and res["resource_type"] == "Cue":
                    cueResource = res

                    CueMatrix = pd.read_csv(res["url"])

                    termList = CueMatrix["Class"]
                    Cue1List = CueMatrix["Cue1"]
                    Cue2List = CueMatrix["Cue2"]
                    Cue3List = CueMatrix["Cue3"]
                    Cue4List = CueMatrix["Cue4"]
                    Cue5List = CueMatrix["Cue5"]
                    Cue6List = CueMatrix["Cue6"]

        # Otherwise return the relative error codes
        except NotFound:
            abort(404, _('Dataset not found'))
        except NotAuthorized:
            abort(403, _('Unauthorized to read dataset %s') % id)

        # Render the page of the service
        return render('package/cue.html',
                      {'dataset_type': dataset_type, 'cueResource': cueResource, 'pkg' : c.pkg_dict, 'lenList': len(termList), 'termList': termList,
                      'Cue1List': Cue1List, 'Cue2List': Cue2List, 'Cue3List': Cue3List, 'Cue4List': Cue4List, 'Cue5List': Cue5List, 'Cue6List': Cue6List})     

    # Define the behaviour of the graph visualization tool
    def visualization(self, id):
        # Build the context using the information obtained by session and user
        context = {'model': model, 'session': model.Session,
                   'user': c.user, 'for_view': True,
                   'auth_user_obj': c.userobj}

        # Resource to eventually show on the web page
        visualizationResource = ""
        # Try to access the information
        try:
            # Define the data_dict to pass to the package_show action
            data_dict = {'id': id, 'include_tracking': True}
            # get the information about the desired package
            c.pkg_dict = get_action('package_show')(context, data_dict)

            # Get the dataset type of the dataset
            dataset_type = c.pkg_dict['type'] or 'dataset'

            for res in c.pkg_dict['resources']:
                if "resource_type" in res.keys() and res["resource_type"] == "Visualization":
                    visualizationResource = res

        # Otherwise return the relative error codes
        except NotFound:
            abort(404, _('Dataset not found'))
        except NotAuthorized:
            abort(403, _('Unauthorized to read dataset %s') % id)

        if visualizationResource:
            # Render the page of the visualization page
            return render('package/visualization.html',
                        {'dataset_type': dataset_type, 'visualizationResource': visualizationResource, 'pkg' : c.pkg_dict}) 
        else:
            # Render the page of the no_visualization page
            return render('package/no_visualization.html',
                        {'dataset_type': dataset_type, 'pkg' : c.pkg_dict}) 



    # Define the behaviour of the graph visualization tool
    def query_catalog(self):
        # Build the context using the information obtained by session and user
        context = {'model': model, 'session': model.Session,
                   'user': c.user, 'for_view': True,
                   'auth_user_obj': c.userobj}

        # If the page has to handle the form resulting from the service
        if request.method == 'POST' and "query" in request.params.keys():
            # Get the given query
            query = request.params['query']

            # Execute the query action
            result = list()
            if query:

                CKAN = helpers.get_site_protocol_and_host()
                CKAN_URL = CKAN[0]+"://" + CKAN[1]
                result = get_action('ckanext_liveschema_theme_query')(context, data_dict={'N3Resource': {'name': "Catalog", 'url': CKAN_URL+"/catalog.n3"}, "query": query})

            # Go to the dataset page
            return render('service/query_catalog.html',
                        {'query': query,  'result': result, 'number': len(result), 'pkg' : c.pkg_dict}) 
        # Example query
        query = "PREFIX dcat:  <http://www.w3.org/ns/dcat#> \n" + \
                "# Get the title of all the Datasets of LiveSchema \n" + \
                "SELECT ?title \n" + \
                "WHERE { \n" + \
                "\t?vocab a dcat:Dataset . \n" + \
                "\t?vocab dct:title ?title. \n" + \
                "} ORDER BY ?title"
        # Render the page of the no_visualization page
        return render('service/query_catalog.html',
                    {'query': query, 'pkg' : c.pkg_dict}) 


    # Define the behaviour of the graph visualization tool
    def query(self, id):
        # Build the context using the information obtained by session and user
        context = {'model': model, 'session': model.Session,
                   'user': c.user, 'for_view': True,
                   'auth_user_obj': c.userobj}

        N3Resource = ""
        # Try to access the information
        try:
            # Define the data_dict to pass to the package_show action
            data_dict = {'id': id, 'include_tracking': True}
            # get the information about the desired package
            c.pkg_dict = get_action('package_show')(context, data_dict)

            # Get the dataset type of the dataset
            dataset_type = c.pkg_dict['type'] or 'dataset'

            for res in c.pkg_dict['resources']:
                if "resource_type" in res.keys() and res["resource_type"] == "Serialized n3":
                    N3Resource = res
        # Otherwise return the relative error codes
        except NotFound:
            abort(404, _('Dataset not found'))
        except NotAuthorized:
            abort(403, _('Unauthorized to read dataset %s') % id)

        # If the page has to handle the form resulting from the service
        if request.method == 'POST' and "query" in request.params.keys():
            # Get the given query
            query = request.params['query']

            # Execute the query action
            result = list()
            if query:
                result = get_action('ckanext_liveschema_theme_query')(context, data_dict={'N3Resource': N3Resource, "query": query})

            # Go to the dataset page
            return render('package/query.html',
                        {'dataset_type': dataset_type, 'N3Resource': N3Resource, 'query': query, 'result': result, 'number': len(result), 'pkg' : c.pkg_dict}) 
        query = "# Get all the triples of the dataset\n" + \
                "SELECT ?Subject ?Predicate ?Object\n" + \
                "WHERE {\n" + \
                "\t?Subject ?Predicate ?Object\n" + \
                "}\n"
        # Render the page of the no_visualization page
        return render('package/query.html',
                    {'dataset_type': dataset_type, 'N3Resource': N3Resource, 'query': query, 'pkg': c.pkg_dict}) 
