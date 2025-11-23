from odoo import _, api, fields, models
from ..utils.utils import format_ref

class TestExecutionLineStep(models.Model):
    _name = 'test.execution.line.step'
    _description = "Étape spécifique dans une ligne d'exécution"

    execution_line_id = fields.Many2one('test.execution.line', string="Ligne d'exécution")
    name = fields.Char(string='Référence', readonly=True, copy=False, default='Nouveau')
    step_id = fields.Many2one('test.step', string="Étape")
    status = fields.Selection([
        ('1_not_run', 'Non exécuté'),
        ('2_run', 'Exécuté'),
        ('3_success', 'Réussi'),
        ('4_failed', 'Échoué'),
        ('5_blocked', 'Bloqué')
    ], string="Statut", default='1_not_run')
    bug_id = fields.Many2one('test.bug', string="Bug lié")
    step_sequence = fields.Integer(
        string="Séquence", related='step_id.sequence', store=False, readonly=True)
    step_action = fields.Text(
        string="Action", related='step_id.action', store=False, readonly=True)
    step_expected_result = fields.Text(
        string="Résultat attendu", related='step_id.expected_result', store=False, readonly=True)


    @api.model
    def create(self, vals):
        execution_line_step = super().create(vals)

        sequence_ref = f"S{format_ref(execution_line_step.step_sequence)}"
        execution_line_step.name = f"{execution_line_step.execution_line_id.name}{sequence_ref}"

        return execution_line_step

    def action_report_bug(self):
        """Créer automatiquement une fiche bug à partir de la ligne d'exécution"""
        self.ensure_one()
        bug = self.env["test.bug"].create({
            "project_id": self.execution_line_id.execution_id.project_id.id,
            "case_id": self.execution_line_id.case_id.id,
            "execution_line_id": self.execution_line_id.id,
            "execution_line_step_id": self.id,
            "reported_by_id": self.env.user.id,
        })
        self.bug_id = bug.id
        return {
            "type": "ir.actions.act_window",
            "res_model": "test.bug",
            "view_mode": "form",
            "res_id": bug.id,
            "target": "current"
        }
