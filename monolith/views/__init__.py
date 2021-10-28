from .auth import auth
from .home import home
from .users import users
from .filters import filters
from .messages import messages
from .mailbox import mailbox

blueprints = [home, auth, users, filters, messages, mailbox]

