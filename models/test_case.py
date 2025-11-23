from odoo import _, api, fields, models


class TestCase(models.Model):
    _name = 'test.case'
    _description = 'Cas de Test'

    STATE_SELECTION = [
        ('1_draft', 'Draft'),
        ('2_ready', 'Ready'),
        ('3_obsolete', 'Obsolete')
    ]

    name = fields.Char('name')
    project_id = fields.Many2one('test.project', string='project')
    description = fields.Text('description')
    preconditions = fields.Text('preconditions')
    priority = fields.Selection([
        ('high', 'High'),
        ('medium', 'Medium'),
        ('low', 'Low')
    ], string='priority')
    status = fields.Selection(STATE_SELECTION, string='status', default='1_draft', group_expand='_group_expand_states')
    step_ids = fields.One2many('test.step', 'case_id', string='step')
    version = fields.Integer('version')
    history_ids = fields.One2many('test.case.history', 'case_id', string='history')

    @api.model
    def _group_expand_states(self, states, domain):
        """
        Retourne toutes les valeurs de state pour forcer l'affichage des colonnes,
        même si aucun enregistrement n'existe pour certains statuts.
        """
        return [key for key, label in self.STATE_SELECTION]