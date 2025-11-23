import odoo
from odoo import api, fields, models, tools, _, Command
from odoo.exceptions import MissingError, ValidationError, AccessError, UserError
from odoo.tools.safe_eval import safe_eval, test_python_expr
from odoo.tools.float_utils import float_compare
from datetime import date, datetime
import base64
import logging

from pytz import timezone

_logger = logging.getLogger(__name__)
_api_endpoint_code = _logger.getChild("api_endpoint_code")


class LoggerProxy:
    """ Proxy of the `_logger` element in order to be used in server actions.
    We purposefully restrict its method as it will be executed in `safe_eval`.
    """
    @staticmethod
    def log(level, message, *args, stack_info=False, exc_info=False):
        _api_endpoint_code.log(level, message, *args, stack_info=stack_info, exc_info=exc_info)

    @staticmethod
    def info(message, *args, stack_info=False, exc_info=False):
        _api_endpoint_code.info(message, *args, stack_info=stack_info, exc_info=exc_info)

    @staticmethod
    def warning(message, *args, stack_info=False, exc_info=False):
        _api_endpoint_code.warning(message, *args, stack_info=stack_info, exc_info=exc_info)

    @staticmethod
    def error(message, *args, stack_info=False, exc_info=False):
        _api_endpoint_code.error(message, *args, stack_info=stack_info, exc_info=exc_info)

    @staticmethod
    def exception(message, *args, stack_info=False, exc_info=True):
        _api_endpoint_code.exception(message, *args, stack_info=stack_info, exc_info=exc_info)




DEFAULT_PYTHON_CODE = """# Available variables:
#  - env: environment on which the action is triggered
#  - model: model of the record on which the action is triggered; is a void recordset
#  - record: record on which the action is triggered; may be void
#  - records: recordset of all records on which the action is triggered in multi-mode; may be void
#  - time, datetime, dateutil, timezone: useful Python libraries
#  - float_compare: utility function to compare floats based on specific precision
#  - b64encode, b64decode: functions to encode/decode binary data
#  - log: log(message, level='info'): logging function to record debug information in ir.logging table
#  - _logger: _logger.info(message): logger to emit messages in server logs
#  - UserError: exception class for raising user-facing warning messages
#  - Command: x2many commands namespace
# To return an action, assign: action = {...}\n\n\n\n"""

class ApiEndpointCode(models.AbstractModel):
    _name = "mixin.code"
    _description = "Mixin Code Python"

    def _run_action_code_multi(self, eval_context):
        safe_eval(self.code.strip(), eval_context, mode="exec", nocopy=True, filename=str(self))  # nocopy allows to return 'action'
        return eval_context.get('action')

    def _get_eval_context(self, action=None):
        """ Prepare the context used when evaluating python code, like the
        python formulas or code server actions.

        :param action: the current server action
        :type action: browse record
        :returns: dict -- evaluation context given to (safe_)safe_eval """
        def log(message, level="info"):
            with self.pool.cursor() as cr:
                cr.execute("""
                    INSERT INTO ir_logging(create_date, create_uid, type, dbname, name, level, message, path, line, func)
                    VALUES (NOW() at time zone 'UTC', %s, %s, %s, %s, %s, %s, %s, %s, %s)
                """, (self.env.uid, 'server', self._cr.dbname, __name__, level, message, "api", action.id, action.endpoint_id.title))

        eval_context = {
            'uid': self._uid,
            'user': self.env.user,
            'time': tools.safe_eval.time,
            'datetime': tools.safe_eval.datetime,
            'dateutil': tools.safe_eval.dateutil,
            'timezone': timezone,
            'float_compare': float_compare,
            'b64encode': base64.b64encode,
            'b64decode': base64.b64decode,
            'Command': Command,
        }
        
        model_name = action.model_id.sudo().model if action.model_id else None
        model = self.env[model_name] if model_name else None
        record = None
        records = None
        if self._context.get('active_model') == model_name and self._context.get('active_id'):
            record = model.browse(self._context['active_id'])
        if self._context.get('active_model') == model_name and self._context.get('active_ids'):
            records = model.browse(self._context['active_ids'])
        eval_context.update({
            # orm
            'env': self.env,
            'model': model,
            # Exceptions
            'UserError': odoo.exceptions.UserError,
            # record
            'record': record,
            'records': records,
            # helpers
            'log': log,
            '_logger': LoggerProxy,
        })
        return eval_context

    def run(self):
        """Exécute le code Python lié à l’endpoint.
        Inspiré de ir.actions.server.run mais simplifié pour API.
        """
        res = False
        for action in self.sudo():
            # --- Vérification des droits d'accès ---
            model_name = action.model_id.model
            try:
                self.env[model_name].check_access("write")
            except AccessError:
                _logger.warning(
                    "Endpoint %r exécuté par %s sans droits sur le modèle %s",
                    action.endpoint_id.title,
                    self.env.user.login,
                    model_name,
                )
                raise

            # --- Préparation du contexte d’exécution ---
            eval_context = self._get_eval_context(action)

            # records = record ou records
            records = eval_context.get('record') or eval_context['model']
            records |= eval_context.get('records') or eval_context['model']

            if records.ids:
                try:
                    records.check_access("write")
                except AccessError:
                    _logger.warning(
                        "Accès interdit pour l’endpoint %r exécuté par %s sur %s",
                        action.endpoint_id.display_name,
                        self.env.user.login,
                        records,
                    )
                    raise

            # --- Exécution du code Python de l’endpoint ---
            _logger.info("Exécution de l’endpoint %s (%s)", action.endpoint_id.name, action.id)
            res = action._run_action_code_multi(eval_context)

        return res or False
