import os

g_log = None

def init(f_path = str):
    if (not os.path.isfile(f_path)):
        return False
    
    global g_log
    g_log = open(f_path, 'a')

    return True

def print(_str = str):
    global g_log
    if (g_log) :
        g_log.write(_str + "\n")

def flush():
    global g_log
    if (g_log) :
        g_log.flush()

def close():
    global g_log
    if (g_log) :
        g_log.close()

def end():
    flush()
    close()