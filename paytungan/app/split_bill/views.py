from drf_yasg.utils import swagger_auto_schema
from rest_framework import viewsets
from rest_framework.decorators import action
from rest_framework.request import Request
from rest_framework.response import Response
from django.db import transaction

from paytungan.app.common.decorators import api_exception
from paytungan.app.base.headers import AUTH_HEADERS
from paytungan.app.auth.utils import firebase_auth, user_auth
from paytungan.app.auth.specs import FirebaseDecodedToken, UserDecoded
from paytungan.app.common.utils import ObjectMapperUtil
from .specs import (
    CreateBillSpec,
    CreateGroupSplitBillSpec,
    DeleteSplitBillSpec,
    GetSplitBillListSpec,
)
from .serializers import (
    CreateBillRequest,
    CreateBillResponse,
    CreateSplitBillRequest,
    CreateSplitBillResponse,
    DeleteSplitBillRequest,
    GetBillResponse,
    GetBillRequest,
    GetSplitBillListCurrentUserResponse,
    GetSplitBillResponse,
    GetSplitBillRequest,
    GetSplitBillListRequest,
    GetSplitBillListResponse,
)
from .services import (
    BillService,
    SplitBillService,
)
from paytungan.app.di import injector

bill_service = injector.get(BillService)
split_bill_service = injector.get(SplitBillService)


class BillViewSet(viewsets.ViewSet):
    @action(
        detail=False,
        url_path="get",
        methods=["get"],
    )
    @swagger_auto_schema(
        query_serializer=GetBillRequest(),
        responses={200: GetBillResponse()},
    )
    @api_exception
    def get_bill(self, request: Request) -> Response:
        """
        Get single bill object by id
        """
        serializer = GetBillRequest(data=request.query_params)
        serializer.is_valid(raise_exception=True)
        data = serializer.data
        bill = bill_service.get_bill(data["id"])
        return Response(GetBillResponse({"data": bill}).data)

    @action(
        detail=False,
        url_path="create",
        methods=["post"],
    )
    @swagger_auto_schema(
        manual_parameters=AUTH_HEADERS,
        request_body=CreateBillRequest(),
        responses={200: CreateBillResponse()},
    )
    @transaction.atomic
    @api_exception
    @user_auth
    def create_bill(self, request: Request, user: UserDecoded) -> Response:
        serializer = CreateBillRequest(data=request.data)
        serializer.is_valid(raise_exception=True)
        data = serializer.data
        spec = CreateBillSpec(
            user_id=user.id,
            split_bill_id=data["split_bill_id"],
            details=data["details"],
        )
        user = bill_service.create_bill(spec)
        return Response(CreateBillResponse({"data": user}).data)


class SplitBillViewSet(viewsets.ViewSet):
    @action(
        detail=False,
        url_path="get",
        methods=["get"],
    )
    @swagger_auto_schema(
        query_serializer=GetSplitBillRequest(),
        responses={200: GetSplitBillResponse()},
    )
    @api_exception
    def get_split_bill(self, request: Request) -> Response:
        """
        Get single split_bill object by id
        """
        serializer = GetSplitBillRequest(data=request.query_params)
        serializer.is_valid(raise_exception=True)
        data = serializer.data
        split_bill = split_bill_service.get_split_bill(data["id"])
        return Response(GetSplitBillResponse({"data": split_bill}).data)

    @action(
        detail=False,
        url_path="create",
        methods=["post"],
    )
    @swagger_auto_schema(
        manual_parameters=AUTH_HEADERS,
        request_body=CreateSplitBillRequest(),
        responses={200: CreateSplitBillResponse()},
    )
    @transaction.atomic
    @api_exception
    @user_auth
    def create_split_bill(self, request: Request, user: UserDecoded) -> Response:
        serializer = CreateSplitBillRequest(data=request.data)
        serializer.is_valid(raise_exception=True)
        data = serializer.data
        spec = CreateGroupSplitBillSpec(
            name=data["name"],
            user_fund_id=data["user_fund_id"],
            withdrawal_method=data["withdrawal_method"],
            withdrawal_number=data["withdrawal_number"],
            details=data["details"],
            user_ids=data["user_ids"],
        )
        split_bill = split_bill_service.create_group_split_bill(spec)
        return Response(CreateSplitBillResponse({"data": split_bill}).data)

    @action(
        detail=False,
        url_path="list/get",
        methods=["get"],
    )
    @swagger_auto_schema(
        manual_parameters=AUTH_HEADERS,
        query_serializer=GetSplitBillListRequest(),
        responses={200: GetSplitBillListResponse()},
    )
    @api_exception
    @firebase_auth
    def get_split_bill_list(
        self, request: Request, cred: FirebaseDecodedToken
    ) -> Response:
        """
        Get list split_bill object
        """
        serializer = GetSplitBillListRequest(data=request.data)
        serializer.is_valid(raise_exception=True)
        spec = ObjectMapperUtil.map(serializer.data, GetSplitBillListSpec)
        split_bills = split_bill_service.get_split_bill_list(spec)
        return Response(GetSplitBillListResponse({"data": split_bills}).data)

    @action(
        detail=False,
        url_path="list/get-current-user",
        methods=["get"],
    )
    @swagger_auto_schema(
        manual_parameters=AUTH_HEADERS,
        responses={200: GetSplitBillListCurrentUserResponse()},
    )
    @api_exception
    @user_auth
    def get_list_current_user(self, request: Request, user: UserDecoded) -> Response:
        """
        Get list split_bill object of current user
        """
        split_bills = split_bill_service.get_list_current_user(user.id)
        return Response(GetSplitBillListCurrentUserResponse({"data": split_bills}).data)

    @action(
        detail=False,
        url_path="delete",
        methods=["delete"],
    )
    @swagger_auto_schema(
        manual_parameters=AUTH_HEADERS,
        request_body=DeleteSplitBillRequest(),
        responses={200: ""},
    )
    @transaction.atomic
    @api_exception
    @user_auth
    def delete_split_bill(self, request: Request, user: UserDecoded) -> Response:
        serializer = CreateSplitBillRequest(data=request.data)
        serializer.is_valid(raise_exception=True)
        data = serializer.data
        spec = DeleteSplitBillSpec(split_bill_ids=[data["split_bill_id"]])
        split_bill = split_bill_service.delete(spec)
        return Response(CreateSplitBillResponse({"data": split_bill}).data)
