
{
    "name": "Portal Management",
    "author": "One Tam US LLC.",
    "version": "1.0",
    "summary": "Portal Management",
    "data": [
            'security/security.xml',
            'security/ir.model.access.csv',
            'views/assets.xml',
            'data/sequence.xml',
            'data/website_menu.xml',
            'data/product_order_email_templates.xml',
            'views/ir_menu.xml',
            'views/res_users.xml',
            'views/portal_dashboard.xml',
            'views/product_order_request.xml',
            'views/new_request.xml',
            'views/purchase_order_views.xml',
            'views/stock_picking_views.xml',
            'views/homepage.xml',
            'views/footer.xml'
            
    ],
    'depends': ['website','portal','backend_theme_v13','purchase','stock'],
    'installable': True,
    'application': True,
}
