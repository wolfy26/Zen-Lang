def copy_scope(scope):
    new_scope = {i: scope[i].copy() if hasattr(scope[i], 'copy') else scope[i] for i in scope}
    for child in new_scope["scopes"]:
        child = copy_scope(child)
        child["parent"] = new_scope
    return new_scope

def create_scope(parent = None, insert_code = False):
    new_scope = {"code":[], "goto":[], "func":{}, "values":{}, "scopes":[], "parent": parent}
    if insert_code and parent:
        new_scope["code"] = parent["code"]
    return new_scope
