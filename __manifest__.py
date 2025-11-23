{
    'name': 'TestTracking',
    'version': '1.0.0',
    'summary': 'Suivi des tests fonctionnels dans Odoo',
    'description': """
        TestTracking est une application Odoo permettant de gérer
        des campagnes de tests fonctionnels, des cas de tests et leur exécution.
        """,
    'author': 'LELAB-DEV',
    'website': 'https://www.lelab-dev.fr',
    'category': 'Project',
    'depends': ['base', 'project', 'website'],
    'data': [
        'security/security.xml',
        'security/ir.model.access.csv',
        'security/test_tracking_rules.xml',
        'views/test_case_views.xml',
        'views/test_execution_views.xml',
        'views/test_project_views.xml',
        'views/test_bug_views.xml',
        'views/api_endpoint_views.xml',
        'views/test_tracking_actions.xml',
        'views/test_tracking_menu.xml',
        'views/test_recipe_report_config_views.xml',
        'report/report_test_recipe_pv.xml',
        'report/ir_action_report.xml',
        'views/swagger_templates.xml',
        'demo/demo.xml'
    ],
    # 'demo': [
    #     'demo/demo.xml',
    # ],
    'assets': {
        'web.assets_backend': [
            # tes fichiers CSS/JS si besoin
        ],
        'web.assets_frontend': [
        ]
    },
    'application': True,
    'license': 'LGPL-3',
    'images': ['static/description/icon.png'],
}
