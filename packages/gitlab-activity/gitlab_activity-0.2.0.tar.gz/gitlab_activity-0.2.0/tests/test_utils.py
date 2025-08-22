"""Tests for utility functions"""
import os
import time
from pathlib import Path
from unittest import mock

import dateutil.parser
import pytz
import toml
from pytest import mark
from pytest import raises

from gitlab_activity import utils
from gitlab_activity.utils import *


@mark.parametrize(
    'value',
    [
        '{"key": "value"}',
        '["v1", "v2"]',
    ],
)
def test_custom_param_type(value):
    """Test CustomParamType casts input properly"""
    assert ActivityParamType.convert(value=value, param=None, ctx=None) == json.loads(
        value.replace("'", '"')
    )


def test_custom_param_type_exceptions():
    """Test CustomParamType raises exceptions on incorrect inputs"""
    with raises(click.exceptions.BadParameter) as excinfo:
        ActivityParamType.convert(value='test', param=None, ctx=None)
        assert 'Failed to cast into list using json.loads' in str(excinfo.value)


@mark.parametrize(
    'config',
    [
        {'options': {'activity': {'foo': 'bar'}}},
        {'options': {'since': 12345678}},
        {'options': {'append': 'True'}},
        {'activity': 'True'},
        {'activity': {'bot_users': {'foo': 'bar'}}},
        {'activity': {'foo': []}},
        {'activity': {'categories': {'issues': {'foo': 'bar'}}}},
        {'activity': {'categories': {'merge_requests': [{'foo': 'bar'}]}}},
    ],
)
def test_read_config_validation(tmpdir, config):
    """Test if read_config catch validation exceptions"""
    path_tmp = Path(tmpdir)
    config_file = path_tmp.joinpath('config.toml')

    # Config that raises validation error
    with open(config_file, 'w') as f:
        toml.dump(config, f)

    with raises(RuntimeError) as excinfo:
        read_config(config_file)


@mark.parametrize(
    'env_name',
    ['NEXT_VERSION_SPECIFIER', 'CI_COMMIT_TAG'],
)
def test_next_version_specifier(env_name):
    """Test if get_next_version_specifier can be taken from different env vars"""
    with mock.patch.dict(os.environ, {env_name: env_name}, clear=True):
        version = get_next_version_specifier()
        assert version == env_name


@mark.parametrize(
    'env_name',
    ['GITLAB_ACCESS_TOKEN', 'CI_JOB_TOKEN'],
)
def test_auth_token(env_name):
    """Test if auth token can be taken from different env vars"""
    with mock.patch.dict(os.environ, {env_name: env_name}, clear=True):
        token = get_auth_token()
        assert token == env_name


@mock.patch('subprocess.run')
def test_auth_token_with_glab(sub_func, sp_completed_process):
    """Test if auth token can be taken glab CLI command"""
    with mock.patch.dict(os.environ, {}, clear=True):
        sub_func.return_value = sp_completed_process(stderr='Token: foo')
        token = get_auth_token()
        assert token == 'foo'


@mock.patch('subprocess.run')
@mark.parametrize(
    'exception',
    [
        subprocess.CalledProcessError('127', 'glab'),
        FileNotFoundError,
    ],
)
def test_auth_token_with_glab_exception(sub_func, exception):
    """Test if auth_token returns None when exception is raised"""
    with mock.patch.dict(os.environ, {}, clear=True):
        sub_func.side_effect = exception
        token = get_auth_token()
        assert token is None


@mark.parametrize(
    'arg,exp_domain,exp_target',
    [
        ('example.domain.io/foo/bar', 'example.domain.io', 'foo/bar'),
        ('http://user@example.domain.io/foo/bar', 'example.domain.io', 'foo/bar'),
    ],
)
def test_parse_target(arg, exp_domain, exp_target):
    """Test parse_target when targets are given in non-standard format"""

    domain, target = sanitize_target(arg)

    assert domain == exp_domain
    assert target == exp_target


def test_get_commits_exception():
    """Test get_commits catches exception when invalid input is given"""
    commits = get_commits('gitlab.com', 'foo', 123456, 'token')
    assert commits == None


def test_all_tags_exception():
    """Test get_all_tags raises Exception when tags not found"""
    with raises(RuntimeError) as excinfo:
        get_all_tags('gitlab.com', 'foo', 12345, 'token')
    assert str(excinfo.value) == 'Failed to get tags for target foo'


def test_get_namespace_projects_exception():
    """Test get_namespace_projects raises exception when invalid target"""
    with raises(RuntimeError) as excinfo:
        get_namespace_projects('gitlab.com', 'foo', 'token')
    assert str(excinfo.value) == 'Failed to retrieve projects for namespace foo'


def test_get_project_id():
    """Test _get_project_id returns None when invalid input"""
    tid = utils._get_project_or_group_id('gitlab.com', 'foo', 'group', 'token')
    assert tid is None


def test_get_latest_tag():
    """Test get_latest_tag returns None when invalid input"""
    assert utils.get_latest_tag('gitlab.com', 'foo', '12345', 'token') is None


def test_get_latest_mr():
    """Test get_latest_mr returns None when invalid input"""
    with raises(RuntimeError) as excinfo:
        utils.get_latest_mr('gitlab.com', 'foo', 'token')
    assert str(excinfo.value) == 'Failed to MRs for target foo'


def test_get_datetime_and_type():
    """Test get_datetime_and_type raises exception when invalid input"""
    with raises(RuntimeError) as excinfo:
        get_datetime_and_type('gitlab.com', 12345, '2023-15-10', 'token')
    assert str(excinfo.value) == '2023-15-10 not found as a ref or valid date format'


def test_get_datetime_and_type_converts_git_ref_datetime_to_utc():
    """Test datetime from a git ref is normalised to UTC."""

    commit_dt = dateutil.parser.parse("2025-01-01T09:00:00+09:00")
    expected_utc_dt = dateutil.parser.parse("2025-01-01T00:00:00+00:00")

    assert commit_dt.astimezone(pytz.utc) == expected_utc_dt.astimezone(pytz.utc)

    with mock.patch("gitlab_activity.utils._get_datetime_from_git_ref") as mock_get_dt:
        mock_get_dt.return_value = commit_dt

        dt, is_ref = utils.get_datetime_and_type(
            "gitlab.com", 12345, "dummy_ref", "token"
        )

    assert is_ref is True
    assert dt.tzinfo == pytz.utc
    assert dt == expected_utc_dt


def test_get_datetime_and_type_converts_string_with_timezone_to_utc():
    """Test string datetime with offset is normalised to UTC"""

    date_str = "2025-07-01T10:00:00+05:30"
    expected_utc_dt = dateutil.parser.parse("2025-07-01T04:30:00+00:00")

    with mock.patch("gitlab_activity.utils._get_datetime_from_git_ref") as mock_get_dt:
        mock_get_dt.side_effect = AssertionError(
            "_get_datetime_from_git_ref should not be called"
        )

        dt, is_ref = utils.get_datetime_and_type("gitlab.com", 12345, date_str, "token")

    assert is_ref is False
    assert dt.tzinfo == pytz.utc
    assert dt == expected_utc_dt


def test_get_datetime_and_type_converts_string_without_timezone_to_utc():
    """Test string datetime without offset is treated as local time and then normalised to UTC"""

    fake_tz_name = "Asia/Tokyo"  # UTC+09:00

    date_str = "2025-07-01T11:30:00"
    expected_utc_dt = dateutil.parser.parse("2025-07-01T02:30:00+00:00")

    with mock.patch.dict(os.environ, {"TZ": fake_tz_name}):
        time.tzset()

        with mock.patch(
            "gitlab_activity.utils._get_datetime_from_git_ref"
        ) as mock_get_dt:
            mock_get_dt.side_effect = AssertionError(
                "_get_datetime_from_git_ref should not be called"
            )

            dt, is_ref = utils.get_datetime_and_type(
                "gitlab.com", 12345, date_str, "token"
            )

    assert is_ref is False
    assert dt.tzinfo == pytz.utc
    assert dt == expected_utc_dt
