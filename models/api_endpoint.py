from odoo import _, api, fields, models
from odoo.exceptions import AccessDenied, ValidationError
from odoo.tools.safe_eval import test_python_expr
import werkzeug
import werkzeug.exceptions
import re
import json

import logging

_logger = logging.getLogger(__name__)


# Map pour les types éventuels
_TYPE_MAP = {
    'int': r'\d+',
    'float': r'\d+(?:\.\d+)?',
    'path': r'.+',
    'uuid': r'[0-9a-fA-F\-]{32,36}',
    None: r'[^/]+',  # défaut
}

class ApiEndpoint(models.Model):
    _name = "api.endpoint"
    _description = "API Endpoint"
    _inherit = ["mixin.code"]
    
    title = fields.Char("titre", required=True)
    version = fields.Char('version', required=True, default='1.0.0')
    description = fields.Text("Description", default='')
    url = fields.Char("URL", required=True)
    method = fields.Selection([
        ('GET', 'GET'),
        ('POST', 'POST'),
        ('PUT', 'PUT'),
        ('DELETE', 'DELETE')
    ], string="Méthode", required=True, default="GET")
    summary = fields.Char("Résumé")  # ex: Lister les projets
    tags = fields.Char("Tags")  # ex: Projets, Cas de test, Bugs
    security = fields.Boolean("Nécessite Authentification Bearer", default=True)

    # paramètres (path, query, header, body)
    params_ids = fields.One2many("api.endpoint.param", "endpoint_id", string="Paramètres")

    # réponses possibles
    response_ids = fields.One2many("api.endpoint.response", "endpoint_id", string="Réponses")

    model_id = fields.Many2one('ir.model', string='Model', required=True, ondelete='cascade', index=True,
                               help="Model on which the server action runs.")
    available_model_ids = fields.Many2many('ir.model', string='Available Models', compute='_compute_available_model_ids', store=False)
    model_name = fields.Char(related='model_id.model', string='Model Name', readonly=True, store=True)

    code = fields.Text('code')
    _sql_constraints = [
        (
            "url_method_unique",  # nom de la contrainte
            "unique(url, method)",  # champ(s) concernés
            "Un endpoint avec cette URL et cette méthode existe déjà."  # message d'erreur
        )
    ]

    def _compute_available_model_ids(self):
        allowed_models = self.env['ir.model'].search(
            [('model', 'in', list(self.env['ir.model.access']._get_allowed_models()))]
        )
        self.available_model_ids = allowed_models.ids

    @api.constrains('code')
    def _check_python_code(self):
        for action in self.sudo().filtered('code'):
            msg = test_python_expr(expr=action.code.strip(), mode="exec")
            if msg:
                raise ValidationError(msg)

    def _normalize_url(self, u: str) -> str:
        u = (u or '').strip()
        if not u.startswith('/'):
            u = '/' + u
        # Si tes endpoints sont stockés sans le préfixe /api,
        # on le rajoute pour matcher full_path = "/api/" + subpath
        if not u.startswith('/api/'):
            u = '/api' + ('' if u == '/' else u)
        return u

    def endpoint_url_to_regex(self, url: str) -> str:
        """
        Transforme:
        - /api/v1/projects/{id} -> ^/api/v1/projects/(?P<id>[^/]+)/?$
        - /api/v1/projects/<int:id> -> ^/api/v1/projects/(?P<id>\d+)/?$
        - /api/v1/test -> ^/api/v1/test/?$
        """
        pattern = self._normalize_url(url)

        # 1) Style OpenAPI: {name} ou {name:type}
        #   ex: {id} ou {id:int}
        type_map = {}
        if "{" in pattern:
            def repl_braces(m):
                name = m.group(1)
                typ = m.group(2)
                type_map[name] = typ or None
                rx = _TYPE_MAP.get(typ, _TYPE_MAP[None])
                return f"(?P<{name}>{rx})"

            pattern = re.sub(r'\{(\w+)(?::(int|float|path|uuid))?\}', repl_braces, pattern)


        # Ancrage + slash final optionnel
        return f'^{pattern}/?$', type_map


    def generate_openapi_spec(self):
        """
        Génère le Swagger/OpenAPI spec à la volée à partir des endpoints configurés
        """
        spec = {
            "openapi": "3.0.0",
            "info": {
                "title": "Test Tracking API",
                "version": "1.0.0",
                "description": "Documentation générée automatiquement depuis Odoo."
            },
            "paths": {},
            "components": {
                "securitySchemes": {
                    "bearerAuth": {
                        "type": "http",
                        "scheme": "bearer",
                        "bearerFormat": "JWT"
                    }
                }
            }
        }

        for endpoint in self.search([]):
            path = endpoint.url
            method = endpoint.method.lower()

            if path not in spec["paths"]:
                spec["paths"][path] = {}

            # Paramètres
            parameters = []
            for param in endpoint.params_ids:
                parameters.append({
                    "name": param.name,
                    "in": param.in_,
                    "required": param.required,
                    "schema": {"type": param.schema_type},
                })

            # Réponses
            responses = {}
            for resp in endpoint.response_ids:
                schema = {}
                try:
                    schema = json.loads(resp.schema) if resp.schema else {}
                except Exception as e:
                    _logger.error(e)
                    schema = {"type": "string"}  # fallback si mauvais JSON

                responses[str(resp.status_code)] = {
                    "description": resp.description or "",
                    "content": {
                        resp.content_type: {
                            "schema": schema,
                            "example": json.loads(resp.example_response) if resp.example_response else {}
                        }
                    }
                }

            # Construction du bloc
            spec["paths"][path][method] = {
                "summary": endpoint.summary,
                "description": endpoint.description or "",
                "tags": [tag.strip() for tag in (endpoint.tags or "").split(",") if tag],
                "parameters": parameters,
                "responses": responses,
            }

            # Ajout de la sécurité si nécessaire
            if endpoint.security:
                spec["paths"][path][method]["security"] = [{"bearerAuth": []}]

        return spec
