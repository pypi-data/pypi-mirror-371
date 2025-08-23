# Copyright 2021 Tecnativa - David Vidal
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).
from odoo import api, models


class ProductSupplierinfo(models.Model):
    _inherit = "product.supplierinfo"

    @api.model
    def search(self, args, offset=0, limit=None, order=None):
        """HACK: With NewId, the linked product_tmpl_id won't be a proper interger
        that we can use in a search. As we need it to get the proper pricelists
        we'll be passing it by context. The propper solution would be to
        use `self.product_tmpl_id._origin.id` in `_prepare_sellers`:
        https://github.com/odoo/odoo/blob/13.0/addons/product/models/product.py#L588"""
        if self.env.context.get("pvc_product_tmpl"):
            args2 = []
            for arg in args:
                if (
                    len(arg) == 3
                    and arg[0] == "product_tmpl_id"
                    and arg[1] == "="
                    and not isinstance(arg[2], int)
                ):
                    arg = (
                        "product_tmpl_id",
                        "=",
                        self.env.context.get("pvc_product_tmpl"),
                    )
                args2.append(arg)
            return super().search(
                args2,
                offset=offset,
                limit=limit,
                order=order,
            )
        return super().search(
            args,
            offset=offset,
            limit=limit,
            order=order,
        )

    def sorted(self, key=None, reverse=False):
        # Override this function to avoid a problem using NewId in the sorted sequence
        # because Odoo converts the .id to it when handling one2many of a virtual
        # record, and thus getting the error:
        # TypeError: '<' not supported between instances of 'NewId' and 'NewId'
        # The workaround is to remove the id sorting criteria for this specific case.
        if callable(key):
            if key.__code__.co_names == ("sequence", "min_qty", "price", "id"):
                key = lambda s=self: (s.sequence, -s.min_qty, s.price)  # noqa
        return super().sorted(key=key, reverse=reverse)
