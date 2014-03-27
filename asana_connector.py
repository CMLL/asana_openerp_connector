#-*- coding: utf-8 -*-

from openerp.osv import orm, fields
from asana.asana import AsanaException, AsanaAPI


class AsanaConnector(orm.Model):

    _name = 'asana.connector'
    _auto = True

    _columns = {
        'name': fields.char('User Name', size=32, help='Your Asana username.',
                            readonly=True),
        'api_key': fields.char('API Key',
                                size=32,
                                required=True,
                                help="""Your Asana Account API key,
                                you can generate this key in your settings
                                page of Asana."""),
        'state': fields.selection((('draft', 'Draft'),
                                   ('connected', 'Connected')), 'State'),
        'email': fields.char('Email', size=32, help='Your Asana email',
                             readonly=True),
        'asana_id': fields.char('Asana Id', size=32, help='Your Asana user id',
                                readonly=True)
    }

    _defaults = {
        'state': 'draft'
    }

    def connect(self, cr, uid, ids, context=None):
        """Perform the connection between Openerp and Asana using
        the api_key parameter."""
        for user in self.browse(cr, uid, ids, context):
            connection = AsanaAPI(user.api_key)
            try:
                user_info = connection.user_info()
                self.write(cr, uid, ids, {'state': 'connected',
                                          'email': user_info.get('email'),
                                          'asana_id': str(user_info.get('id')),
                                          'name': user_info.get('name')}, context)
                return True
            except AsanaException as e:
                raise orm.except_orm('Error', e.message)

    def sync_projects(self, cr, uid, ids, context=None):
        """Sync the projects in Asana with the project.project model in Openerp.

        Returns: [created_project_id]"""
        res = []
        for connection in self.browse(cr, uid, ids, context):
            connect = AsanaAPI(connection.api_key)
            asana_projects = connect.list_projects()
            for project in asana_projects:
                project_id = self.create_project(cr, uid, connection.id, connect, project.get('id'), context)
                res.append(project_id)
        return res

    def create_project(self, cr, uid, id, connection, asana_project_id, context=None):
        """Create the specified asana project to project.project model.

        Args:
            connection; AsanaAPI objecto to retrieve project info.
            asana_project_id; id retrieved from list_projects

        Returns; created project id."""
        project_obj = self.pool.get('project.project')
        project_details = connection.get_project(asana_project_id)
        values = {'name': project_details.get('name'),
                  'use_tasks': True,
                  'privacy_visibility': 'employees'}
        project_id = project_obj.create(cr, uid, values, context)
        return project_id

    def sync_workspaces(self, cr, uid, ids, context=None):
        """Sync the workspaces in asana with asana.workspace model in Openerp

        Returns: [created_workspace_id]
        """
        res = []
        workspace_obj = self.pool.get('asana.workspace')
        for connection in self.browse(cr, uid, ids, context):
            connect = AsanaAPI(connection.api_key)
            asana_workspaces = connect.list_workspaces()
            for workspace in asana_workspaces:
                values = {
                    'name': workspace.get('name'),
                    'asana_id': workspace.get('id'),
                    'connector_id': connection.id
                }
                created_id = workspace_obj.create(cr, uid, values, context)
                res.append(created_id)
        return res
