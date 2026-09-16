import asyncio
from httpx import AsyncClient, ASGITransport
from backend.app.main import app


async def run_tests():
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://testserver") as client:
        # Test root endpoint
        root_res = await client.get("/")
        assert root_res.status_code == 200, f"Expected 200, got {root_res.status_code}"
        root_json = root_res.json()
        assert root_json["name"] == "Employee Support Assistant"
        print("Root endpoint verified:", root_json)

        # Test health endpoint
        health_res = await client.get("/api/v1/health")
        assert health_res.status_code == 200, f"Expected 200, got {health_res.status_code}"
        health_json = health_res.json()
        assert health_json["success"] is True
        assert health_json["data"]["status"] == "healthy"
        assert health_json["data"]["database"] == "connected"
        assert health_json["data"]["db_name"] == "employee_support_assistant"
        print("Health endpoint verified:", health_json)

    print("\nAll backend health & database tests PASSED successfully!")


if __name__ == "__main__":
    asyncio.run(run_tests())
