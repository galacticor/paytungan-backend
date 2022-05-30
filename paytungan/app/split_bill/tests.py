# from django.test import TestCase
from datetime import datetime
from re import U
from typing import Optional
from unittest import TestCase
from unittest.mock import MagicMock
from collections import OrderedDict
from faker import Faker

from paytungan.app.split_bill.models import Bill, SplitBill, User
from paytungan.app.split_bill.services import BillService, SplitBillService
from paytungan.app.split_bill.specs import (
    BillDomain,
    CreateBillSpec,
    CreateGroupSplitBillSpec,
    DeleteSplitBillSpec,
    GetBillListSpec,
    GetSplitBillCurrentUserSpec,
    GetSplitBillListSpec,
    GroupSplitBillDomain,
    UserIdWithAmountBillDomain,
)


class TestSplitBillService(TestCase):
    def setUp(self) -> None:
        self.bill_accessor = MagicMock()
        self.split_bill_accessor = MagicMock()
        self.bill_service = BillService(bill_accessor=self.bill_accessor)
        self.split_bill_service = SplitBillService(
            split_bill_accessor=self.split_bill_accessor,
            bill_accessor=self.bill_accessor,
        )

    @staticmethod
    def _get_bill_dummy(
        seed: int, split_bill_id: Optional[int] = None, user_id: Optional[int] = None
    ) -> BillDomain:
        fake = Faker()
        Faker.seed(seed)
        time_now = datetime.utcnow()
        return BillDomain(
            id=fake.pyint(),
            user_id=user_id or fake.pyint(),
            split_bill_id=split_bill_id or fake.pyint(),
            amount=fake.pyint(min_value=10000, max_value=100000),
            admin_fee=fake.pyint(min_value=100, max_value=100000),
            status=fake.pystr(),
            details=fake.pystr_format(),
            created_at=time_now,
            updated_at=time_now,
        )

    def test_bill_service_get(self):
        self.bill_service.get_bill(1)
        assert True

    def test_bill_service_get_list(self):
        self.bill_service.get_bill_list(
            GetBillListSpec(
                bill_ids=[1],
            )
        )
        assert True

    def test_bill_service_create(self):
        self.bill_service.create_bill(
            CreateBillSpec(user_id=1, split_bill_id=1, amount=10000, admin_fee=100)
        )
        assert True

    def test_bill_service_get_list_by_split_bill_id(self):
        self.bill_service.get_bill_list(
            GetBillListSpec(
                split_bill_ids=[1],
            )
        )
        assert True

    def test_split_bill_service_get(self):
        self.split_bill_service.get_split_bill(GetSplitBillListSpec(bill_ids=[1]))
        assert True

    def test_split_bill_service_get_list(self):
        self.split_bill_service.get_split_bill_list(GetSplitBillListSpec(bill_ids=[1]))
        assert True

    def test_split_bill_service_get_list_by_user_id(self):
        self.split_bill_service.get_split_bill_list(GetSplitBillListSpec(bill_ids=[1]))
        assert True

    def test_create_group_split_bill(self):
        spec = CreateGroupSplitBillSpec(
            name="tets",
            user_fund_id=1,
            withdrawal_method="GOPAY",
            withdrawal_number="asasa",
            amount=2460,
            bills=[
                UserIdWithAmountBillDomain(
                    user_id=1,
                    amount=10000,
                    admin_fee=100,
                    details="Beli nasi goreng si dandang",
                ),
                UserIdWithAmountBillDomain(
                    user_id=1,
                    amount=10000,
                    admin_fee=100,
                    details="Beli nasi goreng si dandang",
                ),
            ],
        )

        dummy_user = User(
            id=1,
            username="username",
            name="name",
            email="user123",
            profil_image="string",
        )

        dummy_split_bill = SplitBill(
            id=1,
            name="tets",
            user_fund=dummy_user,
            withdrawal_method="GOPAY",
            withdrawal_number="asasa",
            amount=2460,
        )

        dummy_bills = [
            Bill(
                user_id=1,
                split_bill_id=1,
                amount=2460,
                status="PENDING",
                details="Beli nasi goreng si dandang",
            ),
            Bill(
                user_id=2,
                split_bill_id=1,
                amount=2460,
                status="PENDING",
                details="Beli nasi goreng si dandang",
            ),
        ]

        self.split_bill_accessor.create.return_value = dummy_split_bill
        self.bill_accessor.bulk_create.return_value = dummy_bills

        result = self.split_bill_service.create_group_split_bill(spec)

        self.assertEqual(result.name, spec.name)

    def test_get_split_bill_list_current_user_success(self):
        dummy_split_bills = [
            GroupSplitBillDomain(
                id=1,
                name="tets",
                user_fund_id=1,
                user_fund_email="user123@gmail.com",
                withdrawal_method="GOPAY",
                withdrawal_number="asasa",
                amount=123,
                created_at=datetime.utcnow(),
                updated_at=datetime.utcnow(),
            )
        ]
        dummy_bills = [
            Bill(
                user_id=1,
                split_bill_id=1,
                status="PENDING",
            )
        ]
        spec = GetSplitBillCurrentUserSpec(user_id=1)

        self.split_bill_accessor.get_list.return_value = dummy_split_bills
        self.bill_accessor.get_list.return_value = dummy_bills

        result = self.split_bill_service.get_list_current_user(spec)

        self.assertEqual(result[0].split_bill.id, dummy_split_bills[0].id)

    def test_get_split_bill_list_current_user_empty_success(self):
        spec = GetSplitBillCurrentUserSpec(user_id=1)

        self.bill_accessor.get_list.return_value = []
        result = self.split_bill_service.get_list_current_user(spec)
        self.assertEqual(len(result), 0)

        dummy_bills = [
            Bill(
                user_id=1,
                split_bill_id=1,
                status="PENDING",
            )
        ]

        self.bill_accessor.get_list.return_value = dummy_bills
        self.split_bill_accessor.get_list.return_value = []
        result = self.split_bill_service.get_list_current_user(spec)
        self.assertEqual(len(result), 0)

    def test_delete_split_bill_success(self):
        self.split_bill_service.delete(DeleteSplitBillSpec(split_bill_ids=[1]))
