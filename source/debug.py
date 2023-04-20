DEBUG = False

def debug(*args, **kwargs):
    if DEBUG:
        print(*args, **kwargs)