# -*- coding: utf-8 -*-
from odoo import fields, models

class AccountCategoryTemplate(models.Model):
    _name = "account.category.template"
    _description = 'Template for Account Categories'
    name = fields.Char(required=True)
    chart_template_id = fields.Many2one('account.chart.template', string='Chart Template', required=True)


class AccountAccountTemplate(models.Model):
    _inherit = "account.account.template"
    _parent_name = "parent_id"
    _parent_store = True

    parent_id = fields.Many2one('account.account.template', 'Parent Account', index=True, ondelete='cascade', check_company=True)
    child_ids = fields.One2many('account.account.template', 'parent_id', 'Contains')
    parent_path = fields.Char(index=True)


class AccountChartTemplate(models.Model):
    _inherit = 'account.chart.template'

    def generate_account(self, tax_template_ref, acc_template_ref, code_digits, company):
        self.ensure_one()
        account_tmpl_obj = self.env['account.account.template']
        acc_template = account_tmpl_obj.search([('nocreate', '!=', True), ('chart_template_id', '=', self.id)], order='id')
        template_vals = []
        for account_template in acc_template:
            # 科目代码不需要补齐到6位
            code_acc = account_template.code or ''
            vals = self._get_account_vals(company, account_template, code_acc, tax_template_ref)
            template_vals.append((account_template, vals))
        accounts = self._create_records_with_xmlid('account.account', template_vals, company)
        for template, account in zip(acc_template, accounts):
            acc_template_ref[template.id] = account.id

        # 更新 parent_id
        for template, account in zip(acc_template, accounts):
            if template.parent_id:
                account.update({'parent_id': acc_template_ref[template.parent_id.id]})

        return acc_template_ref
