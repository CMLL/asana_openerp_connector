#-*- coding: utf-8 -*-

{'name': 'Asana Openerp Connector',
 'author': 'Carlos Llamacho',
 'version': '0.1',
 'category': 'Project Management',
 'description': """
 Does your company uses OpenERP for tracking tasks and teams but you wish something more current were in place?
 Well, this module will allow your team to use Asana as your preferred tool for tracking tasks and still report
 to the company using Openerp.

 Just set it up with your account and all your task, projects, and teams will be imported automatically in Openerp project
 management module for your convenience.""",
 'depends':['base',
            'project'],
 'data':['asana_connector_view.xml',
         'asana_workspace_view.xml'],
 'installable': True,
 'auto': False}

