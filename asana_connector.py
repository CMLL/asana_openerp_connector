#-*- coding: utf-8 -*-

from openerp.osv import orm, fields
from asana import asana
from asana.asana import AsanaException


class AsanaConnector(orm.Model):

    _name = 'asana.connector'
    _auto = True

    _columns = {
        'name': fields.char('User Name', size=32, help='Your Asana username.', readonly=True),
        'api_key': fields.char('API Key', size=32, required=True, help="""Your Asana Account API key,
                               you can generate this key in your settings page of Asana."""),
        'state': fields.selection((('draft', 'Draft'), ('connected', 'Connected')), 'State'),
        'email': fields.char('Email', size=32, help='Your Asana email', readonly=True),
        'asana_id': fields.char('Asana Id', size=32, help='Your Asana user id', readonly=True)
    }

    _defaults = {
        'state': 'draft'
    }

    def connect(self, cr, uid, id, context=None):
        """Perform the connection between Openerp and Asana using
        the api_key parameter."""
        for user in self.browse(cr, uid, id, context):
            connection = asana.AsanaAPI(user.api_key)
            try:
                user_info = connection.user_info()
                self.write(cr, uid, id, {'state': 'connected',
                                        'email': user_info.get('email'),
                                        'asana_id': str(user_info.get('id')),
                                        'name': user_info.get('name')}, context)
                return True
            except AsanaException as e:
                raise orm.except_orm('Error', e.message)







