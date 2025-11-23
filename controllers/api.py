import json
from odoo import http
from odoo.http import request, Response
from werkzeug.exceptions import Unauthorized
from odoo.exceptions import AccessDenied
from odoo.addons.base.models.ir_http import IrHttp
import re

import logging

_logger = logging.getLogger(__name__)


API_BASE = "/api/v1"

def _json(data, status=200):
    return Response(
        json.dumps(data, default=str, ensure_ascii=False),
        status=status,
        content_type="application/json"
    )

class TestTrackingApiController(http.Controller):

    @http.route('/api/<path:subpath>', type='http', auth='none', csrf=False, methods=['GET', 'POST', 'PUT', 'DELETE'], cors="*")
    def dynamic_api(self, subpath, **kwargs):
        method = request.httprequest.method  # GET, POST, PUT, DELETE
        full_path = f"/api/{subpath}"

        # 1. Chercher un endpoint qui match par URL + méthode
        endpoint = request.env['api.endpoint'].sudo().search([('method', '=', method.upper())])

        for ep in endpoint:
            regex, type_map = ep.endpoint_url_to_regex(ep.url)
            m = re.match(regex, full_path, flags=re.IGNORECASE)
            if not m:
                continue

            if ep.security:              
                try:
                    IrHttp._auth_method_bearer()
                except Exception as e:
                    #_logger.warning(f"[DynamicAPI] Auth failed: {e}")
                    # Retourne une erreur 401 si l'authentification échoue
                    raise Unauthorized("Invalid or missing Bearer token")
            
            params = m.groupdict()
            # Conversion des types
            path_params = {}
            for key, value in params.items():
                typ = type_map.get(key)
                if typ == 'int':
                    path_params[key] = int(value)
                elif typ == 'float':
                    path_params[key] = float(value)
                else:
                    path_params[key] = value  # path, uuid ou None restent en str

            query_params = dict(request.params)  # ?page=2&status=done
            headers = dict(request.httprequest.headers)

            body_data = {}
            if method in ("POST", "PUT"):
                try:
                    body_data = json.loads(request.httprequest.data.decode("utf-8"))
                except Exception:
                    body_data = {}

            eval_context = ep._get_eval_context(ep)
            eval_context.update({
                "params": path_params,
                "query": query_params,
                "headers": headers,
                "body": body_data,
            })
            # Exécuter le code Python lié à l’endpoint
            result = ep._run_action_code_multi(eval_context)

            # Retourner JSON
            return _json(result or {"status": "ok"})

        return request.not_found()

    # @http.route(f"{API_BASE}/projects",  type='http', auth='bearer', methods=['GET'], cors="*")
    # def get_test_projects(self, **kwargs):
    #     user = request.env.user
    #     if not user or user._is_public():
    #         return _json({"error": "Unauthorized"}, status=401)

    #     projects = request.env['test.project'].sudo().search([])
    #     data = [
    #         {
    #             "id": p.id,
    #             "name": p.name,
    #             "description": p.description if p.description else '',
    #             "responsible": {
    #                 "responsible_id": p.responsible_id.id,
    #                 "responsable_login": p.responsible_id.login
    #             },
    #             "state": p.state,
    #             "managers": [{
    #                 "manager_id": manager.id,
    #                 "manager_login": manager.login
    #             } for manager in p.manager_ids],
    #             "testers": [{
    #                 "tester_id": tester.id,
    #                 "tester_login": tester.login
    #             } for tester in p.tester_ids]
    #         } for p in projects
    #     ]
    #     return _json(data)
    
    # @http.route(f"{API_BASE}/projects/<int:id>",  type='http', auth='bearer', methods=['GET'], cors="*")
    # def get_test_projects_info(self, id, **kwargs):
    #     user = request.env.user
    #     if not user or user._is_public():
    #         return _json({"error": "Unauthorized"}, status=401)
    #     project = request.env['test.project'].sudo().browse(id)
    #     if not project.exists():
    #         return _json({'error': 'Project not found'})
    #     data = {
    #         "id": project.id,
    #         "name": project.name,
    #         "responsible": {
    #             "responsible_id": project.responsible_id.id,
    #             "responsable_login": project.responsible_id.login
    #         },
    #         "test_case": [{
    #             "test_case_id": case.id,
    #             "test_case_name": case.name
    #         } for case in project.test_case_ids],
    #         "execution": [{
    #             "execution_id": execution.id,
    #             "execution_name": execution.name
    #         } for execution in project.execution_ids],
    #         "state": project.state,
    #         "managers": [{
    #             "manager_id": manager.id,
    #             "manager_login": manager.login
    #         } for manager in project.manager_ids],
    #         "testers": [{
    #             "tester_id": tester.id,
    #             "tester_login": tester.login
    #         } for tester in project.tester_ids]
    #     }
    #     return _json(data)

    # @http.route(f"{API_BASE}/projects/<int:id>/test_case",  type='http', auth='bearer', methods=['GET'], cors="*")
    # def get_test_case(self, id, **kwargs):
    #     user = request.env.user
    #     if not user or user._is_public():
    #         return _json({"error": "Unauthorized"}, status=401)
    #     project = request.env['test.project'].sudo().browse(id)
    #     if not project.exists():
    #         return _json({'error': 'Project not found'})
    #     data = [{
    #         'name': case.name,
    #         'project_id': case.project_id.id,
    #         'description': case.description if case.description else '',
    #         'precondition': case.preconditions if case.preconditions else '',
    #         'priority': case.priority, 
    #         'status': case.status, 
    #         'steps': [{
    #             'case_id': step.case_id.id, 
    #             'sequence': step.sequence, 
    #             'action': step.action, 
    #             'expected_result': step.expected_result
    #         } for step in case.step_ids],
    #         'version': case.version, 
    #     } for case in project.test_case_ids]

    #     return _json(data)
    
    # @http.route(f"{API_BASE}/projects/<int:id>/bug",  type='http', auth='bearer', methods=['GET'], cors="*")
    # def get_bug(self, id, **kwargs):
    #     user = request.env.user
    #     if not user or user._is_public():
    #         return _json({"error": "Unauthorized"}, status=401)
    #     bugs = request.env['test.bug'].sudo().search([('project_id', '=', id)])
    #     data = [{
    #         'name': bug.name,
    #         'description': bug.description if bug.description else '',
    #         'project': {
    #             'project_id': bug.project_id.id,
    #             'project_name': bug.project_id.name
    #         },
    #         'case_id': {
    #             'case_id': bug.case_id.id,
    #             'case_name': bug.case_id.name
    #         },
    #         'execution_line': {
    #             'id': bug.execution_id.id,
    #             'comment': bug.execution_line_id.comment if bug.execution_line_id.comment else '',
    #             'status': bug.execution_line_id.status
    #         }, 
    #         'reporter_by': {
    #             'reporter_by_id': bug.reported_by_id.id,
    #             'reporter_by_name': bug.reporter_by_id.login
    #         }, 
    #         'assigned_to': {
    #             'assigned_to_id': bug.assigned_to_id.id,
    #             'assigned_to_name': bug.assigned_to_id.login
    #         },
    #         'priority': bug.priority,
    #         'state': bug.state, 
    #     } for bug in bugs]

    #     return _json(data)