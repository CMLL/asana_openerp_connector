#-*- coding: utf-8 -*-
from openerp.tests import common
from openerp.osv import orm
from asana.asana import AsanaAPI

#API Key
#TODO Change this api key for a dummy account one.
AKEY = '1qBeMGMB.KaHjfA3jwhoficieElDJDqh'

class TestAsanaConnector(common.TransactionCase):

    def setUp(self):
        super(TestAsanaConnector, self).setUp()
        cr, uid = self.cr, self.uid

        #Models registry
        self.project_obj = self.registry('project.project')
        self.task_obj = self.registry('project.task')
        self.connector_obj = self.registry('asana.connector')

        #Create a new connection for testing purposes.
        #Use the api key of a dummy account.
        self.connection_id = self.connector_obj.create(cr, uid, {'name': 'Dummy account',
                                                                 'api_key' : AKEY,
                                                                 'state': 'draft'})
        #Also create a record with bad information for negative cases.
        self.bad_connection_id = self.connector_obj.create(cr, uid, {'name': 'Bad account',
                                                                     'api_key': '1',
                                                                     'state': 'draft'})
        self.testConnection = AsanaAPI('1qBeMGMB.KaHjfA3jwhoficieElDJDqh')

    def testConnectionParameters(self):
        """Check the parameters for a success connection."""
        cr, uid = self.cr, self.uid
        response = self.connector_obj.connect(cr, uid, self.connection_id)
        self.assertTrue(response)

    def testConnectionState(self):
        """Check that if the connection is a succes the state of the object changes."""
        cr, uid = self.cr, self.uid
        response = self.connector_obj.connect(cr, uid, self.connection_id)
        connector_state = self.connector_obj.browse(cr, uid, self.connection_id).state
        self.assertEqual(connector_state, 'connected')

    def testConnectionBadParameters(self):
        """Check for exception if an error in Api key."""
        cr, uid = self.cr, self.uid
        self.assertRaises(orm.except_orm, self.connector_obj.connect, cr, uid, self.bad_connection_id)

    def testConnectionRetrievesUserInfoEmail(self):
        """Check that when connected the user email is retrieved."""
        cr, uid = self.cr, self.uid
        response = self.connector_obj.connect(cr, uid, self.connection_id)
        connector_email = self.connector_obj.browse(cr, uid, self.connection_id).email
        self.assertEqual(connector_email, self.testConnection.user_info().get('email'))

    def testConnectionRetrievesUserInfoId(self):
        """Check that when connected the user id is retrieved."""
        cr, uid = self.cr, self.uid
        response = self.connector_obj.connect(cr, uid, self.connection_id)
        connector_id = self.connector_obj.browse(cr, uid, self.connection_id).asana_id
        #OpenERP Orm retrieves integer values as string, so parsing is required for test to pass.
        self.assertEqual(int(connector_id), self.testConnection.user_info().get('id'))

    def testConnectionRetrievesUserName(self):
        """Check that when connected the user name is retrieved."""
        cr, uid = self.cr, self.uid
        response = self.connector_obj.connect(cr, uid, self.connection_id)
        connector_name = self.connector_obj.browse(cr, uid, self.connection_id).name
        self.assertEqual(connector_name, self.testConnection.user_info().get('name'))


