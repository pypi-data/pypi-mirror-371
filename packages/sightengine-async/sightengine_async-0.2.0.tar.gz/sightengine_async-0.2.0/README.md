# Async Sight Engine Wrapper

[![Python package](https://github.com/NateShoffner/sightengine-python-async/actions/workflows/python-package.yml/badge.svg?branch=master)](https://github.com/NateShoffner/sightengine-python-async/actions/workflows/python-package.yml)
[![PyPI - Version](https://img.shields.io/pypi/v/sightengine-async)](https://pypi.org/project/sightengine-async/)

Async Python wrapper for the Sight Engine API.

Currently a work in progress.

## Example Usage

```python
import asyncio
import os
from dotenv import load_dotenv

from sightengine.client import SightEngineClient
from sightengine.models import CheckRequest

load_dotenv()


async def main():
    client = SightEngineClient(
        api_user=os.getenv("SIGHTENGINE_API_USER"),
        api_secret=os.getenv("SIGHTENGINE_API_SECRET"),
    )

    request = CheckRequest(
        models=[
            "nudity-2.1",
            "weapon",
            "alcohol",
            "medical",
            "gambling",
        ],
        url="https://sightengine.com/assets/img/examples/example5.jpg",
    )

    response = await client.check(request)
    print(response)

if __name__ == "__main__":
    asyncio.run(main())
```

## TODO

[] Feedback endpoint
[] Genai opt_generators
