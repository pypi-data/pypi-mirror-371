import asyncio
import json
from unittest.mock import AsyncMock, Mock, patch

import pytest

from pantheon.toolsets.remote.backend.base import ServiceInfo
from pantheon.toolsets.remote.backend.nats import (
    NATSBackend,
    NATSMessage,
    NATSRemoteWorker,
    NATSService,
)


class TestNATSMessage:
    """Test NATSMessage dataclass"""

    def test_message_creation(self):
        """Test NATSMessage creation with minimal parameters"""
        msg = NATSMessage(method="test_method", parameters={"param": "value"})

        assert msg.method == "test_method"
        assert msg.parameters == {"param": "value"}
        assert msg.reply_to is None
        assert msg.correlation_id is None

    def test_message_creation_with_all_params(self):
        """Test NATSMessage creation with all parameters"""
        msg = NATSMessage(
            method="test_method",
            parameters={"param": "value"},
            reply_to="reply.subject",
            correlation_id="corr-123",
        )

        assert msg.method == "test_method"
        assert msg.parameters == {"param": "value"}
        assert msg.reply_to == "reply.subject"
        assert msg.correlation_id == "corr-123"


class TestNATSBackend:
    """Test NATSBackend functionality"""

    def test_backend_initialization_default(self):
        """Test backend initialization with default server"""
        backend = NATSBackend([])

        assert backend.server_urls == ["nats://localhost:4222"]
        assert backend.nats_kwargs == {}
        assert backend.servers == ["nats://localhost:4222"]

    def test_backend_initialization_custom(self):
        """Test backend initialization with custom servers and kwargs"""
        server_urls = ["nats://demo.nats.io", "nats://backup.nats.io"]
        backend = NATSBackend(server_urls, timeout=30, max_reconnect_attempts=10)

        assert backend.server_urls == server_urls
        assert backend.nats_kwargs == {"timeout": 30, "max_reconnect_attempts": 10}
        assert backend.servers == server_urls

    @pytest.mark.asyncio
    async def test_get_connection_success(self):
        """Test successful connection establishment"""
        backend = NATSBackend(["nats://demo.nats.io"])

        mock_nc = AsyncMock()
        mock_js = Mock()  # Make this a regular Mock since jetstream() is sync
        mock_kv = AsyncMock()

        mock_nc.jetstream.return_value = mock_js
        mock_js.key_value = AsyncMock(return_value=mock_kv)

        with patch("nats.connect", return_value=mock_nc) as mock_connect:
            nc, js = await backend._get_connection()

            assert nc == mock_nc
            assert js == mock_js
            assert backend._js == mock_js
            assert backend._kv == mock_kv
            mock_connect.assert_called_once()

    @pytest.mark.asyncio
    async def test_get_connection_no_jetstream(self):
        """Test connection when JetStream is not available"""
        backend = NATSBackend(["nats://demo.nats.io"])

        mock_nc = AsyncMock()
        mock_nc.jetstream.side_effect = Exception("JetStream not available")

        with patch("nats.connect", return_value=mock_nc):
            nc, js = await backend._get_connection()

            assert nc == mock_nc
            assert js is None
            assert backend._kv is None

    @pytest.mark.asyncio
    async def test_get_connection_kv_creation(self):
        """Test KV bucket creation when it doesn't exist"""
        backend = NATSBackend(["nats://demo.nats.io"])

        mock_nc = AsyncMock()
        mock_js = Mock()  # Make this a regular Mock since jetstream() is sync
        mock_kv = AsyncMock()

        mock_nc.jetstream.return_value = mock_js
        mock_js.key_value = AsyncMock(side_effect=Exception("Bucket not found"))
        mock_js.create_key_value = AsyncMock(return_value=mock_kv)

        with patch("nats.connect", return_value=mock_nc):
            nc, js = await backend._get_connection()

            assert nc == mock_nc
            assert js == mock_js
            mock_js.create_key_value.assert_called_once_with(bucket="pantheon.service")
            assert backend._kv == mock_kv

    @pytest.mark.asyncio
    async def test_connect_method(self):
        """Test connect method returns NATSService"""
        backend = NATSBackend(["nats://demo.nats.io"])

        mock_nc = AsyncMock()
        backend._nc = mock_nc
        backend._kv = AsyncMock()

        with patch.object(backend, "_get_connection", return_value=(mock_nc, None)):
            service = await backend.connect("test_service", timeout=60)

            assert isinstance(service, NATSService)
            assert service.nc == mock_nc
            assert service.service_id == "test_service"
            assert service.timeout == 60

    def test_create_worker(self):
        """Test create_worker method"""
        backend = NATSBackend(["nats://demo.nats.io"])

        worker = backend.create_worker("test_service", description="Test worker")

        assert isinstance(worker, NATSRemoteWorker)
        assert worker._backend == backend
        assert worker._service_name == "test_service"
        assert worker._description == "Test worker"


class TestNATSService:
    """Test NATSService functionality"""

    def setup_method(self):
        """Setup mock NATS connection for tests"""
        self.mock_nc = AsyncMock()
        self.mock_kv = AsyncMock()
        self.service = NATSService(
            self.mock_nc, "test_service", self.mock_kv, timeout=30.0
        )

    @pytest.mark.asyncio
    async def test_invoke_success(self):
        """Test successful method invocation"""
        # Setup mock response
        mock_response = Mock()
        mock_response.data = b"response_data"
        self.mock_nc.request.return_value = mock_response

        with (
            patch("cloudpickle.dumps") as mock_dumps,
            patch("cloudpickle.loads") as mock_loads,
        ):
            mock_dumps.return_value = b"request_data"
            mock_loads.return_value = {"result": "success"}

            result = await self.service.invoke("test_method", {"arg": "value"})

            assert result == "success"
            self.mock_nc.request.assert_called_once()

            # Verify request parameters
            call_args = self.mock_nc.request.call_args
            assert call_args[0][0] == "pantheon.service.test_service"  # subject
            assert call_args[1]["timeout"] == 30.0

    @pytest.mark.asyncio
    async def test_invoke_with_error_response(self):
        """Test invocation with error in response"""
        mock_response = Mock()
        mock_response.data = b"error_data"
        self.mock_nc.request.return_value = mock_response

        with patch("cloudpickle.dumps"), patch("cloudpickle.loads") as mock_loads:
            mock_loads.return_value = {"error": "Remote error occurred"}

            with pytest.raises(Exception, match="Remote error occurred"):
                await self.service.invoke("test_method")

    @pytest.mark.asyncio
    async def test_invoke_timeout(self):
        """Test invocation timeout"""
        self.mock_nc.request.side_effect = asyncio.TimeoutError()

        with patch("cloudpickle.dumps"):
            with pytest.raises(
                Exception, match="Timeout calling test_method on test_service"
            ):
                await self.service.invoke("test_method")

    @pytest.mark.asyncio
    async def test_invoke_without_args(self):
        """Test invocation without arguments"""
        mock_response = Mock()
        mock_response.data = b"response_data"
        self.mock_nc.request.return_value = mock_response

        with (
            patch("cloudpickle.dumps") as mock_dumps,
            patch("cloudpickle.loads") as mock_loads,
        ):
            mock_loads.return_value = {"result": "no_args"}

            result = await self.service.invoke("test_method")

            assert result == "no_args"

            # Verify message creation
            mock_dumps.assert_called_once()
            message = mock_dumps.call_args[0][0]
            assert message.method == "test_method"
            assert message.args == {}

    @pytest.mark.asyncio
    async def test_fetch_service_info_from_kv(self):
        """Test fetching service info from KV store"""
        # Mock KV entry
        mock_entry = Mock()
        service_data = {
            "service_id": "test_service",
            "service_name": "Test Service",
            "description": "A test service",
            "functions_description": {"func1": {}},
        }
        mock_entry.value.decode.return_value = json.dumps(service_data)
        self.mock_kv.get.return_value = mock_entry

        service_info = await self.service.fetch_service_info()

        assert service_info.service_id == "test_service"
        assert service_info.service_name == "Test Service"
        assert service_info.description == "A test service"
        assert service_info.functions_description == {"func1": {}}

    @pytest.mark.asyncio
    async def test_fetch_service_info_kv_failure(self):
        """Test fetching service info when KV lookup fails"""
        self.mock_kv.get.side_effect = Exception("KV error")

        service_info = await self.service.fetch_service_info()

        # Should return default service info
        assert service_info.service_id == "test_service"
        assert service_info.service_name == ""
        assert service_info.description == ""

    @pytest.mark.asyncio
    async def test_fetch_service_info_no_kv(self):
        """Test fetching service info when no KV store available"""
        service = NATSService(self.mock_nc, "test_service", None)

        service_info = await service.fetch_service_info()

        assert service_info.service_id == "test_service"

    @pytest.mark.asyncio
    async def test_close(self):
        """Test close method (should not raise)"""
        await self.service.close()  # Should complete without error

    def test_service_info_property(self):
        """Test service_info property"""
        service_info = self.service.service_info

        assert isinstance(service_info, ServiceInfo)
        assert service_info.service_id == "test_service"


class TestNATSRemoteWorker:
    """Test NATSRemoteWorker functionality"""

    def setup_method(self):
        """Setup mock backend for tests"""
        self.mock_backend = Mock()
        self.mock_backend.server_urls = ["nats://demo.nats.io"]
        self.mock_backend._kv = AsyncMock()

        self.worker = NATSRemoteWorker(
            self.mock_backend, "test_service", "Test description"
        )

    def test_worker_initialization(self):
        """Test worker initialization"""
        assert self.worker._backend == self.mock_backend
        assert self.worker._service_name == "test_service"
        assert self.worker._description == "Test description"
        assert (
            self.worker.service_subject == f"pantheon.service.{self.worker._service_id}"
        )
        assert not self.worker._running
        assert self.worker._functions == {}

    def test_service_properties(self):
        """Test service ID and name properties"""
        assert isinstance(self.worker.service_id, str)
        assert "test_service_" in self.worker.service_id
        assert self.worker.service_name == "test_service"
        assert self.worker.servers == ["nats://demo.nats.io"]

    def test_register_function(self):
        """Test function registration"""

        def test_func():
            """Test function"""
            return "test"

        self.worker.register(test_func)

        assert "test_func" in self.worker._functions
        assert self.worker._functions["test_func"] == test_func

    def test_unregister_function(self):
        """Test function unregistration"""

        def test_func():
            return "test"

        self.worker.register(test_func)
        assert "test_func" in self.worker._functions

        self.worker.unregister("test_func")
        assert "test_func" not in self.worker._functions

    def test_functions_property(self):
        """Test functions property returns correct format"""

        def test_func():
            """Test function docs"""
            return "test"

        self.worker.register(test_func)
        functions = self.worker.functions

        assert isinstance(functions, dict)
        assert "test_func" in functions
        func_tuple = functions["test_func"]
        assert isinstance(func_tuple, tuple)
        assert len(func_tuple) == 2
        assert func_tuple[0] == test_func
        assert func_tuple[1] == "Test function docs"

    def test_get_service_info(self):
        """Test get_service_info method"""

        def test_func():
            """Test function"""
            return "test"

        self.worker.register(test_func)
        service_info = self.worker.get_service_info()

        assert isinstance(service_info, ServiceInfo)
        assert service_info.service_id == self.worker.service_id
        assert service_info.service_name == "test_service"
        assert service_info.description == "Test description"
        assert "test_func" in service_info.functions_description

    @pytest.mark.asyncio
    async def test_register_to_kv_store(self):
        """Test KV store registration"""

        def test_func():
            """Test function"""
            return "test"

        self.worker.register(test_func)
        self.worker.kv_store = AsyncMock()

        await self.worker._register_to_kv_store()

        self.worker.kv_store.put.assert_called_once()
        call_args = self.worker.kv_store.put.call_args
        assert call_args[0][0] == self.worker.service_id  # key

        # Verify stored data structure
        stored_data = json.loads(call_args[0][1].decode())
        assert stored_data["service_id"] == self.worker.service_id
        assert stored_data["service_name"] == "test_service"
        assert stored_data["subject"] == self.worker.service_subject

    @pytest.mark.asyncio
    async def test_register_to_kv_store_no_kv(self):
        """Test KV store registration when no KV available"""
        self.worker.kv_store = None

        # Should not raise an error
        await self.worker._register_to_kv_store()

    @pytest.mark.asyncio
    async def test_run_worker(self):
        """Test worker run method"""
        mock_nc = AsyncMock()
        mock_subscription = AsyncMock()
        mock_nc.subscribe.return_value = mock_subscription

        self.mock_backend._get_connection.return_value = (mock_nc, None)
        self.worker.kv_store = AsyncMock()

        # Start worker in background
        run_task = asyncio.create_task(self.worker.run())

        # Wait a bit for initialization
        await asyncio.sleep(0.1)

        assert self.worker._running
        assert self.worker.nc == mock_nc

        # Stop worker
        await self.worker.stop()

        # Wait for run task to complete
        await run_task

    @pytest.mark.asyncio
    async def test_handle_request_success(self):
        """Test successful request handling"""

        def test_func(x, y):
            return x + y

        self.worker.register(test_func)

        # Create mock message
        mock_msg = Mock()
        mock_msg.respond = AsyncMock()
        mock_msg.data = b"mock_data"

        with (
            patch("cloudpickle.loads") as mock_loads,
            patch("cloudpickle.dumps") as mock_dumps,
        ):
            # Mock incoming message
            message = NATSMessage(method="test_func", parameters={"x": 5, "y": 3})
            mock_loads.return_value = message
            mock_dumps.return_value = b"response"

            await self.worker._handle_request(mock_msg)

            # Verify response
            mock_msg.respond.assert_called_once_with(b"response")

            # Verify response data
            response_data = mock_dumps.call_args[0][0]
            assert response_data["result"] == 8

    @pytest.mark.asyncio
    async def test_handle_request_method_not_found(self):
        """Test request handling for non-existent method"""
        mock_msg = Mock()
        mock_msg.respond = AsyncMock()
        mock_msg.data = b"mock_data"

        with (
            patch("cloudpickle.loads") as mock_loads,
            patch("cloudpickle.dumps") as mock_dumps,
        ):
            message = NATSMessage(method="non_existent", parameters={})
            mock_loads.return_value = message
            mock_dumps.return_value = b"error_response"

            await self.worker._handle_request(mock_msg)

            # Verify error response
            mock_msg.respond.assert_called_once_with(b"error_response")

            response_data = mock_dumps.call_args[0][0]
            assert "error" in response_data
            assert "Method non_existent not found" in response_data["error"]

    @pytest.mark.asyncio
    async def test_handle_request_async_function(self):
        """Test request handling for async function"""

        async def async_func(value):
            await asyncio.sleep(0.01)  # Short delay
            return value * 2

        self.worker.register(async_func)

        mock_msg = Mock()
        mock_msg.respond = AsyncMock()
        mock_msg.data = b"mock_data"

        with (
            patch("cloudpickle.loads") as mock_loads,
            patch("cloudpickle.dumps") as mock_dumps,
        ):
            message = NATSMessage(method="async_func", parameters={"value": 10})
            mock_loads.return_value = message
            mock_dumps.return_value = b"response"

            await self.worker._handle_request(mock_msg)

            response_data = mock_dumps.call_args[0][0]
            assert response_data["result"] == 20

    @pytest.mark.asyncio
    async def test_handle_request_function_error(self):
        """Test request handling when function raises error"""

        def error_func():
            raise ValueError("Test error")

        self.worker.register(error_func)

        mock_msg = Mock()
        mock_msg.respond = AsyncMock()
        mock_msg.data = b"mock_data"

        with (
            patch("cloudpickle.loads") as mock_loads,
            patch("cloudpickle.dumps") as mock_dumps,
        ):
            message = NATSMessage(method="error_func", parameters={})
            mock_loads.return_value = message
            mock_dumps.return_value = b"error_response"

            await self.worker._handle_request(mock_msg)

            response_data = mock_dumps.call_args[0][0]
            assert "error" in response_data
            assert "Test error" in response_data["error"]

    @pytest.mark.asyncio
    async def test_stop_worker(self):
        """Test worker stop method"""
        # Setup mocks
        mock_subscription = AsyncMock()
        self.worker._subscription = mock_subscription
        self.worker.kv_store = AsyncMock()
        self.worker._running = True

        await self.worker.stop()

        assert not self.worker._running
        mock_subscription.unsubscribe.assert_called_once()
        self.worker.kv_store.delete.assert_called_once_with(self.worker.service_id)

    @pytest.mark.asyncio
    async def test_stop_worker_cleanup_error(self):
        """Test worker stop with cleanup errors"""
        mock_subscription = AsyncMock()
        mock_kv = AsyncMock()
        mock_kv.delete.side_effect = Exception("Cleanup error")

        self.worker._subscription = mock_subscription
        self.worker.kv_store = mock_kv
        self.worker._running = True

        # Should not raise despite cleanup error
        await self.worker.stop()

        assert not self.worker._running


class TestNATSIntegration:
    """Integration tests for NATS backend components"""

    @pytest.mark.asyncio
    async def test_backend_to_service_flow(self):
        """Test complete flow from backend to service creation"""
        backend = NATSBackend(["nats://demo.nats.io"])

        mock_nc = AsyncMock()
        with patch.object(backend, "_get_connection", return_value=(mock_nc, None)):
            service = await backend.connect("integration_test", timeout=45)

            assert isinstance(service, NATSService)
            assert service.nc == mock_nc
            assert service.service_id == "integration_test"
            assert service.timeout == 45

    def test_backend_to_worker_flow(self):
        """Test complete flow from backend to worker creation"""
        backend = NATSBackend(["nats://demo.nats.io"])

        worker = backend.create_worker(
            "integration_service", description="Integration test"
        )

        assert isinstance(worker, NATSRemoteWorker)
        assert worker._backend == backend
        assert worker._service_name == "integration_service"
        assert worker._description == "Integration test"

    def test_worker_lifecycle(self):
        """Test worker lifecycle management"""
        backend = NATSBackend(["nats://demo.nats.io"])
        worker = backend.create_worker("lifecycle_test")

        # Initial state
        assert not worker._running
        assert len(worker._functions) == 0

        # Register functions
        def func1():
            return "func1"

        def func2():
            return "func2"

        worker.register(func1)
        worker.register(func2)

        assert len(worker._functions) == 2
        assert "func1" in worker._functions
        assert "func2" in worker._functions

        # Test unregistration
        worker.unregister("func1")
        assert len(worker._functions) == 1
        assert "func1" not in worker._functions
        assert "func2" in worker._functions

    @pytest.mark.asyncio
    async def test_service_message_handling(self):
        """Test service message creation and parsing"""
        mock_nc = AsyncMock()
        service = NATSService(mock_nc, "message_test")

        # Mock successful response
        mock_response = Mock()
        mock_response.data = b"response_data"
        mock_nc.request.return_value = mock_response

        with (
            patch("cloudpickle.dumps") as mock_dumps,
            patch("cloudpickle.loads") as mock_loads,
        ):
            mock_loads.return_value = {"result": "message_success"}

            result = await service.invoke("test_method", {"param": "value"})

            assert result == "message_success"

            # Verify message structure
            mock_dumps.assert_called_once()
            message = mock_dumps.call_args[0][0]
            assert isinstance(message, NATSMessage)
            assert message.method == "test_method"
            assert message.parameters == {"param": "value"}
            assert message.correlation_id is not None
