#!/usr/bin/env python
# coding=utf-8
"""Exceptions

All exceptions
"""
from __future__ import unicode_literals

# error code
# role   x-xx-xxx  level - module - code
# level: 1 - 99
# module: 00: parameters; 01: auth; 02: user; 03: canvas; 04: cloud account; 99: http;
# code: 001 002 ...
# level为1的，都需要退出到登录页面

except_dict = {
    "ParamsError": {
        "code": "00001",
        "message": "parameter error: {info}",
        "messageKey": "ParamsError"
    },
    "NeedLogin": {
        "code": "01001",
        "message": "need login.",
        "messageKey": "NeedLogin"
    },
    "LoginFailed": {
        "code": "01002",
        "message": "login failed.",
        "messageKey": "LoginFailed"
    },
    "InvalidAcceessToken": {
        "code": "01003",
        "message": "invalid access token",
        "messageKey": "InvalidAcceessToken"
    },
    "AcceessTokenExpired": {
        "code": "01004",
        "message": "access token expired",
        "messageKey": "AcceessTokenExpired"
    },
    "RefreshTokenNotExists": {
        "code": "01005",
        "message": "refresh token doesn't exists",
        "messageKey": "RefreshTokenNotExists"
    },
    "UserCreateFailed": {
        "code": "02001",
        "message": "create user failed.",
        "messageKey": "UserCreateFailed"
    },
    "UserNotFound": {
        "code": "02002",
        "message": "user is not found.",
        "messageKey": "UserNotFound"
    },
    "UserUpdateFailed": {
        "code": "02003",
        "message": "user update failed.",
        "messageKey": "UserUpdateFailed"
    },
    "CanvasCreateFailed": {
        "code": "03001",
        "message": "canvas create failed.",
        "messageKey": "CanvasCreateFailed"
    },
    "CopyCanvasFailed": {
        "code": "03005",
        "message": "copu canvas failed.",
        "messageKey": "CopyCanvasFailed"
    },
    "CanvasNotFound": {
        "code": "03002",
        "message": "canvas is not found.",
        "messageKey": "CanvasNotFound"
    },
    "CanvasVersionCreateFailed": {
        "code": "03003",
        "message": "canvas version create failed.",
        "messageKey": "CanvasVersionCreateFailed"
    },
    "CanvasVersionNotFound": {
        "code": "03004",
        "message": "canvas version is not found.",
        "messageKey": "CanvasVersionNotFound"
    },
    "CanvasUpdateFailed": {
        "code": "03003",
        "message": "canvas update failed.",
        "messageKey": "CanvasUpdateFailed"
    },
    "ListAccountFailed": {
        "code": "04001",
        "message": "list cloudaccount failed.",
        "messageKey": "ListAccountFailed"
    },
    "DeleteAccountFailed": {
        "code": "04002",
        "message": "delete cloudaccount failed.",
        "messageKey": "DeleteAccountFailed"
    },
    "UpadteAccountFailed": {
        "code": "04003",
        "message": "update cloudaccount failed.",
        "messageKey": "UpadteAccountFailed"
    },
    "InsertAccountFailed": {
        "code": "04004",
        "message": "insert cloudaccount failed.",
        "messageKey": "InsertAccountFailed"
    },
    "GetAccountFailed": {
        "code": "04005",
        "message": "get cloudaccount failed.",
        "messageKey": "GetAccountFailed"
    },
    "CloudAccountPoliciesReadOnlyError": {
        "code": "04006",
        "message": "get CloudAccount readonly policy failed.",
        "messageKey": "CloudAccountPoliciesReadOnlyError"
    },
    "CloudAccountExists": {
        "code": "04007",
        "message": "CloudAccount already exist.",
        "messageKey": "CloudAccountExists"
    },
    "CloudAccountError": {
        "code": "04008",
        "message": "CloudAccount do not have sts error.",
        "messageKey": "CloudAccountError"
    },
    "PrimaryCloudAccountNotAllow": {
        "code": "04009",
        "message": "user cloudaccount number as same as primary cloudaccount number.",
        "messageKey": "PrimaryCloudAccountNotAllow"
    },
    "CloudAccountGetPoliciesError": {
        "code": "04010",
        "message": "this accesskey do not have authority to get policies.",
        "messageKey": "CloudAccountGetPoliciesError"
    },
    "SyncResourceError": {
        "code": "04011",
        "message": "sync resource error.",
        "messageKey": "SyncResourceError"
    },
    "CloudAccountDontModify": {
        "code": "04012",
        "message": "This cloudaccount number do not modify exist cloudaccount number.",
        "messageKey": "CloudAccountDontModify"
    },
    "SourceTypeNotFount": {
        "code": "04013",
        "message": "Do not get RescourceType.",
        "messageKey": "SourceTypeNotFount"
    },
    "CloudAccountNotFound": {
        "code": "04013",
        "message": "Do not get CloudAccount.",
        "messageKey": "CloudAccountNotFount"
    },
    "CanvasVersionAlreadyShared": {
        "code": "04014",
        "message": "Canvas already shared to this user.",
        "messageKey": "CanvasVersionAlreadyShared"
    },
    "CanNotShareToYourself": {
        "code": "04015",
        "message": "Canvas can not share to yourself.",
        "messageKey": "CanNotShareToYourself"
    }

}


def __init__(self, **kwargs):
    # make returned error message
    self.message = self.message.format(**kwargs)


def __str__(self):
    return self.message


def __repr__(self):
    return self.message


class HttpException(Exception):
    """HTTP Base exception.

    Base exception for all http exception
    """

    pass


exceptions_list = []
bases = (HttpException,)
attrs = {
    '__init__': __init__,
    '__str__': __str__,
    '__repr__': __repr__
}

# generate error classes,
# add them to exception_list
# and then convert to exceptions tuple

for (eklass_name, attr) in except_dict.items():
    attrs.update(attr)
    eklass = type(str(eklass_name), bases, attrs)
    exceptions_list.append(eklass)
    globals().update({eklass_name: eklass})
