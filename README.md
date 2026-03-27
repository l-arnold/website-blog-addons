# blog_website_filter

**Odoo 14.0 — Multi-Website Blog Filter**

Fixes a behavioral gap in Odoo 14 Community's multi-website blog setup: the **"All"** blog view (`/blog`) normally returns posts from *every* website, ignoring website boundaries. This module overrides the blog controller to scope all blog views — the "All" listing, individual blogs, post detail, and tag views — to the current website context.

---

## The Problem

In a standard Odoo 14 multi-website installation:

- Individual blogs can be assigned to specific websites via the `website_id` field on `blog.blog`
- Blog posts inherit their website from their parent blog
- **However**, the `/blog` ("All") route returns posts from every website regardless of which site the visitor is on

This module corrects that behavior without any schema changes or data migrations.

---

## What It Does

| Route | Behavior |
|---|---|
| `/blog` | Shows only posts from blogs assigned to the current website, plus blogs with no website (shared/global) |
| `/blog/<blog>` | Accessible only if the blog belongs to the current website (or has no website set); returns 404 otherwise |
| `/blog/<blog>/<post>` | Same access check as above, plus validates the post belongs to that blog |
| `/blog/<blog>/tag/<tag>` | Tag filtering within a website-scoped blog view |

**Shared blogs:** Any `blog.blog` record with no `website_id` set will appear on *all* websites. This allows truly global content alongside site-specific blogs.

---

## Compatibility

| Field | Value |
|---|---|
| Odoo Version | 14.0 Community |
| Module Technical Name | `blog_website_filter` |
| Depends | `website_blog`, `website` |
| License | LGPL-3 |

---

## Installation

1. Copy the `blog_website_filter` directory into your Odoo addons path
2. Restart Odoo: `sudo service odoo restart`
3. Activate developer mode
4. Go to **Apps → Update Apps List**
5. Search for **Multi-Website Blog Filter** and install

---

## Configuration

No special configuration is required after installation.

- Assign blogs to specific websites via **Website → Blog → Blogs → Website field**
- Blogs with *no website assigned* will appear on **all** websites
- Blog posts follow the website assignment of their parent blog

---

## Module Structure

```
blog_website_filter/
├── __init__.py                  # Imports controllers package
├── __manifest__.py              # Module metadata and dependencies
├── controllers/
│   ├── __init__.py              # Imports main controller
│   └── main.py                  # WebsiteBlogMultiWebsite — core logic
└── README.md
```

### Controller Overview (`controllers/main.py`)

`WebsiteBlogMultiWebsite` extends Odoo's core `WebsiteBlog` controller:

- **`_get_website_blogs()`** — helper that returns blogs matching the current website, plus blogs with no website set
- **`_check_blog_access(blog)`** — helper that validates a specific blog is accessible from the current website
- **`blog()`** — overrides `/blog` and `/blog/page/<n>`; builds a filtered post domain and renders `website_blog.blog_post_short` with website-scoped data
- **`blog_post()`** — overrides `/blog/<blog>` individual blog routes; applies access check then delegates to parent
- **`blog_post_detail()`** — overrides `/blog/<blog>/<post>`; checks blog access and post/blog relationship, then delegates to parent
- **`blog_tag()`** — overrides tag routes; applies blog access check, then delegates to parent

All overridden methods include exception handling that falls back to the parent controller on unexpected errors, with logging via `_logger`.

---

## Notes

- `__pycache__/` directories are generated at runtime — add them to `.gitignore`
- Developed and tested against Odoo 14.0 Community
- The `price` and `currency` fields have been removed from the manifest (they are not standard Odoo Community fields)
- This addresses a core behavioral gap that may be handled differently in later Odoo versions

---

## Repository

Part of the [`odoo14-website-blog`](https://github.com/l-arnold/odoo14-website-blog) collection of Odoo 14 website/blog customization modules.

---

## Author

Landis Arnold / Nomadic Inc.  
Longmont, Colorado