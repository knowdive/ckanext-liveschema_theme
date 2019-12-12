# Import libraries
import ckan.plugins.toolkit as toolkit

import ckan.authz as authz


@toolkit.auth_allow_anonymous_access
def services(context, data_dict):
    # All users can access the services page
    return {'success': True}

def fca_generator(context, data_dict):
    # All registered users can access the FCA generator page
    return {'success': authz.auth_is_loggedin_user()}

def cue_generator(context, data_dict):
    # All registered users can access the Cue generator page
    return {'success': authz.auth_is_loggedin_user()}

def visualization_generator(context, data_dict):
    # All registered users can access the Visualization generator page
    return {'success': authz.auth_is_loggedin_user()}

def updater(context, data_dict):
    # sysadmins only
    return {'success': False}

def reset(context, data_dict):
    # All registered users can access the Visualization generator page
    return {'success': authz.auth_is_loggedin_user()}