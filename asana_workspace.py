#-*- coding: utf-8 -*-
from openerp.osv import orm, fields


class AsanaWorkspaces(orm.Model):

    _name = 'asana.workspace'
    _columns = {
        'name': fields.char('Workspace Name', size=32, readonly=True),
        'asana_id': fields.char('Workspace Id', size=32, readonly=True),
        'connector_id': fields.many2one('asana.connector', 'Asana Connector',
            readonly=True)
    }