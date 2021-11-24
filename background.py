from mib import create_app, create_celery

flask_app = create_app()
app = create_celery(flask_app)

try:
    import mib.tasks
except ImportError:
    raise RuntimeError('Cannot import celery tasks')
