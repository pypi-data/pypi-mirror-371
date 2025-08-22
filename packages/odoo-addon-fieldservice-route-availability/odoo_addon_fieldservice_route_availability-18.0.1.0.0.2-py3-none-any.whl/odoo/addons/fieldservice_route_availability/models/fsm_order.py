# Copyright 2025 APSL-Nagarro Antoni Marroig
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).
from odoo import api, models
from odoo.exceptions import ValidationError
from odoo.tools.misc import format_date


class FSMRoute(models.Model):
    _inherit = "fsm.order"

    @api.constrains("scheduled_date_start", "location_id")
    def check_black_out_days(self):
        for order in self:
            if order.fsm_route_id and order.scheduled_date_start:
                for group in order.fsm_route_id.fsm_blackout_group_ids:
                    match = group.fsm_blackout_day_ids.filtered(
                        lambda x, order=order: (
                            (not x.zip and x.date == order.scheduled_date_start.date())
                            or (
                                x.zip
                                and x.date == order.scheduled_date_start.date()
                                and x.zip == order.zip
                            )
                        )
                    )
                    if match:
                        raise ValidationError(
                            self.env._(
                                "The date %(date)s is a blackout day for field"
                                " service operations on this route.",
                                date=format_date(order.env, order.scheduled_date_start),
                            )
                        )
