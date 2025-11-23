from odoo import _, api, fields, models


class ApiEndpointResponse(models.Model):
    _name = "api.endpoint.response"
    _description = "Réponse d'API"

    endpoint_id = fields.Many2one("api.endpoint", string="Endpoint", required=True, ondelete="cascade")

    status_code = fields.Integer("Code HTTP", required=True)  # ex: 200, 401, 404
    description = fields.Char("Description")
    content_type = fields.Selection([
        ('application/json', 'application/json'),
        ('text/plain', 'text/plain'),
    ], string="Type de contenu", default="application/json")

    # Exemple JSON renvoyé
    example_response = fields.Text("Exemple de réponse JSON")

    # Schéma JSON (en texte brut pour être flexible)
    schema = fields.Text("Schéma JSON (OpenAPI)")
