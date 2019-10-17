# encoding: utf-8

import ckan.plugins as plugins

import ckan.plugins.toolkit as toolkit


from ckan.plugins import IRoutes, implements, SingletonPlugin
from ckan.controllers.group import GroupController
from ckan.config.routing import SubMapper


def most_popular_catalogs():
    '''Return a sorted list of the catalogs with the most datasets.'''

    # Get a list of all the site's catalogs from CKAN, sorted by number of
    # datasets.
    catalogs = toolkit.get_action('organization_list')(
        data_dict={'sort': 'package_count desc', 'all_fields': True})

    # Truncate the list to the 10 most popular catalogs only.
    catalogs = catalogs[:10]

    return catalogs


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

    # Declare that this plugin will implement ITemplateHelpers.
    plugins.implements(plugins.ITemplateHelpers)

    def get_helpers(self):
        '''Register the most_popular_catalogs() function above as a template
        helper function.

        '''
        # Template helper function names should begin with the name of the
        # extension they belong to, to avoid clashing with functions from
        # other extensions.
        return {'liveschema_theme_most_popular_catalogs': most_popular_catalogs}   


    implements(IRoutes, inherit=True)

    def before_map(self, map):

        # These named routes are used for custom dataset forms which will use
        # the names below based on the dataset.type ('dataset' is the default
        # type)

        with SubMapper(map, controller='ckanext.liveschema_theme.plugin:LiveSchemaGroupController') as m:
            m.connect('ckanext_liveschema_theme_service', '/service', action='search', highlight_actions='index')
            m.connect('ckanext_liveschema_theme_services', '/service/{id}', action='read')

        return map

render = toolkit.render

class LiveSchemaGroupController(GroupController):

    def search(self):
        return render('service/services.html')

    def read(self, id):
        if(id == "fca_generator"):
            return render('service/fca_generator.html')
        
        if(id == "cue_generator"):
            return render('service/cue_generator.html')
