

from app.core.redis import redis_client



def set_account_count(db):
    from app.accounts.crud import get_all_account_count
    account_count = get_all_account_count(db)
    redis_client.set('account_count',account_count)

def get_account_count():
    return redis_client.get('account_count')