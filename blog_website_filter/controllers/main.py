# controllers/main.py
from odoo import http
from odoo.http import request
from odoo.addons.website_blog.controllers.main import WebsiteBlog
from odoo.addons.http_routing.models.ir_http import slug
import logging

_logger = logging.getLogger(__name__)

class WebsiteBlogMultiWebsite(WebsiteBlog):
    
    def _get_website_blogs(self):
        """Helper method to get blogs for current website"""
        current_website = request.website
        Blog = request.env['blog.blog']
        all_blogs = Blog.search([])
        # Filter blogs by current website or blogs without website specified
        website_blogs = all_blogs.filtered(lambda b: b.website_id == current_website or not b.website_id)
        return website_blogs
    
    def _check_blog_access(self, blog):
        """Check if the blog should be accessible from current website"""
        current_website = request.website
        return blog.website_id == current_website or not blog.website_id
    
    @http.route(['/blog', '/blog/page/<int:page>'], type='http', auth="public", website=True, sitemap=False)
    def blog(self, page=1, tag=None, **opt):
        """Handle the "All" blog view - filter by current website"""
        try:
            _logger.info("Custom blog controller called for website: %s", request.website.name)
            
            # Get blogs for current website
            website_blogs = self._get_website_blogs()
            
            if not website_blogs:
                # No blogs for this website - show empty
                return request.render("website_blog.blog_post_short", {
                    'blog': None,
                    'blogs': request.env['blog.blog'].browse([]),
                    'posts': request.env['blog.post'].browse([]),
                    'tag': None,
                    'tags': request.env['blog.tag'].browse([]),
                    'pager': request.website.pager(url="/blog", total=0, page=1, step=20),
                    'blog_url': lambda **kw: '/blog',
                })
            
            # Get posts from these blogs only
            BlogPost = request.env['blog.post']
            post_domain = [
                ('blog_id', 'in', website_blogs.ids),
                ('website_published', '=', True)
            ]
            
            # Handle tag filtering
            tag_obj = None
            if tag:
                try:
                    if hasattr(tag, 'id'):
                        tag_obj = tag
                    else:
                        tag_obj = request.env['blog.tag'].browse(int(tag))
                    
                    if tag_obj and tag_obj.exists():
                        post_domain.append(('tag_ids', 'in', [tag_obj.id]))
                except (ValueError, TypeError):
                    tag_obj = None
            
            # Also check URL parameters for tag
            elif 'tag' in opt:
                try:
                    tag_id = int(opt['tag'])
                    tag_obj = request.env['blog.tag'].browse(tag_id)
                    if tag_obj and tag_obj.exists():
                        post_domain.append(('tag_ids', 'in', [tag_obj.id]))
                except (ValueError, TypeError):
                    tag_obj = None
            
            # Count and get posts
            posts_count = BlogPost.search_count(post_domain)
            step = 20
            pager = request.website.pager(url="/blog", total=posts_count, page=page, step=step, url_args=opt)
            
            posts = BlogPost.search(post_domain, limit=step, offset=pager['offset'], order="post_date desc")
            
            # Get all tags that are used in posts from our website blogs
            all_blog_posts = BlogPost.search([('blog_id', 'in', website_blogs.ids), ('website_published', '=', True)])
            tags = request.env['blog.tag'].search([('post_ids', 'in', all_blog_posts.ids)]) if all_blog_posts else request.env['blog.tag'].browse([])
            
            # Create a proper blog_url function
            def blog_url(tag=None, **kw):
                url = '/blog'
                if tag:
                    if hasattr(tag, 'id'):
                        url += f'?tag={tag.id}'
                    else:
                        # Make sure tag is just the number, not in brackets
                        tag_id = str(tag).strip('[]')
                        url += f'?tag={tag_id}'
                return url
            
            # Get the active tag IDs for template - make sure it's just the ID number
            active_tag_ids = [tag_obj.id] if tag_obj else []
            
            # Helper function for tag list manipulation
            def tags_list(current_tags, new_tag_id):
                if not current_tags:
                    return [new_tag_id]
                if new_tag_id in current_tags:
                    return [t for t in current_tags if t != new_tag_id]
                else:
                    return current_tags + [new_tag_id]
            
            values = {
                'blog': None,
                'blogs': website_blogs,
                'posts': posts,
                'tag': tag_obj,
                'tags': tags,
                'active_tag_ids': active_tag_ids,
                'tags_list': tags_list,
                'pager': pager,
                'blog_url': blog_url,
                'main_object': request.website,
            }
            
            return request.render("website_blog.blog_post_short", values)
            
        except Exception as e:
            _logger.error("Error in custom blog controller: %s", str(e), exc_info=True)
            # Call parent method correctly - no blog parameter for main blog view
            return super().blog(page=page, tag=tag, **opt)

    @http.route(['/blog/<model("blog.blog"):blog>', '/blog/<model("blog.blog"):blog>/page/<int:page>'], type='http', auth="public", website=True, sitemap=False)
    def blog_post(self, blog, page=1, tag=None, **opt):
        """Handle individual blog views - check website access first"""
        try:
            _logger.info("Individual blog controller called for blog: %s, website: %s", blog.name, request.website.name)
            
            # Check if this blog should be accessible from current website
            if not self._check_blog_access(blog):
                _logger.info("Blog %s not accessible from website %s", blog.name, request.website.name)
                return request.not_found()
            
            # Call the parent method with correct signature
            # The parent blog method expects: blog(self, blog=None, tag=None, page=1, **opt)
            return super().blog(blog=blog, tag=tag, page=page, **opt)
            
        except Exception as e:
            _logger.error("Error in individual blog controller: %s", str(e), exc_info=True)
            return request.not_found()

    @http.route(['/blog/<model("blog.blog"):blog>/<model("blog.post"):blog_post>'], 
                type='http', auth="public", website=True, sitemap=False)
    def blog_post_detail(self, blog, blog_post, tag_id=None, **post):
        """Handle individual blog post views - check website access first"""
        try:
            _logger.info("Blog post detail controller called for blog: %s, post: %s, website: %s", 
                        blog.name, blog_post.name, request.website.name)
            
            # Check if this blog should be accessible from current website
            if not self._check_blog_access(blog):
                _logger.info("Blog %s not accessible from website %s", blog.name, request.website.name)
                return request.not_found()
            
            # Also check if the blog post belongs to the correct blog
            if blog_post.blog_id != blog:
                _logger.info("Blog post %s does not belong to blog %s", blog_post.name, blog.name)
                return request.not_found()
            
            # Call the parent method with the correct method name and parameters
            # In Odoo 14, the method is called blog_post, not blog_post_detail
            return super().blog_post(blog=blog, blog_post=blog_post, tag_id=tag_id, **post)
            
        except Exception as e:
            _logger.error("Error in blog post detail controller: %s", str(e), exc_info=True)
            return request.not_found()

    @http.route(['/blog/<model("blog.blog"):blog>/tag/<model("blog.tag"):tag>',
                 '/blog/<model("blog.blog"):blog>/tag/<model("blog.tag"):tag>/page/<int:page>'], 
                 type='http', auth="public", website=True, sitemap=False)
    def blog_tag(self, blog, tag, page=1, **opt):
        """Handle blog tag views - check website access first"""
        try:
            _logger.info("Blog tag controller called for blog: %s, tag: %s, website: %s", 
                        blog.name, tag.name, request.website.name)
            
            # Check if this blog should be accessible from current website
            if not self._check_blog_access(blog):
                _logger.info("Blog %s not accessible from website %s", blog.name, request.website.name)
                return request.not_found()
            
            # Convert tag object to slug string format that parent expects
            tag_slug = slug(tag)
            
            # Call the parent blog method with tag as string
            return super().blog(blog=blog, tag=tag_slug, page=page, **opt)
            
        except Exception as e:
            _logger.error("Error in blog tag controller: %s", str(e), exc_info=True)
            return request.not_found()