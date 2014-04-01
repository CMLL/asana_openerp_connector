#-*- coding: utf-8 -*-

from openerp.osv import orm, fields
from asana.asana import AsanaException, AsanaAPI
from logging import getLogger
from requests import ConnectionError

logger = getLogger(__name__)


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
            logger.info("Attempting to connect to Asana.")
            connection = self.make_connection(cr, uid, user.id)
            try:
                user_info = connection.user_info()
            except AsanaException, api_error:
                logger.error(api_error.message)
                raise orm.except_orm("Error", "Can't retrieve data. Correct api key?")
            self.write(cr, uid, ids, {'state': 'connected',
                                      'email': user_info.get('email'),
                                      'asana_id': str(user_info.get('id')),
                                      'name': user_info.get('name')}, context)
            logger.info("Connection succes.")
            return True

    def make_connection(self, cr, uid, id, context=None):
        """Try to connect and return the AsanaAPI object.

        Returns:
            AsanaAPI object.
        """
        api_key = self.browse(cr, uid, id, context).api_key
        try:
            connection = AsanaAPI(api_key)
            return connection
        except ConnectionError, conenction_error:
            logger.error(conenction_error.message)
            raise orm.except_orm("Error", "Can't connect to Asana. Internet?")


    def sync_projects(self, cr, uid, ids, context=None):
        """Sync the projects in Asana with the project.project model in Openerp.

        Returns: [created_project_id]"""
        res = []
        for connection in self.browse(cr, uid, ids, context):
            logger.info("Performing project synchronization.")
            connect = AsanaAPI(connection.api_key)
            asana_projects = connect.list_projects()
            for project in asana_projects:
                project_id = self.create_project(cr, uid, connection.id, connect, project.get('id'), context)
                logger.info("Created project {0}".format(project.get('name')))
                res.append(project_id)
                tasks = self.sync_tasks(cr, uid, connection.id, project.get('id'), project_id)
                logger.info("Created tasks related to project {0}".format(project.get('name')))
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
            logger.info("Started workspace synchronization.")
            connect = AsanaAPI(connection.api_key)
            asana_workspaces = connect.list_workspaces()
            for workspace in asana_workspaces:
                values = {
                    'name': workspace.get('name'),
                    'asana_id': workspace.get('id'),
                    'connector_id': connection.id
                }
                created_id = workspace_obj.create(cr, uid, values, context)
                logger.info("Created workspace {0}".format(workspace.get('name')))
                res.append(created_id)
        return res

    def sync_tasks(self, cr, uid, connection_id, asana_project_id, openerp_project_id, context=None):
        """Sync the tasks of an asana project with its openerp counterpart.

        Args:
            connection; AsanaAPI object to perform the  pull of data.
            asana_project_id; the project to synchronize data of.
            openerp_project_id; the project to relate the tasks.

        Returns: [created_task_ids]
        """
        task_obj = self.pool.get('project.task')
        connection = AsanaAPI(self.browse(cr, uid, connection_id, context).api_key)
        res = []
        asana_tasks = connection.get_project_tasks(asana_project_id)
        for task in asana_tasks:
            info = connection.get_task(task.get('id'))
            values = {
                    'name': info.get('name'),
                    'description': "Task synced from Asana.",
                    'project_id': openerp_project_id
            }
            created_id = task_obj.create(cr, uid, values, context)
            logger.info("Created task {0}".format(info.get('name')))
            res.append(created_id)
        return res