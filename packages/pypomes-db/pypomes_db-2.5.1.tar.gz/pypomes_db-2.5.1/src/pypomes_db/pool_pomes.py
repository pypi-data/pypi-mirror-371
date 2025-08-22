from __future__ import annotations  # allow forward references
from datetime import datetime, UTC
from enum import StrEnum, auto
from logging import Logger
from pypomes_core import APP_PREFIX, env_get_int, str_positional
from sys import getrefcount
from time import sleep
from threading import Lock
from typing import Any, Final

from .db_common import DbEngine, _DB_ENGINES, _assert_engine


class PoolParam(StrEnum):
    """
    Parameters for configuring the connection pool.
    """
    SIZE = auto()
    TIMEOUT: auto()
    RECYCLE: auto()


class PoolEvent(StrEnum):
    """
    Pool events for tuning and monitoring.
    """
    CREATE = auto()
    CHECKOUT = auto()
    CHECKIN: auto()
    CLOSE: auto()


class ConnStage(StrEnum):
    """
    Stage data of connections in pool.
    """
    CONNECTION: auto()
    TIMESTAMP: auto()
    AVAILABLE: auto()


# DbConnectionPool instances params:
# {
#    <DbEngine>: {
#       <PoolParam.RECYCLE>: <int>,
#       <PoolParam.SIZE>: <int>,
#       <PoolParam.TIMEOUT>: <int>
#    },
#    ...
# }
_POOL_DATA: Final[dict[DbEngine, dict[PoolParam, Any]]] = {}
for _db_engine in _DB_ENGINES:
    _prefix: str = "DB" if len(_DB_ENGINES) == 1 else \
        str_positional(source=_db_engine,
                       list_from=["mysql", "oracle", "postgres", "sqlserver"],
                       list_to=["MSQL", "ORCL", "PG", "SQLS"])
    _POOL_DATA[_db_engine] = {
        PoolParam.SIZE: env_get_int(key=f"{APP_PREFIX}_{_prefix}_POOL_SIZE",
                                    def_value=20),
        PoolParam.TIMEOUT: env_get_int(key=f"{APP_PREFIX}_{_prefix}_POOL_TIMEOUT",
                                       def_value=60),
        PoolParam.RECYCLE: env_get_int(key=f"{APP_PREFIX}_{_prefix}_POOL_RECYCLE",
                                       def_value=3600)
    }

# available DbConnectionPool instances:
# {
#    <DbEngine>: <DbConnectionPool>,
#    ...
# }
_POOL_INSTANCES: dict[DbEngine, DbConnectionPool] = {}

# lock pool instances access
_instances_lock: Lock = Lock()


class DbConnectionPool:
    """
    A robust, transparent, and efficient implementation of a database connection pool.

    This is a mechanism to manage database connections efficiently by reusing them, instead of their being
    repeatedly created and closed. As a result, overall performance is improved, latency is reduced, and
    resource usage is optimized, especially in applications with frequent database interactions.
    The connections are lazily created, as demand for connections arise and cannot be met by the stock
    already in the pool.

    This implementation follows the best practices in the industry, mirroring state-of-the-art products
    such as the *SQLAlchemy* pool package. These are the configuration parameters:
      - *pool_size*: maximum number of connections in the pool
      - *pool_timeout*: number of seconds to wait for a connection to become available, before failing the request
      - *pool_recycle*: number of seconds after which connections in the pool are closed

    These are the events that a pool client may hook up to, with a call to *on_event_actions()*, by
    specifying a callback function to be invoked, and/or SQL commands to be executed:
      - *create*: when a connection is created, allowing for connection session settings customization
      - *checkout*: when a connection is retrieved from the pool, allowing for fine-tuning the connection settings
      - *checkin*: when a connection is returned to the pool, allowing for cleanup of session state
      - *close*: when a connection is closed, allowing for resources cleanup and connection life cycle auditing

    The modules handling the native database operations (namely, *mysql_pomes.py*, *oracle_pomes.py*,
    *postgres_pomes.py*, and *sqlserver_pomes.py*) have no awareness of this pool. The higher level module
    *db_pomes.py* will attempt to obtain a connection from this pool on *db_connect()*, and to return it
    on *db_close()*. It is worth emphasizing that a *close()* operation should not be invoked directly
    on the native connection, as this would prevent it from being reclaimed, and cause it to be eventually
    discarded, thus defeating the very purpose of the pool.
    """
    def __init__(self,
                 errors: list[str] = None,
                 engine: DbEngine = None,
                 pool_size: int = None,
                 pool_timeout: int = None,
                 pool_recycle: int = None,
                 logger: Logger = None) -> None:
        """
        Construct a connection pool specific for the database provided in *engine*.

        The database engine specified must have been previously configured. If not provided, the values
        for pool configuration parameters specified in the environment variables suffixed with their
        uppercase names (nsmely, *POOL_SIZE*, *POOL_TIMEOUT*, and *POOL_RECYCLE*) are used.
        If still not specified, these are the default values used:
          - *pool_size*: 20 connections
          - *pool_timeout*: 60 seconds
          - *pool_recycle*: 3600 seconds (1 hour)

        :param errors: incidental errors
        :param engine: the database engine to use (uses the default engine, if not provided)
        :param pool_size: number of connections to keep in the pool
        :param pool_timeout: number of seconds to wait for an available connection before failing
        :param pool_recycle: number of seconds after which connections in the pool are closed and reopened
        :param logger: optional logger
        """
        # make sure a configured databasee engine has been specified
        engine = _assert_engine(errors=errors,
                                engine=engine)

        # obtain the default values for the pool parameters
        pool_data: dict[PoolParam, Any] | None = None
        if engine:
            with _instances_lock:
                if engine in _POOL_INSTANCES:
                    if isinstance(errors, list):
                        errors.append(f"{engine} pool already exists")
                else:
                    pool_data = _POOL_DATA[engine]
                    # register this instance
                    _POOL_INSTANCES[engine] = self

        if pool_data:
            self.db_engine: DbEngine = engine
            self.pool_size: int = pool_size or pool_data[PoolParam.SIZE]
            self.pool_timeout: int = pool_timeout or pool_data[PoolParam.TIMEOUT]
            self.pool_recycle: int = pool_recycle or pool_data[PoolParam.RECYCLE]
            self.stage_lock: Lock = Lock()
            self.event_lock: Lock = Lock()

            self.event_callbacks: dict[PoolEvent, callable] = {
                PoolEvent.CREATE: None,
                PoolEvent.CHECKOUT: None,
                PoolEvent.CHECKIN: None,
                PoolEvent.CLOSE: None
            }
            self.event_stmts: dict[PoolEvent, list[str]] = {
                PoolEvent.CREATE: [],
                PoolEvent.CHECKOUT: [],
                PoolEvent.CHECKIN: [],
                PoolEvent.CLOSE: []
            }
            self.conn_data: list[dict[ConnStage, Any]] = []

            if logger:
                logger.debug(msg=f"{self.db_engine} pool created: size {self.pool_size}, "
                                 f"timeout {self.pool_timeout}, recycle {self.pool_recycle}")

    def connect(self,
                errors: list[str] = None,
                logger: Logger = None) -> Any | None:
        """
        Obtain a pooled connection.

        :param errors: incidental errors
        :param logger: optional logger
        :return: a connection from the pool, or *None* if error
        """
        # obtain a pooled connection
        result: Any = None

        if not isinstance(errors, list):
            errors = []
        start: float = datetime.now(tz=UTC).timestamp()
        while not result:
            with self.stage_lock:
                self.__revise(errors=errors,
                              logger=logger)
                for conn_item in self.conn_data:
                    if conn_item[ConnStage.AVAILABLE]:
                        conn_item[ConnStage.AVAILABLE] = False
                        result = conn_item[ConnStage.CONNECTION]
                        break
                if not result and len(self.conn_data) < self.pool_size:
                    match self.db_engine:
                        case DbEngine.MYSQL:
                            from . import mysql_pomes
                            result = mysql_pomes.connect(errors=errors,
                                                         autocommit=False,
                                                         logger=logger)
                        case DbEngine.ORACLE:
                            from . import oracle_pomes
                            result = oracle_pomes.connect(errors=errors,
                                                          autocommit=False,
                                                          logger=logger)
                        case DbEngine.POSTGRES:
                            from . import postgres_pomes
                            result = postgres_pomes.connect(errors=errors,
                                                            autocommit=False,
                                                            logger=logger)
                        case DbEngine.SQLSERVER:
                            from . import sqlserver_pomes
                            result = sqlserver_pomes.connect(errors=errors,
                                                             autocommit=False,
                                                             logger=logger)
                    if result:
                        self.__act_on_event(errors=errors,
                                            event=PoolEvent.CREATE,
                                            conn=result,
                                            logger=logger)
                        if not errors:
                            # store the connection
                            self.conn_data.append({
                                ConnStage.TIMESTAMP: datetime.now(tz=UTC).timestamp(),
                                ConnStage.AVAILABLE: False,
                                ConnStage.CONNECTION: result
                            })
                            if logger:
                                logger.debug(msg=f"Connection '{result}' "
                                                 f"created by the {self.db_engine} pool")
            if not result:
                if datetime.now(tz=UTC).timestamp() - start < self.pool_timeout:
                    sleep(seconds=1.5)
                else:
                    errors.append("Timeout waiting for available connection")
                    break

        if result and not errors:
            self.__act_on_event(errors=errors,
                                event=PoolEvent.CHECKOUT,
                                conn=result,
                                logger=logger)

        # a connection may have been found, but errors would prevent it from being used
        if errors:
            result = None

        return result

    def on_event_actions(self,
                         event: PoolEvent,
                         callback: callable = None,
                         stmts: list[str] = None) -> None:
        """
        Specify a callback function to be invoked, and/or SQL commands to be executed, when *event* occurs.

        The possible events are:
          - *PoolEvent.CONNECTION*: a connection is created and added to the pool
          - *PoolEvent.CHECKOUT*: a connection is retrieved from the pool
          - *PoolEvent.CHECKIN*: a connection is returned to the pool
          - *PoolEven.CLOSE*: a connection is closed and removed from the pool

        If *callback* is not specified, any current callback is removed for *event*, otherwise it will be
        invoked with the following parameters:
          - *errors*: an empty list to collect errors in the execution of the callback
          - *connection*: the native connection obtained from the underlying database driver
          - *logger*: the logger in use by the operation that raised the event

        If *stmts* is not specified, any current statements are removed for *event*, otherwise it holds
        one or more SQL commands to be executed, aiming to, among others, and depending on the event:
          - initialize, set, reset, or cleanup the session state
          - set encoding, timezone, and sort order
          - validate connection health
          - audit connection life cycle
          - cleanup resources
          - log usage to database

        :param event: the reference event
        :param callback: the function to be invoked
        :param stmts: optional list of SQL commands to be executed
        """
        with self.event_lock:
            # register the event hook
            self.event_callbacks[event] = callback
            # register the SQL commands
            self.event_stmts[event] = stmts

    def reclaim(self,
                errors: list[str] | None,
                conn: Any,
                logger: Logger = None) -> bool:
        """
        Reclaim the connection given in *conn*, allowing for its reuse.

        :param errors: incidental errors
        :param conn: the connection to be reclaimed
        :param logger: optional logger
        :return: *True* if *conn* was successfully reclaimed, *False* otherwise
        """
        # initialize the return variable
        result: bool = False
        if not isinstance(errors, list):
            errors = []
        with self.stage_lock:
            for data in self.conn_data:
                if data[ConnStage.CONNECTION] == conn:
                    self.__act_on_event(errors=errors,
                                        event=PoolEvent.CHECKIN,
                                        conn=conn,
                                        logger=logger)
                    if not errors:
                        data[ConnStage.AVAILABLE] = True
                        result = True
                        if logger:
                            logger.debug(msg=f"Connection {conn} "
                                             f"reclaimed by the {self.db_engine} pool")
        return result

    def terminate(self,
                  logger: Logger = None) -> None:
        """
        Terminate the pool, releasing all held resources.

        Upon termination, all references to this instance should be disposed of,
        as invocation of any of its functions is guaranteed to fail.
        """
        with _instances_lock:
            _POOL_INSTANCES.pop(self.db_engine)

        with self.stage_lock:
            self.conn_data = None

        with self.event_lock:
            self.event_callbacks = []
            self.event_stmts = []

        if logger:
            logger.debug(msg=f"{self.db_engine} pool terminated")
        self.db_engine = None

    def __act_on_event(self,
                       errors: list[str] | None,
                       event: PoolEvent,
                       conn: Any,
                       logger: Logger | None) -> None:
        """
        Act on *event*, by invoking the hooked callback function, and/or executing the registered SQL statements.

        The possible events are:
          - *PoolEvent.CREATE*: a connection is created and added to the pool
          - *PoolEvent.CHECKOUT*: a connection is retrieved from the pool
          - *PoolEvent.CHECKIN*: a connection is returned to the pool
          - *PoolEven.CLOSE*: a connection is closed and removed from the pool

        If a callback function has been hooked to *event*, it is invoked with the following parameters:
          - *errors*: an empty list to collect errors in the execution of the callback
          - *connection*: the native connection obtained from the underlying database driver
          - *logger*: the logger in use by the operation that raised the event
        If the callback function adds content to *errors*, then the next step
        (execution of the registered SQL statements) is skipped.

        :param errors: incidental errors
        :param event: the reference event
        :param conn: the reference connection
        :param logger: optionqal logger
        """
        if not isinstance(errors, list):
            errors = []
        with self.event_lock:
            # invoke the callback
            callback: callable = self.event_callbacks[event]
            if callback:
                callback(errors=errors,
                         connection=conn,
                         logger=logger)

            # execute the statements
            if not errors and self.event_stmts[event]:
                from . import db_pomes
                for stmt in self.event_stmts[event]:
                    db_pomes.db_execute(errors=errors,
                                        exc_stmt=stmt,
                                        engine=self.db_engine,
                                        connection=conn,
                                        logger=logger)
                    if errors:
                        break

    def __revise(self,
                 errors: list[str] | None,
                 logger: Logger | None) -> None:
        """
        Revise the pool, reclaiming or disposing of connections, if applicable.

        This operation must be invoked within the guardrails of *self.stage_lock*.
        """
        if not isinstance(errors, list):
            errors = []
        # traverse the connection data in reverse order
        length: int = len(self.conn_data)
        rev_data: list[dict[ConnStage, Any]] = list(reversed(self.conn_data))
        for inx, data in enumerate(rev_data):
            # connection was closed elsewhere
            if hasattr(data[ConnStage.CONNECTION], "closed") and data[ConnStage.CONNECTION].closed:
                # dispose of closed connection
                self.conn_data.pop(length - inx - 1)
            elif data[ConnStage.AVAILABLE]:
                # connect exausted its lifetime
                if data[ConnStage.TIMESTAMP] + self.pool_recycle > datetime.now(tz=UTC):
                    # close the connection
                    self.__act_on_event(errors=errors,
                                        event=PoolEvent.CLOSE,
                                        conn=data[ConnStage.CONNECTION],
                                        logger=logger)
                    from . import db_pomes
                    db_pomes.db_close(errors=errors,
                                      connection=data[ConnStage.CONNECTION],
                                      logger=logger)
                    # dispose of closed connection
                    self.conn_data.pop(length - inx - 1)
                    if logger:
                        logger.debug(msg=f"Connection '{data[ConnStage.CONNECTION]}' "
                                         f"closed by the {self.db_engine} pool")
            # with only 2 references (1 held here, and 1 held by the pool), connection is no longer in use
            elif getrefcount(data[ConnStage.CONNECTION]) < 3:
                # reclaim the connection
                self.__act_on_event(errors=errors,
                                    event=PoolEvent.CHECKIN,
                                    conn=data[ConnStage.CONNECTION],
                                    logger=logger)
                if not errors:
                    data[ConnStage.AVAILABLE] = True
                    if logger:
                        logger.debug(msg=f"Connection '{data[ConnStage.CONNECTION]}' "
                                         f"reclaimed by the {self.db_engine} pool")


def pool_acquire(engine: DbEngine = None,
                 logger: Logger = None) -> Any | None:
    """
    Obtain a pooled connection for *engine*.

    :param engine: the database engine to use (uses the default engine, if not provided)
    :param logger: optional logger
    :return: a pooled connection to *engine*, or *None* if it unknown or has not been configured
    """
    # initialize the return variable
    result: Any = None

    # assert the database engine
    engine = _assert_engine(errors=None,
                            engine=engine)
    if engine:
        pool: DbConnectionPool = get_pool(engine=engine)
        # obtain the pooled connection
        if pool:
            result = pool.connect(errors=None,
                                  logger=logger)
    return result


def pool_release(conn: Any,
                 engine: DbEngine = None,
                 logger: Logger = None) -> bool:
    """
    Return *conn* to the pool, to allow it to be resued.

    :param conn: the connection to return to the pool
    :param engine: the database engine to use (uses the default engine, if not provided)
    :param logger: optional logger
    :return: *True* if *conn* was successfully reclaimed by the pool, *False* otherwise
    """
    # initialize the return variable
    result: bool = False

    # assert the database engine
    engine = _assert_engine(errors=None,
                            engine=engine)
    if engine:
        # reclaim the connection
        pool: DbConnectionPool = get_pool(engine=engine)
        if pool:
            result = pool.reclaim(errors=None,
                                  conn=conn,
                                  logger=logger)
    return result


def get_pool(engine: DbEngine = None) -> DbConnectionPool | None:
    """
    Retrieve the instance of the connection pool associated with *engine*.

    :param engine: the database engine to use (uses the default engine, if not provided)
    :return: the connection pool for *engine*, or *None* if no connection has been retrieved
    """
    # initialize the return variable
    result: DbConnectionPool | None = None

    # assert the database engine
    engine = _assert_engine(errors=None,
                            engine=engine)
    if engine:
        with _instances_lock:
            result = _POOL_INSTANCES.get(engine)

    return result
