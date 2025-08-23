import pytest
import os
from pantheon.toolsets.remote.factory import RemoteConfig, RemoteBackendFactory
from pantheon.toolsets.remote.backend.registry import BackendRegistry
from pantheon.toolsets.remote.backend.magique import MagiqueBackend
from pantheon.toolsets.remote.backend.nats import NATSBackend


class TestRemoteConfig:
    """Test RemoteConfig functionality"""

    def test_default_config(self):
        """Test default configuration"""
        config = RemoteConfig()
        assert config.backend == "magique"
        assert isinstance(config.backend_config, dict)

    def test_from_config_magique(self):
        """Test creating config for magique backend"""
        config = RemoteConfig.from_config(backend="magique")
        assert config.backend == "magique"
        assert "server_urls" in config.backend_config

    def test_from_config_nats(self):
        """Test creating config for NATS backend"""
        config = RemoteConfig.from_config(backend="nats")
        assert config.backend == "nats"
        assert "server_urls" in config.backend_config
        assert config.backend_config["server_urls"] == ["nats://localhost:4222"]

    def test_from_config_nats_with_env(self, monkeypatch):
        """Test NATS config with environment variable"""
        monkeypatch.setenv("NATS_SERVERS", "nats://demo.nats.io|nats://backup.nats.io")
        config = RemoteConfig.from_config(backend="nats")
        assert config.backend == "nats"
        assert config.backend_config["server_urls"] == [
            "nats://demo.nats.io",
            "nats://backup.nats.io",
        ]

    def test_from_config_hypha(self):
        """Test creating config for hypha backend"""
        config = RemoteConfig.from_config(backend="hypha")
        assert config.backend == "hypha"
        assert "server_url" in config.backend_config
        assert config.backend_config["server_url"] == "https://ai.imjoy.io"

    def test_from_config_hypha_with_env(self, monkeypatch):
        """Test hypha config with environment variables"""
        monkeypatch.setenv("HYPHA_SERVER_URL", "https://custom.hypha.io")
        monkeypatch.setenv("HYPHA_WORKSPACE", "test-workspace")
        monkeypatch.setenv("HYPHA_TOKEN", "test-token")
        
        config = RemoteConfig.from_config(backend="hypha")
        assert config.backend == "hypha"
        assert config.backend_config["server_url"] == "https://custom.hypha.io"
        assert config.backend_config["workspace"] == "test-workspace"
        assert config.backend_config["token"] == "test-token"

    def test_from_config_with_kwargs(self):
        """Test config creation with additional kwargs"""
        config = RemoteConfig.from_config(
            backend="nats", custom_param="test_value", timeout=30
        )
        assert config.backend == "nats"
        assert config.backend_config["custom_param"] == "test_value"
        assert config.backend_config["timeout"] == 30

    def test_from_config_backend_from_env(self, monkeypatch):
        """Test backend selection from environment"""
        monkeypatch.setenv("PANTHEON_REMOTE_BACKEND", "nats")
        config = RemoteConfig.from_config()
        assert config.backend == "nats"

    def test_string_to_list_conversion(self):
        """Test conversion of string server_urls to list"""
        config = RemoteConfig.from_config(
            backend="nats", backend_config={"server_urls": "nats://single.server"}
        )
        assert config.backend_config["server_urls"] == ["nats://single.server"]

    def test_from_env_backward_compatibility(self):
        """Test from_env method for backward compatibility"""
        config = RemoteConfig.from_env()
        assert config.backend == "magique"  # Default


class TestRemoteBackendFactory:
    """Test RemoteBackendFactory functionality"""

    def test_backend_registration(self):
        """Test that backends are properly registered"""
        # Ensure factory has registered backends
        RemoteBackendFactory.register_backends()
        
        assert BackendRegistry.is_registered("magique")
        assert BackendRegistry.is_registered("nats")
        assert BackendRegistry.is_registered("hypha")

    def test_create_magique_backend(self):
        """Test creating magique backend"""
        config = RemoteConfig.from_config(backend="magique")
        backend = RemoteBackendFactory.create_backend(config)
        
        assert isinstance(backend, MagiqueBackend)
        assert hasattr(backend, "servers")
        assert hasattr(backend, "connect")
        assert hasattr(backend, "create_worker")

    def test_create_nats_backend(self):
        """Test creating NATS backend"""
        config = RemoteConfig.from_config(backend="nats")
        backend = RemoteBackendFactory.create_backend(config)
        
        assert isinstance(backend, NATSBackend)
        assert hasattr(backend, "servers")
        assert hasattr(backend, "connect")
        assert hasattr(backend, "create_worker")
        assert backend.servers == ["nats://localhost:4222"]

    def test_create_hypha_backend(self):
        """Test creating hypha backend"""
        config = RemoteConfig.from_config(backend="hypha")
        backend = RemoteBackendFactory.create_backend(config)
        
        assert backend.__class__.__name__ == "HyphaBackend"
        assert hasattr(backend, "servers")
        assert hasattr(backend, "connect")
        assert hasattr(backend, "create_worker")
        assert backend.servers == ["https://ai.imjoy.io"]

    def test_create_backend_with_none_config(self):
        """Test creating backend with None config (should use defaults)"""
        backend = RemoteBackendFactory.create_backend(None)
        assert isinstance(backend, MagiqueBackend)

    def test_create_backend_with_custom_config(self):
        """Test creating backend with custom configuration"""
        config = RemoteConfig(
            backend="nats",
            backend_config={"server_urls": ["nats://demo.nats.io"], "timeout": 60},
        )
        backend = RemoteBackendFactory.create_backend(config)
        
        assert isinstance(backend, NATSBackend)
        assert backend.servers == ["nats://demo.nats.io"]

    def test_invalid_backend_raises_error(self):
        """Test that invalid backend raises appropriate error"""
        config = RemoteConfig(backend="invalid_backend", backend_config={})
        
        with pytest.raises(ValueError, match="Backend 'invalid_backend' not registered"):
            RemoteBackendFactory.create_backend(config)


class TestBackendInterfaces:
    """Test that all backends implement required interfaces correctly"""

    @pytest.mark.parametrize("backend_name", ["magique", "nats", "hypha"])
    def test_backend_interface_compliance(self, backend_name):
        """Test that backends implement required interface methods"""
        config = RemoteConfig.from_config(backend=backend_name)
        backend = RemoteBackendFactory.create_backend(config)

        # Test required properties
        assert hasattr(backend, "servers")
        assert isinstance(backend.servers, list)

        # Test required methods
        assert hasattr(backend, "connect")
        assert hasattr(backend, "create_worker")

        # Test method signatures (basic check)
        import inspect
        
        connect_sig = inspect.signature(backend.connect)
        assert "service_id" in connect_sig.parameters
        
        create_worker_sig = inspect.signature(backend.create_worker)
        assert "service_name" in create_worker_sig.parameters

    @pytest.mark.parametrize("backend_name", ["magique", "nats", "hypha"])
    def test_worker_interface_compliance(self, backend_name):
        """Test that workers implement required interface methods"""
        config = RemoteConfig.from_config(backend=backend_name)
        backend = RemoteBackendFactory.create_backend(config)
        worker = backend.create_worker("test_service")

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

    def test_worker_function_registration(self):
        """Test function registration across different backends"""
        def test_func(x: int) -> int:
            """Test function"""
            return x * 2

        for backend_name in ["magique", "nats", "hypha"]:
            config = RemoteConfig.from_config(backend=backend_name)
            backend = RemoteBackendFactory.create_backend(config)
            worker = backend.create_worker("test_service")

            # Initially no functions
            assert len(worker.functions) == 0

            # Register function
            worker.register(test_func)
            assert len(worker.functions) == 1
            assert "test_func" in worker.functions

            # Check function tuple format
            func_info = worker.functions["test_func"]
            assert isinstance(func_info, tuple)
            assert len(func_info) == 2
            assert callable(func_info[0])  # Function
            assert isinstance(func_info[1], str)  # Description


class TestIntegrationScenarios:
    """Test integration scenarios and edge cases"""

    def test_config_round_trip(self):
        """Test config creation and backend instantiation round trip"""
        # Test with various configurations
        configs = [
            {"backend": "magique"},
            {"backend": "nats", "server_urls": ["nats://demo.nats.io"]},
            {"backend": "hypha", "server_url": "https://ai.imjoy.io"},
        ]

        for config_data in configs:
            backend_name = config_data.pop("backend")
            config = RemoteConfig.from_config(backend=backend_name, **config_data)
            backend = RemoteBackendFactory.create_backend(config)
            worker = backend.create_worker("test_service")

            assert backend is not None
            assert worker is not None
            assert worker.service_name == "test_service"

    def test_multiple_workers_same_backend(self):
        """Test creating multiple workers from same backend"""
        config = RemoteConfig.from_config(backend="magique")
        backend = RemoteBackendFactory.create_backend(config)

        workers = []
        for i in range(3):
            worker = backend.create_worker(f"service_{i}")
            workers.append(worker)

        # Each worker should have unique service ID
        service_ids = [w.service_id for w in workers]
        assert len(set(service_ids)) == 3

        # But share the same backend
        for worker in workers:
            assert hasattr(worker, "service_id")
            assert hasattr(worker, "service_name")

    def test_environment_variable_precedence(self, monkeypatch):
        """Test environment variable precedence over defaults"""
        # Set environment variables
        monkeypatch.setenv("PANTHEON_REMOTE_BACKEND", "nats")
        monkeypatch.setenv("NATS_SERVERS", "nats://custom.nats.io")

        # Should use env vars
        config = RemoteConfig.from_config()
        assert config.backend == "nats"
        assert "nats://custom.nats.io" in config.backend_config["server_urls"]

        # Explicit params should override env vars
        config = RemoteConfig.from_config(backend="magique")
        assert config.backend == "magique"