from flask import render_template, request, redirect, url_for, abort, current_app, jsonify
from flask_login import login_required, current_user
from flask import flash
from dateutil.parser import parse as parse_date
from react.render import render_component

from .. import main
from ... import data_api_client, content_loader
from app.main.forms import MoveUserForm, InviteForm
from ..auth import role_required

from dmapiclient import HTTPError, APIError
from dmapiclient.audit import AuditTypes
from dmutils.email import send_email, generate_token, EmailError
from dmutils.documents import (
    get_signed_url, get_agreement_document_path, file_is_pdf,
    AGREEMENT_FILENAME, SIGNED_AGREEMENT_PREFIX, COUNTERSIGNED_AGREEMENT_FILENAME,
)
from dmutils import s3
from dmutils.formats import DateFormatter
from dmutils.forms import DmForm, render_template_with_csrf

from itertools import chain


@main.route('/casestudy-assessment', methods=['GET'])
@login_required
@role_required('admin')
def case_study_assessment_list():
    response = data_api_client.req.admin().casestudy().assessment().get()
    case_studies = response.get('case_studies')

    rendered_component = render_component(
        'bundles/CaseStudy/CaseStudyAssessmentsListWidget.js', {
            'casestudies': case_studies,
            'meta': {
                # 'url_case_study_assessment_update': url_for('.add_case_study_assessment', case_study_id=case_study_id),
                # 'url_case_study_view': url_for('.case_study_view', case_study_id=0)
            }
        }
    )

    return render_template(
        '_react.html',
        component=rendered_component
    )

@main.route('/casestudy-assessment/<int:case_study_id>', methods=['GET'])
@login_required
@role_required('admin')
def case_study_view(case_study_id):
    response = data_api_client.req.admin().casestudy(case_study_id).get()
    case_study = response.get('case_study')
    domain = response.get('domain')

    case_study['admin'] = True
    case_study['domain'] = domain

    rendered_component = render_component(
        'bundles/CaseStudy/CaseStudyViewWidget.js', {
            'casestudy': case_study,
            'meta': {
                'url_case_study_assessment_update': url_for('.add_case_study_assessment', case_study_id=case_study_id),
            }
        }
    )

    return render_template(
        '_react.html',
        component=rendered_component
    )

@main.route('/casestudy-assessment/<int:case_study_id>', methods=['POST'])
@login_required
@role_required('admin')
def add_case_study_assessment(case_study_id):
    json_payload = request.get_json(force=True)
    result = (
        data_api_client
            .req
            .admin()
            .casestudy(case_study_id)
            .assessment()
            .post({
            'update_details': {
                'updated_by': current_user.email_address
            },
            "assessment": json_payload
        })
    )

    return jsonify(result)
