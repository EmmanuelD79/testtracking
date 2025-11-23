from odoo import _, api, fields, models


class TestRecipePrintWizard(models.TransientModel):
    _name = 'test.recipe.print.wizard'
    _description = 'Assistant PV de Recette'

    config_id = fields.Many2one(
        'test.recipe.report.config',
        string="Configuration",
        required=True,
        help="Choisissez la configuration de parties pour ce PV."
    )

    def action_print_report(self):
        execution = self.env['test.execution'].browse(self.env.context.get('active_id'))
        return self.env.ref('test_tracking.report_test_recipe_pv').report_action(
            execution,
            data={'config_id': self.config_id.id}
        )