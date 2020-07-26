# Import libraries
from pylons import config

from plugin import format_selection

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
    def services(self):
        # Build the context using the information obtained by session and user
        context = {'model': model, 'session': model.Session,
                   'user': c.user or c.author}
        # Check if the user has the access to this page
        try:
            check_access('ckanext_liveschema_theme_services', context=context, data_dict={})
        # Otherwise abort with NotAuthorized message
        except NotAuthorized:
            abort(401, _('User not authorized to view page'))
        # Render the page desired
        return render('service/services.html')

    # Define the behaviour of the embedder service
    def embedder(self, id=""):
        # Build the context using the information obtained by session and user
        context = {'model': model, 'session': model.Session,
                   'user': c.user or c.author}

        # Check if the user has the access to this page
        try:
            check_access('ckanext_liveschema_theme_embedder', context, {})
        # Otherwise abort with NotAuthorized message
        except NotAuthorized:
            abort(401, _('Anonymous users not authorized to access the Knowledge Embedder'))

        # If the page has to handle the form resulting from the service
        if request.method == 'POST' and "dataset" in request.params.keys() and request.params['dataset']:

            context['ignore_auth'] = True
            # Get the selected dataset
            dataset = request.params['dataset'].split(",")
            dataset_name = dataset[0]
            dataset_link = dataset[1]
            
            # If the dataset does not have the required resource
            if not dataset_link:
                # Redirect to the dataset main page
                #return redirect_to(controller='package', action='read', id=dataset_name)
                # Reset resources and go to the dataset page
                LiveSchemaController = 'ckanext.liveschema_theme.controller:LiveSchemaController'
                return redirect_to(controller=LiveSchemaController, action='reset',
                    id=dataset_name)
            
            # Get the strModel desired, TransE as standard
            strModel = request.params.get('strModel', "TransE")
            if(not strModel):
                strModel = "TransE"

            # Get the embedding_dim desired
            embedding_dim = request.params.get('embedding_dim', 64)
            if(not embedding_dim):
                embedding_dim = 64

            # Get the normalization_of_entities desired
            normalization_of_entities = request.params.get('normalization_of_entities', 2)
            if(not normalization_of_entities):
                normalization_of_entities = 2

            # Get the scoring_function desired
            scoring_function = request.params.get('scoring_function', 1)
            if(not scoring_function):
                scoring_function = 1

            # Get the margin_loss desired
            margin_loss = request.params.get('margin_loss', 1)
            if(not margin_loss):
                margin_loss = 1

            # Get the random_seed desired
            random_seed = request.params.get('random_seed', 2)
            if(not random_seed):
                random_seed = 1

            # Get the num_epochs desired
            num_epochs = request.params.get('num_epochs', 500)
            if(not num_epochs):
                num_epochs = 500

            # Get the learning_rate desired
            learning_rate = request.params.get('learning_rate', 0.001)
            if(not learning_rate):
                learning_rate = 0.001

            # Get the batch_size desired
            batch_size = request.params.get('batch_size', 32)
            if(not batch_size):
                batch_size = 32

            # Get the test_set_ratio desired
            test_set_ratio = request.params.get('test_set_ratio', 0.1)
            if(not test_set_ratio):
                test_set_ratio = 0.1

            # Get the filter_negative_triples desired
            filter_negative_triples = request.params.get('filter_negative_triples', True)
            if(not filter_negative_triples):
                filter_negative_triples = True

            # Get the maximum_number_of_hpo_iters desired
            maximum_number_of_hpo_iters = request.params.get('maximum_number_of_hpo_iters', 3)
            if(not maximum_number_of_hpo_iters):
                maximum_number_of_hpo_iters = 3

            options = {
                "strModel" : str(strModel),
                "embedding_dim" : str(embedding_dim),
                "normalization_of_entities" : str(normalization_of_entities),
                "scoring_function" : str(scoring_function),
                "margin_loss" : str(margin_loss),
                "random_seed" : str(random_seed),
                "num_epochs" : str(num_epochs),
                "learning_rate" : str(learning_rate),
                "batch_size" : str(batch_size),
                "test_set_ratio" : str(test_set_ratio),
                "filter_negative_triples" : str(filter_negative_triples),
                "maximum_number_of_hpo_iters" : str(maximum_number_of_hpo_iters)
            }

            # Add the description of the Embedding specifying the Model
            description = "Knowledge Embedding obtained with options:\n" + \
                          " - Model: " + str(strModel) + "\n" + \
                          " - embedding_dim: " + str(embedding_dim) + "\n" + \
                          " - normalization_of_entities: " + str(normalization_of_entities) + "\n" + \
                          " - scoring_function: " + str(scoring_function) + "\n" + \
                          " - margin_loss: " + str(margin_loss) + "\n" + \
                          " - random_seed: " + str(random_seed) + "\n" + \
                          " - num_epochs: " + str(num_epochs) + "\n" + \
                          " - learning_rate: " + str(learning_rate) + "\n" + \
                          " - batch_size: " + str(batch_size) + "\n" + \
                          " - test_set_ratio: " + str(test_set_ratio) + "\n" + \
                          " - filter_negative_triples: " + str(filter_negative_triples) + "\n" + \
                          " - maximum_number_of_hpo_iters: " + str(maximum_number_of_hpo_iters)

            dataset = toolkit.get_action('package_show')(
                data_dict={"id": dataset_name})

            # Set index to limit the resources up to 9
            i = dataset["num_resources"] - 9
            # Iterate over every resource of the dataset
            for res in dataset["resources"]:
                # Check if they have the relative Embedding file
                if(res["description"] == description or (i > 0 and "resource_type" in res.keys() and res["resource_type"] == "Emb")):
                    # Update the index
                    i -= 1
                    # Delete the older Embedding
                    dataset = toolkit.get_action('resource_delete')(context=context,data_dict={"id": res["id"]})
            
            # Create temp Model resource
            ModelResource = toolkit.get_action("resource_create")(context=context,
                data_dict={"package_id": dataset_name, "format": "temp", "name": dataset_name+"_Model_"+strModel+".pkl", "description": description, "resource_type": "Emb"})
    
            # Create temp Emb resource
            EmbResource = toolkit.get_action("resource_create")(context=context,
                data_dict={"package_id": dataset_name, "format": "temp", "name": dataset_name+"_Emb_"+strModel+".xlsx", "description": description, "resource_type": "Emb"})

            # Execute the embedder action
            get_action('ckanext_liveschema_theme_embedder')(context, data_dict={"res_id": EmbResource["id"], "res_id_model": ModelResource["id"], "dataset_name": dataset_name ,"dataset_link": dataset_link, "options": options, 'apikey': c.userobj.apikey, 'loading': "/dataset/embedding/" + dataset_name + "?GeneratingEmbedding"})
            # Go to the dataset page
            LiveSchemaController = 'ckanext.liveschema_theme.controller:LiveSchemaController'
            return redirect_to(controller=LiveSchemaController, action='embedding',
                    id=dataset_name)

        # Render the page of the service
        return render('service/embedder.html',
                      {'id': id})

    # Define the behaviour of the fca generator
    def fca_generator(self, id = ""):
        # Build the context using the information obtained by session and user
        context = {'model': model, 'session': model.Session,
                   'user': c.user or c.author}
        # Check if the user has the access to this page
        try:
            check_access('ckanext_liveschema_theme_fca_generator', context, {})
        # Otherwise abort with NotAuthorized message
        except NotAuthorized:
            abort(401, _('Anonymous users not authorized to access the FCA generator'))

        # If the page has to handle the form resulting from the service
        if request.method == 'POST' and "dataset" in request.params.keys() and request.params['dataset']:

            context['ignore_auth'] = True
            # Get the selected dataset
            dataset = request.params['dataset'].split(",")
            dataset_name = dataset[0]
            dataset_link = dataset[1]
            
            # If the dataset does not have the required resource
            if not dataset_link:
                # Redirect to the dataset main page
                #return redirect_to(controller='package', action='read', id=dataset_name)
                # Reset resources and go to the dataset page
                LiveSchemaController = 'ckanext.liveschema_theme.controller:LiveSchemaController'
                return redirect_to(controller=LiveSchemaController, action='reset',
                    id=dataset_name)

            strPredicates = request.params.get('strPredicates', " ")

            # Add the description of the FCA Matrix specifying the (eventual) set of predicates for the filtering process
            description = "FCA Matrix containing the information of"
            if(len(strPredicates.split()) == 0):
                description = description + " all the triples"
            else:
                strPredicates = ", ".join(strPredicates.split())
                description = description + " the filtered triples, which have the following predicates: " + strPredicates

            dataset = toolkit.get_action('package_show')(
                data_dict={"id": dataset_name})

            # Set index to limit the resources up to 9
            i = dataset["num_resources"] - 9
            # Iterate over every resource of the dataset
            for res in dataset["resources"]:
                # Check if they have the relative FCA matrix file
                if(res["description"] == description or (i > 0 and "resource_type" in res.keys() and res["resource_type"] == "FCA")):
                    # Update the index
                    i -= 1
                    # Delete the older FCA matrix
                    dataset = toolkit.get_action('resource_delete')(context=context,data_dict={"id": res["id"]})
                
            # Create temp FCA resource
            FCAResource = toolkit.get_action("resource_create")(context=context,
                data_dict={"package_id": dataset_name, "format": "temp", "name": dataset_name+"_FCA.csv", "description": description, "resource_type": "FCA"})

            # Execute the fca_generator action
            get_action('ckanext_liveschema_theme_fca_generator')(context, data_dict={"res_id": FCAResource["id"], "dataset_name": dataset_name ,"dataset_link": dataset_link, "strPredicates": strPredicates, 'apikey': c.userobj.apikey, 'loading': "/dataset/fca/" + dataset_name + "?Generating FCA"})

            # Go to the dataset page
            LiveSchemaController = 'ckanext.liveschema_theme.controller:LiveSchemaController'
            return redirect_to(controller=LiveSchemaController, action='fca',
                    id=dataset_name)

        # Render the page of the service, setting the relative alert
        alert = ""
        if(len(id.split("."))>1):
            alert = id.split(".")
            id = alert[0]
            alert = alert[1]
        return render('service/fca_generator.html',
                      {'id': id, "alert": alert})

    # Define the behaviour of the cue generator
    def cue_generator(self, id = ""):

        # Build the context using the information obtained by session and user
        context = {'model': model, 'session': model.Session,
                   'user': c.user or c.author}
        # Check if the user has the access to this page
        try:
            check_access('ckanext_liveschema_theme_cue_generator', context, {})
        # Otherwise abort with NotAuthorized message
        except NotAuthorized:
            abort(401, _('Anonymous users not authorized to access the Cue generator'))

        # If the page has to handle the form resulting from the service
        if request.method == 'POST' and "dataset" in request.params.keys() and request.params['dataset']:

            context['ignore_auth'] = True

            # Get the selected dataset
            dataset = request.params['dataset'].split(",")
            dataset_name = dataset[0]
            dataset_link = dataset[1]

            # If the dataset does not have the required FCA resource, we need to create it 
            if not dataset_link:
                # Get CSV file to 
                resCSV = format_selection(dataset_name, "CSV")
                # If there is no CSV resource
                if not resCSV: 
                    # Reset that dataset
                    LiveSchemaController = 'ckanext.liveschema_theme.controller:LiveSchemaController'
                    redirect_to(controller=LiveSchemaController, action='reset',
                        id=dataset_name)
                # Create temp FCA resource
                FCAResource = toolkit.get_action("resource_create")(context=context,
                    data_dict={"package_id": dataset_name, "format": "temp", "name": dataset_name+"_FCA.csv", "description": "FCA Matrix containing the information of all the triples", "resource_type": "FCA"})

                # [TODO] Remove dataset_link from the inputs
                # [TODO] Change also visualization and maybe also FCA
                # Execute the fca_generator action
                get_action('ckanext_liveschema_theme_fca_generator')(context, data_dict={"res_id": FCAResource["id"], "dataset_name": dataset_name ,"dataset_link": resCSV, "strPredicates": "", 'apikey': c.userobj.apikey, 'loading': "/dataset/fca/" + dataset_name + "?GeneratingFCA"})

            # Check if the user has the access to this page
            try:
                check_access('ckanext_liveschema_theme_cue_generator', context, data_dict={})
            # Otherwise abort with NotAuthorized message
            except NotAuthorized:
                abort(401, _('User not authorized to view page'))

            # Get the dataset information
            dataset = toolkit.get_action('package_show')(
                data_dict={"id": dataset_name})

            # Iterate over every resource of the dataset
            for res in dataset["resources"]:
                # Check if they have the relative Cue matrix file
                if("resource_type" in res.keys() and res["resource_type"] == "Cue"):
                    # Delete the current Cue matrix
                    dataset = toolkit.get_action('resource_delete')(context=context, data_dict={"id": res["id"]})
                    break

            # Create temp CUE resource
            CUEResource = toolkit.get_action("resource_create")(context=context, 
                data_dict={"package_id": dataset_name, "format": "temp", "name": dataset_name+"_Cue.csv", "description": "Cue metrics of the dataset", "resource_type": "Cue"})

            # Execute the Cue generator action
            get_action('ckanext_liveschema_theme_cue_generator')(context, data_dict={"res_id": CUEResource["id"], "dataset_name": dataset_name ,"dataset_link": dataset_link, 'apikey': c.userobj.apikey, 'loading': "/dataset/cue/" + dataset_name + "?GeneratingCue"})

            # Go to the dataset page
            LiveSchemaController = 'ckanext.liveschema_theme.controller:LiveSchemaController'
            return redirect_to(controller=LiveSchemaController, action='cue',
                    id=dataset_name)

        # Render the page of the service
        return render('service/cue_generator.html',
                      {'id': id})

    # Define the behaviour of the visualization generator
    def visualization_generator(self, id = ""):

        # Build the context using the information obtained by session and user
        context = {'model': model, 'session': model.Session,
                   'user': c.user or c.author}
        # Check if the user has the access to this page
        try:
            check_access('ckanext_liveschema_theme_visualization_generator', context, {})
        # Otherwise abort with NotAuthorized message
        except NotAuthorized:
            abort(401, _('Anonymous users not authorized to access the Visualization generator'))

        # If the page has to handle the form resulting from the service
        if request.method == 'POST' and "dataset" in request.params.keys() and request.params['dataset']:

            # Build the context using the information obtained by session and user
            context = {'model': model, 'session': model.Session,
                       'user': c.user or c.author}
            context['ignore_auth'] = True

            # Get the selected dataset
            dataset = request.params['dataset'].split(",")
            dataset_name = dataset[0]
            dataset_link = dataset[1]

            # If the dataset does not have the required FCA resource, we need to create it 
            if not dataset_link:
                # Get CSV file to 
                resCSV = format_selection(dataset_name, "CSV")
                # If there is no CSV resource
                if not resCSV: 
                    # Reset that dataset
                    LiveSchemaController = 'ckanext.liveschema_theme.controller:LiveSchemaController'
                    return redirect_to(controller=LiveSchemaController, action='reset',
                        id=dataset_name)
                # Create temp FCA resource
                FCAResource = toolkit.get_action("resource_create")(context=context,
                    data_dict={"package_id": dataset_name, "format": "temp", "name": dataset_name+"_FCA.csv", "description": "FCA Matrix containing the information of all the triples", "resource_type": "FCA"})

                # Execute the fca_generator action
                get_action('ckanext_liveschema_theme_fca_generator')(context, data_dict={"res_id": FCAResource["id"], "dataset_name": dataset_name ,"dataset_link": resCSV, "strPredicates": "", 'apikey': c.userobj.apikey, 'loading': "/dataset/fca/" + dataset_name + "?GeneratingFCA"})

            # Check if the user has the access to this page
            try:
                check_access('ckanext_liveschema_theme_visualization_generator', context, data_dict={})
            # Otherwise abort with NotAuthorized message
            except NotAuthorized:
                abort(401, _('User not authorized to view page'))

            # Get the dataset information
            dataset = toolkit.get_action('package_show')(
                data_dict={"id": dataset_name})

            # Iterate over every resource of the dataset
            for res in dataset["resources"]:
                # Check if they have the relative visualization resource
                if("resource_type" in res.keys() and res["resource_type"] == "Visualization"):
                    # Delete the current visualization resource
                    dataset = toolkit.get_action('resource_delete')(context=context,
                        data_dict={"id": res["id"]})
                    break

            # Create temp Visualization resource
            VISResource = toolkit.get_action("resource_create")(context=context, 
                data_dict={"package_id": dataset_name, "format": "temp", "name": dataset_name+"_Visualization.csv", "description": "Visualization input", "resource_type": "Visualization"})

            # Execute the Visualization generator action
            get_action('ckanext_liveschema_theme_visualization_generator')(context, data_dict={"res_id": VISResource["id"], "dataset_name": dataset_name ,"dataset_link": dataset_link, 'apikey': c.userobj.apikey, 'loading': "/dataset/visualization/" + dataset_name + "?GeneratingVisualization"})

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

        # Check if the user has the access to this page
        try:
            check_access('ckanext_liveschema_theme_updater', context, {})
        # Otherwise abort with NotAuthorized message
        except NotAuthorized:
            abort(401, _('Only admins can access the Updater service'))

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
            get_action('ckanext_liveschema_theme_updater')(context, data_dict={"catalogsSelection": catalogsSelection, 'apikey': c.userobj.apikey, 'loading': "/dataset" + "?Updating"})

            # Redirect to the index
            return redirect_to("../")

        # Render the page of the service
        return render('service/updater.html')

    # Define the behaviour of the updater service
    def uploader(self):
        # Build the context using the information obtained by session and user
        context = {'model': model, 'session': model.Session,
                   'user': c.user or c.author}

        # Check if the user has the access to this page
        try:
            check_access('ckanext_liveschema_theme_uploader', context, {})
        # Otherwise abort with NotAuthorized message
        except NotAuthorized:
            abort(401, _('Anonymous users not authorized to access the Upload Dataset service'))

        # If the page has to handle the form resulting from the service
        if request.method == 'POST' and ( (request.params.get("url") != "") or (request.params.get("upload") != "")):

            context['ignore_auth'] = True

            # Use the given name from the form
            datasetName = "users_" + request.params.get("name")

            # Get the information about the desired package
            datasetList = get_action('package_list')(context, {})

            # Add the Dataset if there are no Datasets with the same name
            if(datasetName not in datasetList):
                # Try to remove an eventual deleted resource that might generate errors
                try:
                    get_action('dataset_purge')(context, {'id': datasetName, 'force': True})
                except NotFound:
                    print("No dataset named" + datasetName)

                # Add the url used to generate the resources, either file upload or url link
                url = ""
                filePath = ""
                if(request.params.get("upload") != ""): 
                    # Save the position where the file will be
                    filePath = "src/ckanext-liveschema_theme/ckanext/liveschema_theme/public/resources/" + request.params.get("upload").filename
                    # Use the file to generate the resources
                    url = filePath
                    # Store the uploaded file
                    open(filePath, 'wb').write(request.params.get("upload").file.read())
                else:
                    # Use the link as url to generate the resources
                    url = request.params.get("url")

                # Define the data to pass to the package_show action
                title = request.params.get("title")
                owner_org = request.params.get("owner_org") or 'users'
                version = request.params.get("version") or '1.0'
                private = request.params.get("private")
                data = {'id': datasetName, 'name': datasetName, 'title': title, 'owner_org': owner_org, 'version': version, 'url': url, 'private': private, 'state': 'active', 'include_tracking': True, 'extras': list()}
                
                if(request.params.get("notes") != ""):
                    data["notes"] = request.params.get("notes")

                if(request.params.get("license_id") != "notspecified"):
                    data["license_id"] = request.params.get("license_id")

                if(request.params.get("contact_uri") != ""):
                    data["extras"].append({"key": "contact_uri", "value": request.params.get("contact_uri")})

                if(request.params.get("uri") != ""):
                    data["extras"].append({"key": "uri", "value": request.params.get("uri")})

                if(request.params.get("issued") != ""):
                    data["extras"].append({"key": "issued", "value": request.params.get("issued")})

                if(request.params.get("tags") != None):
                    tags = list()
                    for tag in str(request.params.get("tags")).split(","):
                        tags.append({"name": tag})
                    data["tags"] = tags

                if(request.params.get("author") != ""):
                    data["author"] = request.params.get("author")
                if(request.params.get("author_uri") != ""):
                    data["author_uri"] = request.params.get("author_uri")
                if(request.params.get("author_email") != ""):
                    data["author_email"] = request.params.get("author_email")

                if(request.params.get("maintainer") != ""):
                    data["maintainer"] = request.params.get("maintainer")
                if(request.params.get("maintainer_uri") != ""):
                    data["maintainer_uri"] = request.params.get("maintainer_uri")
                if(request.params.get("maintainer_email") != ""):
                    data["maintainer_email"] = request.params.get("maintainer_email")

                if(request.params.get("extras__0__key") != ""):
                    data["extras"].append({"key": request.params.get("extras__0__key"), "value": request.params.get("extras__0__value") or ""})

                extraIndex = 1
                while((request.params.get("extras__"+str(extraIndex)+"__key") or "") != ""):
                    data["extras"].append({"key": request.params.get("extras__"+str(extraIndex)+"__key"), "value": request.params.get("extras__"+str(extraIndex)+"__value") or ""})
                    extraIndex = extraIndex + 1

                # Create the package on LiveSchema
                CKANpackage = get_action('package_create')(context, data_dict=data)

                # Reset ttl resource
                TTL_Resource = get_action("resource_create")(
                    context, data_dict={"package_id": CKANpackage["name"], "url": "", 'upload': "", "format": "temp", "name": CKANpackage["name"]+".ttl", "resource_type": "Serialized ttl", "description": "Serialized ttl format of the dataset"})
                            
                # Reset rdf resource
                RDFResource = get_action("resource_create")(
                    context, data_dict={"package_id": CKANpackage["name"], "url": "", 'upload': "", "format": "temp", "name": CKANpackage["name"]+".rdf", "resource_type": "Serialized rdf", "description": "Serialized rdf format of the dataset"})
                            
                # Reset csv resource
                CSVResource = get_action("resource_create")(
                    context, data_dict={"package_id": CKANpackage["name"], "url": "", 'upload': "", "format": "temp", "name": CKANpackage["name"]+".csv", "resource_type": "Parsed csv", "description": "Parsed csv containing all the triples of the dataset"})

                # Set the dictionary of IDs
                id = {'ttl_id': TTL_Resource['id'], 'rdf_id': RDFResource['id'], 'csv_id': CSVResource['id']}
                
                # Execute the action of upload the Dataset
                result = get_action('ckanext_liveschema_theme_uploader')(context, data_dict={'id': id, 'package': CKANpackage, 'filePath': filePath, 'data': data})

            # Redirect to the last package read page
            return redirect_to(controller='package', action='read',
                id=datasetName)

        # Render the page of the service
        return render('service/uploader.html')
    
    # Define the behaviour of the query catalog service
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
                result = get_action('ckanext_liveschema_theme_query')(context, data_dict={'TTL_Resource': {'name': "Catalog", 'url': CKAN_URL+"/catalog.ttl"}, "query": query})

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
        # Render the page of the query catalog page
        return render('service/query_catalog.html',
                    {'query': query, 'pkg' : c.pkg_dict}) 


    # Define the behaviour of the package Embedding tool
    def embedding(self, id):
        # Build the context using the information obtained by session and user
        context = {'model': model, 'session': model.Session,
                   'user': c.user, 'for_view': True,
                   'auth_user_obj': c.userobj}

        EmbList = list()
        # Try to access the information
        try:
            # Define the data_dict to pass to the package_show action
            data_dict = {'id': id, 'include_tracking': True}
            # get the information about the desired package
            c.pkg_dict = get_action('package_show')(context, data_dict)

            # Get the dataset type of the dataset
            dataset_type = c.pkg_dict['type'] or 'dataset'

            for res in c.pkg_dict['resources']:
                if "resource_type" in res.keys() and res["resource_type"] == "Emb":
                    EmbList.append(res)

        # Otherwise return the relative error codes
        except NotFound:
            abort(404, _('Dataset not found'))
        except NotAuthorized:
            abort(403, _('Unauthorized to read dataset %s') % id)

        # Render the page of the service
        return render('package/embedding.html',
                      {'dataset_type': dataset_type, 'EmbList': EmbList, 'pkg' : c.pkg_dict}) 

    # Define the behaviour of the package FCA tool
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

    # Define the behaviour of the package Cue tool
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
                    if "format" in res.keys() and res["format"] == "CUE":
                        CueMatrix = pd.read_csv(res["url"])

                        termList = CueMatrix["eType"]
                        Cue1List = CueMatrix["Cue_e"]
                        Cue2List = CueMatrix["Cue_er"]
                        Cue3List = CueMatrix["Cue_ec"]
                        Cue4List = CueMatrix["Cue_c"]
                        Cue5List = CueMatrix["Cue_cr"]
                        Cue6List = CueMatrix["Cue_cc"]

        # Otherwise return the relative error codes
        except NotFound:
            abort(404, _('Dataset not found'))
        except NotAuthorized:
            abort(403, _('Unauthorized to read dataset %s') % id)

        # Render the page of the service
        return render('package/cue.html',
                      {'dataset_type': dataset_type, 'cueResource': cueResource, 'pkg' : c.pkg_dict, 'lenList': len(termList), 'termList': termList,
                      'Cue1List': Cue1List, 'Cue2List': Cue2List, 'Cue3List': Cue3List, 'Cue4List': Cue4List, 'Cue5List': Cue5List, 'Cue6List': Cue6List})     

    # Define the behaviour of the package visualization tool
    def visualization(self, id):
        # Build the context using the information obtained by session and user
        context = {'model': model, 'session': model.Session,
                   'user': c.user, 'for_view': True,
                   'auth_user_obj': c.userobj}

        # If the page has to handle the form resulting from the service to create the KLotus
        if request.method == 'POST':
            # Define the data_dict to pass to the package_show action
            data_dict = {'id': id, 'include_tracking': True}
            # get the information about the desired package
            c.pkg_dict = get_action('package_show')(context, data_dict)

            # Get the dataset type of the dataset
            dataset_type = c.pkg_dict['type'] or 'dataset'

            # Check if all the resources needed for the KLotus creation are present
            FCAResource = ""
            visualizationResource = ""
            visId = ""
            for res in c.pkg_dict['resources']:
                if "resource_type" in res.keys() and res["resource_type"] == "FCA" and "format" in res.keys() and res["format"] != "temp":
                    FCAResource = res["url"]
                if "resource_type" in res.keys() and res["resource_type"] == "Visualization" and "format" in res.keys() and res["format"] != "temp":
                    visualizationResource = res["url"]
                    visId = res["id"]

            # If the dataset does not have the required resource
            if not FCAResource or not visualizationResource:
                # Redirect to the page for the visulization of that resurce
                LiveSchemaController = 'ckanext.liveschema_theme.controller:LiveSchemaController'
                return redirect_to(controller=LiveSchemaController, action='visualization',
                    id=id)

            # Execute the Visualization generator action
            get_action('ckanext_liveschema_theme_visualization_lotus')(context, data_dict={"dataset_name": id, "FCAResource": FCAResource, "visualizationResource": visualizationResource, "visId": visId})

            # Go to the KLotus page
            return redirect_to('/KLotus/' + id + '_KLotus.png')

        # Resource to eventually show on the web page
        visualizationResource = ""
        # 
        FCAResource = False
        # Try to access the information
        try:
            # Define the data_dict to pass to the package_show action
            data_dict = {'id': id, 'include_tracking': True}
            # get the information about the desired package
            c.pkg_dict = get_action('package_show')(context, data_dict)

            # Get the dataset type of the dataset
            dataset_type = c.pkg_dict['type'] or 'dataset'

            # Iterate over all the resources of the dataset
            for res in c.pkg_dict['resources']:
                # Get the eventual visualizationResource
                if "resource_type" in res.keys() and res["resource_type"] == "Visualization":
                    visualizationResource = res
                # Get the eventual FCAResource
                if "resource_type" in res.keys() and res["resource_type"] == "FCA" and "format" in res.keys() and res["format"] != "temp":
                    FCAResource = True

        # Otherwise return the relative error codes
        except NotFound:
            abort(404, _('Dataset not found'))
        except NotAuthorized:
            abort(403, _('Unauthorized to read dataset %s') % id)

        if visualizationResource and "format" in visualizationResource.keys() and visualizationResource["format"] == "VIS":
            # Render the page of the visualization page
            return render('package/visualization.html',
                        {'dataset_type': dataset_type, 'visualizationResource': visualizationResource, 'pkg': c.pkg_dict, "FCAResource": FCAResource}) 
        else:
            # Render the page of the no_visualization page
            return render('package/no_visualization.html',
                        {'dataset_type': dataset_type, 'visualizationResource': visualizationResource, 'pkg': c.pkg_dict}) 

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
            #[TODO] Once deployed, link should have the url of the LiveSchema's relative resource instead of the internal url
            link = c.pkg_dict['url']
        # Otherwise return the relative error codes
        except NotFound:
            abort(404, _('Dataset not found'))
        except NotAuthorized:
            abort(403, _('Unauthorized to read dataset %s') % id)

        # Render the page of the service
        return render('package/graph.html',
                      {'dataset_type': dataset_type, 'link': link})
   
    # Define the behaviour of the package query tool
    def query(self, id):
        # Build the context using the information obtained by session and user
        context = {'model': model, 'session': model.Session,
                   'user': c.user, 'for_view': True,
                   'auth_user_obj': c.userobj}

        TTL_Resource = ""
        # Try to access the information
        try:
            # Define the data_dict to pass to the package_show action
            data_dict = {'id': id, 'include_tracking': True}
            # get the information about the desired package
            c.pkg_dict = get_action('package_show')(context, data_dict)

            # Get the dataset type of the dataset
            dataset_type = c.pkg_dict['type'] or 'dataset'

            for res in c.pkg_dict['resources']:
                if "resource_type" in res.keys() and res["resource_type"] == "Serialized ttl":
                    TTL_Resource = res
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
                result = get_action('ckanext_liveschema_theme_query')(context, data_dict={'TTL_Resource': TTL_Resource, "query": query})

            # Go to the dataset page
            return render('package/query.html',
                        {'dataset_type': dataset_type, 'TTL_Resource': TTL_Resource, 'query': query, 'result': result, 'number': len(result), 'pkg' : c.pkg_dict}) 
        query = "# Get all the triples of the dataset\n" + \
                "SELECT ?Subject ?Predicate ?Object\n" + \
                "WHERE {\n" + \
                "\t?Subject ?Predicate ?Object\n" + \
                "}\n"

        # Render the page of the query page
        return render('package/query.html',
                    {'dataset_type': dataset_type, 'TTL_Resource': TTL_Resource, 'query': query, 'pkg': c.pkg_dict}) 

    # Define the behaviour of the reset resources 
    def reset(self, id):
        # Build the context using the information obtained by session and user
        context = {'model': model, 'session': model.Session,
                   'user': c.user, 'for_view': True,
                   'auth_user_obj': c.userobj}

        # Check if the user has the access to this service
        try:
            check_access('ckanext_liveschema_theme_reset', context, {})
        # Otherwise abort with NotAuthorized message
        except NotAuthorized:
            abort(401, _('Only admins can reset the resources'))

        # Try to access the dataset
        try:
            # Define the data_dict to pass to the package_show action
            data_dict = {'id': id, 'include_tracking': True}
            # get the information about the desired package
            c.pkg_dict = get_action('package_show')(context, data_dict)

            context['ignore_auth'] = True
            # Update or Delete all the current resources of the dataset
            ttl = ""
            rdf = ""
            csv = ""
            for resource in c.pkg_dict["resources"]:
                formatTemp = resource["format"]
                # Reset resource
                resource["format"] = "temp"
                resource = toolkit.get_action("resource_update")(context=context, 
                    data_dict=resource)
                # Store id resources
                if(formatTemp == "TTL" and resource["resource_type"] == "Serialized ttl"):
                    ttl = resource["id"]
                    continue
                if(formatTemp == "RDF" and resource["resource_type"] == "Serialized rdf"):
                    rdf = resource["id"]
                    continue
                if(formatTemp == "CSV" and resource["resource_type"] == "Parsed csv"):
                    csv = resource["id"]
                    continue
                # Delete different formats
                get_action("resource_delete")(context = context, data_dict={"id": resource["id"]})
            
            if(not ttl):
                # Create new ttl resource
                TTL_Resource = toolkit.get_action("resource_create")(
                    data_dict={"package_id":c.pkg_dict["name"], "format": "temp", "name": c.pkg_dict["name"]+".ttl", "resource_type": "Serialized ttl", "description": "Serialized ttl format of the dataset"})
                ttl = TTL_Resource["id"]
            if(not rdf):
                # Create new rdf resource
                RDFResource = toolkit.get_action("resource_create")(
                    data_dict={"package_id":c.pkg_dict["name"], "format": "temp", "name": c.pkg_dict["name"]+".rdf", "resource_type": "Serialized rdf", "description": "Serialized rdf format of the dataset"})
                rdf = RDFResource["id"]
            if(not csv):
                # Create new csv resource
                CSVResource = toolkit.get_action("resource_create")(
                    data_dict={"package_id":c.pkg_dict["name"], "format": "temp", "name": c.pkg_dict["name"]+".csv", "resource_type": "Parsed csv", "description": "Parsed csv containing all the triples of the dataset"})
                csv = CSVResource["id"]

            # Execute the action of reset of all the resources
            result = get_action('ckanext_liveschema_theme_reset')(context, data_dict={'id': {'ttl_id': ttl, 'rdf_id': rdf, 'csv_id': csv}, 'apikey': c.userobj.apikey, 'package': c.pkg_dict})

        # Otherwise return the relative error codes
        except NotFound:
            abort(404, _('Dataset not found'))
        except NotAuthorized:
            abort(403, _('Unauthorized to read dataset %s') % id)
        
        # Redirect to the package read page
        return redirect_to(controller='package', action='read',
            id=id)


    # Define the behaviour of the contact service
    def contact(self):
        # If the page has to handle the form resulting from the service
        if request.method == 'POST' and "mail" in request.params.keys() and request.params['mail']:
            # [TODO] Send mail
            #TMP --> Write on file
            # Name of folder of results
            path = "src/ckanext-liveschema_theme/ckanext/liveschema_theme/public/"
            with open(path + "tmp.txt", "a+") as tmp:
                tmp.write("\n")
                tmp.write("Name: \t\t\t\"" + str(request.params["name"]) + "\"\n")
                tmp.write("eMail: \t\t\t\"" + str(request.params["mail"]) + "\"\n")
                tmp.write("Institution: \t\"" + str(request.params["institution"]) + "\"\n")
                tmp.write("Message: \t\t\"" + str(request.params["message"]) + "\"\n")
                tmp.write("")
            # Redirect to the index
            return redirect_to("../")
        # Render contact page
        return render('service/contact.html')