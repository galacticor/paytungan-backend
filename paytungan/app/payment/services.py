from typing import List, Optional
from injector import inject
from datetime import datetime, timedelta
from django.utils import timezone
import pytz

from paytungan.app.auth.specs import UserDomain
from paytungan.app.base.constants import BillStatus
from paytungan.app.common.exceptions import NotFoundException, ValidationErrorException
from paytungan.app.common.utils import DateUtil, ObjectMapperUtil
from paytungan.app.payment.interfaces import IPaymentAccessor, IXenditProvider
from paytungan.app.payment.models import Payment
from paytungan.app.payment.specs import (
    CreateInvoicePaymentResult,
    CreateInvoicePaymentSpec,
    CreatePaymentSpec,
    CreatePayoutResult,
    CreatePayoutSpec,
    CreateXenditInvoiceSpec,
    CreateXenditPayoutSpec,
    GetPaymentListSpec,
    PaymentDomain,
    PayoutDomain,
    UpdatePaymentSpec,
    UpdateStatusSpec,
    PaymentWithBillDomain,
)
from paytungan.app.split_bill.specs import (
    GetBillListSpec,
    UpdateBillSpec,
    UpdateSplitBillSpec,
)
from paytungan.app.split_bill.interfaces import IBillAccessor, ISplitBillAccessor


class PaymentService:
    @inject
    def __init__(
        self,
        payment_accessor: IPaymentAccessor,
        xendit_provider: IXenditProvider,
        bill_accessor: IBillAccessor,
        split_bill_accessor: ISplitBillAccessor,
    ) -> None:
        self.payment_accessor = payment_accessor
        self.xendit_provider = xendit_provider
        self.bill_accessor = bill_accessor
        self.split_bill_accessor = split_bill_accessor

    def get_payment(self, payment_id: int) -> Optional[PaymentDomain]:
        time_now = timezone.now()
        payment = self.payment_accessor.get(payment_id)

        if not payment:
            return None

        invoice = self.xendit_provider.get_invoice(payment.reference_no)
        if not invoice:
            raise ValidationErrorException(
                f"Payment with id: {payment.id} have no invoice."
            )

        if not payment.expiry_date or payment.expiry_date < time_now:
            result = self.create_invoice_for_payment(
                CreateInvoicePaymentSpec(
                    payment_id=payment.id,
                    payer_email=invoice.payer_email,
                    success_redirect_url=invoice.success_redirect_url,
                    failure_redirect_url=invoice.failure_redirect_url,
                )
            )
            payment = result.payment
            invoice = result.invoice

        payment.invoice = invoice
        payment.payment_url = invoice.invoice_url

        return payment

    def get_payment_by_bill_id(self, payment_bill_id: int) -> List[PaymentDomain]:
        return self.payment_accessor.get_by_bill_id(payment_bill_id)

    def get_payment_list(self, spec: GetPaymentListSpec) -> List[Payment]:
        bills = self.bill_accessor.get_list(
            GetBillListSpec(
                user_ids=[spec.user_id],
            )
        )
        if not bills:
            return []

        bill_ids = [bill.id for bill in bills]
        spec.bill_ids.extend(bill_ids)

        return self.payment_accessor.get_list(spec)

    def create_payment(
        self, spec: CreatePaymentSpec, user: UserDomain
    ) -> PaymentDomain:
        bill = self.bill_accessor.get(spec.bill_id)

        if not bill:
            raise NotFoundException(f"Bill object with id: {spec.bill_id} not found")

        if bill.user_id != user.id:
            raise ValidationErrorException(
                "User of Bill and user from token don't match"
            )

        if bill.status == BillStatus.PAID.value:
            raise ValidationErrorException("Bill already been paid")

        payment = self.payment_accessor.create(
            PaymentDomain(
                bill_id=spec.bill_id,
                **ObjectMapperUtil.default_domain_creation_params(),
            )
        )

        result = self.create_invoice_for_payment(
            CreateInvoicePaymentSpec(
                payment_id=payment.id,
                payer_email=user.email,
                success_redirect_url=spec.success_redirect_url,
                failure_redirect_url=spec.failure_redirect_url,
            )
        )

        return result.payment

    def update_status(self, spec: UpdateStatusSpec) -> Optional[PaymentWithBillDomain]:
        payment_spec = GetPaymentListSpec(
            bill_ids=list([spec.bill_id]),
        )
        payment = self.payment_accessor.get_list(payment_spec)

        obj_payment = payment[0]
        obj_payment.status = "PAID"
        obj_payment.updated_at = datetime.utcnow()

        update_payment_spec = UpdatePaymentSpec(
            obj=obj_payment, updated_fields=["status", "updated_at"]
        )
        payment = self.payment_accessor.update(update_payment_spec)

        obj_bill = obj_payment.bill
        obj_bill.status = "PAID"
        obj_bill.updated_at = datetime.utcnow()

        update_bill_spec = UpdateBillSpec(
            obj=obj_bill, updated_fields=["status", "updated_at"]
        )
        bill = self.bill_accessor.update(update_bill_spec)

        return PaymentWithBillDomain(
            payment=payment,
            bill=bill,
        )

    def create_invoice_for_payment(
        self, spec: CreateInvoicePaymentSpec
    ) -> CreateInvoicePaymentResult:
        payment = self.payment_accessor.get(spec.payment_id)

        if not payment:
            raise ValidationErrorException(
                f"Cant create invoice for payment_id: {spec.payment_id}"
            )

        invoice = self.xendit_provider.create_invoice(
            CreateXenditInvoiceSpec(
                external_id=str(payment.id),
                amount=payment.amount,
                payer_email=spec.payer_email,
                description=payment.number,
                success_redirect_url=spec.success_redirect_url,
                failure_redirect_url=spec.failure_redirect_url,
            )
        )

        payment.reference_no = invoice.id
        payment.expiry_date = invoice.expiry_date
        payment.updated_at = timezone.now()
        payment.invoice = invoice
        payment.payment_url = invoice.invoice_url
        self.payment_accessor.update(
            UpdatePaymentSpec(
                payment, updated_fields=["reference_no", "expiry_date", "updated_at"]
            )
        )

        return CreateInvoicePaymentResult(payment=payment, invoice=invoice)

    def get_or_create_payout(self, spec: CreatePayoutSpec) -> PayoutDomain:
        payout = self.get_payout(spec.split_bill_id)
        if payout:
            return payout

        return self.create_payout(spec)

    def get_payout(self, split_bill_id: int) -> Optional[PayoutDomain]:
        split_bill = self.split_bill_accessor.get(split_bill_id)

        if not split_bill:
            raise ValidationErrorException(
                f"Cant get payout for split_bill: {split_bill_id}"
            )

        if not split_bill.payout_reference_no:
            return None

        return self.xendit_provider.get_payout(split_bill.payout_reference_no)

    def create_payout(self, spec: CreatePayoutSpec) -> PayoutDomain:
        time_now = timezone.now()
        split_bill = self.split_bill_accessor.get(spec.split_bill_id)

        if not split_bill:
            raise ValidationErrorException(
                f"Cant create payout for split_bill: {spec.split_bill_id}"
            )

        payout = self.xendit_provider.get_payout(split_bill.payout_reference_no)
        if payout and DateUtil.transform_str_to_datetime(
            payout.expiration_timestamp
        ) > time_now - timedelta(hours=2):
            raise ValidationErrorException(
                f"Split_bill: {spec.split_bill_id} already have payout"
            )

        bills = self.bill_accessor.get_list(
            GetBillListSpec(split_bill_ids=[split_bill.id])
        )

        bill_user_fund = None
        amount_paid = 0
        for bill in bills:
            if (
                bill.status == BillStatus.PAID.value
                and bill.user_id != split_bill.user_fund_id
            ):
                amount_paid += bill.amount

            if bill.user_id == split_bill.user_fund_id:
                bill_user_fund = bill

        payout = self.xendit_provider.create_payout(
            CreateXenditPayoutSpec(
                external_id=str(split_bill.id),
                amount=amount_paid - bill_user_fund.admin_fee,
                email=split_bill.user_fund_email,
            )
        )

        split_bill.payout_reference_no = payout.id
        split_bill.updated_at = timezone.now()
        self.split_bill_accessor.update(
            UpdateSplitBillSpec(
                obj=split_bill, updated_fields=["payout_reference_no", "updated_at"]
            )
        )

        return payout
