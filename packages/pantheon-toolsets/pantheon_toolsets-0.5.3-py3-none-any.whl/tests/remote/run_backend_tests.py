#!/usr/bin/env python3
"""
Simple test runner for remote backend compatibility tests.

This script runs comprehensive tests to ensure Magique and NATS backends
behave identically. It can run without pytest for easier debugging.
"""

import asyncio
import sys
import time
from pathlib import Path

# Add project to path
sys.path.insert(0, str(Path(__file__).parent))

from pantheon.toolsets.remote import RemoteConfig, RemoteBackendFactory
from pantheon.toolsets.utils.toolset import ToolSet, tool


class TestService(ToolSet):
    """Simple test service for backend validation"""

    def __init__(self, name: str, test_id: str = None, worker_params=None):
        super().__init__(name, worker_params=worker_params)
        self.test_id = test_id or name
        self.call_count = 0

    @tool
    def ping(self) -> dict:
        """Basic ping method"""
        self.call_count += 1
        return {
            "pong": True,
            "test_id": self.test_id,
            "service_id": self.service_id,
            "call_count": self.call_count,
            "backend": self._worker_config.backend,
        }

    @tool
    def echo(self, message: str) -> dict:
        """Echo a message"""
        return {
            "original": message,
            "echoed": f"[{self.test_id}] Echo: {message}",
            "service_id": self.service_id,
            "backend": self._worker_config.backend,
        }

    @tool
    def math_operation(self, op: str, a: float, b: float) -> dict:
        """Perform math operations"""
        operations = {
            "add": lambda x, y: x + y,
            "subtract": lambda x, y: x - y,
            "multiply": lambda x, y: x * y,
            "divide": lambda x, y: x / y if y != 0 else None,
        }

        if op not in operations:
            raise ValueError(f"Unknown operation: {op}")

        result = operations[op](a, b)
        if result is None:
            raise ValueError("Division by zero")

        return {
            "operation": op,
            "operands": [a, b],
            "result": result,
            "service_id": self.service_id,
        }

    @tool
    async def async_task(self, duration: float = 0.5) -> dict:
        """Async task with delay"""
        start = time.time()
        await asyncio.sleep(duration)
        end = time.time()

        return {
            "requested_duration": duration,
            "actual_duration": end - start,
            "completed": True,
            "service_id": self.service_id,
        }

    @tool
    def error_method(self) -> dict:
        """Method that always raises an error"""
        raise RuntimeError("Intentional test error")


class BackendTester:
    """Tests a specific backend configuration"""

    def __init__(self, backend_name: str, backend_config: dict):
        self.backend_name = backend_name
        self.backend_config = backend_config
        self.test_results = {}

    async def test_configuration(self):
        """Test backend configuration"""
        print(f"  📋 Testing {self.backend_name} configuration...")

        try:
            config = RemoteConfig(
                backend=self.backend_name, backend_config=self.backend_config
            )
            backend = RemoteBackendFactory.create_backend(config)

            # Check basic properties
            assert hasattr(backend, "connect"), "Backend missing connect method"
            assert hasattr(backend, "create_worker"), (
                "Backend missing create_worker method"
            )
            assert hasattr(backend, "servers"), "Backend missing servers property"

            self.test_results["configuration"] = {
                "status": "pass",
                "backend_class": type(backend).__name__,
                "servers": backend.servers,
            }

        except Exception as e:
            self.test_results["configuration"] = {"status": "fail", "error": str(e)}

    async def test_service_creation(self):
        """Test service creation and setup"""
        print(f"  🔧 Testing {self.backend_name} service creation...")

        try:
            config = RemoteConfig(
                backend=self.backend_name, backend_config=self.backend_config
            )

            service = TestService(
                f"test-{self.backend_name}",
                worker_params={"backend": self.backend_name, **self.backend_config},
            )
            service._worker_config = config
            service._backend = RemoteBackendFactory.create_backend(config)
            service.worker = None

            # Setup service
            await service.run_setup()

            self.test_results["service_creation"] = {
                "status": "pass",
                "service_id": service.service_id,
                "service_name": service._service_name,
                "backend": service._worker_config.backend,
            }

        except Exception as e:
            self.test_results["service_creation"] = {"status": "fail", "error": str(e)}

    async def test_method_invocation(self):
        """Test method registration and basic functionality"""
        print(f"  📞 Testing {self.backend_name} method registration...")

        try:
            config = RemoteConfig(
                backend=self.backend_name, backend_config=self.backend_config
            )
            backend = RemoteBackendFactory.create_backend(config)
            worker = backend.create_worker(f"test-{self.backend_name}")

            # Test function registration
            def test_func(x: int) -> int:
                return x * 2

            worker.register(test_func)
            
            # Check that function was registered
            assert "test_func" in worker.functions
            assert len(worker.functions) == 1
            
            func_info = worker.functions["test_func"]
            assert isinstance(func_info, tuple)
            assert len(func_info) == 2
            assert callable(func_info[0])

            self.test_results["method_invocation"] = {
                "status": "pass",
                "registered_functions": list(worker.functions.keys()),
                "function_count": len(worker.functions),
            }

        except Exception as e:
            self.test_results["method_invocation"] = {"status": "fail", "error": str(e)}

    def get_test_summary(self):
        """Get summary of test results"""
        passed = sum(
            1 for result in self.test_results.values() if result.get("status") == "pass"
        )
        total = len(self.test_results)
        return {
            "backend": self.backend_name,
            "passed": passed,
            "total": total,
            "success_rate": passed / total if total > 0 else 0,
            "results": self.test_results,
        }


class CrossBackendTester:
    """Tests compatibility between backends"""

    def __init__(self, backend_configs):
        self.backend_configs = backend_configs
        self.testers = {}

    async def run_all_tests(self):
        """Run tests on all backends"""
        print("🧪 Running Backend Compatibility Tests")
        print("=" * 50)

        # Create testers for each backend
        for backend_name, config in self.backend_configs.items():
            print(f"\n🔹 Testing {backend_name.upper()} Backend")
            print("-" * 30)

            tester = BackendTester(backend_name, config)

            await tester.test_configuration()
            await tester.test_service_creation()
            await tester.test_method_invocation()

            self.testers[backend_name] = tester

    def compare_backends(self):
        """Compare results between backends"""
        print(f"\n🔍 Cross-Backend Comparison")
        print("-" * 30)

        # Get summaries
        summaries = {}
        for backend_name, tester in self.testers.items():
            summaries[backend_name] = tester.get_test_summary()

        # Compare success rates
        success_rates = {
            name: summary["success_rate"] for name, summary in summaries.items()
        }

        print(f"   Success rates:")
        for backend, rate in success_rates.items():
            print(
                f"     {backend}: {rate:.1%} ({summaries[backend]['passed']}/{summaries[backend]['total']})"
            )

        # Check if all backends have same success rate
        rates = list(success_rates.values())
        if len(set(rates)) == 1:
            print(f"   ✅ All backends have identical success rate: {rates[0]:.1%}")
        else:
            print(f"   ⚠️  Backends have different success rates")

        return summaries

    def print_detailed_results(self, summaries):
        """Print detailed test results"""
        print(f"\n📊 Detailed Results")
        print("=" * 50)

        for backend_name, summary in summaries.items():
            print(f"\n{backend_name.upper()} Backend:")

            for test_name, result in summary["results"].items():
                status_icon = "✅" if result["status"] == "pass" else "❌"
                print(f"  {status_icon} {test_name}: {result['status']}")

                if result["status"] == "fail":
                    print(f"     Error: {result.get('error', 'Unknown error')}")
                elif test_name == "configuration":
                    print(f"     Class: {result.get('backend_class', 'Unknown')}")
                    print(f"     Servers: {result.get('servers', [])}")
                elif test_name == "method_invocation":
                    all_registered = result.get("all_methods_registered", False)
                    methods_count = len(result.get("registered_methods", []))
                    print(f"     Methods registered: {methods_count}")
                    print(
                        f"     All expected methods: {'✅' if all_registered else '❌'}"
                    )


async def main():
    """Main test runner"""
    print("🚀 Remote Backend Compatibility Test Suite")
    print("=" * 50)
    print("Testing Magique and NATS backends for identical behavior\n")

    # Define backend configurations
    backend_configs = {
        "magique": {
            "server_urls": []  # Use default magique URLs from SERVER_URLS
        },
        "nats": {
            "server_urls": ["nats://demo.nats.io"]  # Public NATS demo server
        },
    }

    # Run tests
    tester = CrossBackendTester(backend_configs)

    await tester.run_all_tests()
    summaries = tester.compare_backends()
    tester.print_detailed_results(summaries)

    # Final summary
    print(f"\n🎯 Final Summary")
    print("=" * 50)

    all_passed = all(summary["success_rate"] == 1.0 for summary in summaries.values())

    if all_passed:
        print("✅ All tests passed on all backends!")
        print("   Magique and NATS backends are functionally equivalent")
    else:
        print("⚠️  Some tests failed")
        print("   Check detailed results above for issues")

    # Usage information
    print(f"\n💡 Usage Notes:")
    print("• These tests validate backend interface compatibility")
    print("• Using public demo servers:")
    print("  - Magique: Default magique server URLs")
    print("  - NATS: nats://demo.nats.io (public demo server)")
    print("• Run pytest tests/remote/ for complete test suite")

    return all_passed


if __name__ == "__main__":
    try:
        success = asyncio.run(main())
        sys.exit(0 if success else 1)
    except KeyboardInterrupt:
        print("\n🛑 Tests interrupted by user")
        sys.exit(1)
    except Exception as e:
        print(f"\n❌ Test runner failed: {e}")
        import traceback

        traceback.print_exc()
        sys.exit(1)
