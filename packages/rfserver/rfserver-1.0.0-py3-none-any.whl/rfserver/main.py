from rfserver.rest_api import rest


def main() -> None:
    rest.app.run()


if __name__ == "__main__":
    main()

"""
Steps:
>>> pwd
>>> python -m venv .venv
>>> source ./venv/bin/activate
>>> pip install -e .
>>> rfserver
"""
