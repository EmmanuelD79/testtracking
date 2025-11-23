from odoo import _, api, fields, models


class TestProject(models.Model):
    _name = "test.project"
    _description = "Projet de test fonctionnel"

    STATE_SELECTION = [
        ('1_draft', 'Draft'),
        ('2_active', 'Active'),
        ('3_closed', 'Closed'),
    ]

    name = fields.Char('name')
    description = fields.Text('description')
    responsible_id = fields.Many2one('res.users', string='responsible')
    test_case_ids = fields.One2many('test.case', 'project_id', string='test_case')
    execution_ids = fields.One2many('test.execution', 'project_id', string='execution')
    state = fields.Selection(STATE_SELECTION, string='state', default='1_draft', group_expand='_group_expand_states')
    active = fields.Boolean('active', default=True)
    manager_ids = fields.Many2many(
        'res.users',
        'test_project_manager_rel',
        'project_id', 'user_id',
        string="Managers"
    )
    tester_ids = fields.Many2many(
        'res.users',
        'test_project_tester_rel',
        'project_id', 'user_id',
        string="Testers"
    )

    test_case_count = fields.Integer("Cas de tests", compute="_compute_stats")
    execution_count = fields.Integer("Exécutions", compute="_compute_stats")
    bug_count = fields.Integer("Bug", compute="_compute_stats")
    success_rate = fields.Float("Taux de succès (%)", compute="_compute_stats")

    @api.depends("test_case_ids", "execution_ids.execution_line_ids.status", "execution_ids.execution_line_ids.execution_step_ids.bug_id")
    def _compute_stats(self):
        for project in self:
            project.test_case_count = len(project.test_case_ids)
            project.execution_count = len(project.execution_ids)
            project.bug_count = len(project.execution_ids.execution_line_ids.execution_step_ids.bug_id)
            # Calcul taux de succès global
            lines = project.execution_ids.mapped("execution_line_ids")
            total = len(lines)
            success = len(lines.filtered(lambda l: l.status == "success"))
            project.success_rate = (success / total * 100) if total > 0 else 0

    # Boutons pour naviguer
    def action_view_cases(self):
        return {
            "type": "ir.actions.act_window",
            "name": "Cas de Tests",
            "res_model": "test.case",
            "view_mode": "kanban,list,form",
            "domain": [("project_id", "=", self.id)],
            "context": {"default_project_id": self.id},
        }

    def action_view_executions(self):
        return {
            "type": "ir.actions.act_window",
            "name": "Exécutions",
            "res_model": "test.execution",
            "view_mode": "kanban,list,form",
            "domain": [("project_id", "=", self.id)],
            "context": {"default_project_id": self.id},
        }

    def action_view_bug(self):
        return {
            "type": "ir.actions.act_window",
            "name": "Bug",
            "res_model": "test.bug",
            "view_mode": "kanban,list,form",
            "domain": [("project_id", "=", self.id)],
            "context": {"default_project_id": self.id},
        }

    def action_view_success_rate(self):
        return {
            "type": "ir.actions.act_window",
            "name": "Résultats des Cas de Tests",
            "res_model": "test.execution.line",
            "view_mode": "graph,pivot,list",
            "domain": [("execution_id.project_id", "=", self.id)],
        }

    @api.model
    def _group_expand_states(self, states, domain):
        """
        Retourne toutes les valeurs de state pour forcer l'affichage des colonnes,
        même si aucun enregistrement n'existe pour certains statuts.
        """
        return [key for key, label in self.STATE_SELECTION]
