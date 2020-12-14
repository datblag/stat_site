import cherrypy
import logging

from site_app.site_config import server_run_mode, SERVER_WORK_MODE
from site_app import app

from site_app.models.authorization import User, Role, Permission
from site_app.models.reference import Mkb10, RefOtdels, RefDoctors
from site_app.models.main_tables import DefectList, Patients
from site_app.models.medical_services import RefKmu

from site_app import db
from site_app.models.db_generate import mkb_loader, ref_loader

logging.Logger.level = logging.WARNING




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
