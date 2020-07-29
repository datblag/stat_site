import cherrypy

from site_app.site_config import server_run_mode, SERVER_WORK_MODE
from site_app import app
from site_app.models import User
from site_app import db


@app.shell_context_processor
def make_shell_context():
    return {'db': db, 'User': User}


if __name__ == '__main__':
    if server_run_mode == SERVER_WORK_MODE:
        cherrypy.tree.graft(app, '/')
        cherrypy.config.update({'server.socket_host': '0.0.0.0',
                                'server.socket_port': 8081,
                                'engine.autoreload.on': False,
                                })
        cherrypy.engine.start()
    else:
        app.run(debug=True)
