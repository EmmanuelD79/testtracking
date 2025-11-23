from odoo import _, api, fields, models


class TestStep(models.Model):
    _name = 'test.step'
    _description = 'Etape de test'
    _order = "sequence, id"

    case_id = fields.Many2one('test.case', string='case')
    sequence = fields.Integer('sequence', default=1)
    action = fields.Text('action')
    expected_result = fields.Text('expected_result')

    @api.model
    def create(self, vals):
        if vals.get("case_id"):
            last_seq = self.search([
                ("case_id", "=", vals["case_id"])
            ], order="sequence desc", limit=1).sequence
            vals["sequence"] = last_seq + 1 if last_seq else 1
        return super().create(vals)

    def write(self, vals):
        res = super().write(vals)
        if "sequence" in vals or "case_id" in vals:
            for step in self:
                step._resequence_case()
        return res

    def _resequence_case(self):
        """Réordonne toutes les étapes du cas de test pour éviter les trous ou doublons."""
        if not self.case_id:
            return
        steps = self.search([("case_id", "=", self.case_id.id)], order="sequence, id")
        for idx, step in enumerate(steps, start=1):
            if step.sequence != idx:
                step.sequence = idx
