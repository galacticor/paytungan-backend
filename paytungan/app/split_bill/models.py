from django.db import models
from django.db.models import Q

from paytungan.app.auth.models import User
from paytungan.app.base.constants import BillStatus
from paytungan.app.base.models import BaseModel


class SplitBill(BaseModel):
    name = models.CharField(max_length=128)
    user_fund = models.ForeignKey(
        User,
        related_name="hosted_split_bills",
        on_delete=models.PROTECT,
    )
    withdrawal_method = models.CharField(max_length=128)
    withdrawal_number = models.CharField(max_length=128)
    details = models.TextField(null=True, blank=True)

    class Meta:
        db_table = "split_bill"
        indexes = [
            models.Index(
                fields=["name"],
                name="index_split_bill_name",
            ),
        ]

    def __str__(self) -> str:
        return f"{str(self.id)} - {str(self.name)}"


class Bill(BaseModel):
    user = models.ForeignKey(
        User,
        related_name="bills",
        on_delete=models.PROTECT,
    )
    split_bill = models.ForeignKey(
        SplitBill, related_name="bills", on_delete=models.PROTECT
    )
    status = models.CharField(max_length=16, default=BillStatus.PENDING.value)
    details = models.TextField(null=True, blank=True)

    class Meta:
        db_table = "bill"
        constraints = [
            models.UniqueConstraint(
                fields=["user_id", "split_bill_id"],
                condition=Q(deleted__isnull=True),
                name="unique_user_id_and_split_bill_id_if_not_deleted",
            ),
        ]

    def __str__(self) -> str:
        return f"{str(self.id)}"
