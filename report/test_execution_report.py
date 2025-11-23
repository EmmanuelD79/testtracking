from odoo import models, api

class ReportTestRecipePV(models.AbstractModel):
    _name = 'testtracking.report_test_recipe_pv_document'
    _description = 'PV de Recette'

    @api.model
    def _get_report_values(self, docids, data=None):
        docs = self.env['test.execution'].browse(docids)
        return {
            'doc_ids': docids,
            'doc_model': 'test.execution',
            'docs': docs,
        }