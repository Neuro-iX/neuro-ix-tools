import pytest

from neuro_ix_tools.bids import BIDSDirectory, ClinicaDirectory


# TESTS ON SUB ONLY DATASET
@pytest.fixture()
def bids_sub():
    return BIDSDirectory("tests/data/bids_sub")


def test_bids_sub_get_subjects(bids_sub):
    subjects = bids_sub.get_subjects()

    assert len(subjects) == 2


def test_bids_sub_get_sessions(bids_sub):
    session = bids_sub.get_sessions("sub-000103")

    assert not bids_sub.has_session
    assert len(session) == 0


def test_bids_sub_walk(bids_sub):
    walked = list(bids_sub.walk())

    assert len(walked) == 2
    assert len(walked[0]) == 1, "Walk seems to report sessions"
    assert len(walked) == len(bids_sub)


def test_bids_sub_get_all_t1w(bids_sub):
    t1ws = list(bids_sub.get_all_t1w("sub-000103"))

    assert len(t1ws) == 1
    assert "T1w.nii.gz" in t1ws[0]


def test_bids_sub_extract_sub_ses(bids_sub):
    t1ws = list(bids_sub.get_all_t1w("sub-000103"))
    sub, ses = bids_sub.extract_sub_ses(t1ws[0])
    assert sub == "sub-000103"
    assert ses is None


# TESTS ON SUB AND SES DATASET
@pytest.fixture()
def bids_sub_ses():
    return BIDSDirectory("tests/data/bids_sub_ses")


def test_bids_sub_ses_get_subjects(bids_sub_ses):
    subjects = bids_sub_ses.get_subjects()

    assert len(subjects) == 2


def test_bids_sub_ses_get_sessions(bids_sub_ses):
    session = bids_sub_ses.get_sessions("sub-000103")

    assert bids_sub_ses.has_session
    assert len(session) == 2


def test_bids_sub_ses_walk(bids_sub_ses):
    walked = list(bids_sub_ses.walk())

    assert len(walked) == 3
    assert len(walked[0]) == 2, "Walk did not report sessions"
    assert len(walked) == len(bids_sub_ses)


def test_bids_sub_ses_get_all_t1w(bids_sub_ses):
    t1ws = list(bids_sub_ses.get_all_t1w("sub-000103", "ses-headmotion2"))

    assert len(t1ws) == 1
    assert "T1w.nii.gz" in t1ws[0]


def test_bids_sub_ses_extract_sub_ses(bids_sub_ses):
    t1ws = list(bids_sub_ses.get_all_t1w("sub-000103", "ses-standard"))
    sub, ses = bids_sub_ses.extract_sub_ses(t1ws[0])
    assert sub == "sub-000103"
    assert ses == "ses-standard"


# TESTS ON CLINICA DATASET
@pytest.fixture()
def clinica():
    return ClinicaDirectory("tests/data/clinica")


def test_clinica_get_subjects(clinica):
    subjects = clinica.get_subjects()

    assert len(subjects) == 2


def test_clinica_get_sessions(clinica):
    session = clinica.get_sessions("sub-000103")

    assert len(session) == 2


def test_clinica_walk(clinica):
    walked = list(clinica.walk())

    assert len(walked) == 3
    assert len(walked[0]) == 2, "Walk did not report sessions"
    assert len(walked) == len(clinica)


def test_clinica_get_all_t1w(clinica):
    t1ws = list(clinica.get_all_t1w("sub-000103", "ses-headmotion2"))

    assert len(t1ws) == 1
    assert "T1w.nii.gz" in t1ws[0]


def test_clinica_extract_sub_ses(clinica):
    t1ws = list(clinica.get_all_t1w("sub-000103", "ses-standard"))
    sub, ses = clinica.extract_sub_ses(t1ws[0])
    assert sub == "sub-000103"
    assert ses == "ses-standard"
