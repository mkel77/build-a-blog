import webapp2
import jinja2
import os

from google.appengine.ext import db

template_dir = os.path.join(os.path.dirname(__file__), 'templates')
jinja_env = jinja2.Environment(loader = jinja2.FileSystemLoader(template_dir), autoescape = True)

class Handler(webapp2.RequestHandler):
    def write(self, *a, **kw):
        self.response.out.write(*a, **kw)

    def render_str(self, template, **params):
        t = jinja_env.get_template(template)
        return t.render(params)

    def render(self, template, **kw):
        self.write(self.render_str(template, **kw))

class Art(db.Model):
    title = db.StringProperty(required = True)
    art = db.TextProperty(required  = True)
    created = db.DateTimeProperty(auto_now_add = True)

class MainPage(Handler):
    def render_newpost(self, title = "", art = "", error = ""):

        self.render("newpost.html", title = title, art = art, error = error)

    def get(self):
        self.render_newpost()

    def post(self):
        title = self.request.get("title")
        art = self.request.get("art")

        if title and art:
            a = Art(title = title, art = art)
            a.put()

            akey = a.key().id()
            self.redirect("/blog/" + str(akey))
            #self.response.write(akey)
            #t = jinja_env.get_template("singlepost.html")
            #content = t.render(a = title)
            #self.response.write(content)
            #"/blog/{{art.key().id()}}"
            #self.redirect("/welcome?username=" + cgi.escape(user_username, quote = True))


        else:
            error="we need both a title and a body!"
            self.render_newpost(title, art, error)

class Blog(Handler):
    def get(self):
        arts = db.GqlQuery("SELECT * FROM Art "
                           "ORDER BY created DESC "
                           "LIMIT 5 ")

        self.render("blog.html", arts = arts)


class ViewPostHandler(webapp2.RequestHandler):
    def get(self, id):
        single_post = Art.get_by_id(int(id))

        # if the id does not exist inthe db, error.
        if not single_post:
            t = jinja_env.get_template("error.html")
            content = t.render(id = id)
            self.response.write(content)

        else:
            t = jinja_env.get_template("singlepost.html")
            content = t.render(a = single_post)
            self.response.write(content)


app = webapp2.WSGIApplication([
    ('/blog/newpost', MainPage),
    ('/blog', Blog),
    webapp2.Route('/blog/<id:\d+>', ViewPostHandler)
], debug=True)
