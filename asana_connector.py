#-*- coding: utf-8 -*-

from openerp.osv import orm, fields


class AsanaConnector(orm.Model):

    _name = 'asana.connector'
    _auto = True

    _columns = {
        'name': fields.char('User Name', size=9, help='Your Asana username.'),
        'api_key': fields.char('API Key', size=32, required=True, help="""Your Asana Account API key,
                               you can generate this key in your settings page of Asana."""),
        'state': fields.selection((('draft', 'Draft'), ('connected', 'Connected')), 'State'),
    }






