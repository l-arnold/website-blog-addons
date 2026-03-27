# -*- coding: utf-8 -*-
{
    'name': 'Multi-Website Blog Filter',
    'version': '14.0.1.0.1',
    'category': 'Website',
    'summary': 'Filter blog posts by current website in multi-website setup',
    'description': """
Multi-Website Blog Filter

This module extends the website blog functionality to filter blog posts
based on the current website in a multi-website Odoo setup.

Features:

* Filter blog posts by current website in the "All" (/blog) view
* Restrict individual blog access based on website assignment
* Maintain blog isolation between different websites
* Support for blog tag filtering per website
* Blog posts and tags filtered on individual blog views

Usage:

* Install the module
* Assign blogs to specific websites using the website field on blog.blog
* Blogs without website assignment will be visible on all websites
* Blog posts will only appear on their assigned website
    """,
    'author': 'Landis Arnold / Nomadic Inc.',
    'website': 'https://github.com/l-arnold/odoo14-website-blog',
    'license': 'LGPL-3',
    'depends': [
        'website_blog',
        'website',
    ],
    'data': [],
    'demo': [],
    'assets': {},
    'images': [],
    'installable': True,
    'auto_install': False,
    'application': False,
}