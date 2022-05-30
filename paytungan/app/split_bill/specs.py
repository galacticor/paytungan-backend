from dataclasses import dataclass, field
from typing import List, Optional
from paytungan.app.base.constants import BillStatus

from paytungan.app.base.specs import BaseDomain
from .models import Bill, SplitBill, User


@dataclass
class GroupSplitBillDomain(BaseDomain):
    name: str
    user_fund_id: int
    user_fund_email: str
    amount: int
    payout_reference_no: Optional[str] = None
    withdrawal_method: Optional[str] = None
    withdrawal_number: Optional[int] = None
    details: Optional[str] = None
    bills: Optional[Bill] = None


@dataclass
class BillDomain(BaseDomain):
    user_id: int
    split_bill_id: int
    amount: int
    admin_fee: int
    status: str = BillStatus.PENDING.value
    user: Optional[User] = None
    details: Optional[str] = None


@dataclass
class SplitBillWithBillDomain:
    split_bill: SplitBill
    bill: Bill


@dataclass
class GetBillListSpec:
    user_ids: Optional[List[int]] = None
    bill_ids: Optional[List[int]] = None
    split_bill_ids: Optional[List[int]] = None


@dataclass
class GetBillListResult:
    bills: List[Bill]


@dataclass
class CreateBillSpec:
    user_id: int
    split_bill_id: int
    amount: int
    admin_fee: int
    details: Optional[str] = None


@dataclass
class GetSplitBillListSpec:
    user_fund_id: Optional[int] = None
    user_id: Optional[int] = None
    name: Optional[str] = None
    bill_ids: Optional[List[int]] = None
    split_bill_ids: List[int] = field(default_factory=list)


@dataclass
class GetSplitBillListResult:
    split_bills: List[SplitBill]


@dataclass
class CreateSplitBillSpec:
    name: str
    user_fund_id: int
    withdrawal_method: str
    withdrawal_number: str
    amount: int
    details: Optional[str] = None


@dataclass
class UserIdWithAmountBillDomain:
    user_id: int
    amount: int
    admin_fee: int
    details: Optional[str] = None


@dataclass
class CreateGroupSplitBillSpec:
    name: str
    user_fund_id: int
    withdrawal_method: str
    withdrawal_number: str
    amount: int
    bills: List[UserIdWithAmountBillDomain]
    details: Optional[str] = None


@dataclass
class DeleteSplitBillSpec:
    user_fund_id: Optional[int] = None
    bill_ids: Optional[List[int]] = None
    split_bill_ids: Optional[List[int]] = None


@dataclass
class GetSplitBillCurrentUserSpec:
    user_id: int
    is_user_fund: Optional[bool] = None


@dataclass
class UpdateBillSpec:
    obj: BillDomain
    updated_fields: Optional[List[str]] = None


@dataclass
class UpdateSplitBillSpec:
    obj: SplitBill
    updated_fields: Optional[List[str]] = None
