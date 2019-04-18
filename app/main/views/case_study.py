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
    searched_supplier_code = request.args.get('supplier_code')

    rendered_component = render_component(
        'bundles/CaseStudy/CaseStudyAssessmentsListWidget.js', {
            'casestudies': case_studies,
            'meta': {
                'searched_supplier_code': searched_supplier_code,
                'url_case_study_status_update': {
                    cs['id']: url_for('.update_case_study_status', case_study_id=cs['id']) for cs in case_studies
                },
                'url_assessment_search': url_for('.case_study_assessment_search')
            }
        }
    )

    return render_template(
        '_react.html',
        component=rendered_component
    )


@main.route('/casestudy-assessment-search', methods=['GET'])
@login_required
@role_required('admin')
def case_study_assessment_search():
    search = request.args.get('search', None)
    response = data_api_client.req.admin().casestudy().assessment().get({
        'search': search
    })
    case_studies = response.get('case_studies')

    return jsonify(case_studies)


@main.route('/casestudy/<int:case_study_id>/assessment', methods=['GET'])
@main.route('/casestudy/<int:case_study_id>/assessment/<int:case_study_assessment_id>', methods=['GET'])
@login_required
@role_required('admin')
def case_study_view(case_study_id, case_study_assessment_id=None):
    role = request.args.get('role', None)
    response = data_api_client.req.admin().casestudy(case_study_id).get()
    case_study = response.get('case_study')
    domain = response.get('domain')
    case_study['domain'] = domain

    response = data_api_client.req.admin().casestudy().assessment().get({
        'case_study_id': case_study_id
    })
    case_studies = response.get('case_studies')

    userList = data_api_client.req.casestudy().users('admin').get()['user_list']
    adminUserNameIdList = {}

    for i in range(len(userList)):
            adminUserNameIdList.update({
                userList[i]["id"]: userList[i]['name']
                }
            )

    assessment_results = case_studies[0].get('assessment_results', [])
    delete_cs_assessment_url = None
    try:
        delete_cs_assessment_url = [{
            'url_case_study_assessment_delete': url_for(
                '.delete_case_study_assessment',
                case_study_id=case_study_id,
                case_study_assessment_id=ar.get('id')),
            'assessment_id': ar.get('id')
        }
            for ar in assessment_results]

    except Exception:
        pass

    rendered_component = render_component(
        'bundles/CaseStudy/CaseStudyViewWidget.js', {
            'casestudy': case_study,
            'meta': {
                'adminUserNameIdList': adminUserNameIdList,
                'casestudies': case_studies,
                'url_case_study_assessment_add': url_for('.add_case_study_assessment', case_study_id=case_study_id),
                'urls_case_study_assessment_delete': delete_cs_assessment_url,
                'url_case_study_assessment_update': url_for(
                    '.update_case_study_assessment',
                    case_study_id=case_study_id,
                    case_study_assessment_id=case_study_assessment_id
                ) if case_study_assessment_id else None,
                'role': role
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
            "assessor_user_id": json_payload.get('assessor_user_id')
        })
    )

    return jsonify(result)


@main.route('/casestudy/<int:case_study_id>/assessment/<int:case_study_assessment_id>', methods=['DELETE'])
@login_required
@role_required('admin' or 'manager')
def delete_case_study_assessment(case_study_id, case_study_assessment_id):
    json_payload = request.get_json(force=True)
    result = (
        data_api_client
        .req
        .admin()
        .casestudy(case_study_id)
        .assessment(case_study_assessment_id)
        .delete({
            'update_details': {
                'updated_by': current_user.email_address
            },
            "assessment": json_payload
        })
    )

    return jsonify(result)


@main.route('/casestudy/<int:case_study_id>/assessment/<int:case_study_assessment_id>', methods=['PUT'])
@login_required
@role_required('admin')
def update_case_study_assessment(case_study_id, case_study_assessment_id):
    json_payload = request.get_json(force=True)
    result = (
        data_api_client
        .req
        .admin()
        .casestudy(case_study_id)
        .assessment(case_study_assessment_id)
        .put({
            'update_details': {
                'updated_by': current_user.email_address
            },
            "assessment": json_payload
        })
    )

    return jsonify(result)


@main.route('/casestudy-assessment/<int:case_study_id>', methods=['PUT'])
@login_required
@role_required('admin')
def update_case_study_status(case_study_id):
    json_payload = request.get_json(force=True)
    result = (
        data_api_client
        .req
        .admin()
        .casestudy(case_study_id)
        .status()
        .put({
            'update_details': {
                'updated_by': current_user.email_address
            },
            "data": json_payload
        })
    )

    return jsonify(result)
