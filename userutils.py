import queries
import datetime
import logging

logger = logging.getLogger(__name__)

def active_users(executor):
    return queries.all_active_nicks(executor)


def is_user_a_bot(nick):
    return nick[-1] == '^'
