#-*- coding: utf-8 -*-

from openerp.osv import orm, fields
from asana import asana


class AsanaConnector(orm.Model):

    _name = 'asana.connector'
    _auto = True

    _columns = {
        'name': fields.char('User Name', size=32, help='Your Asana username.', required=True),
        'api_key': fields.char('API Key', size=32, required=True, help="""Your Asana Account API key,
                               you can generate this key in your settings page of Asana."""),
        'state': fields.selection((('draft', 'Draft'), ('connected', 'Connected')), 'State'),
    }

    _defaults = {
        'state': 'draft'
    }

    def connect(self, cr, uid, id, context=None):
        """Perform the connection between Openerp and Asana using
        the api_key parameter."""
        import ipdb; ipdb.set_trace()  # XXX BREAKPOINT
        user = self.browse(cr, uid, id, context)
        connection = asana.AsanaAPI(user.api_key)
        return True






