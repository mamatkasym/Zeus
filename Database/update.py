try:
    from Database.db import Account, db, Device
except:
    from .db import Account, db, Device

def update_token(account_id, account_atr_value):
    Account.query.filter_by(id=account_id).update(dict(_csrftoken=account_atr_value))
    db.session.commit()

def update_last_login(account_id, account_atr_value):
    Account.query.filter_by(id=account_id).update(dict(last_login=account_atr_value))
    db.session.commit()

def update_is_logged_in(account_id, account_atr_value):
    Account.query.filter_by(id=account_id).update(dict(is_logged_in=account_atr_value))
    db.session.commit()

def update_x_pigeon(account_username, account_atr_value):
    Device.query.filter_by(account_username=account_username).update(dict(x_pigeon=account_atr_value))
    db.session.commit()

def update_user_id(account_username, account_atr_value):
    Account.query.filter_by(username=account_username).update(dict(user_id=account_atr_value))
    db.session.commit()

def update_cookie(account_username, account_atr_value):
    Account.query.filter_by(username=account_username).update(dict(cookie=account_atr_value))
    db.session.commit()

def update_last_media_id(account_id, account_atr_value):
    Account.query.filter_by(id=account_id).update(dict(last_media_id=account_atr_value))
    db.session.commit()

def update_last_media_owner(account_id, account_atr_value):
    Account.query.filter_by(id=account_id).update(dict(last_media_owner=account_atr_value))
    db.session.commit()
