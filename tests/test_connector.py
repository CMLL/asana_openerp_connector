#-*- coding: utf-8 -*-
from openerp.tests import common
from openerp.osv import orm

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

    def testConnectionParameters(self):
        """Check the parameters for a success connection."""
        cr, uid = self.cr, self.uid

        response = self.connector_obj.connect(cr, uid, self.connection_id)
        self.assertTrue(response)



