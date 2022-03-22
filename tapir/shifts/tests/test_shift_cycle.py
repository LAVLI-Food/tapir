import datetime

from tapir.accounts.tests.factories.factories import TapirUserFactory
from tapir.shifts.models import (
    ShiftCycleEntry,
    ShiftExemption,
)
from tapir.utils.tests_utils import TapirFactoryTestBase


class TestShiftCycle(TapirFactoryTestBase):
    FIRST_CYCLE_START_DATE = datetime.date(day=18, month=1, year=2021)
    SECOND_CYCLE_START_DATE = datetime.date(day=15, month=2, year=2021)

    def test_shift_cycle_start(self):
        user = TapirUserFactory.create(share_owner__is_investing=False)

        ShiftCycleEntry.apply_cycle_start(self.FIRST_CYCLE_START_DATE)
        self.assertEqual(
            user.shift_user_data.get_account_balance(),
            -1,
            "After once cycle, the user's balance should be -1.",
        )

        ShiftCycleEntry.apply_cycle_start(self.FIRST_CYCLE_START_DATE)
        self.assertEqual(
            user.shift_user_data.get_account_balance(),
            -1,
            "After applying the same cycle, the user's balance should not have changed.",
        )

        ShiftCycleEntry.apply_cycle_start(self.SECOND_CYCLE_START_DATE)
        self.assertEqual(
            user.shift_user_data.get_account_balance(),
            -2,
            "After a second, different cycle, the user's balance should be -2.",
        )

    def test_user_is_investing(self):
        user = TapirUserFactory.create(share_owner__is_investing=True)
        ShiftCycleEntry.apply_cycle_start(self.FIRST_CYCLE_START_DATE)
        self.assertEqual(
            user.shift_user_data.get_account_balance(),
            0,
            "Since that user is investing, they should not loose point at the beginning of the cycle.",
        )

    def test_exempted_once(self):
        user = TapirUserFactory.create(share_owner__is_investing=False)
        ShiftExemption.objects.create(
            start_date=self.FIRST_CYCLE_START_DATE - datetime.timedelta(days=1),
            end_date=self.SECOND_CYCLE_START_DATE - datetime.timedelta(days=1),
            shift_user_data=user.shift_user_data,
        )

        ShiftCycleEntry.apply_cycle_start(self.FIRST_CYCLE_START_DATE)
        self.assertEqual(
            user.shift_user_data.get_account_balance(),
            0,
            "The user is exempted from the first cycle, the account balance should be 0.",
        )

        ShiftCycleEntry.apply_cycle_start(self.SECOND_CYCLE_START_DATE)
        self.assertEqual(
            user.shift_user_data.get_account_balance(),
            -1,
            "The user is not exempted from the first cycle, the account balance should be 0.",
        )

    def test_exempted_both(self):
        user = TapirUserFactory.create(share_owner__is_investing=False)
        ShiftExemption.objects.create(
            start_date=self.FIRST_CYCLE_START_DATE - datetime.timedelta(days=1),
            end_date=self.SECOND_CYCLE_START_DATE + datetime.timedelta(days=1),
            shift_user_data=user.shift_user_data,
        )

        ShiftCycleEntry.apply_cycle_start(self.FIRST_CYCLE_START_DATE)
        ShiftCycleEntry.apply_cycle_start(self.SECOND_CYCLE_START_DATE)
        self.assertEqual(
            user.shift_user_data.get_account_balance(),
            0,
            "The user is exempted from both cycle, the account balance should be 0.",
        )

    def test_exemption_no_end_date(self):
        user = TapirUserFactory.create(share_owner__is_investing=False)
        ShiftExemption.objects.create(
            start_date=self.FIRST_CYCLE_START_DATE - datetime.timedelta(days=1),
            end_date=None,
            shift_user_data=user.shift_user_data,
        )

        ShiftCycleEntry.apply_cycle_start(self.FIRST_CYCLE_START_DATE)
        ShiftCycleEntry.apply_cycle_start(self.SECOND_CYCLE_START_DATE)
        self.assertEqual(
            user.shift_user_data.get_account_balance(),
            0,
            "The user is exempted from both cycle, the account balance should be 0.",
        )
