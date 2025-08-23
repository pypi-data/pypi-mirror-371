Image = pool.get('product.image')
Template = pool.get('product.template')
Category = pool.get('product.category')
Product = pool.get('product.product')
Attachment = pool.get('ir.attachment')

attachs = Attachment.search([
    ('type', '=', 'data'),
    ('image', '=', True),
    ])
resources = []
for attach in attachs:
    resources.append(attach.resource)

images = []
delete_flask_images = []
for resource in resources:
    for fimage in template.flask_images:
        new_image = Image()
        new_image.image = fimage.data
        new_image.web_shop = True
        if isinstance(resource, Template):
            new_image.template = resource
        elif isinstance(resource, Product):
            new_image.product = resource
        elif isinstance(resource, Category):
            new_image.category = resource
        images.append(new_image)
        delete_flask_images.append(fimage)

Image.save(images)
Attachment.delete(delete_flask_images)
transaction.commit()
