# S3 Locks

A library for distributed locking using Amazon S3.
Uses [S3 Conditional Writes](https://aws.amazon.com/about-aws/whats-new/2024/11/amazon-s3-functionality-conditional-writes/).

## Usage

```python
from s3_locks import S3Lock

with S3Lock(bucket='my-bucket', key='locks/my-resource', ttl=60) as lock:
    # code is only executed if the lock is acquired
    print("Lock acquired, performing protected operation")
    # lock will be released automatically when exiting the context manager
```
