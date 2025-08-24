from nanodjango import Django

from compose import postgres, sentry

app = Django()

app.pm.register(postgres)
app.pm.register(sentry)

@app.route("/")
def hello_world(request):
    return "<p>Hello, World!</p>"
