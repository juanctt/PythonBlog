# -*- coding: utf8 -*-

from flask import render_template
from werkzeug.exceptions import HTTPException
from app.helpers import render_json, is_json_request
from email import  ThreadedSMTPHandler
import logging


class ErrorHelper(object):

    http_codes = [400, 401, 403, 404, 500]
    template_http_codes = [401, 403, 404, 500]

    def __init__(self, app, **kwargs):

        if app is None:
            raise ValueError("`app` must be an instance Flask")

        self.app = app
        self._set_email_error_handlers()
        self._set_errors()

    def _set_email_error_handlers(self):
        config = self.app.config

        if not config.get('LOG_EMAIL_ENABLED'):
            return

        mail_handler = ThreadedSMTPHandler(self.app)
        mail_handler.setLevel(logging.ERROR)
        self.app.logger.addHandler(mail_handler)

    def _set_errors(self):

        for code in self.http_codes:
            self.app.register_error_handler(code, self._internal_http_error)

        self.app.register_error_handler(HTTPException,
                                        self._internal_http_error)

        if not self.app.config.get('DEBUG'):
            self.app.register_error_handler(Exception,
                                            self._internal_server_error)

    def _internal_http_error(self, error):
        self.app.logger.error('Internal HTTP Exception, code[%s] => %s',
                              error.code,
                              error,
                              exc_info=True)

        if is_json_request():
            return render_json(error=error)

        template = 'errors/500.html'

        if error.code in self.template_http_codes:
            template = 'errors/%s.html' % error.code

        return render_template(template, title=error), error.code

    def _internal_server_error(self, error):
        self.app.logger.error('Internal server error => %s',
                              error,
                              exc_info=True)

        if is_json_request():
            return render_json(error=error)

        return render_template('errors/500.html', title=error), 500
