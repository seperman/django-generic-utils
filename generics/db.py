from django.db import transaction

@transaction.commit_manually
def flush_transaction():
    """
    Flush the current transaction so we don't read stale data.
    This is needed for long running processes that data might have changed during the process.
    """
    transaction.commit()

