from flask import Flask, session, redirect, url_for, request
from src.FlaskDiscordAuth.discord_auth import DiscordAuth

app = Flask(__name__)
app.secret_key = 'your_secret_key_here'

# Discord configuration
CLIENT_ID = '1271127749515546656'
CLIENT_SECRET = 'R5Zm9PRfiHvksefwMtghScOFOtLxbccU'
REDIRECT_URI = 'http://127.0.0.1:5000/callback'

discord_auth = DiscordAuth(CLIENT_ID, CLIENT_SECRET, REDIRECT_URI)

def html_wrap(content, banner_url=None):
    banner_style = ""
    if banner_url:
        banner_style = f"""
            background-image: url('{banner_url}');
            background-size: cover;
            background-position: center;
            background-attachment: fixed;
            background-blend-mode: overlay;
            background-color: rgba(0, 0, 0, 0.25);
        """
    
    return f"""
    <!DOCTYPE html>
    <html>
    <head>
        <title>FlaskDiscordAuth Example</title>
        <style>
            body {{ 
                font-family: Arial, sans-serif; 
                max-width: 800px; 
                margin: 0 auto; 
                padding: 20px;
                {banner_style}
            }}
            .container {{ 
                background: rgba(240, 240, 240, 0.95); 
                padding: 20px; 
                border-radius: 8px; 
                box-shadow: 0 0 10px rgba(0,0,0,0.1);
            }}
            .btn {{ 
                background: #5865F2; 
                color: white; 
                padding: 10px 15px; 
                text-decoration: none; 
                border-radius: 4px; 
                display: inline-block; 
                margin: 5px; 
                transition: all 0.3s;
            }}
            .btn:hover {{
                background: #4752c4;
                transform: translateY(-2px);
                box-shadow: 0 2px 5px rgba(0,0,0,0.2);
            }}
            .info {{ margin: 10px 0; }}
            .user-table {{ 
                width: 100%; 
                border-collapse: collapse; 
                margin: 20px 0; 
                background: white;
            }}
            .user-table th, .user-table td {{ 
                border: 1px solid #ddd; 
                padding: 8px; 
                text-align: left; 
            }}
            .user-table tr:nth-child(even) {{ 
                background-color: #f9f9f9; 
            }}
            .avatar-container {{ 
                text-align: center; 
                margin-bottom: 20px; 
            }}
            .avatar {{ 
                border-radius: 50%; 
                width: 150px; 
                height: 150px; 
                border: 3px solid white;
                box-shadow: 0 0 10px rgba(0,0,0,0.2);
            }}
        </style>
    </head>
    <body>
        <div class="container">
            {content}
        </div>
    </body>
    </html>
    """

@app.route('/')
def home():
    if 'user' in session:
        user = session['user']
        has_guilds_scope = 'guilds' in session.get('scope', '')
        
        # Ссылка на серверы только при наличии scope
        guilds_link = ""
        if has_guilds_scope:
            guilds_link = """
            <a href=\"/guilds\" class=\"btn\">Мои серверы</a>
            <a href="/moderator" class="btn">Панель модератора</a>
            <a href="/admin" class="btn">Панель администратора</a>"""
        
        # Аватар и баннер пользователя
        avatar_html = ""
        banner_url = None
        if user.get('avatar'):
            avatar_url = f"https://cdn.discordapp.com/avatars/{user['id']}/{user['avatar']}.png?size=256"
            avatar_html = f"<div class='avatar-container'><img src='{avatar_url}' class='avatar' alt='Аватар'></div>"
        if user.get('banner'):
            banner_url = f"https://cdn.discordapp.com/banners/{user['id']}/{user['banner']}.png?size=1024"
        
        # Таблица с информацией о пользователе
        user_info = "<table class='user-table'>"
        for key, value in user.items():
            if isinstance(value, bool):
                value = 'Да (True)' if value else 'Нет (False)'
            elif value is None:
                value = 'Не указано (None)'
            user_info += f"<tr><td><b>{key}</b></td><td>{value}</td></tr>"
        user_info += "</table>"
        
        content = f"""
            {avatar_html}
            <h1>Привет, {user.get('username', 'Пользователь')}!</h1>
            {user_info}
            {guilds_link}
            <a href="/logout" class="btn">Выйти</a>
        """
    else:
        content = """
            <h1>Добро пожаловать!</h1>
            <a href="/login" class="btn">Войти через Discord</a>
            <br><br>
            <a href="/login_with_guilds" class="btn">Войти с доступом к серверам</a>
        """
        banner_url = None
    
    return html_wrap(content, banner_url)

@app.route('/login')
def login():
    return redirect(discord_auth.get_login_url())

@app.route('/login_with_guilds')
def login_with_guilds():
    return redirect(discord_auth.get_login_url(scope='identify email guilds'))

@app.route('/callback')
def callback():
    code = request.args.get('code')
    token_data = discord_auth.get_token(code)
    session['access_token'] = token_data['access_token']
    session['refresh_token'] = token_data.get('refresh_token')
    session['scope'] = token_data.get('scope', '')  # Сохраняем scope
    session['user'] = discord_auth.get_user_info(session['access_token'])
    return redirect(url_for('home'))

@app.route('/guilds')
@discord_auth.login_required
def user_guilds():
    try:
        guilds = discord_auth.get_user_guilds(session['access_token'])
        guild_list = "<ul>"
        for guild in guilds:
            guild_list += f"<li>{guild['name']} (ID: {guild['id']})</li>"
        guild_list += "</ul>"
        
        content = f"""
            <h1>Ваши серверы</h1>
            <div>Всего серверов: {len(guilds)}</div>
            {guild_list}
            <a href="/" class="btn">На главную</a>
        """
        banner_url = session.get('user', {}).get('banner') and f"https://cdn.discordapp.com/banners/{session['user']['id']}/{session['user']['banner']}.png?size=1024"
        return html_wrap(content, banner_url)
    except Exception as e:
        content = f"""
            <h1>Ошибка</h1>
            <p>Не удалось получить список серверов: {str(e)}</p>
            <p>Возможно, вы не предоставили доступ к серверам при авторизации.</p>
            <a href="/login_with_guilds" class="btn">Войти с доступом к серверам</a>
            <a href="/" class="btn">На главную</a>
        """
        banner_url = session.get('user', {}).get('banner') and f"https://cdn.discordapp.com/banners/{session['user']['id']}/{session['user']['banner']}.png?size=1024"
        return html_wrap(content, banner_url), 403

@app.route('/moderator')
@discord_auth.guilds_required('1234567890')  # Замените на реальный ID сервера
def moderator_panel():
    content = """
        <h1>Панель модератора</h1>
        <p>Вы имеете доступ к этому разделу, так как состоите в сервере модераторов.</p>
        <a href="/" class="btn">На главную</a>
    """
    banner_url = session.get('user', {}).get('banner') and f"https://cdn.discordapp.com/banners/{session['user']['id']}/{session['user']['banner']}.png?size=1024"
    return html_wrap(content, banner_url)

@app.route('/admin')
@discord_auth.guilds_required('0987654321')  # Замените на реальный ID сервера
def admin_panel():
    content = """
        <h1>Панель администратора</h1>
        <p>Вы имеете доступ к этому разделу, так как состоите в сервере администраторов.</p>
        <a href="/" class="btn">На главную</a>
    """
    banner_url = session.get('user', {}).get('banner') and f"https://cdn.discordapp.com/banners/{session['user']['id']}/{session['user']['banner']}.png?size=1024"
    return html_wrap(content, banner_url)

@app.route('/logout')
def logout():
    access_token = session.get('access_token')
    if access_token:
        discord_auth.revoke_token(access_token)
    session.clear()
    return redirect(url_for('home'))

if __name__ == '__main__':
    app.run(debug=True)