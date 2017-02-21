import os
import sys
import mock
import pytest
import codecs
from sh_scrapy.hsref import _HubstorageRef
from sh_scrapy.compat import to_native_str, to_bytes

TEST_AUTH = to_native_str(codecs.encode(to_bytes('1/2/3:authstr'), 'hex_codec'))


def test_init_disabled():
    hsref = _HubstorageRef()
    assert not hsref._client
    assert not hsref._project
    assert not hsref._job
    assert not hsref.enabled
    assert not hasattr(hsref, 'jobkey')
    assert not hsref._projectid
    assert not hsref._spiderid
    assert not hsref._jobcounter


@pytest.fixture
@mock.patch.dict(os.environ, {'SHUB_JOBKEY': '1/2/3'})
def hsref():
    return _HubstorageRef()


@pytest.fixture
def hsc_class(monkeypatch):
    hsc_class = mock.Mock()
    monkeypatch.setattr('scrapinghub.HubstorageClient', hsc_class)
    return hsc_class


def test_init(hsref):
    assert not hsref._client
    assert not hsref._project
    assert not hsref._job
    assert hsref.enabled
    assert hsref.jobkey == '1/2/3'
    assert hsref._projectid == 1
    assert hsref._spiderid == 2
    assert hsref._jobcounter == 3


@mock.patch.dict(os.environ, {'SHUB_JOBAUTH': TEST_AUTH})
def test_auth(hsref):
    assert hsref.auth == '1/2/3:authstr'


@mock.patch.dict(os.environ, {'SHUB_STORAGE': 'storage-url'})
def test_endpoint(hsref):
    assert hsref.endpoint == 'storage-url'


def test_job_ids(hsref):
    assert hsref.projectid == 1
    assert hsref.spiderid == 2
    assert hsref.jobid == 3


@mock.patch.dict(os.environ, {'SHUB_JOBAUTH': TEST_AUTH,
                              'SHUB_STORAGE': 'storage-url'})
def test_client(hsref, hsc_class):
    assert not hsref._client
    assert hsref.client == hsc_class.return_value
    hsc_class.assert_called_with(endpoint='storage-url',
                                 auth='1/2/3:authstr',
                                 user_agent=None)
    assert hsref._client
    assert hsref.client == hsref._client


@mock.patch.dict(os.environ, {'SHUB_JOBAUTH': TEST_AUTH,
                              'SHUB_STORAGE': 'storage-url',
                              'SHUB_HS_USER_AGENT': 'testUA'})
def test_client_custom_ua(hsref, hsc_class):
    assert not hsref._client
    assert hsref.client == hsc_class.return_value
    hsc_class.assert_called_with(endpoint='storage-url',
                                 auth='1/2/3:authstr',
                                 user_agent='testUA')
    assert hsref._client
    assert hsref.client == hsref._client


def test_project(hsref):
    hsc = mock.Mock()
    hsc.get_project.return_value = 'Project'
    hsref._client = hsc

    assert not hsref._project
    assert hsref.project == 'Project'
    hsc.get_project.assert_called_with('1')
    assert hsref._project == hsref.project


def test_job(hsref):
    project = mock.Mock()
    project.get_job.return_value = 'Job'
    hsref._project = project

    assert not hsref._job
    assert hsref.job == 'Job'
    project.get_job.assert_called_with((2, 3))
    assert hsref._job == hsref.job


def test_close(hsref):
    assert not hsref._client
    hsref.close()
    client = mock.Mock()
    hsref._client = client
    hsref.close()
    client.close.assert_called_with()
