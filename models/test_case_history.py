from odoo import models, fields, api
from datetime import datetime

class TestCaseHistory(models.Model):
    _name = "test.case.history"
    _description = "Historique des cas de test"
    _order = "date desc"

    case_id = fields.Many2one(
        "test.case", 
        string="Cas de test", 
        required=True,
        ondelete="cascade"
    )
    version = fields.Integer(string="Version", required=True)
    date = fields.Datetime(string="Date", default=lambda self: fields.Datetime.now(), required=True)
    user_id = fields.Many2one("res.users", string="Auteur", default=lambda self: self.env.user, required=True)
    description = fields.Text(string="Description des modifications")
    preconditions = fields.Text(string="Préconditions")
    step_snapshot = fields.Text(string="Étapes (snapshot)")  
    expected_snapshot = fields.Text(string="Résultats attendus (snapshot)")

    # Permet de copier les infos d’un cas de test lors d’une mise à jour
    @api.model
    def create_from_case(self, case):
        """Crée un enregistrement d'historique à partir d'un cas de test"""
        return self.create({
            "case_id": case.id,
            "version": case.version,
            "user_id": self.env.user.id,
            "description": case.description,
            "preconditions": case.preconditions,
            "step_snapshot": "\n".join([f"{s.sequence}. {s.action}" for s in case.step_ids]),
            "expected_snapshot": "\n".join([f"{s.sequence}. {s.expected_result}" for s in case.step_ids]),
        })
