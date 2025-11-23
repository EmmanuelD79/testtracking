from odoo import _, api, fields, models


class ApiEndpointParam(models.Model):
    _name = "api.endpoint.param"
    _description = "Paramètre d'API"

    endpoint_id = fields.Many2one("api.endpoint", string="Endpoint", required=True, ondelete="cascade")

    name = fields.Char("Nom", required=True)  # ex: id
    in_ = fields.Selection([
        ('path', 'Path'),
        ('query', 'Query'),
        ('header', 'Header'),
        ('body', 'Body')
    ], string="Localisation", required=True)

    required = fields.Boolean("Obligatoire", default=False)
    schema_type = fields.Selection([
        ('string', 'String'),
        ('integer', 'Integer'),
        ('boolean', 'Boolean'),
        ('object', 'Object'),
        ('array', 'Array'),
    ], string="Type de schéma", required=True, default="string")
