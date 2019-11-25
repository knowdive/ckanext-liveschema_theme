# Import libraries
import ckan.plugins.toolkit as toolkit


@toolkit.auth_allow_anonymous_access
def services(context, data_dict):
    # All users can access the services page
    return {'success': True}

@toolkit.auth_allow_anonymous_access
def fca_generator(context, data_dict):
    # All users can access the services page
    return {'success': True}


@toolkit.auth_allow_anonymous_access
def cue_generator(context, data_dict):
    # All users can access the services page
    return {'success': True}


@toolkit.auth_allow_anonymous_access
def visualization_generator(context, data_dict):
    # All users can access the services page
    return {'success': True}

def updater(context, data_dict):
    # sysadmins only
    return {'success': False}