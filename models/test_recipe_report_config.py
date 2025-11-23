from odoo import models, fields

class TestRecipeReportConfig(models.Model):
    _name = "test.recipe.report.config"
    _description = "Configuration du PV de recette"

    name = fields.Char("Nom", required=True)

    include_header = fields.Boolean("Inclure l'en-tête", default=True)
    include_participants = fields.Boolean("Inclure les participants", default=True)
    include_summary = fields.Boolean("Inclure le résumé", default=True)
    include_anomalies = fields.Boolean("Inclure les anomalies", default=True)
    include_decision = fields.Boolean("Inclure la décision", default=True)
    include_signatures = fields.Boolean("Inclure les signatures", default=True)