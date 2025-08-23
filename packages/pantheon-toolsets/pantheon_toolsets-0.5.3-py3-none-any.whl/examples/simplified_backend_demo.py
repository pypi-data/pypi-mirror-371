#!/usr/bin/env python3
"""
Example: Simplified Backend Configuration

This example demonstrates the simplified backend configuration,
focusing on the easy 1:1 communication model.
"""

import os
import sys
import asyncio
from pathlib import Path

# Add project root to path
sys.path.insert(0, str(Path(__file__).parent.parent))

from pantheon.toolsets.utils.toolset import ToolSet, tool


class SimpleEchoService(ToolSet):
    """Simple service that works with any backend"""
    
    @tool
    def echo(self, message: str) -> dict:
        """Echo a message back"""
        return {
            "echo": message,
            "backend": self._worker_config.backend,
            "service_id": self.service_id
        }
    
    @tool
    def get_info(self) -> dict:
        """Get service information"""
        return {
            "service_name": self._service_name,
            "service_id": self.service_id,
            "backend": self._worker_config.backend,
            "backend_class": type(self._backend).__name__
        }


async def demo_backends():
    """Demonstrate all backends with simplified configuration"""
    
    print("🚀 Simplified Backend Configuration Demo")
    print("=" * 50)
    
    # Clean environment first
    for key in list(os.environ.keys()):
        if key.startswith('PANTHEON_') or key.startswith('NATS_'):
            del os.environ[key]
    
    print("\n🔹 1. Default Backend (Magique)")
    print("-" * 30)
    service1 = SimpleEchoService("demo-service-1")
    await service1.run_setup()
    print(f"✓ Backend: {service1._worker_config.backend}")
    print(f"✓ Type: {type(service1._backend).__name__}")
    
    print("\n🔹 2. NATS Backend (Simplified 1:1)")
    print("-" * 30)
    os.environ['PANTHEON_REMOTE_BACKEND'] = 'nats'
    os.environ['NATS_SERVERS'] = 'nats://localhost:4222'
    
    service2 = SimpleEchoService("demo-service-2")
    print(f"✓ Backend: {service2._worker_config.backend}")
    print(f"✓ Type: {type(service2._backend).__name__}")
    print(f"✓ Servers: {service2._worker_config.backend_config['server_urls']}")
    print(f"✓ Communication: Direct 1:1 (like Magique)")
    
    print("\n🔹 3. Hypha Backend")
    print("-" * 30)
    os.environ['PANTHEON_REMOTE_BACKEND'] = 'hypha'
    
    service3 = SimpleEchoService("demo-service-3")
    print(f"✓ Backend: {service3._worker_config.backend}")
    print(f"✓ Type: {type(service3._backend).__name__}")
    
    print("\n🔹 4. Override via Parameters")
    print("-" * 30)
    # Override environment with parameters
    custom_params = {
        'backend': 'nats',
        'server_urls': ['nats://custom:4222']
    }
    
    service4 = SimpleEchoService("demo-service-4", worker_params=custom_params)
    print(f"✓ Backend: {service4._worker_config.backend}")
    print(f"✓ Custom Servers: {service4._worker_config.backend_config['server_urls']}")
    
    print("\n" + "=" * 50)
    print("✅ All backends configured successfully!")
    print("\n📋 Summary:")
    print("• Magique: WebSocket-based, simple setup")
    print("• NATS: Message-based, 1:1 communication, optional persistence") 
    print("• Hypha: RPC-based, browser integration")
    print("• All use the same ToolSet API - just change configuration!")
    
    print("\n🔧 Configuration Methods:")
    print("1. Environment variables (PANTHEON_REMOTE_BACKEND, NATS_SERVERS)")
    print("2. worker_params override in ToolSet constructor")
    print("3. Programmatic RemoteConfig creation")
    
    print("\n🎯 Key Benefits:")
    print("• Drop-in replacement - no code changes needed")
    print("• Environment-based switching")
    print("• Simplified configuration (no complex work queue settings)")
    print("• Same 1:1 communication model across all backends")


if __name__ == "__main__":
    asyncio.run(demo_backends())