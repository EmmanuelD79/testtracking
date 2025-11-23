from odoo import http
from odoo.http import request, Response
import json

API_BASE = "/api/v1"

class TestTrackingApiDocs(http.Controller):

    @http.route(f"{API_BASE}/docs/swagger.json", type="http", auth="public", methods=["GET"], csrf=False, cors="*")
    def swagger_json(self, **kwargs):
        endpoints = request.env["api.endpoint"].sudo()
        spec = endpoints.generate_openapi_spec()
        return Response(
            json.dumps(spec, indent=2),
            content_type="application/json"
        )


    # @http.route(f"{API_BASE}/docs/swagger.json", type="http", auth="public", methods=["GET"], csrf=False, cors="*")
    # def swagger_spec(self, **kwargs):
    #     spec = {
    #         "openapi": "3.0.0",
    #         "info": {
    #             "title": "Test Tracking API",
    #             "version": "1.0.0",
    #             "description": "API pour gérer les projets, cas de test et bugs."
    #         },
    #         "paths": {
    #             "/api/v1/projects": {
    #                 "get": {
    #                     "summary": "Lister les projets",
    #                     "tags": ["Projets"],
    #                     "security": [{"bearerAuth": []}],
    #                     "responses": {
    #                         "200": {
    #                             "description": "Liste des projets",
    #                             "content": {
    #                                 "application/json": {
    #                                     "schema": {
    #                                         "type": "array",
    #                                         "items": {
    #                                             "type": "object",
    #                                             "properties": {
    #                                                 "id": {"type": "integer"},
    #                                                 "name": {"type": "string"},
    #                                                 "description": {"type": "string"},
    #                                                 "state": {"type": "string"},
    #                                                 "responsible": {
    #                                                     "type": "object",
    #                                                     "properties": {
    #                                                         "responsible_id": {"type": "integer"},
    #                                                         "responsable_login": {"type": "string"}
    #                                                     }
    #                                                 },
    #                                                 "managers": {
    #                                                     "type": "array",
    #                                                     "items": {
    #                                                         "type": "object",
    #                                                         "properties": {
    #                                                             "manager_id": {"type": "integer"},
    #                                                             "manager_login": {"type": "string"}
    #                                                         }
    #                                                     }
    #                                                 },
    #                                                 "testers": {
    #                                                     "type": "array",
    #                                                     "items": {
    #                                                         "type": "object",
    #                                                         "properties": {
    #                                                             "tester_id": {"type": "integer"},
    #                                                             "tester_login": {"type": "string"}
    #                                                         }
    #                                                     }
    #                                                 }
    #                                             }
    #                                         }
    #                                     }
    #                                 }
    #                             }
    #                         },
    #                         "401": {"description": "Unauthorized"}
    #                     }
    #                 }
    #             },
    #             "/api/v1/projects/{id}": {
    #                 "get": {
    #                     "summary": "Détails d’un projet",
    #                     "tags": ["Projets"],
    #                     "parameters": [
    #                         {
    #                             "name": "id",
    #                             "in": "path",
    #                             "required": True,
    #                             "schema": {"type": "integer"}
    #                         }
    #                     ],
    #                     "security": [{"bearerAuth": []}],
    #                     "responses": {
    #                         "200": {
    #                             "description": "Projet détaillé",
    #                             "content": {
    #                                 "application/json": {
    #                                     "schema": {
    #                                         "type": "object",
    #                                         "properties": {
    #                                             "id": {"type": "integer"},
    #                                             "name": {"type": "string"},
    #                                             "state": {"type": "string"},
    #                                             "responsible": {
    #                                                 "type": "object",
    #                                                 "properties": {
    #                                                     "responsible_id": {"type": "integer"},
    #                                                     "responsable_login": {"type": "string"}
    #                                                 }
    #                                             },
    #                                             "test_case": {
    #                                                 "type": "array",
    #                                                 "items": {
    #                                                     "type": "object",
    #                                                     "properties": {
    #                                                         "test_case_id": {"type": "integer"},
    #                                                         "test_case_name": {"type": "string"}
    #                                                     }
    #                                                 }
    #                                             },
    #                                             "execution": {
    #                                                 "type": "array",
    #                                                 "items": {
    #                                                     "type": "object",
    #                                                     "properties": {
    #                                                         "execution_id": {"type": "integer"},
    #                                                         "execution_name": {"type": "string"}
    #                                                     }
    #                                                 }
    #                                             },
    #                                             "managers": {
    #                                                 "type": "array",
    #                                                 "items": {
    #                                                     "type": "object",
    #                                                     "properties": {
    #                                                         "manager_id": {"type": "integer"},
    #                                                         "manager_login": {"type": "string"}
    #                                                     }
    #                                                 }
    #                                             },
    #                                             "testers": {
    #                                                 "type": "array",
    #                                                 "items": {
    #                                                     "type": "object",
    #                                                     "properties": {
    #                                                         "tester_id": {"type": "integer"},
    #                                                         "tester_login": {"type": "string"}
    #                                                     }
    #                                                 }
    #                                             }
    #                                         }
    #                                     }
    #                                 }
    #                             }
    #                         },
    #                         "404": {"description": "Project not found"},
    #                         "401": {"description": "Unauthorized"}
    #                     }
    #                 }
    #             },
    #             "/api/v1/projects/{id}/test_case": {
    #                 "get": {
    #                     "summary": "Lister les cas de test d’un projet",
    #                     "tags": ["Cas de test"],
    #                     "parameters": [
    #                         {
    #                             "name": "id",
    #                             "in": "path",
    #                             "required": True,
    #                             "schema": {"type": "integer"}
    #                         }
    #                     ],
    #                     "security": [{"bearerAuth": []}],
    #                     "responses": {
    #                         "200": {
    #                             "description": "Cas de test d’un projet",
    #                             "content": {
    #                                 "application/json": {
    #                                     "schema": {
    #                                         "type": "array",
    #                                         "items": {
    #                                             "type": "object",
    #                                             "properties": {
    #                                                 "name": {"type": "string"},
    #                                                 "project_id": {"type": "integer"},
    #                                                 "description": {"type": "string"},
    #                                                 "precondition": {"type": "string"},
    #                                                 "priority": {"type": "string"},
    #                                                 "status": {"type": "string"},
    #                                                 "version": {"type": "string"},
    #                                                 "steps": {
    #                                                     "type": "array",
    #                                                     "items": {
    #                                                         "type": "object",
    #                                                         "properties": {
    #                                                             "case_id": {"type": "integer"},
    #                                                             "sequence": {"type": "integer"},
    #                                                             "action": {"type": "string"},
    #                                                             "expected_result": {"type": "string"}
    #                                                         }
    #                                                     }
    #                                                 }
    #                                             }
    #                                         }
    #                                     }
    #                                 }
    #                             }
    #                         },
    #                         "404": {"description": "Project not found"},
    #                         "401": {"description": "Unauthorized"}
    #                     }
    #                 }
    #             },
    #             "/api/v1/projects/{id}/bug": {
    #                 "get": {
    #                     "summary": "Lister les bugs d’un projet",
    #                     "tags": ["Bugs"],
    #                     "parameters": [
    #                         {
    #                             "name": "id",
    #                             "in": "path",
    #                             "required": True,
    #                             "schema": {"type": "integer"}
    #                         }
    #                     ],
    #                     "security": [{"bearerAuth": []}],
    #                     "responses": {
    #                         "200": {
    #                             "description": "Bugs d’un projet",
    #                             "content": {
    #                                 "application/json": {
    #                                     "schema": {
    #                                         "type": "array",
    #                                         "items": {
    #                                             "type": "object",
    #                                             "properties": {
    #                                                 "name": {"type": "string"},
    #                                                 "description": {"type": "string"},
    #                                                 "priority": {"type": "string"},
    #                                                 "state": {"type": "string"},
    #                                                 "project": {
    #                                                     "type": "object",
    #                                                     "properties": {
    #                                                         "project_id": {"type": "integer"},
    #                                                         "project_name": {"type": "string"}
    #                                                     }
    #                                                 },
    #                                                 "case_id": {
    #                                                     "type": "object",
    #                                                     "properties": {
    #                                                         "case_id": {"type": "integer"},
    #                                                         "case_name": {"type": "string"}
    #                                                     }
    #                                                 },
    #                                                 "execution_line": {
    #                                                     "type": "object",
    #                                                     "properties": {
    #                                                         "id": {"type": "integer"},
    #                                                         "comment": {"type": "string"},
    #                                                         "status": {"type": "string"}
    #                                                     }
    #                                                 },
    #                                                 "reporter_by": {
    #                                                     "type": "object",
    #                                                     "properties": {
    #                                                         "reporter_by_id": {"type": "integer"},
    #                                                         "reporter_by_name": {"type": "string"}
    #                                                     }
    #                                                 },
    #                                                 "assigned_to": {
    #                                                     "type": "object",
    #                                                     "properties": {
    #                                                         "assigned_to_id": {"type": "integer"},
    #                                                         "assigned_to_name": {"type": "string"}
    #                                                     }
    #                                                 }
    #                                             }
    #                                         }
    #                                     }
    #                                 }
    #                             }
    #                         },
    #                         "404": {"description": "Project not found"},
    #                         "401": {"description": "Unauthorized"}
    #                     }
    #                 }
    #             }
    #         },
    #         "components": {
    #             "securitySchemes": {
    #                 "bearerAuth": {
    #                     "type": "http",
    #                     "scheme": "bearer",
    #                     "bearerFormat": "JWT"
    #                 }
    #             }
    #         }
    #     }

    #     return Response(
    #         json.dumps(spec),
    #         content_type="application/json",
    #         status=200
    #     )

    @http.route("/api/docs", type="http", auth="public", website=True, csrf=False)
    def swagger_ui(self, **kwargs):
        return request.render("TestTracking.swagger_ui_page")
