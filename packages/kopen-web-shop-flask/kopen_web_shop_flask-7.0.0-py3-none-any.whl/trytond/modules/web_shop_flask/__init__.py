# The COPYRIGHT file at the top level of this repository contains the full
# copyright notices and license terms.
from trytond.pool import Pool

__all__ = ['register']

from . import product
from . import web


def register():
    Pool.register(
        product.Category,
        product.Template,
        product.Product,
        web.Shop,
        module='web_shop_flask', type_='model')
    Pool.register(
        web.ShopAccountPayment,
        web.ShopPaymentMethod,
        web.Shop_PaymentMethod,
        web.SalePaymentMethod,
        module='web_shop_flask', type_='model', depends=['account_payment'])
