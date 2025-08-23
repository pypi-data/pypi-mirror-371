"""
Simple backend tests focusing on core functionality without complex mocking.
"""

import pytest
from pantheon.toolsets.remote.factory import RemoteConfig, RemoteBackendFactory
from pantheon.toolsets.remote.backend.registry import BackendRegistry
from pantheon.toolsets.remote.backend.base import RemoteBackend, RemoteService, RemoteWorker


class TestBackendBasics:
    """Test basic backend functionality"""

    def test_all_backends_registered(self):
        """Test that standard backends are registered"""
        expected_backends = {"magique", "nats", "hypha"}
        registered = set(BackendRegistry.list_backends())
        
        assert expected_backends.issubset(registered)

    def test_backend_creation_from_config(self):
        """Test creating backends from different configs"""
        configs = [
            {"backend": "magique"},
            {"backend": "nats", "server_urls": ["nats://demo.nats.io"]},
            {"backend": "hypha", "server_url": "https://ai.imjoy.io"},
        ]
        
        for config_data in configs:
            backend_name = config_data["backend"]
            config = RemoteConfig.from_config(**config_data)
            backend = RemoteBackendFactory.create_backend(config)
            
            assert isinstance(backend, RemoteBackend)
            assert hasattr(backend, 'connect')
            assert hasattr(backend, 'create_worker')
            assert hasattr(backend, 'servers')
            assert isinstance(backend.servers, list)

    def test_worker_creation_consistency(self):
        """Test that all backends create workers consistently"""
        backend_names = ["magique", "nats", "hypha"]
        
        for backend_name in backend_names:
            config = RemoteConfig.from_config(backend=backend_name)
            backend = RemoteBackendFactory.create_backend(config)
            worker = backend.create_worker(f"test_{backend_name}")
            
            # Test worker interface
            assert isinstance(worker, RemoteWorker)
            assert worker.service_name == f"test_{backend_name}"
            assert isinstance(worker.service_id, str)
            assert hasattr(worker, 'functions')
            assert hasattr(worker, 'register')
            assert callable(worker.register)
            assert hasattr(worker, 'run')
            assert hasattr(worker, 'stop')

    def test_function_registration(self):
        """Test function registration across backends"""
        def test_function(x: int) -> int:
            """Test function docstring"""
            return x * 2
        
        backend_names = ["magique", "nats", "hypha"]
        
        for backend_name in backend_names:
            config = RemoteConfig.from_config(backend=backend_name)
            backend = RemoteBackendFactory.create_backend(config)
            worker = backend.create_worker("func_test")
            
            # Initially no functions
            assert len(worker.functions) == 0
            
            # Register function
            worker.register(test_function)
            
            # Should have one function
            assert len(worker.functions) == 1
            assert "test_function" in worker.functions
            
            # Test function info format (function, description)
            func_info = worker.functions["test_function"]
            assert isinstance(func_info, tuple)
            assert len(func_info) == 2
            assert func_info[0] == test_function
            assert isinstance(func_info[1], str)


class TestConfigurationHandling:
    """Test configuration creation and validation"""

    def test_default_config(self):
        """Test default configuration"""
        config = RemoteConfig()
        assert config.backend == "magique"
        assert isinstance(config.backend_config, dict)

    def test_config_from_parameters(self):
        """Test config creation from parameters"""
        config = RemoteConfig.from_config(
            backend="nats",
            server_urls=["nats://demo.nats.io"],
            timeout=30
        )
        
        assert config.backend == "nats"
        assert config.backend_config["server_urls"] == ["nats://demo.nats.io"]
        assert config.backend_config["timeout"] == 30

    def test_string_to_list_conversion(self):
        """Test that string server_urls get converted to list"""
        config = RemoteConfig.from_config(
            backend="nats",
            backend_config={"server_urls": "nats://single.server"}
        )
        
        assert config.backend_config["server_urls"] == ["nats://single.server"]

    def test_hypha_specific_config(self):
        """Test Hypha-specific configuration"""
        config = RemoteConfig.from_config(
            backend="hypha",
            server_url="https://custom.hypha.io",
            workspace="test_workspace",
            token="test_token"
        )
        
        assert config.backend == "hypha"
        assert config.backend_config["server_url"] == "https://custom.hypha.io"
        assert config.backend_config["workspace"] == "test_workspace"
        assert config.backend_config["token"] == "test_token"

    def test_environment_config(self, monkeypatch):
        """Test configuration from environment variables"""
        monkeypatch.setenv("PANTHEON_REMOTE_BACKEND", "nats")
        monkeypatch.setenv("NATS_SERVERS", "nats://env.server.io")
        
        config = RemoteConfig.from_config()
        assert config.backend == "nats"
        assert "nats://env.server.io" in config.backend_config["server_urls"]


class TestBackendSpecificFeatures:
    """Test backend-specific features"""

    def test_magique_backend_servers(self):
        """Test Magique backend server configuration"""
        config = RemoteConfig.from_config(
            backend="magique",
            server_urls=["ws://server1.com", "ws://server2.com"]
        )
        backend = RemoteBackendFactory.create_backend(config)
        
        assert backend.servers == ["ws://server1.com", "ws://server2.com"]

    def test_nats_backend_servers(self):
        """Test NATS backend server configuration"""
        config = RemoteConfig.from_config(
            backend="nats",
            server_urls=["nats://demo.nats.io", "nats://backup.nats.io"]
        )
        backend = RemoteBackendFactory.create_backend(config)
        
        assert backend.servers == ["nats://demo.nats.io", "nats://backup.nats.io"]

    def test_hypha_backend_servers(self):
        """Test Hypha backend server configuration"""
        config = RemoteConfig.from_config(
            backend="hypha",
            server_url="https://custom.hypha.io"
        )
        backend = RemoteBackendFactory.create_backend(config)
        
        assert backend.servers == ["https://custom.hypha.io"]

    def test_nats_worker_service_id_format(self):
        """Test NATS worker service ID format"""
        config = RemoteConfig.from_config(backend="nats")
        backend = RemoteBackendFactory.create_backend(config)
        worker = backend.create_worker("my_service")
        
        assert worker.service_name == "my_service"
        assert "my_service_" in worker.service_id
        assert len(worker.service_id) > len("my_service_")  # Should have unique suffix

    def test_worker_properties_consistency(self):
        """Test that worker properties are consistent across backends"""
        for backend_name in ["magique", "nats", "hypha"]:
            config = RemoteConfig.from_config(backend=backend_name)
            backend = RemoteBackendFactory.create_backend(config)
            worker = backend.create_worker("prop_test")
            
            # All workers should have these properties
            assert hasattr(worker, 'service_id')
            assert hasattr(worker, 'service_name')
            assert hasattr(worker, 'functions')
            
            # Properties should return expected types
            assert isinstance(worker.service_id, str)
            assert isinstance(worker.service_name, str)
            assert isinstance(worker.functions, dict)
            
            assert worker.service_name == "prop_test"


class TestErrorHandling:
    """Test error handling and edge cases"""

    def test_invalid_backend_name(self):
        """Test error handling for invalid backend name"""
        with pytest.raises(ValueError, match="Backend 'invalid_backend' not registered"):
            config = RemoteConfig(backend="invalid_backend", backend_config={})
            RemoteBackendFactory.create_backend(config)

    def test_empty_config(self):
        """Test handling of empty configurations"""
        # Should use defaults
        config = RemoteConfig.from_config()
        backend = RemoteBackendFactory.create_backend(config)
        
        assert backend is not None
        assert hasattr(backend, 'servers')

    def test_worker_multiple_function_registration(self):
        """Test registering multiple functions to worker"""
        config = RemoteConfig.from_config(backend="magique")
        backend = RemoteBackendFactory.create_backend(config)
        worker = backend.create_worker("multi_func_test")
        
        def func1():
            return 1
            
        def func2():
            return 2
            
        def func3():
            return 3
        
        worker.register(func1)
        assert len(worker.functions) == 1
        
        worker.register(func2)
        assert len(worker.functions) == 2
        
        worker.register(func3)
        assert len(worker.functions) == 3
        
        assert "func1" in worker.functions
        assert "func2" in worker.functions
        assert "func3" in worker.functions

    def test_config_parameter_merging(self):
        """Test that config parameters are properly merged"""
        config = RemoteConfig.from_config(
            backend="nats",
            server_urls=["nats://demo.nats.io"],
            custom_param1="value1",
            custom_param2=42,
            backend_config={"custom_param3": "value3"}
        )
        
        assert config.backend_config["server_urls"] == ["nats://demo.nats.io"]
        assert config.backend_config["custom_param1"] == "value1"
        assert config.backend_config["custom_param2"] == 42
        assert config.backend_config["custom_param3"] == "value3"


class TestRegistryOperations:
    """Test backend registry operations"""

    def setup_method(self):
        """Setup clean registry state"""
        self.original_backends = BackendRegistry._backends.copy()

    def teardown_method(self):
        """Restore original registry state"""
        BackendRegistry._backends = self.original_backends

    def test_registry_basic_operations(self):
        """Test basic registry operations"""
        # Clear and check empty
        BackendRegistry.clear()
        assert len(BackendRegistry.list_backends()) == 0
        
        # Register test backend
        from pantheon.toolsets.remote.backend.magique import MagiqueBackend
        BackendRegistry.register("test_backend", MagiqueBackend)
        
        assert BackendRegistry.is_registered("test_backend")
        assert "test_backend" in BackendRegistry.list_backends()
        
        # Get backend
        backend_class = BackendRegistry.get_backend("test_backend")
        assert backend_class == MagiqueBackend
        
        # Unregister
        BackendRegistry.unregister("test_backend")
        assert not BackendRegistry.is_registered("test_backend")

    def test_registry_re_registration(self):
        """Test re-registering backends"""
        # Re-register standard backends
        RemoteBackendFactory.register_backends()
        
        expected_backends = {"magique", "nats", "hypha"}
        registered = set(BackendRegistry.list_backends())
        
        assert expected_backends.issubset(registered)
        
        # Should be able to create backends after re-registration
        for backend_name in expected_backends:
            config = RemoteConfig.from_config(backend=backend_name)
            backend = RemoteBackendFactory.create_backend(config)
            assert backend is not None