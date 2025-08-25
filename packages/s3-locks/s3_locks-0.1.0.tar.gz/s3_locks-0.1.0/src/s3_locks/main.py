import json
import time
from abc import ABC, abstractmethod
from typing import Callable, Optional, Tuple

import boto3
from botocore.exceptions import ClientError
from loguru import logger


class LockStateChangedError(Exception):
    pass


class FailedToAcquireLockError(Exception):
    pass


class LockAlreadyAcquiredError(FailedToAcquireLockError):
    pass


class MaxAttemptsReachedError(FailedToAcquireLockError):
    pass


class LockNotFoundError(Exception):
    pass


class InvalidLockError(Exception):
    pass


class ObjectAlreadyExistsError(Exception):
    """Raised when attempting to acquire a lock but the target object already exists."""

    pass


class BaseS3Lock(ABC):
    """
    Base class for S3-based distributed locking implementations.
    """

    def __init__(
        self,
        bucket: str,
        key: str,
        ttl: float,
        retries: int = 0,
        retry_interval: Optional[float] = None,
        s3_client: Optional[boto3.client] = None,
    ):
        """
        Initialize a new BaseS3Lock instance.

        Args:
            bucket: The S3 bucket name
            key: The S3 key to use for the lock
            ttl: Time (in seconds) after which the lock expires if not renewed
            retries: Maximum number of retry attempts to acquire the lock
            retry_interval: Time (in seconds) between acquisition attempts
            s3_client: Optional boto3 s3 client
        """
        self.bucket = bucket
        self.key = key
        self.ttl = ttl
        if retries < 0 or not isinstance(retries, int):
            raise ValueError("retries must be a non-negative integer")
        self.retries = retries
        if self.retries > 0 and retry_interval is None:
            raise ValueError("retry_interval must be specified when retries > 0")
        self.retry_interval = retry_interval
        self._s3_client = s3_client or boto3.client("s3")
        self._lock_etag = None

    def __enter__(self):
        """Context manager entry - acquire the lock."""
        self.acquire()
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        """Context manager exit - release the lock."""
        self.release()

    def _get_lock(self) -> Tuple[bytes, str]:
        """
        Retrieve the lock file from S3.

        Returns:
            Tuple[bytes, str]: A tuple containing the lock content and its ETag

        Raises:
            LockNotFoundError: If the lock file doesn't exist in S3
            ClientError: For other S3 API errors
        """
        try:
            response = self._s3_client.get_object(Bucket=self.bucket, Key=self.key)
            body = response["Body"].read()
            etag = response["ETag"]
            return body, etag
        except ClientError as e:
            if e.response["Error"]["Code"] == "NoSuchKey":
                raise LockNotFoundError from e

    @staticmethod
    def _get_expires_at(body: bytes) -> float:
        """
        Parse the lock content and extract the expiration timestamp.

        Args:
            body: The raw content of the lock file as bytes

        Returns:
            float: The timestamp when the lock expires, or 0 if the lock is corrupted
        """
        try:
            body = body.decode("utf-8")
            body = json.loads(body)
            expires_at = body["expires_at"]
            expires_at = float(expires_at)
        except (json.JSONDecodeError, UnicodeDecodeError, KeyError, ValueError) as e:
            logger.warning(
                f"Corrupt lock object detected ({repr(e)}) but will continue"
            )
            return 0
        return expires_at

    def _confirm_valid(self, expires_at: float) -> None:
        """
        Check if the lock has expired.

        Args:
            expires_at: The timestamp when the lock expires

        Raises:
            InvalidLockError: If the lock has expired
        """
        if time.time() > expires_at:
            msg = f"lock has expired on {self.key}"
            logger.debug(msg)
            raise InvalidLockError(msg)

    def _conditional_put_object(
        self, put_args: dict, etag: Optional[str] = None
    ) -> dict:
        """
        Execute a conditional PUT operation to S3.

        Args:
            put_args: Dictionary of arguments to pass to put_object
            etag: Optional ETag for conditional request

        Returns:
            dict: The response from S3 put_object operation

        Raises:
            LockStateChangedError: If the condition fails due to the lock being modified
            ClientError: For other S3 API errors
        """
        args = put_args.copy()
        if etag:
            args["IfMatch"] = etag
        else:
            args["IfNoneMatch"] = "*"
        try:
            return self._s3_client.put_object(**args)
        except ClientError as e:
            error = e.response["Error"]
            error_code = error["Code"]
            if error_code in (
                "PreconditionFailed",
                "ConditionalRequestConflict",
                "NoSuchKey",
            ):
                raise LockStateChangedError(error)
            else:
                raise e

    def _create_lock(self, etag: Optional[str] = None) -> None:
        """
        Attempt to create the lock file in S3.

        Args:
            etag: Optional ETag for conditional creation

        Raises:
            LockStateChangedError: If the lock state has changed

        Note:
            If successful, updates the internal _lock_etag attribute
        """
        lock_data = {
            "expires_at": time.time() + self.ttl,
        }
        put_args = {
            "Bucket": self.bucket,
            "Key": self.key,
            "Body": json.dumps(lock_data),
            "ContentType": "application/json",
        }
        response = self._conditional_put_object(put_args, etag=etag)
        self._lock_etag = response.get("ETag")

    def _wait(self, start_time: float, retry_idx: int):
        """
        Calculate and wait for the appropriate retry interval.

        Args:
            start_time: The timestamp when the acquisition attempts started
            retry_idx: The current retry attempt count
        """
        next_attempt_time = start_time + (self.retry_interval * (retry_idx + 1))
        time_to_wait = next_attempt_time - time.time()
        if time_to_wait > 0:
            logger.debug(
                f"waiting {time_to_wait:.2f}s before attempting to acquire lock again"
            )
            time.sleep(time_to_wait)

    @abstractmethod
    def acquire(self) -> None:
        """
        Attempt to acquire the lock.

        Must be implemented by subclasses.
        """
        raise NotImplementedError("Subclasses must implement acquire() method")

    def _attempt_acquire(self) -> bool:
        """
        Attempt to acquire the lock once.

        Returns:
            bool: True if lock was acquired, False otherwise
        """
        etag = None
        try:
            contents, etag = self._get_lock()
            expires_at = self._get_expires_at(contents)
            self._confirm_valid(expires_at)
        except (LockNotFoundError, InvalidLockError):
            try:
                self._create_lock(etag)
                logger.debug(f"acquired lock on {self.key}")
                return True
            except LockStateChangedError:
                pass
        return False

    def release(self) -> None:
        """
        Release the lock if it is currently held.
        """
        if not self._lock_etag:
            return
        lock_data = {"expires_at": 0}
        put_args = {
            "Bucket": self.bucket,
            "Key": self.key,
            "Body": json.dumps(lock_data),
            "ContentType": "application/json",
        }
        try:
            self._conditional_put_object(put_args, etag=self._lock_etag)
        except LockStateChangedError:
            pass
        self._lock_etag = None


class S3Lock(BaseS3Lock):
    """
    A distributed lock implementation using Amazon S3.

    This class provides a mechanism for distributed locking across multiple
    processes or machines using S3's consistency guarantees.
    """

    def acquire(self) -> None:
        """
        Attempt to acquire the lock, handling expired locks.

        Raises:
            LockAlreadyAcquiredError: If the lock is already held by this instance
            MaxAttemptsReachedError: If max retries have been reached without acquiring the lock
        """
        start_time = time.time()
        if self._lock_etag:
            raise LockAlreadyAcquiredError
        if self._attempt_acquire():
            return
        if self.retries > 0:
            for retry_idx in range(self.retries):
                self._wait(start_time, retry_idx)
                if self._attempt_acquire():
                    return
            msg = f"couldn't acquire lock on {self.key} after {retry_idx + 2} attempts"
        else:
            msg = f"couldn't acquire lock on {self.key}"
        logger.warning(msg)
        raise MaxAttemptsReachedError(msg)


class S3ObjectLock(BaseS3Lock):
    """
    A specialized S3 lock that can bypass acquisition if a target object exists.

    This is useful for get_or_create patterns where multiple processes might
    try to create the same expensive resource.
    """

    def __init__(
        self,
        bucket: str,
        key: str,
        object_key: str,
        ttl: float,
        retries: int = 0,
        retry_interval: Optional[float] = None,
        s3_client: Optional[boto3.client] = None,
    ):
        """
        Initialize a new S3ObjectLock instance.

        Args:
            bucket: The S3 bucket name
            key: The S3 key to use for the lock
            object_key: The S3 key of the object to check for existence
            ttl: Time (in seconds) after which the lock expires if not renewed
            retries: Maximum number of retry attempts to acquire the lock
            retry_interval: Time (in seconds) between acquisition attempts
            s3_client: Optional boto3 s3 client
        """
        super().__init__(bucket, key, ttl, retries, retry_interval, s3_client)
        self.object_key = object_key

    def _object_exists(self) -> bool:
        """
        Check if the target object exists in S3.

        Returns:
            bool: True if the object exists, False otherwise
        """
        try:
            self._s3_client.head_object(Bucket=self.bucket, Key=self.object_key)
            return True
        except ClientError as e:
            if e.response["Error"]["Code"] == "404":
                return False
            raise

    def acquire(self) -> None:
        """
        Attempt to acquire the lock, but raise ObjectAlreadyExistsError if the target object already exists.

        Raises:
            LockAlreadyAcquiredError: If the lock is already held by this instance
            ObjectAlreadyExistsError: If the target object already exists
            MaxAttemptsReachedError: If max retries have been reached without acquiring the lock
        """
        start_time = time.time()
        if self._lock_etag:
            raise LockAlreadyAcquiredError
        if self._object_exists():
            raise ObjectAlreadyExistsError(f"Object {self.object_key} already exists")
        if self._attempt_acquire():
            return

        if self.retries > 0:
            for retry_idx in range(self.retries):
                self._wait(start_time, retry_idx)
                if self._object_exists():
                    raise ObjectAlreadyExistsError(
                        f"Object {self.object_key} already exists"
                    )
                if self._attempt_acquire():
                    return
            msg = f"couldn't acquire lock on {self.key} after {retry_idx + 2} attempts"
        else:
            msg = f"couldn't acquire lock on {self.key}"
        logger.warning(msg)
        raise MaxAttemptsReachedError(msg)


def _get_object(s3_client: boto3.client, bucket: str, key: str) -> bytes:
    response = s3_client.get_object(Bucket=bucket, Key=key)
    return response["Body"].read()


def get_or_create(
    bucket: str,
    key: str,
    create_fn: Callable[[], bytes],
    lock_ttl: float = 60,
    lock_retries: int = 0,
    lock_retry_interval: Optional[float] = None,
    s3_client: Optional[boto3.client] = None,
    cache_read: bool = True,
    cache_write: bool = True,
) -> bytes:
    """
    Get an object from S3 or create it if it doesn't exist.

    Uses distributed locking to ensure only one process creates the object.
    Other processes will either get the existing object or wait for it to be created.

    Args:
        bucket: S3 bucket name
        key: S3 object key
        create_fn: Function that creates and returns the object content as bytes
        lock_ttl: Time-to-live for the lock in seconds
        lock_retries: Number of retries for lock acquisition
        lock_retry_interval: Interval between lock acquisition retries
        s3_client: Optional boto3 S3 client
        cache_read: Whether to read from cache (S3) if object exists
        cache_write: Whether to write to cache (S3) after creating object

    Returns:
        bytes: The object content

    Example:
        def expensive_function():
            # Simulate an expensive operation
            import time
            time.sleep(5)
            return b"Expensive Result"

        result = get_or_create(
            bucket="my_bucket",
            key="my_thing",
            create_fn=expensive_function,
        )
    """
    if s3_client is None:
        s3_client = boto3.client("s3")
    lock_key = f"{key}.lock"
    if cache_read:
        lock = S3ObjectLock(
            bucket=bucket,
            key=lock_key,
            object_key=key,
            ttl=lock_ttl,
            retries=lock_retries,
            retry_interval=lock_retry_interval,
            s3_client=s3_client,
        )
        try:
            return _get_object(s3_client, bucket, key)
        except ClientError as e:
            if e.response["Error"]["Code"] != "NoSuchKey":
                raise
        try:
            logger.info(f"Attempting to acquire lock for s3://{bucket}/{key} ...")
            with lock:
                logger.info(f"Got lock! Creating value for s3://{bucket}/{key}")
                content = create_fn()
                if cache_write:
                    logger.info(f"Writing value to s3://{bucket}/{key}")
                    s3_client.put_object(Bucket=bucket, Key=key, Body=content)
                return content
        except ObjectAlreadyExistsError:
            return _get_object(s3_client, bucket, key)
    else:
        lock = S3Lock(
            bucket=bucket,
            key=lock_key,
            ttl=lock_ttl,
            retries=lock_retries,
            retry_interval=lock_retry_interval,
            s3_client=s3_client,
        )
        with lock:
            content = create_fn()
            if cache_write:
                s3_client.put_object(Bucket=bucket, Key=key, Body=content)
            return content
