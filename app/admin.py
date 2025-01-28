from flask_admin import Admin, AdminIndexView, expose
from flask_admin.contrib.sqla import ModelView
from flask_login import current_user
from flask import redirect, url_for
from app.models import User, TelegramBot
from app import db

class SecureModelView(ModelView):
    def is_accessible(self):
        return current_user.is_authenticated and current_user.is_admin
    
    def inaccessible_callback(self, name, **kwargs):
        return redirect(url_for('auth.login'))

class UserModelView(SecureModelView):
    column_exclude_list = ['password_hash']
    column_searchable_list = ['username']
    column_filters = ['is_admin']
    form_excluded_columns = ['password_hash', 'bots']
    
    def on_model_change(self, form, model, is_created):
        if form.password.data:
            model.set_password(form.password.data)

class BotModelView(SecureModelView):
    column_list = ['bot_username', 'owner', 'status', 'bot_type', 'last_activity']
    column_searchable_list = ['bot_username', 'bot_type']
    column_filters = ['status', 'bot_type']
    form_excluded_columns = ['last_activity', 'created_at', 'updated_at', 'webhook_url', 'error_message']
    
    def on_model_change(self, form, model, is_created):
        if is_created and model.bot_token:
            from app.tasks import update_bot_status
            update_bot_status.delay(model.id)

class CustomAdminIndexView(AdminIndexView):
    @expose('/')
    def index(self):
        if not current_user.is_authenticated or not current_user.is_admin:
            return redirect(url_for('auth.login'))
        return self.render('admin/index.html')

def init_admin(app):
    admin = Admin(
        app,
        name='Bot Manager Admin',
        template_mode='bootstrap4',
        index_view=CustomAdminIndexView(),
        base_template='base.html'
    )
    
    admin.add_view(UserModelView(User, db.session, name='Users'))
    admin.add_view(BotModelView(TelegramBot, db.session, name='Bots'))