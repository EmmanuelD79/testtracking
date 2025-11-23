from odoo import _, api, fields, models
from ..utils.utils import format_ref


class TestExecutionLine(models.Model):

    _name = 'test.execution.line'
    _description = "Ligne d'execution"

    execution_id = fields.Many2one('test.execution', string='execution')
    name = fields.Char(string='Référence', readonly=True, copy=False, default='Nouveau')
    case_id = fields.Many2one('test.case', string='case', required=True)
    execution_step_ids = fields.One2many(
            'test.execution.line.step',
            'execution_line_id',
            string='Étapes d’exécution',
            readonly=False,
    )
    status = fields.Selection([
        ('not_run', 'Not run'),
        ('success', 'Success'),
        ('failed', 'Failed'),
        ('blocked', 'Blocked')
    ], string='status')
    comment = fields.Text('comment')
    attachment_ids = fields.Many2many('ir.attachment', string="Pièces jointes")

    @api.model
    def create(self, vals):
        """Lors de la création d'une exécution, créer automatiquement les lignes
        correspondant aux cas de test du projet/campagne."""
        execution_line = super().create(vals)

        project_ref = f"P{format_ref(execution_line.execution_id.project_id.id)}"
        execution_ref = f"E{format_ref(execution_line.execution_id.id)}"
        case_ref = f"C{format_ref(execution_line.case_id.id)}"

        execution_line.name = f"{project_ref}{execution_ref}{case_ref}"

        if execution_line.case_id:
            # Récupérer tous les cas de tests du projet
            test_steps = self.env['test.step'].search([('case_id', '=', execution_line.case_id.id)])
            lines = []
            for step in test_steps:
                lines.append((0, 0, {
                    'execution_line_id': execution_line.id,
                    'step_id': step.id,
                    'status': '1_not_run'
                }))
            if lines:
                execution_line.write({'execution_step_ids': lines})

        return execution_line

