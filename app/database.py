from pathlib import Path

from flask import _app_ctx_stack, current_app, has_app_context
from sqlalchemy import create_engine
from sqlalchemy.engine.url import URL
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import scoped_session, sessionmaker
from werkzeug.local import LocalProxy

# Constants
DB_EXTENSION_KEY = "sa_session"
SQLALCHEMY_DATABASE_URL = URL("sqlite", database=str(Path.cwd().joinpath("test.db")))
# SQLALCHEMY_DATABASE_URL = URL(
#     "postgresql",
#     username="user",
#     password="password",
#     host="postgresd",
#     database="db",
# )


# I see people adding this here and not sure if it's needed since `NullPool` is the default for SqLite.
# Does need to be added when `StaticPool` is used.
engine = create_engine(
    SQLALCHEMY_DATABASE_URL, connect_args={"check_same_thread": False}
)

SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

# The mixin could have passed the mixin here as well.
# Base = declarative_base(cls=DictMixIn)
Base = declarative_base()


def init_db(app):
    """

    Create ``scoped_session`` only if we are initializing within flask because sessions
    will not close properly outside of the context.
    We can add optional ``query_property`` to the ``Base``.

    Parameters
    ----------
    app : flask.Flask

    """

    # Import models locally just to ensure they get added to the registry on app load
    from app import models

    db_session = scoped_session(SessionLocal, scopefunc=_app_ctx_stack.__ident_func__)
    Base.query = db_session.query_property()
    Base.metadata.create_all(bind=engine)

    if DB_EXTENSION_KEY not in app.extensions:
        app.extensions[DB_EXTENSION_KEY] = db_session
        app.db = db_session

    @app.teardown_appcontext
    def remove_db_session(exception=None):
        """Terminates all connections, transactions or stale, in session and checks them back into pool"""
        db_session.remove()


# A little too advanced maybe? skip?
def _get_db():
    """

    Returns
    -------
    sqlalchemy.orm.Session
        session obj stored in global Flask App.
    """
    if has_app_context():
        assert (
            DB_EXTENSION_KEY in current_app.extensions
        ), "`db_session` might not have been registered with the current app"
        return current_app.extensions[DB_EXTENSION_KEY]
    raise RuntimeError("No application context found.")


db = LocalProxy(_get_db)
