import cherrypy
import logging

from site_app.site_config import server_run_mode, SERVER_WORK_MODE
from site_app import app
from site_app.models import User, DefectList, Mkb10, Patients, RefOtdels, RefDoctors, Role, Permission
from site_app import db
from site_app.db_generate import mkb_loader, ref_loader


logging.Logger.level = logging.WARNING

@app.shell_context_processor
def make_shell_context():
    return {'db': db, 'User': User, 'DefectList': DefectList, 'session': db.session, 'Mkb10': Mkb10,
            'mkb_loader': mkb_loader, 'ref_loader': ref_loader, 'Patients': Patients, 'RefOtdels': RefOtdels,
            'RefDoctors': RefDoctors, 'Role': Role, 'Permission': Permission}


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
