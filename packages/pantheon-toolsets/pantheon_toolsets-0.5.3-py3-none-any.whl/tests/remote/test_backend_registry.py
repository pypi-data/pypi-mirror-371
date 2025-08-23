import pytest
from pantheon.toolsets.remote.backend.registry import BackendRegistry
from pantheon.toolsets.remote.backend.base import RemoteBackend, RemoteService, RemoteWorker


class MockBackend(RemoteBackend):
    """Mock backend for testing"""
    
    def __init__(self, **kwargs):
        self.config = kwargs
    
    async def connect(self, service_id: str, **kwargs) -> RemoteService:
        pass
    
    def create_worker(self, service_name: str, **kwargs) -> RemoteWorker:
        pass
    
    @property
    def servers(self) -> list[str]:
        return ["mock://server"]


class AnotherMockBackend(RemoteBackend):
    """Another mock backend for testing"""
    
    async def connect(self, service_id: str, **kwargs) -> RemoteService:
        pass
    
    def create_worker(self, service_name: str, **kwargs) -> RemoteWorker:
        pass
    
    @property
    def servers(self) -> list[str]:
        return ["another://server"]


class TestBackendRegistry:
    """Test BackendRegistry functionality"""
    
    def setup_method(self):
        """Clear registry before each test"""
        BackendRegistry._backends.clear()
    
    def teardown_method(self):
        """Clean up after each test"""
        BackendRegistry._backends.clear()

    def test_register_backend(self):
        """Test registering a new backend"""
        BackendRegistry.register("mock", MockBackend)
        
        assert "mock" in BackendRegistry._backends
        assert BackendRegistry._backends["mock"] == MockBackend

    def test_register_backend_overwrite(self):
        """Test that registering overwrites existing backend"""
        BackendRegistry.register("test", MockBackend)
        BackendRegistry.register("test", AnotherMockBackend)
        
        assert BackendRegistry._backends["test"] == AnotherMockBackend

    def test_get_backend_success(self):
        """Test getting a registered backend"""
        BackendRegistry.register("mock", MockBackend)
        
        backend_class = BackendRegistry.get_backend("mock")
        assert backend_class == MockBackend

    def test_get_backend_not_found(self):
        """Test getting a non-existent backend raises error"""
        with pytest.raises(ValueError, match="Backend 'nonexistent' not registered"):
            BackendRegistry.get_backend("nonexistent")

    def test_is_registered_true(self):
        """Test is_registered returns True for registered backend"""
        BackendRegistry.register("mock", MockBackend)
        
        assert BackendRegistry.is_registered("mock") is True

    def test_is_registered_false(self):
        """Test is_registered returns False for unregistered backend"""
        assert BackendRegistry.is_registered("nonexistent") is False

    def test_list_backends_empty(self):
        """Test list_backends with empty registry"""
        backends = BackendRegistry.list_backends()
        assert backends == []

    def test_list_backends_with_entries(self):
        """Test list_backends with registered backends"""
        BackendRegistry.register("mock1", MockBackend)
        BackendRegistry.register("mock2", AnotherMockBackend)
        
        backends = BackendRegistry.list_backends()
        assert set(backends) == {"mock1", "mock2"}

    def test_unregister_backend(self):
        """Test unregistering a backend"""
        BackendRegistry.register("mock", MockBackend)
        assert BackendRegistry.is_registered("mock")
        
        BackendRegistry.unregister("mock")
        assert not BackendRegistry.is_registered("mock")

    def test_unregister_nonexistent_backend(self):
        """Test unregistering a non-existent backend"""
        # Should not raise an error
        BackendRegistry.unregister("nonexistent")

    def test_clear_registry(self):
        """Test clearing the entire registry"""
        BackendRegistry.register("mock1", MockBackend)
        BackendRegistry.register("mock2", AnotherMockBackend)
        
        assert len(BackendRegistry.list_backends()) == 2
        
        BackendRegistry.clear()
        assert len(BackendRegistry.list_backends()) == 0

    def test_backend_instantiation(self):
        """Test that retrieved backend can be instantiated"""
        BackendRegistry.register("mock", MockBackend)
        
        backend_class = BackendRegistry.get_backend("mock")
        backend = backend_class(param1="value1", param2="value2")
        
        assert isinstance(backend, MockBackend)
        assert backend.config == {"param1": "value1", "param2": "value2"}
        assert backend.servers == ["mock://server"]

    def test_registry_isolation(self):
        """Test that registry operations don't interfere with each other"""
        # Register in one test scope
        BackendRegistry.register("isolated1", MockBackend)
        assert BackendRegistry.is_registered("isolated1")
        
        # Modify registry
        BackendRegistry.register("isolated2", AnotherMockBackend)
        assert BackendRegistry.is_registered("isolated2")
        
        # Original registration should still exist
        assert BackendRegistry.is_registered("isolated1")
        
        # Both should be in the list
        backends = BackendRegistry.list_backends()
        assert "isolated1" in backends
        assert "isolated2" in backends

    def test_case_sensitive_backend_names(self):
        """Test that backend names are case-sensitive"""
        BackendRegistry.register("Mock", MockBackend)
        BackendRegistry.register("mock", AnotherMockBackend)
        
        assert BackendRegistry.get_backend("Mock") == MockBackend
        assert BackendRegistry.get_backend("mock") == AnotherMockBackend
        assert not BackendRegistry.is_registered("MOCK")

    def test_invalid_backend_class(self):
        """Test registering invalid backend class"""
        class InvalidBackend:
            """Not a RemoteBackend"""
            pass
        
        # Registry doesn't validate at registration time
        # But should be caught when trying to use
        BackendRegistry.register("invalid", InvalidBackend)
        assert BackendRegistry.is_registered("invalid")
        
        # The validation would happen at instantiation time
        backend_class = BackendRegistry.get_backend("invalid")
        assert backend_class == InvalidBackend

    def test_registry_thread_safety_basic(self):
        """Basic test for registry operations (not full thread safety test)"""
        import threading
        
        def register_backend(name, backend_class):
            BackendRegistry.register(name, backend_class)
        
        def get_backend(name):
            try:
                return BackendRegistry.get_backend(name)
            except ValueError:
                return None
        
        # Start multiple threads
        threads = []
        for i in range(5):
            t1 = threading.Thread(target=register_backend, args=(f"thread{i}", MockBackend))
            t2 = threading.Thread(target=get_backend, args=(f"thread{i}",))
            threads.extend([t1, t2])
        
        for thread in threads:
            thread.start()
        
        for thread in threads:
            thread.join()
        
        # Check that some registrations succeeded
        backends = BackendRegistry.list_backends()
        assert len(backends) > 0


class TestBackendRegistryIntegration:
    """Integration tests for BackendRegistry with actual backend classes"""
    
    def setup_method(self):
        """Clear registry before each test"""
        BackendRegistry._backends.clear()
    
    def teardown_method(self):
        """Clean up after each test"""
        BackendRegistry._backends.clear()

    def test_register_actual_backends(self):
        """Test registering actual backend implementations"""
        from pantheon.toolsets.remote.backend.magique import MagiqueBackend
        from pantheon.toolsets.remote.backend.nats import NATSBackend
        
        BackendRegistry.register("magique", MagiqueBackend)
        BackendRegistry.register("nats", NATSBackend)
        
        assert BackendRegistry.is_registered("magique")
        assert BackendRegistry.is_registered("nats")
        
        # Test instantiation
        magique_class = BackendRegistry.get_backend("magique")
        nats_class = BackendRegistry.get_backend("nats")
        
        magique_backend = magique_class(server_urls=["ws://test.com"])
        nats_backend = nats_class(server_urls=["nats://test.com"])
        
        assert isinstance(magique_backend, MagiqueBackend)
        assert isinstance(nats_backend, NATSBackend)

    def test_factory_integration(self):
        """Test registry integration with factory pattern"""
        from pantheon.toolsets.remote.factory import RemoteBackendFactory
        
        # Factory should have auto-registered backends
        RemoteBackendFactory.register_backends()
        
        assert BackendRegistry.is_registered("magique")
        assert BackendRegistry.is_registered("nats")
        assert BackendRegistry.is_registered("hypha")

    def test_backend_interface_compliance(self):
        """Test that all registered backends implement required interface"""
        from pantheon.toolsets.remote.factory import RemoteBackendFactory
        
        RemoteBackendFactory.register_backends()
        
        for backend_name in BackendRegistry.list_backends():
            backend_class = BackendRegistry.get_backend(backend_name)
            
            # Check that it's a subclass of RemoteBackend
            assert issubclass(backend_class, RemoteBackend)
            
            # Check required methods exist
            assert hasattr(backend_class, 'connect')
            assert hasattr(backend_class, 'create_worker')
            assert hasattr(backend_class, 'servers')

    def test_registry_state_consistency(self):
        """Test that registry state remains consistent across operations"""
        from pantheon.toolsets.remote.backend.magique import MagiqueBackend
        from pantheon.toolsets.remote.backend.nats import NATSBackend
        
        # Initial state
        assert len(BackendRegistry.list_backends()) == 0
        
        # Register backends
        BackendRegistry.register("magique", MagiqueBackend)
        assert len(BackendRegistry.list_backends()) == 1
        assert BackendRegistry.is_registered("magique")
        
        BackendRegistry.register("nats", NATSBackend)
        assert len(BackendRegistry.list_backends()) == 2
        assert BackendRegistry.is_registered("nats")
        
        # Unregister one
        BackendRegistry.unregister("magique")
        assert len(BackendRegistry.list_backends()) == 1
        assert not BackendRegistry.is_registered("magique")
        assert BackendRegistry.is_registered("nats")
        
        # Clear all
        BackendRegistry.clear()
        assert len(BackendRegistry.list_backends()) == 0
        assert not BackendRegistry.is_registered("nats")