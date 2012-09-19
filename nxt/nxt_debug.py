import threading
DEBUGLEVEL = 7
print_lock = threading.Lock()

def synchronized(lock):
    '''Synchronization decorator.'''

    def wrap(f):
        def new_function(*args, **kw):
            lock.acquire()
            try:
                return f(*args, **kw)
            finally:
                lock.release()
        return new_function
    return wrap

@synchronized(print_lock)
def dbg_print(element, dbglevel=0, bot=-2):
    if dbglevel == 0:
        print('#'+str(bot+1)+' '+element)
        return
    if dbglevel < DEBUGLEVEL:
        print("DEBUG(%d) #%d-> %s"%(dbglevel, bot+1, element))
