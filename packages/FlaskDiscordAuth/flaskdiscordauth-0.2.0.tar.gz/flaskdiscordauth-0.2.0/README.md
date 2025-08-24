# FlaskDiscordAuth

### Обзор

FlaskDiscordAuth - это Python-библиотека, разработанная для упрощения интеграции аутентификации Discord OAuth2 с приложениями Flask. Она предоставляет простой способ аутентификации пользователей через Discord, получения их основной информации, управления серверами и защиты маршрутов, требующих аутентификации.

### Установка

```bash
pip install FlaskDiscordAuth
```

### Требования

- Flask
- requests

### Базовое использование

Вот простой пример использования FlaskDiscordAuth:

```python
from flask import Flask, redirect, url_for, session, request
from FlaskDiscordAuth.discord_auth import DiscordAuth

app = Flask(__name__)
app.secret_key = 'your_secret_key'

# Настройки Discord
CLIENT_ID = 'your_client_id'
CLIENT_SECRET = 'your_client_secret'
REDIRECT_URI = 'http://127.0.0.1:5000/callback'

# Инициализируем объект аутентификации Discord
discord_auth = DiscordAuth(CLIENT_ID, CLIENT_SECRET, REDIRECT_URI)

@app.route('/')
def home():
    if 'user' in session:
        user = session['user']
        return f"Привет, {user['username']}!"
    return 'Добро пожаловать! <a href="/login">Войти через Discord</a>'

@app.route('/login')
def login():
    return redirect(discord_auth.get_login_url())

@app.route('/callback')
def callback():
    code = request.args.get('code')
    token_data = discord_auth.get_token(code)
    session['access_token'] = token_data['access_token']
    session['refresh_token'] = token_data.get('refresh_token')
    session['scope'] = token_data.get('scope', '')
    user_info = discord_auth.get_user_info(session['access_token'])
    session['user'] = user_info
    return redirect(url_for('home'))

@app.route('/logout')
def logout():
    access_token = session.get('access_token')
    if access_token:
        discord_auth.revoke_token(access_token)
    session.clear()
    return redirect(url_for('home'))

if __name__ == '__main__':
    app.run(debug=True)
```

### Защита маршрутов

Вы можете использовать предоставленные декораторы для защиты маршрутов:

```python
@app.route('/profile')
@discord_auth.login_required
def profile():
    user = session['user']
    return f"Профиль пользователя {user['username']}"

@app.route('/moderator')
@discord_auth.guilds_required('1234567890', '0987654321')
def moderator_panel():
    return "Панель модератора"
```

### Расширенные возможности

#### Получение серверов пользователя

```python
@app.route('/guilds')
@discord_auth.login_required
def user_guilds():
    access_token = session.get('access_token')
    guilds = discord_auth.get_user_guilds(access_token)
    return f"Вы состоите в {len(guilds)} серверах"
```

#### Динамические scopes

```python
@app.route('/login_with_guilds')
def login_with_guilds():
    return redirect(discord_auth.get_login_url(scope='identify email guilds'))
```

#### Обновление токена

```python
refresh_token = session.get('refresh_token')
if refresh_token:
    new_tokens = discord_auth.refresh_token(refresh_token)
    session['access_token'] = new_tokens['access_token']
    session['refresh_token'] = new_tokens['refresh_token']
```

#### Получение баннера и аватара пользователя

Библиотека теперь поддерживает получение дополнительной информации о пользователе, включая баннер:

```python
user_info = discord_auth.get_user_info(access_token)
banner_url = f"https://cdn.discordapp.com/banners/{user_info['id']}/{user_info['banner']}.png" if user_info.get('banner') else None
avatar_url = f"https://cdn.discordapp.com/avatars/{user_info['id']}/{user_info['avatar']}.png" if user_info.get('avatar') else None
```

#### Сохранение scope

Библиотека автоматически сохраняет scope в сессии, что позволяет проверять доступные разрешения:

```python
# Проверка наличия scope guilds
has_guilds_scope = 'guilds' in session.get('scope', '')
```

#### Улучшенная обработка ошибок

Декоратор `guilds_required` автоматически загружает информацию о серверах пользователя, если она отсутствует в сессии.