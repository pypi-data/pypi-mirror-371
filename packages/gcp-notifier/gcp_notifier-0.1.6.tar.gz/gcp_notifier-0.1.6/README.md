
# GCP Notifier

[![Upload Python Package](https://github.com/marcellusmontilla/gcp_notifier/actions/workflows/python-publish.yml/badge.svg)](https://github.com/marcellusmontilla/gcp_notifier/actions/workflows/python-publish.yml)

## Synchronous Usage

Import and use in your Python code:

```python
from gcp_notifier import notify, notify_on_failure

# Send a notification (choose channels: "email", "gchat", or both)
notify(
  subject="Alert Subject",
  body="Alert body text",
  channels=["email", "gchat"]  # or ["email"] or ["gchat"]
)

# Use as tenacity retry_error_callback
from tenacity import retry, stop_after_attempt

@retry(stop=stop_after_attempt(3), retry_error_callback=notify_on_failure)
def always_fails():
  # This function will always fail, triggering notify_on_failure after retries
  raise ValueError("This is a test error for notification.")

always_fails()
```

## Async Usage

You can send notifications asynchronously using the async API.

### Async notify example

```python
import asyncio  # only if running a script, otherwise, do not import
from gcp_notifier import async_notify

async def main():
  await async_notify(
    subject="Async Alert",
    body="This is an async alert!",
    channels=["email", "gchat"]
  )

asyncio.run(main()) # if running a script
await main()        # if using a notebook
```

---

### Async tenacity error callback example

```python
import asyncio  # only if running a script, otherwise, do not import
from gcp_notifier import async_notify_on_failure
from tenacity import retry, stop_after_attempt

@retry(stop=stop_after_attempt(3), retry_error_callback=async_notify_on_failure)
async def always_fails_async():
  raise ValueError("This is a test error for async notification.")

asyncio.run(always_fails_async())   # if running a script
await always_fails_async()          # if using a notebook
```

## Installation

Install from PyPI (recommended):

```sh
pip install gcp-notifier
```

For async features (async_notify, async_notify_on_failure), install with the optional async dependencies:

```sh
pip install 'gcp-notifier[async]'
```

This will install the package plus the required async libraries (aiosmtplib, httpx).

## Quick Start

1. Install the package (see Installation above).

2. The account (personal or service) running this code must have the 'Secret Manager Secret Accessor' role in your GCP project.

3. The required secrets must be in the same GCP project where your Python script or notebook is running.

4. Add your required secrets to Google Secret Manager in your GCP project:

   - `GCHAT_WEBHOOK_URL` (for Google Chat)
   - `EMAIL_SENDER` (sender email address for Email)
   - `EMAIL_PASSWORD` (password or app password for sender)
   - `EMAIL_RECIPIENTS` (comma-separated list of recipient email addresses)

5. Import and use `notify` in your code as shown below.

## Building and Publishing

This project uses a modern Python packaging workflow with `pyproject.toml`.

To build the package:

```sh
python -m pip install --upgrade build
python -m build
```

To check and upload to PyPI:

```sh
python -m pip install --upgrade twine
twine check dist/*
twine upload dist/*
```

See [Python Packaging User Guide](https://packaging.python.org/en/latest/tutorials/packaging-projects/) for more details.

## License

MIT
