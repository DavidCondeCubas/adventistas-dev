# -*- coding: utf-8 -*-
{
    "name": "Point of Sale Payment Report",
    "summary": """Point of Sale Payment Report""",
    "description": """
        Point of Sale Payment Report
    """,
    "author": "Eduwebgroup",
    "website": "http://www.eduwebgroup.com",
    "category": "Point of Sale",
    "version": "1.0",
    "depends": [
        "point_of_sale"
    ],
    "data": [
        "security/ir.model.access.csv",
        "report/pos_payment_report_views.xml",
        "views/pos_session_views.xml"
    ],
}
