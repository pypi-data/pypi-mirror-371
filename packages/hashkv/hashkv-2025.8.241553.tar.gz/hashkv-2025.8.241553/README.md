[![PyPI version](https://badge.fury.io/py/hashkv.svg)](https://badge.fury.io/py/hashkv)
[![License: MIT](https://img.shields.io/badge/License-MIT-green.svg)](https://opensource.org/licenses/MIT)
[![Downloads](https://static.pepy.tech/badge/hashkv)](https://pepy.tech/project/hashkv)
[![LinkedIn](https://img.shields.io/badge/LinkedIn-blue)](https://www.linkedin.com/in/eugene-evstafev-716669181/)

# hashkv

Async helpers to **get/set string values** for hashed Redis keys with TTL.

Key format: `"{prefix}:{hash_hex}"`. You pass a precomputed hash string.

## Install
```bash
pip install hashkv
````

## Usage

```python
import asyncio
from hashkv import get_hash_value, set_hash_value

async def main():
    url = "redis://localhost:6379/0"
    prefix = "some_prefix"
    hash_hex = "cf2d9b0f..."  # your hash

    await set_hash_value(hash_hex, value="ok", ttl_seconds=600, redis_url=url, key_prefix=prefix)
    cur = await get_hash_value(hash_hex, redis_url=url, key_prefix=prefix)
    print(cur)  # "ok"

if __name__ == "__main__":
    asyncio.run(main())
```

MIT © Eugene Evstafev
