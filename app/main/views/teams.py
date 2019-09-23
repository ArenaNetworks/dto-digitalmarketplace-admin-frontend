from dmutils.forms import render_template_with_csrf
from flask import render_template, request, flash, jsonify, url_for, redirect
from flask_login import login_required, current_user
from react.render import render_component

from .. import main
from ... import data_api_client
from ..auth import role_required
from dmapiclient.errors import HTTPError

@main.route('/teams', methods=['GET'])
@login_required
@role_required('admin')
def find_team_by_team_id():
    team_id = request.args.get('team_id')

    try:
        teams = data_api_client.get_team(team_id).get('teams')
    except:  # noqa
        flash('no_team', 'error')
        return render_template(
            "view_teams.html",
            users=list(),
            team_id=team_id,
            teams=None
        ), 404

    users = brief.get('users')
    title = brief.get('title')
    return render_template_with_csrf(
        "view_teams.html",
        users=users,
        title=title,
        team_id=team_id,
        teams=teams
    )