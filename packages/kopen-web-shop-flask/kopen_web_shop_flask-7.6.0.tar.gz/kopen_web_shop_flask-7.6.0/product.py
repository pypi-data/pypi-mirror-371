# The COPYRIGHT file at the top level of this repository contains
# the full copyright notices and license terms.
from sql import Literal
from sql.operators import Equal

from trytond.model import fields, Exclude
from trytond.pool import PoolMeta
from trytond.pyson import Bool, Eval
from trytond.tools import slugify


class OrderMixin:
    __slots__ = ()

    flask_sequence = fields.Integer("Flask Sequence")


class SlugMixin:
    __slots__ = ()
    _flask_slug_field = 'rec_name'

    flask_slug = fields.Char("Slug",
        states={
            'readonly': ~Eval('flask_slug_custom'),
            },
        depends=['flask_slug_custom'])
    flask_slug_custom = fields.Boolean("Custom Slug",
        states={
            'invisible': ~Bool(Eval('flask_slug')),
            },
        depends=['flask_slug'])

    @classmethod
    def __setup__(cls):
        super().__setup__()

        t = cls.__table__()
        where = (t.flask_slug != '')
        if (hasattr(cls, 'active')
                and not isinstance(cls.active, fields.Function)):
            where &= (t.active == Literal(True))
        cls._sql_constraints = [
            ('flask_slug_exclude', Exclude(t,
                    (t.flask_slug, Equal),
                    where=where),
                'web_shop_flask.msg_product_slug_unique'),
            ]

    def compute_slug(self):
        if self.flask_slug_custom:
            return self.flask_slug
        return slugify(getattr(self, self._flask_slug_field)).lower()

    @property
    def needs_slug(self):
        return False

    @classmethod
    def sync_slug(cls, records):
        for record in records:
            if not record.needs_slug:
                continue
            slug = record.compute_slug()
            if slug != record.flask_slug:
                record.flask_slug = slug
        cls.save(records)

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
    def copy(cls, templates, default=None):
        if default is None:
            default = {}
        else:
            default = default.copy()
        default.setdefault('flask_slug', '')
        default.setdefault('flask_slug_custom', False)
        return super().copy(templates, default=default)


class Category(OrderMixin, SlugMixin, metaclass=PoolMeta):
    __name__ = 'product.category'

    @property
    def needs_slug(self):
        return any(s.type == 'flask' for s in self.web_shops)


class Template(OrderMixin, SlugMixin, metaclass=PoolMeta):
    __name__ = 'product.template'

    @classmethod
    def search_rec_name(cls, name, clause):
        _, operator, value = clause
        domain = super().search_rec_name(name, clause)
        domain.append(('flask_slug', operator, value),)
        return domain

    @property
    def needs_slug(self):
        return any(s.type == 'flask' for p in self.products
            for s in p.web_shops)


class Product(metaclass=PoolMeta):
    __name__ = 'product.product'

    @classmethod
    def copy(cls, products, default=None):
        if default is None:
            default = {}
        else:
            default = default.copy()
        default.setdefault('web_shops', [])
        return super().copy(products, default=default)
