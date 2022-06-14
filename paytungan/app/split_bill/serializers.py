from rest_framework import serializers
from paytungan.app.base.constants import BillStatus, WithdrawalMethod

from paytungan.app.common.utils import EnumUtil


class GetBillRequest(serializers.Serializer):
    id = serializers.IntegerField(min_value=1)


class UserProfileSerializer(serializers.Serializer):
    phone_number = serializers.CharField()
    username = serializers.CharField(
        required=False, default=None, allow_null=True, allow_blank=True
    )
    email = serializers.CharField(
        required=False, default=None, allow_null=True, allow_blank=True
    )
    name = serializers.CharField(
        required=False, default=None, allow_null=True, allow_blank=True
    )
    profil_image = serializers.CharField(
        required=False, default=None, allow_null=True, allow_blank=True
    )


class BillSerializer(serializers.Serializer):
    id = serializers.IntegerField(min_value=1)
    user_id = serializers.IntegerField(min_value=1)
    split_bill_id = serializers.IntegerField(min_value=1)
    status = serializers.ChoiceField(choices=EnumUtil.extract_enum_values(BillStatus))
    amount = serializers.IntegerField(min_value=10000)
    admin_fee = serializers.IntegerField(min_value=0, required=False, default=0)
    created_at = serializers.DateTimeField()
    updated_at = serializers.DateTimeField()
    user = UserProfileSerializer(required=False, allow_null=True)
    details = serializers.CharField(required=False, allow_null=True)


class GetBillResponse(serializers.Serializer):
    data = BillSerializer()


class CreateBillRequest(serializers.Serializer):
    split_bill_id = serializers.IntegerField(min_value=1)
    amount = serializers.IntegerField(min_value=10000)
    admin_fee = serializers.IntegerField(min_value=1, required=False, default=0)
    details = serializers.CharField(required=False, allow_null=True, allow_blank=True)


class CreateBillResponse(serializers.Serializer):
    data = BillSerializer()


class GetSplitBillRequest(serializers.Serializer):
    id = serializers.IntegerField(min_value=1)


class SplitBillSerializer(serializers.Serializer):
    id = serializers.IntegerField(min_value=1)
    name = serializers.CharField()
    user_fund_id = serializers.IntegerField(min_value=1)
    user_fund_email = serializers.CharField()
    payout_reference_no = serializers.CharField(required=False)
    withdrawal_method = serializers.CharField(required=False)
    withdrawal_number = serializers.CharField(required=False)
    amount = serializers.IntegerField(min_value=0)
    details = serializers.CharField(required=False, allow_null=True)


class GroupSplitBillSerializer(SplitBillSerializer):
    bills = BillSerializer(many=True, required=False)


class GetSplitBillResponse(serializers.Serializer):
    data = SplitBillSerializer()


class UserIdWithAmountBillSerializer(serializers.Serializer):
    user_id = serializers.IntegerField(min_value=1)
    amount = serializers.IntegerField(min_value=10000)
    admin_fee = serializers.IntegerField(min_value=1, required=False, default=0)
    details = serializers.CharField(required=False, allow_null=True, default=None)


class CreateSplitBillRequest(serializers.Serializer):
    name = serializers.CharField()
    user_fund_id = serializers.IntegerField(min_value=1)
    withdrawal_method = serializers.ChoiceField(
        choices=EnumUtil.extract_enum_values(WithdrawalMethod),
        required=False,
        allow_null=True,
        allow_blank=True,
    )
    withdrawal_number = serializers.CharField(
        required=False,
        allow_null=True,
        allow_blank=True,
    )
    amount = serializers.IntegerField(min_value=10000)
    details = serializers.CharField(required=False, allow_null=True)
    bills = UserIdWithAmountBillSerializer(many=True)


class CreateSplitBillResponse(serializers.Serializer):
    data = GroupSplitBillSerializer()


class SplitBillWithBillCurrentUserSerializer(serializers.Serializer):
    split_bill = SplitBillSerializer()
    bill = BillSerializer()


class GetSplitBillListRequest(serializers.Serializer):
    user_id = serializers.IntegerField(min_value=1, required=False)
    user_fund_id = serializers.IntegerField(min_value=1, required=False)
    name = serializers.CharField(required=False)
    bill_ids = serializers.ListField(
        child=serializers.IntegerField(min_value=1), required=False
    )
    split_bill_ids = serializers.ListField(
        child=serializers.IntegerField(min_value=1), required=False
    )


class GetSplitBillListResponse(serializers.Serializer):
    data = GroupSplitBillSerializer(many=True)


class GetSplitBillListCurrentUserRequest(serializers.Serializer):
    is_user_fund = serializers.BooleanField(default=False)


class GetSplitBillListCurrentUserResponse(serializers.Serializer):
    data = SplitBillWithBillCurrentUserSerializer(many=True)


class DeleteSplitBillRequest(serializers.Serializer):
    split_bill_id = serializers.IntegerField(min_value=1)


class GetBillListRequest(serializers.Serializer):
    user_ids = serializers.ListField(
        child=serializers.IntegerField(min_value=1), required=False
    )
    bill_ids = serializers.ListField(
        child=serializers.IntegerField(min_value=1), required=False
    )
    split_bill_ids = serializers.ListField(
        child=serializers.IntegerField(min_value=1), required=False
    )


class GetBillListResponse(serializers.Serializer):
    data = BillSerializer(many=True)
