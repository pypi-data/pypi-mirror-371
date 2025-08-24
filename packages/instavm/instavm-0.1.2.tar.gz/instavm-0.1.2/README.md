# InstaVM Client

A Python client library for interacting with a simple API.

## Installation

You can install the package using pip:
     ```
     pip install instavm
     ```

## Usage

     ```python
    from instavm import InstaVM

    client = InstaVM(api_key='your_api_key', base_url='https://api.instavm.io')

    # Execute a command
    result = client.execute("print(100**100)")
    print(result)

    # Get usage info for the session
    usage = client.get_usage()
    print(usage)
     ```
