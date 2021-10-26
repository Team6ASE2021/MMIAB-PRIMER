from monolith.classes import read_messages
from .auth import auth
from .home import home
from .users import users
from .filters import filters
from .messages import messages 
from .read_message import read_message

blueprints = [home, auth, users, filters, messages, read_message]

