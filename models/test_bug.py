from odoo import models, fields, api
from ..utils.utils import format_ref


class TestBug(models.Model):
    _name = "test.bug"
    _description = "Bug détecté lors d'une exécution"

    STATE_SELECTION = [
        ('1_new', 'Nouveau'),
        ('2_open', 'Open'),
        ('3_in_progress', 'En cours'),
        ('4_resolved', 'Résolu'),
        ('5_closed', 'Fermé'),
    ]
    
    name = fields.Char("ref", readonly=True)
    description = fields.Text("Description détaillée")
    project_id = fields.Many2one("test.project", string="Projet/Campagne")
    case_id = fields.Many2one("test.case", string="Cas de Test")
    execution_line_id = fields.Many2one("test.execution.line", string="Ligne d'exécution")
    execution_line_step_id = fields.Many2one("test.execution.line.step", string="Etape du cas de test d'exécution")
    reported_by_id = fields.Many2one("res.users", string="Signalé par", default=lambda self: self.env.user)
    assigned_to_id = fields.Many2one("res.users", string="Assigné à")
    priority = fields.Selection([
        ("0", "Très basse"),
        ("1", "Basse"),
        ("2", "Normale"),
        ("3", "Haute"),
        ("4", "Critique"),
    ], default="2", string="Priorité")
    state = fields.Selection(STATE_SELECTION, default="1_new", string="Statut", group_expand='_group_expand_states')
    attachment_ids = fields.Many2many("ir.attachment", string="Pièces jointes")

    @api.model
    def create(self, vals):
        bug = super().create(vals)

        bug_items = self.env['test.bug'].search([('project_id', '=', bug.project_id.id), ('case_id', '=', bug.case_id.id)])
        seq_ref = f"B{format_ref(len(bug_items)+1)}"
        bug.name = f"{bug.execution_line_id.name}{seq_ref}"
        bug.description = f"Action: {bug.execution_line_step_id.step_action}"


        return bug
    
    
    
    @api.model
    def _group_expand_states(self, states, domain):
        """
        Retourne toutes les valeurs de state pour forcer l'affichage des colonnes,
        même si aucun enregistrement n'existe pour certains statuts.
        """
        return [key for key, label in self.STATE_SELECTION]