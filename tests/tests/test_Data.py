import os.path

import pytest

import pymadx

PATH_TO_TEST_INPUT = "{}/../test_input/".format(
    os.path.dirname(os.path.abspath(__file__)))

@pytest.fixture
def atf2():
    return "{}/atf2-nominal-twiss-v5.2.tfs.tar.gz".format(
        PATH_TO_TEST_INPUT)

@pytest.mark.sanity
def test_loading_atf2(atf2):
    pymadx.Data.Tfs(atf2)
