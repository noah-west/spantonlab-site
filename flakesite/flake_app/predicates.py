import rules

@rules.predicate
def is_owner(user, object):
    return object.owner == user