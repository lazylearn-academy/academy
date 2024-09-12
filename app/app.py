from flask import Flask, render_template, send_from_directory, render_template, make_response
import os
from jinja2 import StrictUndefined

app = Flask(__name__)
app.jinja_env.undefined = StrictUndefined

@app.route('/')
@app.route('/home')
def home():
    return render_template("index.html", link_styles=[
        "color:white;", "", "", "", "", ""
    ])


@app.route('/about')
def about():
    return render_template("about.html", link_styles=[
        "", "color:white;", "", "", "", ""
    ])


@app.route('/blog')
def blog():
    return render_template("blog.html", link_styles=[
        "", "", "", "color:white;", "", ""
    ])


@app.route('/contacts')
def contacts():
    return render_template("contacts.html", link_styles=[
        "", "", "", "", "color:white;", ""
    ])


@app.route('/courses')
def courses():
    return render_template("courses.html", link_styles=[
        "", "", "color:white;", "", "", ""
    ])


@app.route('/helpproject')
def helpproject():
    return render_template("helpproject.html", link_styles=[
        "", "", "", "", "", "color:white;"
    ])


@app.route('/courses/<course_name>')
def get_course(course_name):
    return render_template(f"courses/{course_name}/course_{course_name}.html", link_styles=[
        "", "", "color:white;", "", "", ""
    ])



@app.route('/courses/<course_name>/themes/<theme_name>')
def get_theme(course_name, theme_name):
    return render_template(f"courses/{course_name}/{theme_name}.html", link_styles=[
        "", "", "color:white;", "", "", ""
    ])


@app.route('/blog/articles/<article_name>')
def get_article(article_name):
    return render_template(f"blog/{article_name}.html", link_styles=[
        "", "", "", "color:white;", "", ""
    ])


@app.route('/favicon.ico')
def favicon():
    return send_from_directory(os.path.join(app.root_path, 'static'),
                               'favicon.ico', mimetype='image/vnd.microsoft.icon')


@app.route('/sitemap.xml', methods=["GET"])
def sitemap():
    course_folder = 'templates/courses'

    themes = []
    for root, dirs, files in os.walk(course_folder):
        for dir in dirs:
            dir_path = os.path.join(root, dir)
            for file in os.listdir(dir_path):
                file_name, file_ext = os.path.splitext(file)
                themes.append(f"courses/{dir}/themes/{file_name}")

    articles = list(map(lambda x: os.path.splitext(x)[0], os.listdir("templates/blog")))
    sm_xml = render_template("sitemap.xml", themes=themes, articles=articles)
    response = make_response(sm_xml)
    response.headers["Content-Type"] = "application/rss+xml"
    response.mimetype = "application/xml"
    return response


@app.route('/robots.txt', methods=["GET"])
def robots():
    rb_txt = render_template("robots.txt")
    response = make_response(rb_txt)
    response.headers["Content-Type"] = "text/plain; charset=utf-8;"
    response.mimetype = "text/plain"
    return response


if __name__ == "__main__":
    app.run("0.0.0.0")
