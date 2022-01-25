# tools

def get_ip(request):
    if request.META.get('HTTP_X_FORWARDED_FOR'):
        ip = request.META.get("HTTP_X_FORWARDED_FOR")
    else:
        ip = request.META.get("REMOTE_ADDR")
    
    return ip

def get_ua(request):
    ua = request.META.get('HTTP_USER_AGENT')
    return ua or 0
