# -*- coding: utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing details.
#
# Please note that these reports are not multi-currency !!!
#
from odoo import api, fields, models, tools, _


class GradeLevelStudentCountReport(models.Model):
    _name = "grade.level.student.count.report"
    _description = "View object for Reporting Student Count per"
    _auto = False
    _order = 'grade_level_sequence, student_order_type'

    res_id = fields.Integer('related id')
    grade_level_sequence = fields.Integer('grade level sequence')
    res_model = fields.Char('related model')
    next_grade_level_id = fields.Many2one('school_base.grade_level', 'Next Year\'s Grade Level', readonly=True)
    student_count = fields.Integer('Student Count', readonly=True)
    student_count_type = fields.Char(string="Student Count Type", readonly=True)
    school_code_id = fields.Many2one('school_base.school_code', 'School Code', readonly=True)
    student_order_type = fields.Integer()

    @api.model
    def read_group(self, domain, fields, groupby, offset=0, limit=None, orderby=False, lazy=True):
        groupby = groupby or []
        groupby.append('student_order_type')
        groupby.append('grade_level_sequence')
        res = super().read_group(domain, fields, groupby, offset, limit, orderby='grade_level_sequence, student_order_type', lazy=lazy)
        return res

    def init(self):
        # if self.is_stage_installed('adm.rereenrollment'):
        #     extra_with_sql,extra_union_sql = self._reenrollment_sql()
        # else:
        #     extra_with_sql,extra_union_sql = self._no_reenrollment_sql()
        # report_sql = self._report_sql(extra_with_sql=extra_with_sql, extra_union_sql=extra_union_sql)
        tools.drop_view_if_exists(self.env.cr, self._table)
        self.env.cr.execute("""CREATE or REPLACE VIEW %s as (
            %s
            %s
            %s
            %s
            )""" % (
            self._table,
            self._sql_cte_tables(),
            self._select(),
            self._from(),
            self._where()
            )
        )
        print("""CREATE or REPLACE VIEW %s as (
            %s
            %s
            %s
            %s
            )""" % (
            self._table,
            self._sql_cte_tables(),
            self._select(),
            self._from(),
            self._where()
            ))

    @api.model
    def _get_cte_names(self):
        """ This is used for translations """
        return {
            'capacity': _("Capacity"),
            'next_year_enrolled': _("Next year enrolled"),
            'inquiries': _("Inquiries"),
            'applications': _("Applications"),
            }

    @api.model
    def _sql_cte_tables(self):
        """ This is used to create the report
            This query uses """
        return """ 
        WITH 
        enrolled_students AS (
            SELECT  students.id AS res_id,
                    students.next_grade_level_id AS next_grade_level_id,
                    COUNT(students.id) as student_count,
                    '%(next_year_enrolled)s' as student_count_type,
                    50 as student_order_type,
                    'res.partner' AS res_model
            FROM    res_partner students
            INNER   JOIN school_base_enrollment_status status
                        ON students.student_next_status_id = status.id
            WHERE   students.person_type = 'student' 
                    AND next_grade_level_id IS NOT NULL
                    AND status.key in ('enrolled')
            GROUP   BY students.grade_level_id, students.id
        ),
        inquiries AS (
            SELECT  inquiry.id as res_id,
                    inquiry.grade_level_id as next_grade_level_id,
                    COUNT(inquiry.id) as student_count,
                    '%(inquiries)s' as student_count_type,
                    0 as student_order_type,
                    'adm.inquiry' AS res_model
            FROM    adm_inquiry inquiry
            INNER   JOIN adm_inquiry_status status
                        ON status.id = inquiry.status_id
            WHERE   inquiry.partner_id NOT IN (SELECT res_id FROM enrolled_students)
                    AND status.type_id in ('stage')
                    AND inquiry.grade_level_id IS NOT NULL
            GROUP   BY inquiry.grade_level_id, inquiry.id
        ),
        applications AS (
            SELECT  app.id AS res_id,
                    app.grade_level_id AS next_grade_level_id,
                    COUNT(app.id) AS student_count,
                    '%(applications)s' AS student_count_type,
                    10 AS student_order_type,
                    'adm.application' AS res_model
            FROM    adm_application app
            INNER   JOIN adm_application_status status
                        ON status.id = app.status_id
            WHERE   app.partner_id NOT IN (SELECT res_id FROM enrolled_students)
                    AND status.type_id IN ('started', 'return','stage',  'submitted')
            GROUP   BY app.grade_level_id, app.id
        ),
        grade_capacity AS (
            SELECT  grade.id as res_id,
                    grade.id as next_grade_level_id,
                    COALESCE (grade.capacity, 0) AS student_count,
                    '%(capacity)s' as student_count_type,
                    60 as student_order_type,
                    'school_base.grade_level' AS res_model
            FROM    school_base_grade_level grade
            GROUP   BY grade.id
        ) """ % self._get_cte_names()

    @api.model
    def _select(self):
        return """
        SELECT  ROW_NUMBER () OVER (ORDER BY grade.sequence, student_order_type, res_id) AS ID,
        cteUnion.*,
        grade.school_code_id,
        grade.sequence AS grade_level_sequence
        """

    @api.model
    def _from(self):
        return """
            FROM (
                %s
            ) cteUnion
            LEFT    JOIN school_base_grade_level grade
                        ON grade.id = cteUnion.next_grade_level_id
        """ % self._from_union()

    @api.model
    def _from_union(self):
        return """
        SELECT * FROM inquiries
        UNION ALL
        SELECT * FROM applications
        UNION ALL
        SELECT * FROM grade_capacity
        UNION ALL
        SELECT * FROM enrolled_students
        """

    @api.model
    def _where(self):
        return "WHERE   grade.active_admissions = TRUE"

    def is_stage_installed(self, stage):
        stage_model = self.env['ir.model'].search([('model', '=', stage)])

        if stage_model:
            return True
        return False

    def _report_sql(self, extra_union_sql=None, extra_with_sql=None):
        sql = """
        with report as (
            with grade_capacity as (
                -- Capacity
                SELECT
                    grade.id as id,
                    grade.id as next_grade_level_id,
                    CASE
                        WHEN grade.capacity is NULL THEN 0
                        ELSE grade.capacity
                    END as student_count,
                    'Capacity' as student_count_type,
                    50 as student_order_type
                    FROM school_base_grade_level grade
                    GROUP by grade.id
            ),
            enrolled_students as (
                -- Enrolled
                SELECT
                    grade.id as id,
                    grade.id as next_grade_level_id,
                    COUNT(student.id) as student_count,
                    'Next Year Enrolled' as student_count_type,
                    60 as student_order_type
                    FROM school_base_grade_level grade
                    LEFT JOIN res_partner student
                        ON grade.id = student.next_grade_level_id
                    LEFT JOIN school_base_enrollment_status status
                        on student.student_next_status_id = status.id
                    WHERE
                        student.person_type = 'student' AND
                        status.key in ('enrolled', 'pre-enrolled')
                    GROUP by grade.id
            ),
            grade_availability as (
                -- Available
                SELECT
                    grade.id as id,
                    grade.id as next_grade_level_id,
                    CASE
                        WHEN grade.capacity is NULL THEN 0
                    ELSE
                        grade.capacity - COUNT(student.id)
                    END as student_count,
                    'Available' as student_count_type,
                    70 as student_order_type
                    FROM school_base_grade_level grade
                    LEFT JOIN res_partner student
                        ON grade.id = student.next_grade_level_id
                    LEFT JOIN school_base_enrollment_status status
                        on student.student_next_status_id = status.id
                    WHERE
                        student.person_type = 'student' AND
                        status.key in ('enrolled', 'pre-enrolled')
                    GROUP by grade.id
            ),
            grade_application as (
                -- Applications
                SELECT
                    grade.id as id,
                    grade.id as next_grade_level_id,
                    COUNT(application.id) as student_count,
                    'Applications' as student_count_type,
                    10 as student_order_type
                    FROM school_base_grade_level grade
                    LEFT JOIN adm_application application
                        ON application.grade_level_id = grade.id
                    LEFT JOIN adm_application_status status
                        ON status.id = application.status_id
                    WHERE status.type_id in ('started', 'return','stage',  'submitted')
                    GROUP BY grade.id
            ),
            grade_inquiry as (
                    -- Inquiries
                    SELECT
                        grade.id as id,
                        grade.id as next_grade_level_id,
                        COUNT(inquiry.id) as student_count,
                        'Inquiries' as student_count_type,
                        0 as student_order_type
                        FROM school_base_grade_level grade
                        LEFT JOIN adm_inquiry inquiry
                            ON inquiry.current_grade_level_id = grade.id
                        LEFT JOIN adm_inquiry_status status
                            ON status.id = inquiry.status_id
                        WHERE status.type_id in ('stage')
                        GROUP BY grade.id
            ){extra_with_sql}
            SELECT * from grade_availability
            UNION ALL
            SELECT * FROM grade_application
            UNION ALL
            SELECT * FROM grade_inquiry
            UNION ALL
            SELECT * FROM enrolled_students
            UNION ALL
            SELECT * FROM grade_capacity
            {extra_union_sql}
        )
        SELECT
            report.id as id,
            report.next_grade_level_id as next_grade_level_id,
            report.student_count as student_count,
            report.student_count_type as student_count_type,
            grade.school_code_id as school_code_id,
            report.student_order_type as student_order_type
            from report
            LEFT JOIN school_base_grade_level grade
                ON grade.id = report.id
            WHERE grade.active_admissions = True
        """.format(
                extra_with_sql=extra_with_sql,
                extra_union_sql=extra_union_sql,
        )
        return sql

    @api.model
    def _reenrollment_sql(self):
        extra_with_sql = """,
        grade_reenrollment as (
        -- reenrollment
         SELECT
            reenrollment.next_grade_level_id as id,
            reenrollment.next_grade_level_id as next_grade_level_id,
            COUNT(reenrollment.id) as student_count,
            'reenrollment' as student_count_type,
            8 as student_order_type
            FROM adm_reenrollment reenrollment
            LEFT JOIN adm_reenrollment_stage stage
                ON stage.id = reenrollment.stage_id
            WHERE stage.type = ('returning') AND reenrollment.active = True
            GROUP BY reenrollment.next_grade_level_id
        """
        extra_union_sql = """
            UNION ALL
            SELECT * from grade_reenrollment
            UNION ALL
            -- Admissions
            SELECT
                grade.id as id,
                grade.id as next_grade_level_id,
                COALESCE(application.student_count,0) + 
                    COALESCE(inquiry.student_count,0) + 
                    COALESCE(reenrollment.student_count,0)
                as student_count,
                'Total Admissions (Inquiries + Applications + Reenrollments)' as student_count_type
                FROM school_base_grade_level grade
                LEFT JOIN grade_application application
                    ON application.next_grade_level_id = grade.id
                LEFT JOIN grade_inquiry inquiry
                    ON inquiry.next_grade_level_id = grade.id
                LEFT JOIN grade_reenrollment reenrollment
                    ON reenrollment.next_grade_level_id = grade.id
            UNION ALL
            SELECT 
                grade.id as id,
                grade.id as next_grade_level_id,
                COALESCE(application.student_count,0) + 
                    COALESCE(inquiry.student_count,0) + 
                    COALESCE(reenrollment.student_count,0) +
                    COALESCE(enrolled.student_count,0)
                as student_count,
                'Total Prospect Students' as student_count_type
                FROM school_base_grade_level grade
                LEFT JOIN grade_application application
                    ON application.next_grade_level_id = grade.id
                LEFT JOIN grade_inquiry inquiry
                    ON inquiry.next_grade_level_id = grade.id
                LEFT JOIN grade_reenrollment reenrollment
                    ON reenrollment.next_grade_level_id = grade.id
                LEFT JOIN enrolled_students as enrolled
                    ON enrolled.next_grade_level_id = grade.id
        """

        return (extra_with_sql, extra_union_sql)

    def _no_reenrollment_sql(self):
        extra_union_sql = """
        UNION ALL
        -- Admissions
        SELECT
            grade.id as id,
            grade.id as next_grade_level_id,
            COALESCE(application.student_count,0) + COALESCE(inquiry.student_count,0) as student_count,
            'Total Admissions\n (Inquiries + Applications)' as student_count_type,
            30 as student_order_type
            FROM school_base_grade_level grade
            LEFT JOIN grade_application application
                ON application.next_grade_level_id = grade.id
            LEFT JOIN grade_inquiry inquiry
                ON inquiry.next_grade_level_id = grade.id
        UNION ALL
        SELECT 
            grade.id as id,
            grade.id as next_grade_level_id,
            COALESCE(application.student_count,0) + 
                COALESCE(inquiry.student_count,0) + 
                COALESCE(enrolled.student_count,0)
            as student_count,
            'Total Prospect Students' as student_count_type,
            40 as student_order_type
            FROM school_base_grade_level grade
            LEFT JOIN grade_application application
                ON application.next_grade_level_id = grade.id
            LEFT JOIN grade_inquiry inquiry
                ON inquiry.next_grade_level_id = grade.id
            LEFT JOIN enrolled_students as enrolled
                ON enrolled.next_grade_level_id = grade.id
        """

        return ('', extra_union_sql)

