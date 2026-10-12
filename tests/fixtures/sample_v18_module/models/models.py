# -*- coding: utf-8 -*-
from odoo import models, fields, api


class SampleModel(models.Model):
    _name = 'sample.model'
    _description = 'Sample Model'

    name = fields.Char(string='Name', required=True)
    state = fields.Selection([('draft', 'Draft'), ('done', 'Done')], default='draft')

    _sql_constraints = [
        ('uniq_name', 'unique(name)', 'The name must be unique!'),
    ]
