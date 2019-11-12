# Import libraries
from pylons import config

import ckan.lib.base as base
from ckan.lib.base import BaseController

from ckan.plugins import toolkit
import ckan.model as model
import ckan.lib.helpers as helpers
import ckan.logic as logic

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
    def fca_generator(self):
        # If the page has to handle the form resulting from the service
        if request.method == 'POST' and "dataset" in request.params.keys():
            # Get the selected dataset
            dataset = request.params['dataset'].split(",")
            dataset_name = dataset[0]
            dataset_link = dataset[1]

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
            get_action('ckanext_liveschema_theme_fca_generator')(context, data_dict={"dataset_name": dataset_name ,"dataset_link": dataset_link, "strPredicates": strPredicates})

            # Go to the dataset page
            return redirect_to(controller='package', action='read',
                    id=dataset_name)

        # Render the page of the service
        return render('service/fca_generator.html')
    

    # Define the behaviour of the cue generator
    def cue_generator(self):
        # If the page has to handle the form resulting from the service
        if request.method == 'POST' and "dataset" in request.params.keys():
            # Get the selected dataset
            dataset = request.params['dataset']
            # Go to the dataset page
            return redirect_to(controller='package', action='read',
                    id=dataset)

        # Render the page of the service
        return render('service/cue_generator.html')

    # Define the behaviour of the updater service
    def updater(self):
        # Build the context using the information obtained by session and user
        context = {'model': model, 'session': model.Session,
                   'user': c.user or c.author}


        # If the page has to handle the form resulting from the service
        if request.method == 'POST' and "catalogs" in request.params.keys():
            # Check if the user has the access to this page
            try:
                check_access('ckanext_liveschema_theme_fca_generator', context, data_dict={})
            # Otherwise abort with NotAuthorized message
            except NotAuthorized:
                abort(401, _('User not authorized to view page'))

            catalogsSelection = list()

            for key, value in request.params.iteritems():
                catalogsSelection.append(value)
            
            # Execute the update action
            get_action('ckanext_liveschema_theme_updater')(context, data_dict={"catalogsSelection": catalogsSelection})

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

        # Define the data_dict to pass to the package_show action
        data_dict = {'id': id}
        # Declare link variable to be obtained 
        link = ''

        # Try to access the information
        try:
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
