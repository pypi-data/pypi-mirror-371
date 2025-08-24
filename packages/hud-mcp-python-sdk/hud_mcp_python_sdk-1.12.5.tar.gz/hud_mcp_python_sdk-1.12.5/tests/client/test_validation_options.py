"""Tests for client-side validation options."""

import logging
from contextlib import contextmanager
from unittest.mock import patch

import pytest

from mcp.client.session import ValidationOptions
from mcp.server.lowlevel import Server
from mcp.shared.memory import (
    create_connected_server_and_client_session as client_session,
)
from mcp.types import Tool


@contextmanager
def bypass_server_output_validation():
    """
    Context manager that bypasses server-side output validation.
    This simulates a non-compliant server that doesn't validate its outputs.
    """
    with patch("mcp.server.lowlevel.server.jsonschema.validate"):
        yield


class TestValidationOptions:
    """Test validation options for MCP client sessions."""

    @pytest.mark.anyio
    async def test_strict_validation_default(self):
        """Test that strict validation is enabled by default."""
        server = Server("test-server")

        output_schema = {
            "type": "object",
            "properties": {"result": {"type": "integer"}},
            "required": ["result"],
        }

        @server.list_tools()
        async def list_tools():
            return [
                Tool(
                    name="test_tool",
                    description="Test tool",
                    inputSchema={"type": "object"},
                    outputSchema=output_schema,
                )
            ]

        @server.call_tool()
        async def call_tool(name: str, arguments: dict):
            # Return unstructured content instead of structured content
            # This will trigger the validation error we want to test
            return "This is unstructured text content"

        with bypass_server_output_validation():
            async with client_session(server) as client:
                # Should raise by default
                with pytest.raises(RuntimeError) as exc_info:
                    await client.call_tool("test_tool", {})
                assert "has an output schema but did not return structured content" in str(exc_info.value)

    @pytest.mark.anyio
    async def test_lenient_validation_missing_content(self, caplog):
        """Test lenient validation when structured content is missing."""
        server = Server("test-server")

        output_schema = {
            "type": "object",
            "properties": {"result": {"type": "integer"}},
            "required": ["result"],
        }

        @server.list_tools()
        async def list_tools():
            return [
                Tool(
                    name="test_tool",
                    description="Test tool",
                    inputSchema={"type": "object"},
                    outputSchema=output_schema,
                )
            ]

        @server.call_tool()
        async def call_tool(name: str, arguments: dict):
            # Return unstructured content instead of structured content
            # This will trigger the validation error we want to test
            return "This is unstructured text content"

        # Set logging level to capture warnings
        caplog.set_level(logging.WARNING)

        # Create client with lenient validation
        validation_options = ValidationOptions(strict_output_validation=False)
        
        with bypass_server_output_validation():
            async with client_session(server, validation_options=validation_options) as client:
                # Should not raise with lenient validation
                result = await client.call_tool("test_tool", {})
                
                # Should have logged a warning
                assert "has an output schema but did not return structured content" in caplog.text
                assert "Continuing without structured content validation" in caplog.text
                
                # Result should still be returned
                assert result.isError is False
                assert result.structuredContent is None

    @pytest.mark.anyio
    async def test_lenient_validation_invalid_content(self, caplog):
        """Test lenient validation when structured content is invalid."""
        server = Server("test-server")

        output_schema = {
            "type": "object",
            "properties": {"result": {"type": "integer"}},
            "required": ["result"],
        }

        @server.list_tools()
        async def list_tools():
            return [
                Tool(
                    name="test_tool",
                    description="Test tool",
                    inputSchema={"type": "object"},
                    outputSchema=output_schema,
                )
            ]

        @server.call_tool()
        async def call_tool(name: str, arguments: dict):
            # Return invalid structured content (string instead of integer)
            return {"result": "not_an_integer"}

        # Set logging level to capture warnings
        caplog.set_level(logging.WARNING)

        # Create client with lenient validation
        validation_options = ValidationOptions(strict_output_validation=False)
        
        with bypass_server_output_validation():
            async with client_session(server, validation_options=validation_options) as client:
                # Should not raise with lenient validation
                result = await client.call_tool("test_tool", {})
                
                # Should have logged a warning
                assert "Invalid structured content returned by tool test_tool" in caplog.text
                assert "Continuing due to lenient validation mode" in caplog.text
                
                # Result should still be returned with the invalid content
                assert result.isError is False
                assert result.structuredContent == {"result": "not_an_integer"}

    @pytest.mark.anyio
    async def test_strict_validation_with_valid_content(self):
        """Test that valid content passes with strict validation."""
        server = Server("test-server")

        output_schema = {
            "type": "object",
            "properties": {"result": {"type": "integer"}},
            "required": ["result"],
        }

        @server.list_tools()
        async def list_tools():
            return [
                Tool(
                    name="test_tool",
                    description="Test tool",
                    inputSchema={"type": "object"},
                    outputSchema=output_schema,
                )
            ]

        @server.call_tool()
        async def call_tool(name: str, arguments: dict):
            # Return valid structured content
            return {"result": 42}

        async with client_session(server) as client:
            # Should succeed with valid content
            result = await client.call_tool("test_tool", {})
            assert result.isError is False
            assert result.structuredContent == {"result": 42}

    @pytest.mark.anyio
    async def test_schema_errors_always_raised(self):
        """Test that schema errors are always raised regardless of validation mode."""
        server = Server("test-server")

        # Invalid schema (missing required 'type' field)
        output_schema = {"properties": {"result": {}}}

        @server.list_tools()
        async def list_tools():
            return [
                Tool(
                    name="test_tool",
                    description="Test tool",
                    inputSchema={"type": "object"},
                    outputSchema=output_schema,
                )
            ]

        @server.call_tool()
        async def call_tool(name: str, arguments: dict):
            return {"result": 42}

        # Test with lenient validation
        validation_options = ValidationOptions(strict_output_validation=False)
        
        with bypass_server_output_validation():
            async with client_session(server, validation_options=validation_options) as client:
                # Should still raise for schema errors
                with pytest.raises(RuntimeError) as exc_info:
                    await client.call_tool("test_tool", {})
                assert "Invalid schema for tool test_tool" in str(exc_info.value)
