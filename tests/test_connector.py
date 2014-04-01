#-*- coding: utf-8 -*-
from openerp.tests import common
from openerp.osv import orm
from asana.asana import AsanaAPI

# API Key
# TODO Change this api key for a dummy account one.
AKEY = '1qBeMGMB.KaHjfA3jwhoficieElDJDqh'


class TestAsanaConnector(common.TransactionCase):

    def setUp(self):
        super(TestAsanaConnector, self).setUp()
        cr, uid = self.cr, self.uid

        # Models registry
        self.project_obj = self.registry('project.project')
        self.task_obj = self.registry('project.task')
        self.connector_obj = self.registry('asana.connector')
        self.workspace_obj = self.registry('asana.workspace')

        # Create a new connection for testing purposes.
        # Use the api key of a dummy account.
        # OpenERP passes the ids as a list to a bunch their methods, so we need to comply
        # with this API specification.
        self.connection_id = [self.connector_obj.create(
            cr, uid, {'name': 'Dummy account', 'api_key': AKEY, 'state': 'draft'})]
        # Also create a record with bad information for negative cases.
        self.bad_connection_id = [self.connector_obj.create(
            cr, uid, {'name': 'Bad account', 'api_key': '1', 'state': 'draft'})]
        self.testConnection = AsanaAPI('1qBeMGMB.KaHjfA3jwhoficieElDJDqh')

    def testConnectionParameters(self):
        """Check the parameters for a success connection."""
        cr, uid = self.cr, self.uid
        response = self.connector_obj.connect(cr, uid, self.connection_id)
        self.assertTrue(response)

    def testConnectionState(self):
        """Check that if the connection is a succes the state of the object changes."""
        cr, uid = self.cr, self.uid
        self.connector_obj.connect(cr, uid, self.connection_id)
        for connector_state in self.connector_obj.browse(cr, uid, self.connection_id):
            self.assertEqual(connector_state.state, 'connected')

    def testConnectionBadParameters(self):
        """Check for exception if an error in Api key."""
        cr, uid = self.cr, self.uid
        self.assertRaises(
            orm.except_orm, self.connector_obj.connect, cr, uid, self.bad_connection_id)

    def testConnectionRetrievesUserInfoEmail(self):
        """Check that when connected the user email is retrieved."""
        cr, uid = self.cr, self.uid
        self.connector_obj.connect(cr, uid, self.connection_id)
        for connector_email in self.connector_obj.browse(cr, uid, self.connection_id):
            self.assertEqual(
                connector_email.email, self.testConnection.user_info().get('email'))

    def testConnectionRetrievesUserInfoId(self):
        """Check that when connected the user id is retrieved."""
        cr, uid = self.cr, self.uid
        self.connector_obj.connect(cr, uid, self.connection_id)
        for connector_id in self.connector_obj.browse(cr, uid, self.connection_id):
            # OpenERP Orm retrieves integer values as string, so parsing is
            # required for test to pass.
            self.assertEqual(
                int(connector_id.asana_id), self.testConnection.user_info().get('id'))

    def testConnectionRetrievesUserName(self):
        """Check that when connected the user name is retrieved."""
        cr, uid = self.cr, self.uid
        self.connector_obj.connect(cr, uid, self.connection_id)
        for connector_name in self.connector_obj.browse(cr, uid, self.connection_id):
         self.assertEqual(
             connector_name.name, self.testConnection.user_info().get('name'))

    def testSyncAllProjects(self):
        """Check for a succes project syncing."""
        cr, uid = self.cr, self.uid
        asana_projects = self.testConnection.list_projects()
        self.connector_obj.sync_projects(cr, uid, self.connection_id)
        for project in asana_projects:
            self.assertTrue(self.project_obj.search(
                cr, uid, [('name', '=', project.get('name'))]))

    def testSyncProject(self):
        """Check for helper method that creates the projects in OpenERP."""
        cr, uid = self.cr, self.uid
        asana_projects = self.testConnection.list_projects()
        project_details = self.testConnection.get_project(asana_projects[0].get('id'))
        self.connector_obj.create_project(cr, uid, self.connection_id, self.testConnection, project_details.get('id'))
        openerp_project = self.project_obj.search(cr, uid, [('name', '=', project_details.get('name'))])
        self.assertTrue(openerp_project)
        asana_tasks = self.testConnection.get_project_tasks(project_details.get('id'))
        task_names = []
        for task in asana_tasks:
            task_names.append(task.get('name'))
        openerp_tasks = self.task_obj.search(cr, uid, [('project_id', '=', openerp_project[0])])
        for task in self.task_obj.browse(cr, uid, openerp_tasks):
            self.assertIn(task.name, task_names)

    def testSyncWorkspaces(self):
        """Check for method that sync all workspaces."""
        cr, uid = self.cr, self.uid
        asana_workspaces = self.testConnection.list_workspaces()
        self.connector_obj.sync_workspaces(cr, uid, self.connection_id)
        for workspace in asana_workspaces:
            self.assertTrue(self.workspace_obj.search(cr, uid, [('name', '=', workspace.get('name'))]))

    def testProjectTasks(self):
        """Check for method that syncs all of a project tasks."""
        cr, uid = self.cr, self.uid
        #TODO Used second element 'cause i know that one has tasks.
        asana_project = self.testConnection.list_projects()[1]
        asana_tasks = []
        for task in self.testConnection.get_project_tasks(asana_project.get('id')):
            asana_tasks.append(task.get('name'))
        openerp_project = self.project_obj.search(cr, uid, [('name', '=', asana_project.get('name'))])
        task_ids = self.connector_obj.sync_tasks(cr, uid, self.connection_id[0],
                                                 asana_project.get('id'),
                                                 openerp_project[0])
        for openerp_task in self.task_obj.browse(cr, uid, task_ids):
            self.assertIn(openerp_task.name, asana_tasks)


