# -*- coding: utf-8 -*-
"""Cheque lifecycle rules."""

import pytest

from modules.checks import CheckModule


def _register(checks, admin, party_id=None, direction="received", amount=500000):
    return checks.register_check(
        check_number="123456", bank_name="ملت", amount=amount, due_date="20261231",
        direction=direction, party_id=party_id, box_id=admin["box_id"], user_id=admin["id"],
    )


def test_collecting_received_check_creates_receipt(db, admin, party):
    db.execute("UPDATE parties SET balance = 800000 WHERE id = ?;", (party["id"],))
    checks = CheckModule()
    check_id = _register(checks, admin, party_id=party["id"])

    checks.mark_collected(check_id, admin["id"])

    check = db.fetch_one("SELECT * FROM checks WHERE id = ?;", (check_id,))
    assert check["status"] == "collected"

    treasury = db.fetch_all("SELECT * FROM treasury_transactions;")
    assert len(treasury) == 1
    assert treasury[0]["trans_type"] == "receive"
    assert treasury[0]["amount"] == pytest.approx(500000)

    balance = db.fetch_one("SELECT balance FROM parties WHERE id = ?;", (party["id"],))["balance"]
    assert balance == pytest.approx(300000)


def test_issued_check_is_paid_out_on_collection(db, admin):
    checks = CheckModule()
    check_id = _register(checks, admin, direction="issued", amount=250000)

    checks.mark_collected(check_id, admin["id"])

    treasury = db.fetch_all("SELECT * FROM treasury_transactions;")
    assert len(treasury) == 1
    assert treasury[0]["trans_type"] == "pay"

    entry = db.fetch_one("SELECT * FROM journal_entries WHERE source_type = 'treasury';")
    assert entry is not None


def test_check_cannot_be_collected_twice(db, admin):
    checks = CheckModule()
    check_id = _register(checks, admin)

    checks.mark_collected(check_id, admin["id"])
    with pytest.raises(ValueError):
        checks.mark_collected(check_id, admin["id"])


def test_bounced_check_has_no_cash_effect(db, admin):
    checks = CheckModule()
    check_id = _register(checks, admin)

    checks.mark_bounced(check_id)

    assert db.fetch_one("SELECT status FROM checks WHERE id = ?;", (check_id,))["status"] == "bounced"
    assert db.fetch_one("SELECT COUNT(*) AS c FROM treasury_transactions;")["c"] == 0


def test_only_pending_checks_can_be_edited_or_deleted(db, admin):
    checks = CheckModule()
    pending_id = _register(checks, admin)
    collected_id = _register(checks, admin)

    checks.update_check(pending_id, "999", "صادرات", 600000, "20270101", "")
    checks.delete_check(pending_id)
    assert db.fetch_one("SELECT COUNT(*) AS c FROM checks WHERE id = ?;", (pending_id,))["c"] == 0

    checks.mark_collected(collected_id, admin["id"])
    with pytest.raises(ValueError):
        checks.update_check(collected_id, "1", "x", 1, "20270101")
    with pytest.raises(ValueError):
        checks.delete_check(collected_id)


def test_checks_are_filtered_by_status_and_box(db, admin):
    checks = CheckModule()
    pending_id = _register(checks, admin)
    _register(checks, admin, amount=1000)
    checks.mark_bounced(pending_id)

    assert len(checks.get_checks()) == 2
    assert len(checks.get_checks(status="bounced")) == 1
    assert len(checks.get_checks(box_id=admin["box_id"])) == 2
