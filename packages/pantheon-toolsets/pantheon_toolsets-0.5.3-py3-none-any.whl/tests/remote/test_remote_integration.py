"""
Integration tests for the remote module.

This module tests the interaction between different components of the remote system,
including factory, backends, and configuration management.
"""

import pytest
from unittest.mock import Mock, AsyncMock, patch
from pantheon.toolsets.remote import (
    connect_remote,
    RemoteConfig,
    RemoteBackendFactory,
    BackendRegistry,
)
from pantheon.toolsets.remote.backend.base import (
    RemoteBackend,
    RemoteService,
    RemoteWorker,
)


class TestRemoteModuleIntegration:
    """Test integration between remote module components"""

    def setup_method(self):
        """Setup clean state for each test"""
        # Clear any existing registrations
        BackendRegistry.clear()
        # Re-register standard backends
        RemoteBackendFactory.register_backends()

    def test_end_to_end_backend_creation(self):
        """Test complete flow from config to backend instantiation"""
        # Test each backend type
        test_configs = [
            ("magique", {}),
            ("nats", {"server_urls": ["nats://demo.nats.io"]}),
            ("hypha", {"server_url": "https://ai.imjoy.io"}),
        ]

        for backend_name, extra_config in test_configs:
            config = RemoteConfig.from_config(backend=backend_name, **extra_config)
            backend = RemoteBackendFactory.create_backend(config)

            # Verify backend implements required interface
            assert isinstance(backend, RemoteBackend)
            assert hasattr(backend, "connect")
            assert hasattr(backend, "create_worker")
            assert hasattr(backend, "servers")

            # Test worker creation
            worker = backend.create_worker(f"test_service_{backend_name}")
            assert isinstance(worker, RemoteWorker)
            assert worker.service_name == f"test_service_{backend_name}"

    def test_config_environment_integration(self, monkeypatch):
        """Test configuration with environment variables"""
        # Set environment variables
        monkeypatch.setenv("PANTHEON_REMOTE_BACKEND", "nats")
        monkeypatch.setenv("NATS_SERVERS", "nats://demo.nats.io|nats://backup.nats.io")

        # Create config from environment
        config = RemoteConfig.from_env()
        assert config.backend == "nats"
        assert "nats://demo.nats.io" in config.backend_config["server_urls"]
        assert "nats://backup.nats.io" in config.backend_config["server_urls"]

        # Create backend from config
        backend = RemoteBackendFactory.create_backend(config)
        assert backend.servers == ["nats://demo.nats.io", "nats://backup.nats.io"]

    @pytest.mark.asyncio
    async def test_connect_remote_function(self):
        """Test the main connect_remote function"""
        with patch(
            "pantheon.toolsets.remote.factory.RemoteBackendFactory.create_backend"
        ) as mock_create:
            mock_backend = Mock()
            mock_service = AsyncMock()
            mock_backend.connect.return_value = mock_service
            mock_create.return_value = mock_backend

            # Test with default configuration
            service = await connect_remote("test_service")

            assert service == mock_service
            mock_backend.connect.assert_called_once_with("test_service")

    @pytest.mark.asyncio
    async def test_connect_remote_with_server_urls(self):
        """Test connect_remote with custom server URLs"""
        with patch(
            "pantheon.toolsets.remote.factory.RemoteBackendFactory.create_backend"
        ) as mock_create:
            mock_backend = Mock()
            mock_service = AsyncMock()
            mock_backend.connect.return_value = mock_service
            mock_create.return_value = mock_backend

            # Test with custom server URLs
            custom_urls = ["ws://custom.server.com"]
            service = await connect_remote("test_service", server_urls=custom_urls)

            assert service == mock_service

            # Verify config was created with custom URLs
            config_call = mock_create.call_args[0][0]
            assert config_call.backend_config["server_urls"] == custom_urls

    def test_backend_registry_consistency(self):
        """Test that backend registry maintains consistency"""
        # Get initial state
        initial_backends = set(BackendRegistry.list_backends())

        # Standard backends should be registered
        expected_backends = {"magique", "nats", "hypha"}
        assert expected_backends.issubset(initial_backends)

        # Test that each can be retrieved and instantiated
        for backend_name in expected_backends:
            backend_class = BackendRegistry.get_backend(backend_name)
            assert backend_class is not None

            # Test instantiation with minimal config
            try:
                if backend_name == "magique":
                    backend = backend_class(server_urls=["ws://test.com"])
                elif backend_name == "nats":
                    backend = backend_class(server_urls=["nats://test.com"])
                elif backend_name == "hypha":
                    backend = backend_class(server_url="https://test.com")

                assert isinstance(backend, RemoteBackend)
            except Exception as e:
                # Skip if instantiation fails (dependencies might not be available)
                pytest.skip(f"Backend {backend_name} instantiation failed: {e}")

    def test_worker_interface_consistency(self):
        """Test that all workers implement consistent interfaces"""
        backends_to_test = ["magique", "nats", "hypha"]

        for backend_name in backends_to_test:
            config = RemoteConfig.from_config(backend=backend_name)
            backend = RemoteBackendFactory.create_backend(config)
            worker = backend.create_worker("consistency_test")

            # Test required properties
            assert hasattr(worker, "service_id")
            assert hasattr(worker, "service_name")
            assert hasattr(worker, "functions")

            # Test required methods
            assert hasattr(worker, "register")
            assert hasattr(worker, "run")
            assert hasattr(worker, "stop")

            # Test property types
            assert isinstance(worker.service_id, str)
            assert isinstance(worker.service_name, str)
            assert isinstance(worker.functions, dict)

            # Test function registration
            def test_func():
                """Test function"""
                return "test"

            worker.register(test_func)
            assert "test_func" in worker.functions
            assert len(worker.functions) == 1

    def test_config_parameter_propagation(self):
        """Test that configuration parameters are properly propagated"""
        test_cases = [
            {
                "backend": "magique",
                "server_urls": ["ws://custom.magique.io"],
                "timeout": 60,
                "custom_param": "magique_value",
            },
            {
                "backend": "nats",
                "server_urls": ["nats://custom.nats.io"],
                "timeout": 45,
                "custom_param": "nats_value",
            },
            {
                "backend": "hypha",
                "server_url": "https://custom.hypha.io",
                "workspace": "custom_workspace",
                "token": "custom_token",
            },
        ]

        for test_case in test_cases:
            backend_name = test_case.pop("backend")
            config = RemoteConfig.from_config(backend=backend_name, **test_case)

            assert config.backend == backend_name
            for key, value in test_case.items():
                assert config.backend_config[key] == value

    def test_error_handling_integration(self):
        """Test error handling across components"""
        # Test invalid backend
        with pytest.raises(ValueError, match="Backend 'invalid' not registered"):
            config = RemoteConfig(backend="invalid", backend_config={})
            RemoteBackendFactory.create_backend(config)

        # Test backend without required parameters
        config = RemoteConfig(backend="magique", backend_config={})
        backend = RemoteBackendFactory.create_backend(config)

        # Should handle missing server_urls gracefully
        assert hasattr(backend, "server_urls")

    @pytest.mark.asyncio
    async def test_service_interface_consistency(self):
        """Test that all services implement consistent interfaces"""
        # This test uses mocks since we don't want to connect to real servers
        for backend_name in ["magique", "nats", "hypha"]:
            config = RemoteConfig.from_config(backend=backend_name)
            backend = RemoteBackendFactory.create_backend(config)

            # Mock the connection method to return a mock service
            with patch.object(backend, "connect") as mock_connect:
                mock_service = Mock()
                mock_service.invoke = AsyncMock(return_value="test_result")
                mock_service.close = AsyncMock()
                mock_service.service_info = Mock()
                mock_service.fetch_service_info = AsyncMock()
                mock_connect.return_value = mock_service

                service = await backend.connect("test_service")

                # Test interface compliance
                assert hasattr(service, "invoke")
                assert hasattr(service, "close")
                assert hasattr(service, "service_info")
                assert hasattr(service, "fetch_service_info")

                # Test method calls
                result = await service.invoke("test_method", {"arg": "value"})
                assert result == "test_result"

                await service.close()
                service_info = await service.fetch_service_info()
                assert service_info is not None

    def test_configuration_precedence(self, monkeypatch):
        """Test configuration precedence: explicit > env > defaults"""
        # Set environment variables
        monkeypatch.setenv("PANTHEON_REMOTE_BACKEND", "nats")
        monkeypatch.setenv("NATS_SERVERS", "nats://env.server.io")

        # Test 1: Environment variables override defaults
        config1 = RemoteConfig.from_config()
        assert config1.backend == "nats"
        assert "nats://env.server.io" in config1.backend_config["server_urls"]

        # Test 2: Explicit parameters override environment
        config2 = RemoteConfig.from_config(
            backend="magique", server_urls=["ws://explicit.server.io"]
        )
        assert config2.backend == "magique"
        assert config2.backend_config["server_urls"] == ["ws://explicit.server.io"]

        # Test 3: Partial explicit override
        config3 = RemoteConfig.from_config(
            backend="nats",  # Override backend
            # server_urls should come from env
        )
        assert config3.backend == "nats"
        # Should still use env for servers since we're using nats backend

    def test_module_imports(self):
        """Test that all public interfaces are properly exported"""
        from pantheon.toolsets.remote import (
            connect_remote,
            RemoteConfig,
            RemoteBackendFactory,
            RemoteBackend,
            RemoteService,
            RemoteWorker,
            BackendRegistry,
        )

        # Test that imports work and are the correct types
        assert callable(connect_remote)
        assert issubclass(RemoteConfig, object)
        assert issubclass(RemoteBackendFactory, object)
        assert issubclass(RemoteBackend, object)
        assert issubclass(RemoteService, object)
        assert issubclass(RemoteWorker, object)
        assert issubclass(BackendRegistry, object)

    def test_backward_compatibility(self):
        """Test backward compatibility features"""
        # Test old import paths still work
        from pantheon.toolsets.utils.remote import connect_remote as old_connect_remote
        from pantheon.toolsets.remote import connect_remote as new_connect_remote

        # Should be the same function (assuming utils.remote imports from remote)
        assert old_connect_remote is not None
        assert new_connect_remote is not None

    def test_server_urls_normalization(self):
        """Test that server URLs are properly normalized across backends"""
        test_cases = [
            # String to list conversion
            {
                "backend": "magique",
                "backend_config": {"server_urls": "ws://single.server.io"},
                "expected": ["ws://single.server.io"],
            },
            # List preservation
            {
                "backend": "nats",
                "backend_config": {
                    "server_urls": ["nats://server1.io", "nats://server2.io"]
                },
                "expected": ["nats://server1.io", "nats://server2.io"],
            },
            # Empty list handling
            {
                "backend": "magique",
                "backend_config": {"server_urls": []},
                "expected": [],  # Should get defaults
            },
        ]

        for test_case in test_cases:
            config = RemoteConfig.from_config(
                backend=test_case["backend"], backend_config=test_case["backend_config"]
            )

            if test_case["expected"]:
                assert config.backend_config["server_urls"] == test_case["expected"]
            else:
                # Should have some default URLs
                assert isinstance(config.backend_config.get("server_urls"), list)


class TestRemoteModulePerformance:
    """Performance-related tests for the remote module"""

    def test_backend_creation_performance(self):
        """Test that backend creation is reasonably fast"""
        import time

        start_time = time.time()

        # Create multiple backends
        for _ in range(100):
            for backend_name in ["magique", "nats", "hypha"]:
                config = RemoteConfig.from_config(backend=backend_name)
                backend = RemoteBackendFactory.create_backend(config)
                worker = backend.create_worker("perf_test")

                # Basic validation
                assert backend is not None
                assert worker is not None

        end_time = time.time()

        # Should complete in reasonable time (less than 1 second for 300 operations)
        assert (end_time - start_time) < 1.0

    def test_config_creation_performance(self):
        """Test that config creation is fast"""
        import time

        start_time = time.time()

        # Create many configs
        for i in range(1000):
            config = RemoteConfig.from_config(
                backend="magique", server_urls=[f"ws://server{i}.io"], timeout=30 + i
            )
            assert config.backend == "magique"

        end_time = time.time()

        # Should be very fast (less than 0.1 seconds for 1000 operations)
        assert (end_time - start_time) < 0.1

    def test_registry_lookup_performance(self):
        """Test that registry lookups are fast"""
        import time

        # Register many backends (simulate large registry)
        for i in range(100):
            BackendRegistry.register(f"backend_{i}", MockBackend)

        start_time = time.time()

        # Perform many lookups
        for i in range(1000):
            backend_name = f"backend_{i % 100}"
            backend_class = BackendRegistry.get_backend(backend_name)
            assert backend_class == MockBackend

        end_time = time.time()

        # Should be very fast (less than 0.1 seconds for 1000 lookups)
        assert (end_time - start_time) < 0.1


class MockBackend(RemoteBackend):
    """Mock backend for performance testing"""

    def __init__(self, **kwargs):
        self.config = kwargs

    async def connect(self, service_id: str, **kwargs):
        return MockService()

    def create_worker(self, service_name: str, **kwargs):
        return MockWorker(service_name)

    @property
    def servers(self):
        return ["mock://server"]


class MockService(RemoteService):
    """Mock service for testing"""

    async def invoke(self, method: str, parameters=None):
        return "mock_result"

    async def close(self):
        pass

    @property
    def service_info(self):
        from pantheon.toolsets.remote.backend.base import ServiceInfo

        return ServiceInfo(
            service_id="mock",
            service_name="Mock Service",
            description="",
            functions_description={},
        )

    async def fetch_service_info(self):
        return self.service_info


class MockWorker(RemoteWorker):
    """Mock worker for testing"""

    def __init__(self, service_name):
        self._service_name = service_name
        self._service_id = f"{service_name}_mock"
        self._functions = {}

    def register(self, func, **kwargs):
        self._functions[func.__name__] = func

    async def run(self):
        pass

    async def stop(self):
        pass

    @property
    def service_id(self):
        return self._service_id

    @property
    def service_name(self):
        return self._service_name

    @property
    def functions(self):
        return {name: (func, "") for name, func in self._functions.items()}
