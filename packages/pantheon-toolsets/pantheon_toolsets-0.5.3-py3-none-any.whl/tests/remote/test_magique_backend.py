import pytest
import asyncio
from unittest.mock import Mock, AsyncMock, patch
from pantheon.toolsets.remote.backend.magique import MagiqueBackend, MagiqueService, MagiqueRemoteWorker
from pantheon.toolsets.remote.backend.base import ServiceInfo


class TestMagiqueBackend:
    """Test MagiqueBackend functionality"""

    def test_backend_initialization(self):
        """Test backend initialization with server URLs"""
        server_urls = ["ws://server1.com", "ws://server2.com"]
        backend = MagiqueBackend(server_urls, timeout=30)
        
        assert backend.server_urls == server_urls
        assert backend.default_kwargs == {"timeout": 30}
        assert backend.servers == server_urls

    def test_servers_property(self):
        """Test servers property returns correct URLs"""
        server_urls = ["ws://demo.magique.io"]
        backend = MagiqueBackend(server_urls)
        assert backend.servers == server_urls

    @pytest.mark.asyncio
    async def test_connect_method(self):
        """Test connect method with mocked magique client"""
        server_urls = ["ws://demo.magique.io"]
        backend = MagiqueBackend(server_urls)

        # Mock the magique client components
        mock_server = AsyncMock()
        mock_service_proxy = Mock()
        mock_service_proxy.service_info = Mock()
        mock_service_proxy.service_info.service_id = "test_service"
        mock_service_proxy.service_info.service_name = "test_service"
        mock_service_proxy.service_info.description = "Test service"
        mock_service_proxy.service_info.functions_description = {}
        
        mock_server.get_service.return_value = mock_service_proxy

        with patch('pantheon.toolsets.remote.backend.magique.connect_to_server', return_value=mock_server):
            service = await backend.connect("test_service", timeout=60)
            
            assert isinstance(service, MagiqueService)
            assert service._service == mock_service_proxy
            
            # Verify connect_to_server was called with correct parameters
            mock_server.get_service.assert_called_once_with("test_service")

    def test_create_worker(self):
        """Test create_worker method"""
        server_urls = ["ws://demo.magique.io"]
        backend = MagiqueBackend(server_urls, timeout=30)

        with patch('pantheon.toolsets.remote.backend.magique.MagiqueWorker') as mock_worker_class:
            mock_worker = Mock()
            mock_worker_class.return_value = mock_worker
            
            worker = backend.create_worker("test_service", custom_param="value")
            
            assert isinstance(worker, MagiqueRemoteWorker)
            assert worker._worker == mock_worker
            
            # Verify MagiqueWorker was created with correct parameters
            expected_kwargs = {
                "service_name": "test_service",
                "server_url": server_urls,
                "need_auth": False,
                "timeout": 30,
                "custom_param": "value"
            }
            mock_worker_class.assert_called_once_with(**expected_kwargs)


class TestMagiqueService:
    """Test MagiqueService functionality"""

    def setup_method(self):
        """Setup mock service proxy for tests"""
        self.mock_service_proxy = Mock()
        self.mock_service_proxy.service_info = Mock()
        self.mock_service_proxy.service_info.service_id = "test_service"
        self.mock_service_proxy.service_info.service_name = "Test Service"
        self.mock_service_proxy.service_info.description = "A test service"
        self.mock_service_proxy.service_info.functions_description = {"test_func": {}}
        
        self.service = MagiqueService(self.mock_service_proxy)

    @pytest.mark.asyncio
    async def test_invoke_with_args(self):
        """Test invoke method with arguments"""
        self.mock_service_proxy.invoke = AsyncMock(return_value="test_result")
        
        result = await self.service.invoke("test_method", {"arg1": "value1"})
        
        assert result == "test_result"
        self.mock_service_proxy.invoke.assert_called_once_with("test_method", {"arg1": "value1"})

    @pytest.mark.asyncio
    async def test_invoke_without_args(self):
        """Test invoke method without arguments"""
        self.mock_service_proxy.invoke = AsyncMock(return_value="no_args_result")
        
        result = await self.service.invoke("test_method")
        
        assert result == "no_args_result"
        self.mock_service_proxy.invoke.assert_called_once_with("test_method")

    @pytest.mark.asyncio
    async def test_invoke_with_none_args(self):
        """Test invoke method with None arguments"""
        self.mock_service_proxy.invoke = AsyncMock(return_value="none_args_result")
        
        result = await self.service.invoke("test_method", None)
        
        assert result == "none_args_result"
        self.mock_service_proxy.invoke.assert_called_once_with("test_method")

    @pytest.mark.asyncio
    async def test_close(self):
        """Test close method (should not raise)"""
        await self.service.close()  # Should complete without error

    def test_service_info_property(self):
        """Test service_info property"""
        service_info = self.service.service_info
        
        assert isinstance(service_info, ServiceInfo)
        assert service_info.service_id == "test_service"
        assert service_info.service_name == "Test Service"
        assert service_info.description == "A test service"
        assert service_info.functions_description == {"test_func": {}}

    @pytest.mark.asyncio
    async def test_fetch_service_info(self):
        """Test fetch_service_info method"""
        service_info = await self.service.fetch_service_info()
        
        assert isinstance(service_info, ServiceInfo)
        assert service_info.service_id == "test_service"


class TestMagiqueRemoteWorker:
    """Test MagiqueRemoteWorker functionality"""

    def setup_method(self):
        """Setup mock MagiqueWorker for tests"""
        self.mock_magique_worker = Mock()
        self.mock_magique_worker.service_id = "worker_123"
        self.mock_magique_worker.service_name = "test_worker"
        self.mock_magique_worker.servers = ["ws://demo.magique.io"]
        self.mock_magique_worker.functions = {}
        
        self.worker = MagiqueRemoteWorker(self.mock_magique_worker)

    def test_worker_properties(self):
        """Test worker properties"""
        assert self.worker.service_id == "worker_123"
        assert self.worker.service_name == "test_worker"
        assert self.worker.servers == ["ws://demo.magique.io"]
        assert self.worker.functions == {}

    def test_register_function(self):
        """Test function registration"""
        def test_func():
            """Test function"""
            return "test"
        
        self.worker.register(test_func, param1="value1")
        
        self.mock_magique_worker.register.assert_called_once_with(test_func, param1="value1")

    @pytest.mark.asyncio
    async def test_run(self):
        """Test worker run method"""
        self.mock_magique_worker.run = AsyncMock(return_value=None)
        
        result = await self.worker.run()
        
        self.mock_magique_worker.run.assert_called_once()
        assert result is None

    @pytest.mark.asyncio
    async def test_stop(self):
        """Test worker stop method (should not raise)"""
        await self.worker.stop()  # Should complete without error

    def test_functions_property_with_data(self):
        """Test functions property when worker has functions"""
        def test_func(x):
            """Doubles the input"""
            return x * 2
        
        def triple_func(x):
            return x * 3
        
        self.mock_magique_worker.functions = {
            "double": (test_func, "Doubles the input"),
            "triple": (triple_func, "Triples the input")
        }
        
        functions = self.worker.functions
        assert isinstance(functions, dict)
        assert "double" in functions
        assert "triple" in functions


class TestMagiqueIntegration:
    """Integration tests for Magique backend components"""

    def test_backend_to_worker_flow(self):
        """Test complete flow from backend to worker creation"""
        server_urls = ["ws://demo.magique.io"]
        backend = MagiqueBackend(server_urls, timeout=30)

        with patch('pantheon.toolsets.remote.backend.magique.MagiqueWorker') as mock_worker_class:
            mock_worker = Mock()
            mock_worker.service_id = "integration_test"
            mock_worker.service_name = "integration_service"
            mock_worker.servers = server_urls
            mock_worker.functions = {}
            mock_worker_class.return_value = mock_worker
            
            worker = backend.create_worker("integration_service")
            
            assert isinstance(worker, MagiqueRemoteWorker)
            assert worker.service_id == "integration_test"
            assert worker.service_name == "integration_service"
            assert worker.servers == server_urls

    @pytest.mark.asyncio
    async def test_service_invocation_flow(self):
        """Test complete service invocation flow"""
        # Create mock service proxy
        mock_service_proxy = Mock()
        mock_service_proxy.invoke = AsyncMock(return_value={"result": "success"})
        mock_service_proxy.service_info = Mock()
        mock_service_proxy.service_info.service_id = "flow_test"
        mock_service_proxy.service_info.service_name = "Flow Test"
        mock_service_proxy.service_info.description = "Test flow"
        mock_service_proxy.service_info.functions_description = {}

        service = MagiqueService(mock_service_proxy)
        
        # Test invocation
        result = await service.invoke("test_method", {"input": "test_data"})
        
        assert result == {"result": "success"}
        mock_service_proxy.invoke.assert_called_once_with("test_method", {"input": "test_data"})

    def test_worker_function_management(self):
        """Test worker function registration and management"""
        mock_worker = Mock()
        mock_worker.service_id = "func_test"
        mock_worker.service_name = "Function Test"
        mock_worker.servers = ["ws://demo.magique.io"]
        mock_worker.functions = {}
        
        worker = MagiqueRemoteWorker(mock_worker)
        
        def test_func1():
            """Function 1"""
            return 1
            
        def test_func2():
            """Function 2"""
            return 2
        
        # Register functions
        worker.register(test_func1)
        worker.register(test_func2, description="Custom description")
        
        assert mock_worker.register.call_count == 2
        
        # Verify calls
        calls = mock_worker.register.call_args_list
        assert calls[0][0][0] == test_func1
        assert calls[1][0][0] == test_func2
        assert calls[1][1]["description"] == "Custom description"

    def test_error_handling_in_components(self):
        """Test error handling in various components"""
        # Test service with failing invoke
        mock_service_proxy = Mock()
        mock_service_proxy.invoke = AsyncMock(side_effect=Exception("Service error"))
        mock_service_proxy.service_info = Mock()
        mock_service_proxy.service_info.service_id = "error_test"
        mock_service_proxy.service_info.service_name = "Error Test"
        mock_service_proxy.service_info.description = ""
        mock_service_proxy.service_info.functions_description = {}
        
        service = MagiqueService(mock_service_proxy)
        
        # Should propagate the exception
        with pytest.raises(Exception, match="Service error"):
            asyncio.run(service.invoke("failing_method"))

    def test_service_info_consistency(self):
        """Test that service info is consistent across methods"""
        mock_service_info = Mock()
        mock_service_info.service_id = "consistency_test"
        mock_service_info.service_name = "Consistency Test Service"
        mock_service_info.description = "Testing consistency"
        mock_service_info.functions_description = {"func1": {}, "func2": {}}
        
        mock_service_proxy = Mock()
        mock_service_proxy.service_info = mock_service_info
        
        service = MagiqueService(mock_service_proxy)
        
        # Test property access
        info1 = service.service_info
        
        # Test fetch method
        info2 = asyncio.run(service.fetch_service_info())
        
        # Should be equivalent
        assert info1.service_id == info2.service_id
        assert info1.service_name == info2.service_name
        assert info1.description == info2.description
        assert info1.functions_description == info2.functions_description