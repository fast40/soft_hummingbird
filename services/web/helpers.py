def url_bool(url_parameter):
    url_parameter = url_parameter.lower()

    if url_parameter in ['true', '1']:
        return True
    elif url_parameter in ['false', '0']:
        return False
    else:
        return None