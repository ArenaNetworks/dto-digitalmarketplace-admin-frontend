from dmutils.forms import render_template_with_csrf
from flask import render_template, request, flash, jsonify, url_for, redirect
from flask_login import login_required, current_user
from react.render import render_component

from .. import main
from ... import data_api_client
from ..auth import role_required
from dmapiclient.errors import HTTPError


@main.route('/team', methods=['GET'])
@login_required
@role_required('admin')
def find_team_by_team_id():
    team = data_api_client.req.team(team_id).get()
    return render_template_with_csrf(
        "view_teams.html",
        team=team
    )
    