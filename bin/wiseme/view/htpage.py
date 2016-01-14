# -*- coding: utf-8 -*-
from flask.views import MethodView
from flask import render_template, request, session, redirect
from ..utils.logincheck import get_access_token, check_login
from ..utils.response import error, QFRET
from ..utils.logincheck import logout
from ..qflogger import log
from .. import app
from ..dao.dao import get_wisemeuser


class HtMain(MethodView):
    """
    main
    """
    @check_login
    def get(self):
        profile = self.qf_u
        return render_template("htmain.html", profile=profile)


