# These are tests for Zulip's database migrations.  System documented at:
#   https://zulip.readthedocs.io/en/latest/subsystems/schema-migrations.html
#
# You can also read
#   https://www.caktusgroup.com/blog/2016/02/02/writing-unit-tests-django-migrations/
# to get a tutorial on the framework that inspired this feature.
from decimal import Decimal
from typing import Optional

import orjson
from django.db.migrations.state import StateApps
from django.utils.timezone import now as timezone_now

from zerver.lib.test_classes import MigrationsTestCase
from zerver.lib.test_helpers import use_db_models

# Important note: These tests are very expensive, and details of
# Django's database transaction model mean it does not super work to
# have a lot of migrations tested in this file at once; so we usually
# delete the old migration tests when adding a new one, so this file
# always has a single migration test in it as an example.
#
# The error you get with multiple similar tests doing migrations on
# the same table is this (table name may vary):
#
#   django.db.utils.OperationalError: cannot ALTER TABLE
#   "zerver_subscription" because it has pending trigger events
#
# As a result, we generally mark these tests as skipped once they have
# been tested for a migration being merged.

USER_ACTIVATED = 102
USER_FULL_NAME_CHANGED = 124
REALM_DISCOUNT_CHANGED = 209
OLD_VALUE = "1"
NEW_VALUE = "2"


class RealmAuditLogExtraData(MigrationsTestCase):
    migrate_from = "0459_remove_invalid_characters_from_user_group_name"
    migrate_to = "0460_backfill_realmauditlog_extradata_to_json_field"

    full_name_change_log_id: Optional[int] = None
    valid_json_log_id: Optional[int] = None
    str_json_log_id: Optional[int] = None
    # The BATCH_SIZE is defined as 5000 in
    # backfill_realmauditlog_extradata_to_json_field, this later is used to test
    # if batching works properly.
    DATA_SIZE = 10005
    expected_console_output = """Audit log entry 50003 with event type REALM_DISCOUNT_CHANGED is skipped.
The data consistency needs to be manually checked.
  Discount data to remove after the upcoming JSONField migration:
{'old_discount': Decimal('25.0000'), 'new_discount': Decimal('50')}
  Discount data to keep after the upcoming JSONField migration:
{}

Audit log entry 50004 with event type REALM_DISCOUNT_CHANGED is skipped.
The data consistency needs to be manually checked.
  Discount data to remove after the upcoming JSONField migration:
{'old_discount': Decimal('25.0000'), 'new_discount': Decimal('50')}
  Discount data to keep after the upcoming JSONField migration:
{'new_discount': '50', 'old_discount': '25.0000'}

Audit log entry with id 50001 has extra_data_json been inconsistently overwritten.
  The old value is:
{"corrupted":"foo"}
  The new value is:
{"key":"value"}

Audit log entry with id 50002 has extra_data_json been inconsistently overwritten.
  The old value is:
{"corrupted":"bar"}
  The new value is:
{"key":"value"}

"""

    @use_db_models
    def setUpBeforeMigration(self, apps: StateApps) -> None:
        Realm = apps.get_model("zerver", "Realm")
        RealmAuditLog = apps.get_model("zerver", "RealmAuditLog")
        event_time = timezone_now()
        realm = Realm.objects.get(string_id="zulip")

        full_name_change_log = RealmAuditLog(
            realm=realm,
            event_type=USER_FULL_NAME_CHANGED,
            event_time=event_time,
            extra_data="foo",
        )

        new_full_name_change_log = RealmAuditLog(
            realm=realm,
            event_type=USER_FULL_NAME_CHANGED,
            event_time=event_time,
            extra_data="foo",
            extra_data_json={OLD_VALUE: "foo", NEW_VALUE: "bar"},
        )

        valid_json_log = RealmAuditLog(
            realm=realm,
            event_type=USER_ACTIVATED,
            event_time=event_time,
            extra_data=orjson.dumps({"key": "value"}).decode(),
        )

        str_json_log = RealmAuditLog(
            realm=realm,
            event_type=USER_ACTIVATED,
            event_time=event_time,
            extra_data=str({"key": "value"}),
        )

        self.backfilled_inconsistent_log_id = RealmAuditLog.objects.create(
            realm=realm,
            event_type=USER_ACTIVATED,
            event_time=event_time,
            extra_data=orjson.dumps({"key": "baz"}).decode(),
            extra_data_json={
                "key": "baz",
                "inconsistent_old_extra_data": orjson.dumps({"key": "baz"}).decode(),
                "inconsistent_old_extra_data_json": {"key": "value corrupted"},
            },
        ).id

        # The following audit log entries have preset ids because we use
        # them to assert the generated log output that is defined before
        # the test case is run.
        inconsistent_json_log = RealmAuditLog(
            id=50001,
            realm=realm,
            event_type=USER_ACTIVATED,
            event_time=event_time,
            extra_data=orjson.dumps({"key": "value"}).decode(),
            extra_data_json={"corrupted": "foo"},
        )

        inconsistent_str_json_log = RealmAuditLog(
            id=50002,
            realm=realm,
            event_type=USER_ACTIVATED,
            event_time=event_time,
            extra_data=str({"key": "value"}),
            extra_data_json={"corrupted": "bar"},
        )

        self.old_decimal_log_id = RealmAuditLog.objects.create(
            id=50003,
            realm=realm,
            event_type=REALM_DISCOUNT_CHANGED,
            event_time=event_time,
            extra_data=str({"old_discount": Decimal("25.0000"), "new_discount": Decimal("50")}),
        ).id

        self.new_decimal_log_id = RealmAuditLog.objects.create(
            id=50004,
            realm=realm,
            event_type=REALM_DISCOUNT_CHANGED,
            event_time=event_time,
            extra_data=str({"old_discount": Decimal("25.0000"), "new_discount": Decimal("50")}),
            extra_data_json={"old_discount": Decimal("25.0000"), "new_discount": Decimal("50")},
        ).id

        RealmAuditLog.objects.bulk_create(
            [
                full_name_change_log,
                new_full_name_change_log,
                valid_json_log,
                str_json_log,
                inconsistent_json_log,
                inconsistent_str_json_log,
            ]
        )
        self.full_name_change_log_id = full_name_change_log.id
        self.new_full_name_change_log_id = new_full_name_change_log.id
        self.valid_json_log_id = valid_json_log.id
        self.str_json_log_id = str_json_log.id

        other_logs = []
        for i in range(self.DATA_SIZE):
            other_logs.append(
                RealmAuditLog(
                    realm=realm,
                    event_type=USER_ACTIVATED,
                    event_time=event_time,
                    extra_data=orjson.dumps({"data": i}).decode(),
                )
            )
        self.other_logs_id = [
            audit_log.id for audit_log in RealmAuditLog.objects.bulk_create(other_logs)
        ]

        # No new audit log entry should have extra_data_json populated as of
        # now except for the entries created with non-default values.
        self.assert_length(
            RealmAuditLog.objects.filter(
                event_time__gte=event_time,
            ).exclude(
                extra_data_json={},
            ),
            5,
        )

    def test_realmaudit_log_extra_data_to_json(self) -> None:
        RealmAuditLog = self.apps.get_model("zerver", "RealmAuditLog")

        self.assertIsNotNone(self.full_name_change_log_id)
        self.assertIsNotNone(self.valid_json_log_id)
        self.assertIsNotNone(self.str_json_log_id)

        full_name_change_log = RealmAuditLog.objects.filter(id=self.full_name_change_log_id).first()
        new_full_name_change_log = RealmAuditLog.objects.filter(
            id=self.new_full_name_change_log_id
        ).first()
        valid_json_log = RealmAuditLog.objects.filter(id=self.valid_json_log_id).first()
        str_json_log = RealmAuditLog.objects.filter(id=self.str_json_log_id).first()

        self.assertIsNotNone(full_name_change_log)
        self.assertEqual(full_name_change_log.extra_data_json, {"1": "foo", "2": None})

        self.assertIsNotNone(new_full_name_change_log)
        self.assertEqual(new_full_name_change_log.extra_data_json, {"1": "foo", "2": "bar"})

        self.assertIsNotNone(valid_json_log)
        self.assertEqual(valid_json_log.extra_data_json, {"key": "value"})

        self.assertIsNotNone(str_json_log)
        self.assertEqual(str_json_log.extra_data_json, {"key": "value"})

        other_logs = RealmAuditLog.objects.filter(id__in=self.other_logs_id).order_by("id")
        self.assertIsNotNone(other_logs)
        self.assert_length(other_logs, self.DATA_SIZE)
        for index, audit_log in enumerate(other_logs):
            self.assertEqual(audit_log.extra_data_json, {"data": index})

        inconsistent_json_log = RealmAuditLog.objects.get(
            extra_data_json__inconsistent_old_extra_data=orjson.dumps({"key": "value"}).decode()
        )
        self.assertIsNotNone(inconsistent_json_log)
        self.assertEqual(inconsistent_json_log.id, 50001)
        self.assertEqual(
            inconsistent_json_log.extra_data_json["inconsistent_old_extra_data_json"],
            {"corrupted": "foo"},
        )

        inconsistent_str_json_log = RealmAuditLog.objects.get(
            extra_data_json__inconsistent_old_extra_data=str({"key": "value"})
        )
        self.assertIsNotNone(inconsistent_str_json_log)
        self.assertEqual(inconsistent_str_json_log.id, 50002)
        self.assertEqual(
            inconsistent_str_json_log.extra_data_json["inconsistent_old_extra_data_json"],
            {"corrupted": "bar"},
        )

        backfilled_inconsistent_log = RealmAuditLog.objects.get(
            id=self.backfilled_inconsistent_log_id
        )
        self.assertIsNotNone(backfilled_inconsistent_log)
        self.assertEqual(
            backfilled_inconsistent_log.extra_data_json,
            {
                "key": "baz",
                "inconsistent_old_extra_data": orjson.dumps({"key": "baz"}).decode(),
                "inconsistent_old_extra_data_json": {"key": "value corrupted"},
            },
        )
