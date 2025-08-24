# IBKR Authentication Workflow

Documentation for the IBKR Web API is [here](https://www.interactivebrokers.com/campus/ibkr-api-page/webapi-ref/).

1. Pull the repository.
2. Create and activate a virtual environment.
3. Install dependencies from `requirements.txt`.
4. Create a YAML configuration file:

    ```yaml
    client_id: ""
    client_key_id: ""
    credential: ""
    private_key_file: ""
    domain: "api.ibkr.com"
    ```

    The private key file will usually have a `.pem` extension. The domain will
    normally be `api.ibkr.com` but it's also possible to access the API via
    other sub-domains like `1.api.ibkr.com`.
5. Run the test script.

    ```bash
    python auth.py
    ```

## Installation

You can install from GitHub.

```bash
pip3 install git+https://github.com/datawookie/ibkr-oauth-flow
```

## Deploying to PyPi

This requires `UV_PUBLISH_TOKEN` to be set to a PyPi token in environment.

```bash
make deploy
```
