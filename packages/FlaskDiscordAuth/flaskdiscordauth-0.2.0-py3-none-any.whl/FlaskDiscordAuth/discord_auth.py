import requests
from flask import redirect, session, url_for, request, current_app
from urllib.parse import urlencode
from functools import wraps

class DiscordAuth:
    def __init__(self, client_id, client_secret, redirect_uri, scope='identify email'):
        """Инициализация с данными Discord приложения."""
        self.client_id = client_id
        self.client_secret = client_secret
        self.redirect_uri = redirect_uri
        self.scope = scope
        self.auth_url = 'https://discord.com/api/oauth2/authorize'
        self.token_url = 'https://discord.com/api/oauth2/token'
        self.user_url = 'https://discord.com/api/users/@me'
        self.guilds_url = 'https://discord.com/api/users/@me/guilds'
        self.revoke_url = 'https://discord.com/api/oauth2/token/revoke'

    def get_login_url(self, state=None, scope=None):
        """Генерирует URL для авторизации через Discord."""
        params = {
            'client_id': self.client_id,
            'redirect_uri': self.redirect_uri,
            'response_type': 'code',
            'scope': scope or self.scope
        }
        if state:
            params['state'] = state
        return f"{self.auth_url}?{urlencode(params)}"

    def get_token(self, code):
        """Обменивает код авторизации на access token."""
        data = {
            'client_id': self.client_id,
            'client_secret': self.client_secret,
            'grant_type': 'authorization_code',
            'code': code,
            'redirect_uri': self.redirect_uri
        }
        headers = {'Content-Type': 'application/x-www-form-urlencoded'}
        response = requests.post(self.token_url, data=data, headers=headers)
        response.raise_for_status()
        return response.json()

    def refresh_token(self, refresh_token):
        """Обновляет access token с помощью refresh token."""
        data = {
            'client_id': self.client_id,
            'client_secret': self.client_secret,
            'grant_type': 'refresh_token',
            'refresh_token': refresh_token
        }
        headers = {'Content-Type': 'application/x-www-form-urlencoded'}
        response = requests.post(self.token_url, data=data, headers=headers)
        response.raise_for_status()
        return response.json()

    def revoke_token(self, token):
        """Отзывает access token."""
        data = {
            'client_id': self.client_id,
            'client_secret': self.client_secret,
            'token': token,
            'token_type_hint': 'access_token'
        }
        headers = {'Content-Type': 'application/x-www-form-urlencoded'}
        response = requests.post(self.revoke_url, data=data, headers=headers)
        
        if response.status_code != 200:
            current_app.logger.warning(f"Token revocation failed: {response.status_code} - {response.text}")
            return False
        return True

    def get_user_info(self, access_token):
        """Получает информацию о пользователе по access token."""
        headers = {'Authorization': f'Bearer {access_token}'}
        response = requests.get(self.user_url, headers=headers)
        response.raise_for_status()
        return response.json()

    def get_user_guilds(self, access_token):
        """Получает список серверов пользователя по access token."""
        headers = {'Authorization': f'Bearer {access_token}'}
        response = requests.get(self.guilds_url, headers=headers)
        response.raise_for_status()
        return response.json()

    def login_required(self, func):
        """Декоратор для защиты маршрутов, требующих авторизации."""
        @wraps(func)
        def wrapper(*args, **kwargs):
            if 'user' not in session:
                return redirect(url_for('login'))
            return func(*args, **kwargs)
        return wrapper

    def guilds_required(self, *guild_ids):
        """Декоратор для проверки серверов пользователя."""
        def decorator(func):
            @wraps(func)
            def wrapper(*args, **kwargs):
                if 'user' not in session:
                    return redirect(url_for('login'))

                guilds = session.get('guilds', [])
                if not guilds:
                    access_token = session.get('access_token')
                    if access_token:
                        guilds = self.get_user_guilds(access_token)
                        session['guilds'] = guilds
                
                user_guild_ids = [g['id'] for g in guilds]
                if not any(gid in user_guild_ids for gid in guild_ids):
                    return "Доступ запрещен: вы не состоите в требуемом сервере", 403
                    
                return func(*args, **kwargs)
            return wrapper
        return decorator