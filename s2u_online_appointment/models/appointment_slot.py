# -*- coding: utf-8 -*-

from odoo.addons.s2u_online_appointment.helpers import functions
from odoo import models, fields, api, _
from odoo.exceptions import ValidationError


class AppointmentSlot(models.Model):
    _name = 's2u.appointment.slot'
    _order = 'user_id, day, slot'
    _description = "Appointment Slot"
    
    @api.model
    def _get_week_days(self):
        return [
            ('0', _('Senin ')),
            ('1', _('Selasa')),
            ('2', _('Rabu')),
            ('3', _('Kamis')),
            ('4', _('Jumat')),
            ('5', _('Sabtu')),
            ('6', _('Minggu'))
        ]

    user_id = fields.Many2one('res.users', string='User', required=True)
    employee_id = fields.Many2one('hr.employee', string='Therapist', required=True)
    date =fields.Date(string='Tanggal')
    day = fields.Selection(selection=_get_week_days, default='0', string="Hari", required=True)
    slot = fields.Float('Jam', required=True)

    @api.constrains('slot')
    def _slot_validation(self):
        for slot in self:
            if functions.float_to_time(slot.slot) < '00:00' or functions.float_to_time(slot.slot) > '23:59':
                raise ValidationError(_('The slot value must be between 0:00 and 23:59!'))
