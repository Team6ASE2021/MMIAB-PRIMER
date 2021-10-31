from .auth import auth
from .filters import filters
from .home import home
from .messages import messages 
from .users import users

blueprints = [home, auth, users, filters, messages]
