# coding: utf-8

from odoo import models, api, _
from odoo.exceptions import MissingError

class AccountChartTemplate(models.Model):
    _inherit = "account.chart.template"

    def _create_bank_journals(self, company, acc_template_ref):
        res = super(AccountChartTemplate, self)._create_bank_journals(company, acc_template_ref)
        if self == self.env.ref("l10n_adventistas.cuentas_plantilla"):

            # create analytic account groups
            analytic_grp_obj = self.env["account.analytic.group"]
            analytic_grp_obj.search([("company_id","=",company.id)]).unlink()
            analytic_grps_vals = [
                {"name": "SERVICIOS ADMINISTRATIVOS"},
                {"name": "SERVICIOS ACADEMICOS"},
                {"name": "SERVICIOS INDUSTRIALES"},
                {"name": "SERVICIOS DE APOYO"},
            ]
            analytic_grps = analytic_grp_obj
            for analytic_grp_vals in analytic_grps_vals:
                analytic_grp_vals["company_id"] = company.id
                analytic_grps += analytic_grp_obj.create(analytic_grp_vals)

            # create analytic accounts
            analytic_obj = self.env["account.analytic.account"]
            analytic_obj.search([("company_id","=",company.id)]).unlink()
            analytics_vals = [
                {"name": "Dirección General", "code": "101", "group_id": "SERVICIOS ADMINISTRATIVOS"},
                {"name": "Gerente / Administrador Financiero", "code": "102", "group_id": "SERVICIOS ADMINISTRATIVOS"},
                {"name": "Academico - Sub Dirección", "code": "103", "group_id": "SERVICIOS ADMINISTRATIVOS"},
                {"name": "Asuntos Estudiantiles - Sub Dirección", "code": "104", "group_id": "SERVICIOS ADMINISTRATIVOS"},
                {"name": "Contabilidad", "code": "105", "group_id": "SERVICIOS ADMINISTRATIVOS"},
                {"name": "Capellania", "code": "106", "group_id": "SERVICIOS ADMINISTRATIVOS"},
                {"name": "Bilingue Pre-Basica -  K4, K5", "code": "201", "group_id": "SERVICIOS ACADEMICOS"},
                {"name": "Bilingue 1er  Ciclo Basica -  1 - 3 grado", "code": "202", "group_id": "SERVICIOS ACADEMICOS"},
                {"name": "Bilingue 2do Ciclo Basica -  4 - 6 grado", "code": "203", "group_id": "SERVICIOS ACADEMICOS"},
                {"name": "Bilingue 3er  Ciclo Basica -  7 - 9 grado", "code": "204", "group_id": "SERVICIOS ACADEMICOS"},
                {"name": "Bilingue Media -  10mo a 12vo", "code": "205", "group_id": "SERVICIOS ACADEMICOS"},
                {"name": "Español Pre-Basica -  K4, K5", "code": "206", "group_id": "SERVICIOS ACADEMICOS"},
                {"name": "Español 1er  Ciclo Basica -  1 - 3 grado", "code": "207", "group_id": "SERVICIOS ACADEMICOS"},
                {"name": "Español 2do Ciclo Basica -  4 - 6 grado", "code": "208", "group_id": "SERVICIOS ACADEMICOS"},
                {"name": "Español 3er  Ciclo Basica -  7 - 9 grado", "code": "209", "group_id": "SERVICIOS ACADEMICOS"},
                {"name": "Español Media -  10mo a 12vo", "code": "210", "group_id": "SERVICIOS ACADEMICOS"},
                {"name": "Psicologia", "code": "211", "group_id": "SERVICIOS ACADEMICOS"},
                {"name": "Biblioteca", "code": "212", "group_id": "SERVICIOS ACADEMICOS"},
                {"name": "Cafeteria ", "code": "301", "group_id": "SERVICIOS INDUSTRIALES"},
                {"name": "Finca", "code": "302", "group_id": "SERVICIOS INDUSTRIALES"},
                {"name": "Glorietas", "code": "303", "group_id": "SERVICIOS INDUSTRIALES"},
                {"name": "Tiendas Escolares", "code": "304", "group_id": "SERVICIOS INDUSTRIALES"},
                {"name": "Casa de Huespedes", "code": "305", "group_id": "SERVICIOS INDUSTRIALES"},
                {"name": "Dormitorio Varones", "code": "401", "group_id": "SERVICIOS DE APOYO"},
                {"name": "Dormitorio Señoritas", "code": "402", "group_id": "SERVICIOS DE APOYO"},
                {"name": "Clinica Medica", "code": "403", "group_id": "SERVICIOS DE APOYO"},
                {"name": "Transporte", "code": "404", "group_id": "SERVICIOS DE APOYO"},
                {"name": "Generales de la Institución", "code": "405", "group_id": "SERVICIOS DE APOYO"},
                {"name": "Servicios Sistemas de Informacion", "code": "406", "group_id": "SERVICIOS DE APOYO"},
                {"name": "In-House Operation", "code": "407", "group_id": "SERVICIOS DE APOYO"},
                {"name": "Seguridad / Vigilancia", "code": "408", "group_id": "SERVICIOS DE APOYO"},
            ]
            analytics = analytic_obj
            for analytic_vals in analytics_vals:
                analytic_vals["company_id"] = company.id
                group = analytic_grps.filtered(lambda x: x.name == analytic_vals["group_id"])
                if not group:
                    raise MissingError("Cannot find analytic account group with name: %s" % analytic_vals["group_id"])
                analytic_vals["group_id"] = group[0].id
                analytics += analytic_obj.create(analytic_vals)

            # create asset models
            model_obj = self.env["account.asset"].with_context({
                "asset_type": "purchase",
                "default_asset_type": "purchase",
                "default_state": "model",
            })
            model_obj.search([("company_id","=",company.id)]).unlink()
            models_vals = [
                {
                    "name": "Edificios IASD -  ladrillos, piedra o cemento reforzado",
                    "account_asset_id": acc_template_ref[self.env.ref("l10n_adventistas.cta12177210").id],
                    "account_depreciation_id": acc_template_ref[self.env.ref("l10n_adventistas.cta12199210").id],
                    "account_depreciation_expense_id": acc_template_ref[self.env.ref("l10n_adventistas.cta61366207").id],
                    "account_analytic_id": "Generales de la Institución",
                    "method": "linear",
                    "method_number": 480,
                    "method_period": "1",
                    "prorata": True,
                },
                {
                    "name": "Residencias IASD -  ladrillos, piedra o cemento reforzado",
                    "account_asset_id": acc_template_ref[self.env.ref("l10n_adventistas.cta12177211").id],
                    "account_depreciation_id": acc_template_ref[self.env.ref("l10n_adventistas.cta12199211").id],
                    "account_depreciation_expense_id": acc_template_ref[self.env.ref("l10n_adventistas.cta61366207").id],
                    "account_analytic_id": "Generales de la Institución",
                    "method": "linear",
                    "method_number": 480,
                    "method_period": "1",
                    "prorata": True,
                },
                {
                    "name": "Mejoras a Terrenos IASD",
                    "account_asset_id": acc_template_ref[self.env.ref("l10n_adventistas.cta12177209").id],
                    "account_depreciation_id": acc_template_ref[self.env.ref("l10n_adventistas.cta12199209").id],
                    "account_depreciation_expense_id": acc_template_ref[self.env.ref("l10n_adventistas.cta61366207").id],
                    "account_analytic_id": "Generales de la Institución",
                    "method": "linear",
                    "method_number": 180,
                    "method_period": "1",
                    "prorata": True,
                },
                {
                    "name": "Otros Edificios IASD - de paneles enyesados con buena cimentación",
                    "account_asset_id": acc_template_ref[self.env.ref("l10n_adventistas.cta12177210A").id],
                    "account_depreciation_id": acc_template_ref[self.env.ref("l10n_adventistas.cta12199210").id],
                    "account_depreciation_expense_id": acc_template_ref[self.env.ref("l10n_adventistas.cta61366207").id],
                    "account_analytic_id": "Generales de la Institución",
                    "method": "linear",
                    "method_number": 180,
                    "method_period": "1",
                    "prorata": True,
                },
                {
                    "name": "Otras Residencias IASD -  de paneles enyesados con buena cimentación",
                    "account_asset_id": acc_template_ref[self.env.ref("l10n_adventistas.cta12177211A").id],
                    "account_depreciation_id": acc_template_ref[self.env.ref("l10n_adventistas.cta12199211").id],
                    "account_depreciation_expense_id": acc_template_ref[self.env.ref("l10n_adventistas.cta61366207").id],
                    "account_analytic_id": "Generales de la Institución",
                    "method": "linear",
                    "method_number": 180,
                    "method_period": "1",
                    "prorata": True,
                },
                {
                    "name": "Mobiliarios durables de oficina ",
                    "account_asset_id": acc_template_ref[self.env.ref("l10n_adventistas.cta12155205").id],
                    "account_depreciation_id": acc_template_ref[self.env.ref("l10n_adventistas.cta12199205").id],
                    "account_depreciation_expense_id": acc_template_ref[self.env.ref("l10n_adventistas.cta61366205").id],
                    "account_analytic_id": "Generales de la Institución",
                    "method": "linear",
                    "method_number": 120,
                    "method_period": "1",
                    "prorata": True,
                },
                {
                    "name": "Mobiliarios de oficina ligeros",
                    "account_asset_id": acc_template_ref[self.env.ref("l10n_adventistas.cta12155205A").id],
                    "account_depreciation_id": acc_template_ref[self.env.ref("l10n_adventistas.cta12199205").id],
                    "account_depreciation_expense_id": acc_template_ref[self.env.ref("l10n_adventistas.cta61366205").id],
                    "account_analytic_id": "Generales de la Institución",
                    "method": "linear",
                    "method_number": 72,
                    "method_period": "1",
                    "prorata": True,
                },
                {
                    "name": "Mobiliarios institucionales durables y pesados ",
                    "account_asset_id": acc_template_ref[self.env.ref("l10n_adventistas.cta12155205B").id],
                    "account_depreciation_id": acc_template_ref[self.env.ref("l10n_adventistas.cta12199205").id],
                    "account_depreciation_expense_id": acc_template_ref[self.env.ref("l10n_adventistas.cta61366205").id],
                    "account_analytic_id": "Generales de la Institución",
                    "method": "linear",
                    "method_number": 120,
                    "method_period": "1",
                    "prorata": True,
                },
                {
                    "name": "Mobiliarios institucionales y escolares ligeros ",
                    "account_asset_id": acc_template_ref[self.env.ref("l10n_adventistas.cta12155205C").id],
                    "account_depreciation_id": acc_template_ref[self.env.ref("l10n_adventistas.cta12199205").id],
                    "account_depreciation_expense_id": acc_template_ref[self.env.ref("l10n_adventistas.cta61366205").id],
                    "account_analytic_id": "Generales de la Institución",
                    "method": "linear",
                    "method_number": 60,
                    "method_period": "1",
                    "prorata": True,
                },
                {
                    "name": "Equipos de oficina ",
                    "account_asset_id": acc_template_ref[self.env.ref("l10n_adventistas.cta12155205D").id],
                    "account_depreciation_id": acc_template_ref[self.env.ref("l10n_adventistas.cta12199205").id],
                    "account_depreciation_expense_id": acc_template_ref[self.env.ref("l10n_adventistas.cta61366205").id],
                    "account_analytic_id": "Generales de la Institución",
                    "method": "linear",
                    "method_number": 60,
                    "method_period": "1",
                    "prorata": True,
                },
                {
                    "name": "Mobiliarios de dormitorios ",
                    "account_asset_id": acc_template_ref[self.env.ref("l10n_adventistas.cta12155205E").id],
                    "account_depreciation_id": acc_template_ref[self.env.ref("l10n_adventistas.cta12199205").id],
                    "account_depreciation_expense_id": acc_template_ref[self.env.ref("l10n_adventistas.cta61366205").id],
                    "account_analytic_id": "Generales de la Institución",
                    "method": "linear",
                    "method_number": 72,
                    "method_period": "1",
                    "prorata": True,
                },
                {
                    "name": "Máquinas y calentadores ",
                    "account_asset_id": acc_template_ref[self.env.ref("l10n_adventistas.cta12188208").id],
                    "account_depreciation_id": acc_template_ref[self.env.ref("l10n_adventistas.cta12199208").id],
                    "account_depreciation_expense_id": acc_template_ref[self.env.ref("l10n_adventistas.cta61366208").id],
                    "account_analytic_id": "Generales de la Institución",
                    "method": "linear",
                    "method_number": 60,
                    "method_period": "1",
                    "prorata": True,
                },
                {
                    "name": "Oficina - Computadoras de escritorio y portátiles",
                    "account_asset_id": acc_template_ref[self.env.ref("l10n_adventistas.cta12155205F").id],
                    "account_depreciation_id": acc_template_ref[self.env.ref("l10n_adventistas.cta12199205").id],
                    "account_depreciation_expense_id": acc_template_ref[self.env.ref("l10n_adventistas.cta61366205").id],
                    "account_analytic_id": "Generales de la Institución",
                    "method": "linear",
                    "method_number": 48,
                    "method_period": "1",
                    "prorata": True,
                },
                {
                    "name": "Laboratorios - Computadoras de escritorio y portátiles",
                    "account_asset_id": acc_template_ref[self.env.ref("l10n_adventistas.cta12155205G").id],
                    "account_depreciation_id": acc_template_ref[self.env.ref("l10n_adventistas.cta12199205").id],
                    "account_depreciation_expense_id": acc_template_ref[self.env.ref("l10n_adventistas.cta61366205").id],
                    "account_analytic_id": "Generales de la Institución",
                    "method": "linear",
                    "method_number": 36,
                    "method_period": "1",
                    "prorata": True,
                },
                {
                    "name": "Equipo audiovisual ",
                    "account_asset_id": acc_template_ref[self.env.ref("l10n_adventistas.cta12155205H").id],
                    "account_depreciation_id": acc_template_ref[self.env.ref("l10n_adventistas.cta12199205").id],
                    "account_depreciation_expense_id": acc_template_ref[self.env.ref("l10n_adventistas.cta61366205").id],
                    "account_analytic_id": "Generales de la Institución",
                    "method": "linear",
                    "method_number": 36,
                    "method_period": "1",
                    "prorata": True,
                },
            ]
            models = model_obj
            for model_vals in models_vals:
                model_vals["company_id"] = company.id
                account_analytic = analytics.filtered(lambda x: x.name == model_vals["account_analytic_id"])
                if not account_analytic:
                    raise MissingError("Cannot find analytic account with name: %s" % model_vals["account_analytic_id"])
                model_vals["account_analytic_id"] = account_analytic[0].id
                models += model_obj.create(model_vals)

        return res

    def _load(self, sale_tax_rate, purchase_tax_rate, company):
        res = super(AccountChartTemplate, self)._load(sale_tax_rate, purchase_tax_rate, company)
        if self == self.env.ref("l10n_adventistas.cuentas_plantilla"):

            # create departments
            dept_obj = self.env["hr.department"]
            dept_obj.search([("company_id","=",company.id)]).unlink()
            depts_vals = [
                {"name": "SERVICIOS ACADEMICOS"},
                {"name": "SERVICIOS ADMINISTRATIVOS"},
                {"name": "SERVICIOS DE APOYO"},
                {"name": "SERVICIOS INDUSTRIALES"},
                {"name": "ADMINISTRACION", "parent_id": "SERVICIOS ADMINISTRATIVOS"},
                {"name": "BIBLIOTECA", "parent_id": "SERVICIOS ACADEMICOS"},
                {"name": "CAFETERIA", "parent_id": "SERVICIOS INDUSTRIALES"},
                {"name": "CAPELLANIA", "parent_id": "SERVICIOS ADMINISTRATIVOS"},
                {"name": "CASA DE HUESPEDES", "parent_id": "SERVICIOS INDUSTRIALES"},
                {"name": "CLINICA MEDICA", "parent_id": "SERVICIOS DE APOYO"},
                {"name": "CONSEJERIA", "parent_id": "SERVICIOS ACADEMICOS"},
                {"name": "CONTABILIDAD", "parent_id": "SERVICIOS ADMINISTRATIVOS"},
                {"name": "DIRECCION - ACADEMICA", "parent_id": "SERVICIOS ADMINISTRATIVOS"},
                {"name": "DIRECCION - ASUNTOS ESTUDIANTILES", "parent_id": "SERVICIOS ADMINISTRATIVOS"},
                {"name": "DIRECCION GENERAL", "parent_id": "SERVICIOS ADMINISTRATIVOS"},
                {"name": "DORMITORIO SEÑORITAS", "parent_id": "SERVICIOS DE APOYO"},
                {"name": "DORMITORIO VARONES", "parent_id": "SERVICIOS DE APOYO"},
                {"name": "FINCA", "parent_id": "SERVICIOS INDUSTRIALES"},
                {"name": "GENERALES DE LA INSTITUCION", "parent_id": "SERVICIOS DE APOYO"},
                {"name": "GLORIETAS", "parent_id": "SERVICIOS INDUSTRIALES"},
                {"name": "IN-HOUSE OPERATION", "parent_id": "SERVICIOS DE APOYO"},
                {"name": "PSICOLOGIA", "parent_id": "SERVICIOS ACADEMICOS"},
                {"name": "SEGURIDAD / VIGILANCIA", "parent_id": "SERVICIOS DE APOYO"},
                {"name": "SERVICIOS SISTEMAS DE INFORMACION", "parent_id": "SERVICIOS DE APOYO"},
                {"name": "SUB DIRECCION - BILINGUE ", "parent_id": "SERVICIOS ACADEMICOS"},
                {"name": "SUB DIRECCION - BILINGUE PRE-BASICA", "parent_id": "SERVICIOS ACADEMICOS"},
                {"name": "SUB DIRECCION - ESPAÑOL", "parent_id": "SERVICIOS ACADEMICOS"},
                {"name": "SUB DIRECCION BILINGUE BASICA", "parent_id": "SERVICIOS ACADEMICOS"},
                {"name": "SUB DIRECCION BILINGUE MEDIA", "parent_id": "SERVICIOS ACADEMICOS"},
                {"name": "SUB DIRECCION ESPAÑOL BASICA", "parent_id": "SERVICIOS ACADEMICOS"},
                {"name": "SUB DIRECCION ESPAÑOL MEDIA", "parent_id": "SERVICIOS ACADEMICOS"},
                {"name": "SUB DIRECCION ESPAÑOL PRE-BASICA", "parent_id": "SERVICIOS ACADEMICOS"},
                {"name": "TIENDAS ESCOLARES", "parent_id": "SERVICIOS INDUSTRIALES"},
                {"name": "TRANSPORTE", "parent_id": "SERVICIOS DE APOYO"},
            ]
            depts = dept_obj
            for dept_vals in depts_vals:
                dept_vals["company_id"] = company.id
                if dept_vals.get("parent_id"):
                    parent = depts.filtered(lambda x: x.name == dept_vals["parent_id"])
                    if not parent:
                        raise MissingError("Cannot find department with name: %s" % dept_vals["parent_id"])
                    dept_vals["parent_id"] = parent[0].id
                depts += dept_obj.create(dept_vals)

            # create job positions
            job_obj = self.env["hr.job"]
            job_obj.search([("company_id","=",company.id)]).unlink()
            jobs_vals = [
                {"name": "DIRECTOR GENERAL", "department_id": "SERVICIOS ADMINISTRATIVOS / DIRECCION GENERAL"},
                {"name": "ASISTENTE DIRECCION", "department_id": "SERVICIOS ADMINISTRATIVOS / DIRECCION GENERAL"},
                {"name": "ADMINISTRADOR(A)", "department_id": "SERVICIOS ADMINISTRATIVOS / ADMINISTRACION"},
                {"name": "SECRETARIA ADMINISTRATIVA", "department_id": "SERVICIOS ADMINISTRATIVOS / ADMINISTRACION"},
                {"name": "DIRECTOR ACADEMICO ESPAÑOL", "department_id": "SERVICIOS ADMINISTRATIVOS / DIRECCION - ACADEMICA"},
                {"name": "DIRECTOR ACADEMICO PRE-ESCOLAR Y ESC BILINGUE", "department_id": "SERVICIOS ADMINISTRATIVOS / DIRECCION - ACADEMICA"},
                {"name": "DIRECTOR ACADEMICO ACADEMIA BILINGUE", "department_id": "SERVICIOS ADMINISTRATIVOS / DIRECCION - ACADEMICA"},
                {"name": "SECRETARIA ACADEMICA", "department_id": "SERVICIOS ADMINISTRATIVOS / DIRECCION - ACADEMICA"},
                {"name": "ASISTENTE ADMINISTRATIVO 1", "department_id": "SERVICIOS ADMINISTRATIVOS / CONTABILIDAD"},
                {"name": "ASISTENTE ADMINISTRATIVO 2", "department_id": "SERVICIOS ADMINISTRATIVOS / CONTABILIDAD"},
                {"name": "CAPELLANIA", "department_id": "SERVICIOS ADMINISTRATIVOS / CAPELLANIA"},
                {"name": "MAESTRA PRE-ESCOLAR BILINGUE", "department_id": "SERVICIOS ACADEMICOS / SUB DIRECCION - BILINGUE PRE-BASICA"},
                {"name": "ASISTENTE PRE-ESCOLAR BILINGUE", "department_id": "SERVICIOS ACADEMICOS / SUB DIRECCION - BILINGUE PRE-BASICA"},
                {"name": "MAESTRO(A) SCIENCE 1-6 BILINGUE", "department_id": "SERVICIOS ACADEMICOS / SUB DIRECCION BILINGUE BASICA"},
                {"name": "MAESTRO(A) COMPUTER 1-6 BILINGUE", "department_id": "SERVICIOS ACADEMICOS / SUB DIRECCION BILINGUE BASICA"},
                {"name": "MAESTRA(O)S 1-3 GRADO BILINGUE", "department_id": "SERVICIOS ACADEMICOS / SUB DIRECCION BILINGUE BASICA"},
                {"name": "MAESTRA(O)S 4-6 GRADO BILINGUE", "department_id": "SERVICIOS ACADEMICOS / SUB DIRECCION BILINGUE BASICA"},
                {"name": "PROFESORES NIVEL BASICA 7-9 BILINGUE", "department_id": "SERVICIOS ACADEMICOS / SUB DIRECCION BILINGUE BASICA"},
                {"name": "PROFESORES NIVEL MEDIA BILINGUE", "department_id": "SERVICIOS ACADEMICOS / SUB DIRECCION BILINGUE MEDIA"},
                {"name": "MAESTRA PRE-ESCOLAR ESPAÑOL", "department_id": "SERVICIOS ACADEMICOS / SUB DIRECCION ESPAÑOL PRE-BASICA"},
                {"name": "ASISTENTE PRE-ESCOLAR ESPAÑOL", "department_id": "SERVICIOS ACADEMICOS / SUB DIRECCION ESPAÑOL PRE-BASICA"},
                {"name": "MAESTRO(A)S 1-3 GRADO ESPAÑOL", "department_id": "SERVICIOS ACADEMICOS / SUB DIRECCION ESPAÑOL BASICA"},
                {"name": "MAESTRO(A)S 4-6 GRADO ESPAÑOL", "department_id": "SERVICIOS ACADEMICOS / SUB DIRECCION ESPAÑOL BASICA"},
                {"name": "PROFESORES NIVEL BASICA 7-9 ESPAÑOL", "department_id": "SERVICIOS ACADEMICOS / SUB DIRECCION ESPAÑOL BASICA"},
                {"name": "PROFESOR(A) ESPAÑOL SECUNDARIA", "department_id": "SERVICIOS ACADEMICOS / SUB DIRECCION ESPAÑOL BASICA"},
                {"name": "PROFESORES NIVEL MEDIA ESPAÑOL", "department_id": "SERVICIOS ACADEMICOS / SUB DIRECCION ESPAÑOL MEDIA"},
                {"name": "BIBLIOTECARIOS", "department_id": "SERVICIOS ACADEMICOS / BIBLIOTECA"},
                {"name": "PSICOLOGO(A)", "department_id": "SERVICIOS ACADEMICOS / PSICOLOGIA"},
                {"name": "CONSEJEROS", "department_id": "SERVICIOS ACADEMICOS / CONSEJERIA"},
                {"name": "ASISTENTES CAFETERIA", "department_id": "SERVICIOS INDUSTRIALES / CAFETERIA"},
                {"name": "ASISTENTES - GLORIETAS", "department_id": "SERVICIOS INDUSTRIALES / GLORIETAS"},
                {"name": "ASISTENTES TIENDAS ESCOLARES - COPIADORAS", "department_id": "SERVICIOS INDUSTRIALES / TIENDAS ESCOLARES"},
                {"name": "PRECEPTOR", "department_id": "SERVICIOS DE APOYO / DORMITORIO VARONES"},
                {"name": "PRECEPTORA", "department_id": "SERVICIOS DE APOYO / DORMITORIO SEÑORITAS"},
                {"name": "IT TECNOLOGIAS DE LA INFORMACION", "department_id": "SERVICIOS DE APOYO / SERVICIOS SISTEMAS DE INFORMACION"},
                {"name": "MANTENIMIENTO", "department_id": "SERVICIOS DE APOYO / IN-HOUSE OPERATION"},
                {"name": "PLANTEL", "department_id": "SERVICIOS DE APOYO / IN-HOUSE OPERATION"},
                {"name": "VIGILANTES", "department_id": "SERVICIOS DE APOYO / SEGURIDAD / VIGILANCIA"},
            ]
            jobs = job_obj
            for job_vals in jobs_vals:
                job_vals["company_id"] = company.id
                department = depts.filtered(lambda x: x.display_name == job_vals["department_id"])
                if not department:
                    raise MissingError("Cannot find department with name: %s" % job_vals["department_id"])
                job_vals["department_id"] = department[0].id
                jobs += job_obj.create(job_vals)

        return res