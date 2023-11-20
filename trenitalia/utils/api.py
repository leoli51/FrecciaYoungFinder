from typing import Any

import requests


def get(url: str, params: dict[str, Any] | None) -> dict[str, Any]:
    response = requests.get(url=url, params=params)
    return response.json()


def post(
    url: str, params: dict[str, Any] | None, body: dict[str, Any]
) -> dict[str, Any]:
    response = requests.post(url=url, params=params, json=body)
    return response.json()
