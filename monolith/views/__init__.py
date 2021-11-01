from .auth import auth
from .filters import filters
from .home import home
from .users import users
from .messages import messages
from .mailbox import mailbox
from .read_message import read_message
from .forward import forward

blueprints = [home, auth, users, filters, messages, read_message, mailbox,forward]
