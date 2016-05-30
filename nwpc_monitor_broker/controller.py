# coding=utf-8
from nwpc_monitor_broker import app, db
from nwpc_monitor.model import Owner

from flask import json, request, jsonify,render_template


@app.route('/')
def get_index_page():
    return render_template("index.html")

@app.route('/<owner>')
def get_owner_page(owner):

    query = db.session.query(Owner).filter(Owner.owner_name == owner)
    owner_object = query.first()

    if owner_object.owner_type == "org":
        return get_org_page(owner)
    elif owner_object.owner_type == "user":
        return get_user_page(owner)
    else:
        result = {'error':'wrong'}
        return jsonify(result)


def get_user_page(user):
    return render_template("user.html", user=user)


def get_org_page(org):
    return render_template("organization.html", org=org)