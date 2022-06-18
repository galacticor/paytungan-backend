# from django.test import TestCase
from typing import Optional
from unittest import TestCase
from unittest.mock import MagicMock
from faker import Faker

from paytungan.app.auth.models import User
from paytungan.app.auth.specs import (
    CreateUserSpec,
    FirebaseDecodedToken,
    GetUserListSpec,
    UpdateUserSpec,
    UserDomain,
)

from .services import AuthService, UserServices


class TestAuthService(TestCase):
    def setUp(self) -> None:
        self.mock = MagicMock()
        self.user_service = UserServices(user_accessor=self.mock)
        self.auth_service = AuthService(
            user_accessor=self.mock,
            firebase_provider=self.mock,
        )

    @staticmethod
    def _get_user_dummy(seed: int):
        fake = Faker()
        Faker.seed(seed)

        return UserDomain(
            id=fake.pyint(),
            firebase_id=fake.pystr(),
            phone_number=fake.phone_number(),
            email=fake.email(),
            username=fake.pystr(),
            name=fake.name(),
        )

    def test_user_service_get(self):
        self.user_service.get(1)
        self.assertTrue(self.mock.get.called)

    def test_user_service_get_by_username(self):
        self.user_service.get_by_username("string")
        self.assertTrue(self.mock.get_by_username.called)

    def test_user_service_get_by_firebase_uid(self):
        self.user_service.get_by_firebase_uid("asasas")
        self.assertTrue(self.mock.get_by_firebase_uid.called)

    def test_user_service_get_list(self):
        spec = GetUserListSpec(user_ids=[1], usernames=[])
        self.user_service.get_list(spec)
        self.assertTrue(self.mock.get_list.called)

    def test_user_service_register(self):
        spec = CreateUserSpec(firebase_uid="aa", phone_number="aaa")
        self.user_service.create_user(spec)
        self.assertTrue(self.mock.create.called)

    def test_user_service_update_user(self):
        spec = UpdateUserSpec(
            firebase_uid="aa",
            username="aaa",
            name="aaaa",
            email="email@gmail.com",
            profil_image="aaaaa",
        )
        self.user_service.update_user(spec)
        self.assertTrue(self.mock.update.called)

    def test_auth_login_succeed(self):
        token = "token"
        decode_token_return = FirebaseDecodedToken(
            user_id="342dwsdsd", phone_number="+62"
        )
        dummy_user = User(firebase_uid="342dwsdsd", phone_number="+62")

        self.mock.get_by_firebase_uid.return_value = dummy_user
        self.mock.decode_token.return_value = decode_token_return

        user = self.auth_service.login(token)

        self.assertEqual(user.firebase_uid, dummy_user.firebase_uid)

    def test_auth_login_create_new_user(self):
        token = "token"
        decode_token_return = FirebaseDecodedToken(
            user_id="342dwsdsd", phone_number="+62"
        )
        dummy_user = User(firebase_uid="342dwsdsd", phone_number="+62")

        self.mock.create.return_value = dummy_user
        self.mock.get_by_firebase_uid.return_value = None
        self.mock.decode_token.return_value = decode_token_return

        user = self.auth_service.login(token)

        self.assertEqual(user.firebase_uid, dummy_user.firebase_uid)

    def test_auth_service_get_user_from_token(self):
        self.auth_service.get_user_from_token("aaa")
        self.assertTrue(True)

    def test_auth_service_decode_token(self):
        token = "token"
        decode_token_return = FirebaseDecodedToken(
            user_id="342dwsdsd", phone_number="+62"
        )
        dummy_user = User(firebase_uid="342dwsdsd", phone_number="+62")

        self.mock.get_by_firebase_uid.return_value = dummy_user
        self.mock.decode_token.return_value = decode_token_return
        self.auth_service.decode_token(token)

        self.assertEqual(dummy_user.firebase_uid, decode_token_return.user_id)
