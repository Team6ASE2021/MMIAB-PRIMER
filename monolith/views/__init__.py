from .auth import auth
from .filters import filters
from .forward import forward
from .home import home
from .lottery import lottery
from .mailbox import mailbox
from .messages import messages
from .read_message import read_message
from .users import users

blueprints = [
    home,
    auth,
    users,
    filters,
    messages,
    read_message,
    mailbox,
    forward,
    lottery,
]
