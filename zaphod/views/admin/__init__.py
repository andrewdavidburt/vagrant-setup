def includeme(config):
    config.add_route('admin:dashboard', '/dashboard')

    config.add_route('admin:creators', '/creators')
    config.add_route('admin:creators:new', '/creators/new')
    config.add_route('admin:creator', '/creator/{id}')

    config.add_route('admin:projects', '/projects')
    config.add_route('admin:projects:new', '/projects/new')
    config.add_route('admin:projects:search', '/projects/search')

    config.add_route('admin:project', '/project/{id}')
    config.add_route('admin:project:products', '/project/{id}/products')
    config.add_route('admin:project:products:new',
                     '/project/{id}/products/new')

    config.add_route('admin:project:owners', '/project/{id}/owners')
    config.add_route('admin:project:owners:new', '/project/{id}/owners/new')
    config.add_route('admin:project:updates', '/project/{id}/updates')
    config.add_route('admin:project:updates:new', '/project/{id}/updates/new')
    config.add_route('admin:project:emails', '/project/{id}/emails')
    config.add_route('admin:project:ship', '/project/{id}/ship')
    config.add_route('admin:project:mark-successful',
                     '/project/{id}/mark-successful')
    config.add_route('admin:project:capture-funds',
                     '/project/{id}/capture-funds')
    config.add_route('admin:project:suspend', '/project/{id}/suspend')
    config.add_route('admin:project:transfers', '/project/{id}/transfers')
    config.add_route('admin:project:transfers:new',
                     '/project/{id}/transfers/new')

    config.add_route('admin:project:reports', '/project/{id}/reports')
    config.add_route('admin:project:reports:funding', '/project/{id}/funding')
    config.add_route('admin:project:reports:status', '/project/{id}/status')
    config.add_route('admin:project:reports:balance', '/project/{id}/balance')
    config.add_route('admin:project:reports:skus', '/project/{id}/skus')

    config.add_route('admin:products:search', '/products/search')
    config.add_route('admin:product', '/product/{id}')
    config.add_route('admin:product:schedule', '/product/{id}/schedule')
    config.add_route('admin:product:options', '/product/{id}/options')
    config.add_route('admin:product:skus', '/product/{id}/skus')
    config.add_route('admin:product:info', '/product/{id}/info')

    config.add_route('admin:adjust-inventory', '/adjust-inventory/{id}')

    config.add_route('admin:update', '/update/{id}')
    config.add_route('admin:transfer', '/transfer/{id}')

    config.add_route('admin:users', '/users')
    config.add_route('admin:users:new', '/users/new')
    config.add_route('admin:users:search', '/users/search')
    config.add_route('admin:user', '/user/{id}')
    config.add_route('admin:user:send-password-reset',
                     '/user/{id}/send-password-reset')
    config.add_route('admin:user:send-welcome-email',
                     '/usr/{id}/send-welcome-email')

    config.add_route('admin:articles', '/articles')
    config.add_route('admin:articles:new', '/articles/new')
    config.add_route('admin:article', '/article/{id}')
    config.add_route('admin:article:delete', '/article/{id}/delete')

    config.add_route('admin:orders', '/orders')
    config.add_route('admin:orders:new', '/orders/new')
    config.add_route('admin:orders:open', '/orders/open')
    config.add_route('admin:orders:open-stock', '/orders/open-stock')
    config.add_route('admin:orders:overdue', '/orders/overdue')
    config.add_route('admin:order', '/order/{id}')
    config.add_route('admin:order:resend-confirmation',
                     '/order/{id}/resend-confirmation')
    config.add_route('admin:order:resend-shipping-confirmation',
                     '/order/{id}/resend-shipping-confirmation')
    config.add_route('admin:order:send-update-payment',
                     '/order/{id}/send-update-payment')
    config.add_route('admin:order:prepare-invoice',
                     '/order/{id}/prepare-invoice')
    config.add_route('admin:order:print-invoice',
                     '/order/{id}/print-invoice')
    config.add_route('admin:order:cancel', '/order/{id}/cancel')
    config.add_route('admin:order:fill', '/order/{id}/fill')
    config.add_route('admin:order:address', '/order/{id}/address')
    config.add_route('admin:order:user', '/order/{id}/user')
    config.add_route('admin:order:payment-cc-existing',
                     '/order/{id}/existing-credit-card-payment')
    config.add_route('admin:order:payment-cc-new',
                     '/order/{id}/new-credit-card-payment')
    config.add_route('admin:order:payment-cash', '/order/{id}/cash-payment')
    config.add_route('admin:order:payment-check', '/order/{id}/check-payment')
    config.add_route('admin:order:refund-cash', '/order/{id}/refund-cash')
    config.add_route('admin:order:refund-check', '/order/{id}/refund-check')
    config.add_route('admin:order:add-item', '/order/{id}/add-item')
    config.add_route('admin:order:remove-item',
                     '/order/{id}/remove-item/{item_id}')

    config.add_route('admin:payment:capture', '/payment/{id}/capture')
    config.add_route('admin:payment:void', '/payment/{id}/void')
    config.add_route('admin:payment:refund', '/payment/{id}/refund')
    config.add_route('admin:payment:mark-chargeback',
                     '/payment/{id}/mark-chargeback')
    config.add_route('admin:payment:mark-chargeback-won',
                     '/payment/{id}/mark-chargeback-won')
    config.add_route('admin:payment:mark-chargeback-lost',
                     '/payment/{id}/mark-chargeback-lost')

    config.add_route('admin:vendors', '/vendors')
    config.add_route('admin:vendors:new', '/vendors/new')
    config.add_route('admin:vendor', '/vendor/{id}')

    config.add_route('admin:vendor-orders', '/vendor-orders')
    config.add_route('admin:vendor-orders:new', '/vendor-orders/new')
    config.add_route('admin:vendor-order', '/vendor-order/{id}')
    config.add_route('admin:vendor-order:mark-sent',
                     '/vendor-order/{id}/mark-sent')
    config.add_route('admin:vendor-order:mark-confirmed',
                     '/vendor-order/{id}/mark-confirmed')
    config.add_route('admin:vendor-order:receive-invoice',
                     '/vendor-order/{id}/receive-invoice')
    config.add_route('admin:vendor-order:receive-shipment',
                     '/vendor-order/{id}/receive-shipment')

    config.add_route('admin:vendor-shipment', '/vendor-shipment/{id}')
    config.add_route('admin:vendor-invoice', '/vendor-invoice/{id}')

    config.add_route('admin:images', '/images')
    config.add_route('admin:images:upload', '/images/upload')
    config.add_route('admin:images:search', '/images/search')
    config.add_route('admin:image', '/image/{id}')

    config.add_route('admin:provider-types', '/provider-types')
    config.add_route('admin:provider-types:new', '/provider-types/new')
    config.add_route('admin:provider-type', '/provider-type/{id}')
    config.add_route('admin:provider-type:delete',
                     '/provider-type/{id}/delete')

    config.add_route('admin:providers', '/providers')
    config.add_route('admin:providers:new', '/providers/new')
    config.add_route('admin:provider', '/provider/{id}')
    config.add_route('admin:provider:delete', '/provider/{id}/delete')

    config.add_route('admin:tags', '/tags')
    config.add_route('admin:tags:new', '/tags/new')
    config.add_route('admin:tags:ajax-list', '/tags/ajax-list')
    config.add_route('admin:tag', '/tag/{id}')
    config.add_route('admin:tag:delete', '/tag/{id}/delete')

    config.add_route('admin:leads', '/leads')
    config.add_route('admin:leads:new', '/leads/new')
    config.add_route('admin:lead', '/lead/{id}')

    config.add_route('admin:discounts', '/discounts')
    config.add_route('admin:discounts:new', '/discounts/new')
    config.add_route('admin:discount', '/discount/{id}')

    config.add_route('admin:settings', '/settings')

    config.add_route('admin:mail_template', '/mail-template/{template_name}')

    config.add_route('admin:help', '/help')
    config.add_route('admin:help:markdown', '/help/markdown')
    config.add_route('admin:help:image-tags', '/help/image-tags')

    config.add_route('admin:docs', '/docs/{path:.*}')
    config.add_route('admin:status', '/status')

    config.include('.reports', route_prefix='/reports')
