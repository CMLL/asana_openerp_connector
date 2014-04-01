#-*- coding: utf-8 -*-
from openerp.osv import orm, fields


class Project(orm.Model):

    _inherit = 'project.project'
    _auto = True
    _columns = {
    'connector_id': fields.many2one('asana.connector', "Asana Connector",
        help ="This projects connector with Asana.com"),
    }