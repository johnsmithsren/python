#!/usr/bin/env python
# coding=utf-8
"""Cloud Account Controller.

Cloud Account controller functions
"""
from __future__ import unicode_literals

import time
import json
import yaml
from jiagouyun.models import session_scope
from jiagouyun.models.entities import CloudAccount
from jiagouyun.models.entities import User
from jiagouyun.utils import aliyun
from jiagouyun.utils import exceptions
from jiagouyun.utils import params


# list policy info

def cloud_account_list_policies(akId, akSecret):
    ak = {
        'access_key_id': akId,
        'access_key_secret': akSecret
    }
    p = {}
    p['Action'] = 'ListPolicies'
    p['PolicyType'] = 'System'
    result, code = aliyun.invoke_api(ak, 'ram', p)
    if code != 200:
        raise exceptions.CloudAccountGetPoliciesError()

    policiesDict = json.loads(result)
    if 'Policies' not in policiesDict:
        raise exceptions.CloudAccountPoliciesReadOnlyError()

    return policiesDict


def cloud_account_quota_validate(user):
    # quota_validate权限鉴定
    with session_scope() as db_session:
        curUser = db_session.query(users) \
            .filter(users.id == user['id']) \
            .first()

        uidCount = db_session.query(CloudAccount)\
            .filter(AccountUid.user_id == user['id'])\
            .count()

        return uidCount < curUser.uid_quota


def cloud_account_exists(uid, cloud_platform, user):
    # uid_validate
    with session_scope() as db_session:
        existsUid = db_session.query(CloudAccount).filter(CloudAccount.unique_id == uid, CloudAccount.platform == cloud_platform, CloudAccount.user_id == user).count()
        return existsUid > 0


def get_cloud_account_identity(akId, akSecret):
    p = {
        'Action': 'GetCallerIdentity',
        'RegionId': 'cn-hangzhou'
    }
    print akId, akSecret
    ak = {
        'access_key_id': akId,
        'access_key_secret': akSecret
    }
    result, code = aliyun.invoke_api(ak, 'sts', p)

    if code != 200:
        raise exceptions.CloudAccountError()

    resultDict = json.loads(result)

    return resultDict


def cloud_account_verify(param):

    # unique_id鉴定
    print param
    _params = param["info"]
    _params = json.loads(_params.replace("'", "\""))
    accountUid = {
        'access_key_id': _params["akid"],
        'access_key_secret': _params["aksecret"]
    }
    result = get_cloud_account_identity(accountUid["access_key_id"], accountUid["access_key_secret"])
    accountId = result['AccountId']
    userId = result['UserId']
    if accountId == userId:
        raise exceptions.PrimaryCloudAccountNotAllow()

    accountUid["pk"] = accountId
    accountUid["name"] = accountId
    accountUid["userId"] = accountId

    policiesDict = cloud_account_list_policies(accountUid["access_key_id"], accountUid["access_key_secret"])

    policies = policiesDict['Policies']
    policy = policies['Policy']
    # 有只读权限
    if len(filter(lambda x: x['PolicyName'] == 'ReadOnlyAccess', policy)) >= 1:
        return accountUid
    else:
        raise exceptions.CloudAccountPoliciesReadOnlyError()


def list_cloud_account(page, results_per_page, user_id=None):
    with session_scope() as db_session:
        start = (page - 1) * results_per_page
        end = start + results_per_page
        query = db_session.query(CloudAccount)
        if user_id is not None:
            query = query.filter(CloudAccount.user_id == user_id)
        count = query.count()
        cloud_accounts = query.order_by(CloudAccount.create_time.desc()).slice(start, end).all()
        user_dict = db_session.query(User).filter(User.id == user_id).first()
        return count, [cloud_account.to_dict(exclude_columns=["info"]) for cloud_account in cloud_accounts]
    return None


def get_cloud_account(cloud_account_id):
    with session_scope() as db_session:
        cloud_account = db_session.query(CloudAccount).get(cloud_account_id)
        if cloud_account is not None:
            return cloud_account.to_dict(exclude_columns=["info"])
    return None


def get_invoke_ak(cloud_account_id):
    with session_scope() as db_session:
        cloud_account = db_session.query(CloudAccount).get(cloud_account_id)
        if cloud_account is not None:
            return cloud_account.to_dict()
    return None


def create_cloud_account(user_id, data):
    with session_scope() as db_session:
        cloud_account_result = cloud_account_verify(data)
        if cloud_account_exists(cloud_account_result["userId"], data['platform'], user_id):
            raise exceptions.CloudAccountExists()
        cloud_account = CloudAccount()
        cloud_account.set_create_table_base()
        support_columns = ("description", "info", "platform", "description", "account_name")
        for column in support_columns:
            if column in data:
                setattr(cloud_account, column, data[column])
        cloud_account.status = 1
        cloud_account.unique_id = cloud_account_result["userId"]
        cloud_account.user_id = user_id
        db_session.add(cloud_account)
        db_session.commit()
        return cloud_account.to_dict(exclude_columns=["info"])
    return None


def update_cloud_account(cloud_account_id, data):
    with session_scope() as db_session:
        account = db_session.query(CloudAccount).get(cloud_account_id)
        if account is not None:
            if 'info' in data:
                cloud_account_result = cloud_account_verify(data)
                if cloud_account_result["userId"] != account.unique_id:
                    raise exceptions.CloudAccountDontModify()
            account.set_update_table_base()
            support_columns = ("info", "description", "account_name", "status")
            for column in support_columns:
                if column in data:
                    setattr(account, column, data[column])
            db_session.commit()
            return account.to_dict(exclude_columns=["info"])
    return None


def delete_cloud_account(cloud_account_id):
    with session_scope() as db_session:
        db_session.query(CloudAccount).filter(CloudAccount.id == cloud_account_id).delete(False)
        db_session.commit()
