def copy_scope(scope):
    new_scope = scope
    new_scope["values"] = scope["values"].copy()
    return new_scope

def create_scope(parent = None, insert_code = False):
    new_scope = {"code":[], "goto":[], "func":{}, "values":{}, "scopes":[], "parent": parent}
    if insert_code and parent:
        new_scope["code"] = parent["code"]
    return new_scope
