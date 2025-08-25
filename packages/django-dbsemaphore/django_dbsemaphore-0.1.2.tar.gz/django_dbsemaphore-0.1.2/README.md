# Django-DBSemaphore

This gives you multi-ticket DB-defined semaphores implemented on top of DB row locks.

# Alternatives

The orthodox alternatives are:
- Posix semaphores (eg using [posix_ipc](https://pypi.org/project/posix-ipc/))
- SysV semaphores (eg using [sysv-ipc](https://pypi.org/project/sysv-ipc/))

## Why not use those then?
If a process which holds a Posix or SysV mutex ticket crashes while holding the ticket, it can't return it to the semaphore.
Thus, you can leak tickets.
But if a process which holds a ticket from Django-DBSemaphore crashes, its database connection goes with it, which terminates the DB transaction and frees the ticket. Crashing processes don't leak tickets.

## And why not a lockfile?
Locked files (or locked byte ranges) disappear when a process crashes; its file descriptors are gone thus so are its locks.
That's a great property. However, file locks are not multi-ticket. The file (or byterange therein) is either locked or not.
The OS file locking APIs are good to implement *mutexes* with, but not *semaphores* — except, trivially, a 1-ticket semaphore — which is a mutex ;-).

# Quirks
- In contrast to Posix/SysV semaphores and `lockf`-based approaches, with django-dbsemaphore you can't block until a ticket becomes available.
- From within the same transaction you can acquire tickets you already have over and over. In fact, it's currently impossible to get new tickets of a semaphore on a transaction that already has a ticket of that same semaphore. Typically, you won't need multiple tickets of the same semaphore in the same transaction, but a future version of this software might make it possible. In the meantime, consider using multiple semaphores for your multistage semaphore needs.
- At the base level, they work within transactions. If you want to use `dbsemaphore.semaphore.acquire()`, you'll need to structure your ticket acquisitions around DB transactions, and close those transactions (rollback or commit) to return the tickets. However, there is a context manager (`dbsemaphore.contextmanager.semaphore_ticket()`) that abstracts all of that away for you and makes it easy to use a ticket from anywhere in your code. See below.

# Compatibility
Currently this is tested on PostgreSQL 14 and Django 3.2.
- It currently doesn't work on SQLite due to the way in which tables are locked in `semaphore.make()`
- MySQL, Oracle: Untested.
- (neat) Patches welcome!

# Installing
1. `pip install django-dbsemaphore`
2. add 'dbsemaphore' to your Django's `settings.INSTALLED_APPS`.
3. run `./manage.py migrate dbsemaphore` or some variation of such

# How to use it

Have a look at the below examples, run the Django test, or read `test.py`.


## Semaphore management

```python
from dbsemaphore import semaphore as sem

# Creates a semaphore called 'test' with 3 tickets
>>> sem.make('test', 3)

# Increases the number of tickets of semaphore 'test' to 4.
# Blocks on concurrent calls of `make`.
# If 'test' doesn't exist, it will be created (with 4 tickets).
>>> sem.make('test', 4)

# Decreases the number of tickets of semaphore 'test' to 2.
# This can block, in the worst case until all tickets have been returned.
# As `make` calls block on eachother, this thus also blocks any *increase* of tickets until this decrease has succeeded.
>>> sem.make('test', 2)

# Returns a dictionary of available semaphores, with their ticket counts.
>>> sem.list()
{'test', 2}

# Destroys the semaphore. Blocks until all its tickets have been returned.
>>> sem.destroy('test')
```

## Acquiring tickets; what we're here for!

### With the contextmanager

```python
from dbsemaphore.contextmanager import semaphore_ticket

# We use the semaphore named 'test' that we have created above.
with semaphore_ticket('test') as theticket:
    if theticket is None:
        print("Boo! No ticket was available!")
    else:
        do_the_ticketed_thing()
```

### Using the lower-level API

```python
from django.db import transaction
from dbsemaphore import semaphore as sem

@transaction.atomic
def do_something_potentially_from_many_processes_or_threads_but_not_too_many_at_the_same_time():
    # We use the semaphore named 'test' that we have created above.
    if ticket := sem.acquire('test'):
        do_that_something()

# When the transaction terminates, the ticket is returned to the semaphore.
# In fact, there isn't any API function to explicitly return a ticket...
```