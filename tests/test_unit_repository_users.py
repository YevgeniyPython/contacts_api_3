import unittest
from unittest.mock import patch, MagicMock
from sqlalchemy.orm import Session
from models import User
from schemas import UserModel
from repository.users import get_user_by_email, create_user, update_token, confirmed_email, update_avatar


class TestUserFunctions(unittest.IsolatedAsyncioTestCase):
    
    def setUp(self):
        # Мокируем сессию базы данных
        self.db = MagicMock(spec=Session)
        # Мокируем пользователя
        self.user = User(id=1, email="test@example.com", refresh_token=None, confirmed=False, avatar=None)

    @patch('repository.users.Gravatar')  # Мокируем Gravatar
    async def test_create_user(self, mock_gravatar):
        # Мокируем поведение Gravatar
        mock_gravatar_instance = mock_gravatar.return_value
        mock_gravatar_instance.get_image.return_value = "http://gravatar.com/avatar"
        
        # Создаем тело для нового пользователя
        body = UserModel(username="testname", email="test@example.com", password="password")
        
        # Тестируем создание пользователя
        result = await create_user(body, self.db)
        
        # Проверяем, что пользователь был добавлен и коммит был вызван
        self.db.add.assert_called_once()
        self.db.commit.assert_called_once()
        
        # Проверяем, что аватар установлен правильно
        self.assertEqual(result.avatar, "http://gravatar.com/avatar")
    
    async def test_get_user_by_email(self):
        # Мокируем поведение запроса к базе данных
        self.db.query().filter().first.return_value = self.user
        
        # Тестируем получение пользователя по email
        result = await get_user_by_email("test@example.com", self.db)
        
        # Проверяем, что пользователь был найден
        self.db.query().filter().first.assert_called_once()
        self.assertEqual(result.email, "test@example.com")
    
    async def test_update_token(self):
        # Обновляем refresh_token пользователя
        await update_token(self.user, "new_token", self.db)
        
        # Проверяем, что токен обновлен
        self.assertEqual(self.user.refresh_token, "new_token")
        self.db.commit.assert_called_once()
    
    async def test_confirmed_email(self):
        # Мокируем поведение get_user_by_email
        self.db.query().filter().first.return_value = self.user
        
        # Тестируем подтверждение email
        await confirmed_email("test@example.com", self.db)
        
        # Проверяем, что флаг confirmed установлен в True
        self.assertTrue(self.user.confirmed)
        self.db.commit.assert_called_once()
    
    async def test_update_avatar(self):
        # Мокируем поведение get_user_by_email
        self.db.query().filter().first.return_value = self.user
        
        # Тестируем обновление аватара
        result = await update_avatar("test@example.com", "http://newavatar.com/avatar", self.db)
        
        # Проверяем, что аватар обновлен
        self.assertEqual(self.user.avatar, "http://newavatar.com/avatar")
        self.db.commit.assert_called_once()


if __name__ == "__main__":
    unittest.main()
