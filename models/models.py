from typing import Optional
from pydantic import BaseModel, field_validator
import re


class UserReg(BaseModel):
    """Валидация данных регистрации."""
    email: str
    login: str
    password: str
    password_two: Optional[str] = None

    class Config:
        anystr_strip_whitespace = True

    @field_validator('email')
    def validate_email(cls, value: str):
        if not re.match(r'^[\w\.-]+@[\w\.-]+\.\w+$', value):
            raise ValueError('Неверный формат почты')
        return value

    @field_validator('login')
    def validate_login(cls, value: str):
        if len(value) < 7:
            raise ValueError(
                'Длина логина должна быть не менее 7 символов')
        if not any(char.islower() for char in value):
            raise ValueError(
                'Логин должен содержать хотя бы одну строчную букву')
        if not any(char.isupper() for char in value):
            raise ValueError(
                'Логин должен содержать хотя бы одну заглавную букву')
        if not any(char.isdigit() for char in value):
            raise ValueError('Логин должен содержать хотя бы одну цифру')
        return value

    @field_validator('password')
    def validate_password(cls, value: str):
        if len(value) < 7:
            raise ValueError(
                'Длина пароля должна быть не менее 7 символов')
        if not any(char.islower() for char in value):
            raise ValueError(
                'Пароль должен содержать хотя бы одну строчную букву')
        if not any(char.isupper() for char in value):
            raise ValueError(
                'Пароль должен содержать хотя бы одну заглавную букву')
        if not any(char.isdigit() for char in value):
            raise ValueError('Пароль должен содержать хотя бы одну цифру')
        return value


class CodeConfirm(BaseModel):
    """Валидация кода подтверждения."""
    code: str

    class Config:
        str_strip_whitespace = True


class UserAuth(BaseModel):
    """Валидация данных авторизации."""
    login: str
    password: str
    memorize_user: bool = False

    class Config:
        anystr_strip_whitespace = True


class Recover(BaseModel):
    """Валидация пользователя для смены пароля."""
    user: str

    class Config:
        anystr_strip_whitespace = True


class PasswordChange(BaseModel):
    """Валидация данных для смены пароля."""
    user: str
    password: str
    password_two: str

    class Config:
        anystr_strip_whitespace = True

    @field_validator('password')
    def validate_password(cls, value: str):
        if len(value) < 7:
            raise ValueError(
                'Длина пароля должна быть не менее 7 символов')
        if not any(char.islower() for char in value):
            raise ValueError(
                'Пароль должен содержать хотя бы одну строчную букву')
        if not any(char.isupper() for char in value):
            raise ValueError(
                'Пароль должен содержать хотя бы одну заглавную букву')
        if not any(char.isdigit() for char in value):
            raise ValueError('Пароль должен содержать хотя бы одну цифру')
        if not ('-' in value or '_' in value):
            raise ValueError(
                'Пароль должен содержать один из символов - или _')
        return value


class Token(BaseModel):
    """Валидация токена."""
    token: str
