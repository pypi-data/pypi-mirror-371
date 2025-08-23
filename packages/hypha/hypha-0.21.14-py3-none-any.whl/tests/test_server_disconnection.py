"""Test the hypha server."""

import os
import subprocess
import sys
import asyncio

import pytest
import requests
from hypha_rpc import connect_to_server

from . import (
    SERVER_URL,
    SERVER_URL_REDIS_1,
    SERVER_URL_REDIS_2,
    SIO_PORT2,
    WS_SERVER_URL,
    find_item,
)

# All test coroutines will be treated as marked.
pytestmark = pytest.mark.asyncio


async def test_server_reconnection(fastapi_server, root_user_token):
    """Test the server reconnection."""
    async with connect_to_server(
        {"server_url": WS_SERVER_URL, "client_id": "admin", "token": root_user_token}
    ) as root:
        admin = await root.get_service("admin-utils")

        api = await connect_to_server(
            {"server_url": WS_SERVER_URL, "client_id": "client1"}
        )
        assert api.config["client_id"] == "client1"
        await admin.kickout_client(
            api.config.workspace,
            api.config.client_id,
            1008,
            "simulated abnormal closure",
        )
        await asyncio.sleep(1)

        # It should reconnect
        assert await api.echo("hi") == "hi"
        await api.disconnect()

        api = await connect_to_server(
            {"server_url": WS_SERVER_URL, "client_id": "client1"}
        )
        assert api.config["client_id"] == "client1"
        await admin.kickout_client(
            api.config.workspace, api.config.client_id, 1000, "normal closure"
        )
        await asyncio.sleep(1)
        try:
            assert await api.echo("hi") == "hi"
        except Exception as e:
            assert "Connection is closed" in str(e)
            await api.disconnect()
