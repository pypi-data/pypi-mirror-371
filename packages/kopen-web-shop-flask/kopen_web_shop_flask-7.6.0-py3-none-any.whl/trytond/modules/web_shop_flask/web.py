# The COPYRIGHT file at the top level of this repository contains the full
# copyright notices and license terms.

from trytond.pool import PoolMeta, Pool
from trytond.model import ModelSQL, ModelView, fields, sequence_ordered
from trytond.pyson import Eval


class Shop(metaclass=PoolMeta):
    __name__ = 'web.shop'

    @classmethod
    def __setup__(cls):
        super().__setup__()
        cls.type.selection.append(('flask', "Flask"))
        order = cls.products.order or []
        order.insert(0,
            ('product.template.flask_sequence', 'ASC NULLS FIRST'))
        cls.products.order = order
        order = cls.categories.order or []
        order.insert(0,
            ('category.flask_sequence', 'ASC NULLS FIRST'))
        cls.categories.order = order

    @classmethod
    def create(cls, vlist):
        records = super().create(vlist)
        cls.sync_slug(records)
        return records

    @classmethod
    def write(cls, *args):
        super().write(*args)
        records = sum(args[0:None:2], [])
        cls.sync_slug(records)

    @classmethod
    def sync_slug(cls, records):
        pool = Pool()
        Category = pool.get('product.category')
        Template = pool.get('product.template')
        categories = set()
        templates = set()
        for record in records:
            categories |= set(record.categories)
            templates |= set([p.template for p in record.products])
        Category.sync_slug(Category.browse(categories))
        Template.sync_slug(Template.browse(templates))


class ShopAccountPayment(metaclass=PoolMeta):
    __name__ = 'web.shop'

    payment_methods = fields.Many2Many('web.shop-web.shop.payment_method',
        'shop', 'payment_method', "Payment Methods",
        states={
            'invisible': Eval('type') != 'flask',
            },
        depends=['type'])

    @classmethod
    def view_attributes(cls):
        return super().view_attributes() + [
            ('//page[@id="payments"]', 'states', {
                    'invisible': Eval('type') != 'flask',
                    }),
            ]


class ShopPaymentMethod(sequence_ordered(), ModelSQL, ModelView):
    'Web Shop Payment Method'
    __name__ = 'web.shop.payment_method'

    name = fields.Char("Name", translate=True)
    description = fields.Text("Description", translate=True)
    confirm_message = fields.Text("Confirmation message", translate=True)
    journal = fields.Many2One(
        'account.payment.journal', "Journal", ondelete='RESTRICT')


class Shop_PaymentMethod(ModelSQL):
    'Web Shop - Payment Method'
    __name__ = 'web.shop-web.shop.payment_method'

    shop = fields.Many2One(
        'web.shop', "Shop", ondelete='CASCADE', required=True)
    payment_method = fields.Many2One(
        'web.shop.payment_method', "Payment Method", ondelete='RESTRICT',
        required=True)

    def get_rec_name(self, name):
        return self.payment_method.rec_name


class SalePaymentMethod(metaclass=PoolMeta):
    __name__ = 'sale.sale'

    payment_method = fields.Many2One(
        'web.shop.payment_method', "WebShop Payment Method",
        ondelete='RESTRICT',
        states={
            'readonly': Eval('state') != 'draft',
            })
