from odoo import _, api, fields, models


class TestExecution(models.Model):
    _name = 'test.execution'
    _description = 'Execution du test'

    STATE_SELECTION = [
        ('1_draft', 'Draft'),
        ('2_in_progress', 'In progress'),
        ('3_failed', 'Failed'),
        ('4_done', 'Done'),
    ]

    name = fields.Char('name')
    project_id = fields.Many2one('test.project', string='Projet/Campagne', ondelete='cascade')
    date = fields.Datetime('date')
    tester_id = fields.Many2one('res.users', string='tester')
    execution_line_ids = fields.One2many('test.execution.line', 'execution_id', string='execution_line')
    status = fields.Selection(STATE_SELECTION, string='status', default='1_draft', group_expand='_group_expand_states')

    @api.model
    def create(self, vals):
        """Lors de la création d'une exécution, créer automatiquement les lignes
        correspondant aux cas de test du projet/campagne."""
        execution = super().create(vals)

        if execution.project_id:
            # Récupérer tous les cas de tests du projet
            test_cases = self.env['test.case'].search([('project_id', '=', execution.project_id.id),('status', '=', '2_ready')])
            lines = []
            for case in test_cases:
                lines.append((0, 0, {
                    'execution_id': execution.id,
                    'case_id': case.id,
                    'status': 'not_run'
                }))
            if lines:
                execution.write({'execution_line_ids': lines})

        return execution

    @api.model
    def _group_expand_states(self, status, domain):
        """
        Retourne toutes les valeurs de state pour forcer l'affichage des colonnes,
        même si aucun enregistrement n'existe pour certains statuts.
        """
        return [key for key, label in self.STATE_SELECTION]


