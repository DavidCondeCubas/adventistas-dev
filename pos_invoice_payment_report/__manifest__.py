# -*- coding: utf-8 -*-
{
    "name": "Point of Sale Invoice Payment Report",
    "summary": """Point of Sale Invoice Payment Report""",
    "description": """
        Point of Sale Invoice Payment Report
    """,
    "author": "Eduwebgroup",
    "website": "http://www.eduwebgroup.com",
    "category": "Point of Sale",
    "version": "1.0",
    "depends": [
        "pos_payment_report",
        "pos_pr"
    ],
    "data": [
        "views/pos_session_views.xml",
        "report/pos_payment_report_views.xml"
    ],
}
