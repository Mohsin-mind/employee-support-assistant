import asyncio
import sys
from pathlib import Path
from datetime import date, timedelta

# Ensure repository root is on sys.path
TEST_DIR = Path(__file__).resolve().parent
REPO_ROOT = TEST_DIR.parents[2]
if str(REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(REPO_ROOT))

from httpx import AsyncClient, ASGITransport
from backend.app.main import app
from backend.app.core.helpers import generate_uuid


async def run_phase2_tests():
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://testserver") as client:
        unique_suffix = generate_uuid()[:8]
        test_email = f"john.doe.{unique_suffix}@example.com"

        print("=== 1. Testing Employee Management APIs ===")
        # Create employee
        create_emp_payload = {
            "first_name": "John",
            "last_name": "Doe",
            "email": test_email,
            "department": "Engineering",
            "role": "Software Engineer",
            "is_active": True,
        }
        res = await client.post("/api/v1/employees", json=create_emp_payload)
        assert res.status_code == 201, f"Create employee failed: {res.text}"
        emp_data = res.json()["data"]
        emp_id = emp_data["id"]
        assert emp_data["email"] == test_email
        print(f"Created employee id={emp_id}")

        # Duplicate email conflict test
        dup_res = await client.post("/api/v1/employees", json=create_emp_payload)
        assert dup_res.status_code == 409, f"Expected 409 conflict, got {dup_res.status_code}"
        print("Duplicate email conflict handled correctly (409).")

        # Get employee by ID
        get_res = await client.get(f"/api/v1/employees/{emp_id}")
        assert get_res.status_code == 200
        assert get_res.json()["data"]["id"] == emp_id

        # List employees
        list_res = await client.get("/api/v1/employees?page=1&page_size=10&department=Engineering")
        assert list_res.status_code == 200
        assert list_res.json()["data"]["pagination"]["total_items"] >= 1
        print("List employees verified.")

        # Update employee
        update_res = await client.patch(f"/api/v1/employees/{emp_id}", json={"role": "Senior Software Engineer"})
        assert update_res.status_code == 200
        assert update_res.json()["data"]["role"] == "Senior Software Engineer"
        print("Update employee verified.")

        print("\n=== 2. Testing Leave Management APIs ===")
        # Verify default leave balances were auto-created
        bal_res = await client.get(f"/api/v1/leave/balances/{emp_id}")
        assert bal_res.status_code == 200
        balances = bal_res.json()["data"]
        assert len(balances) >= 3  # annual, sick, casual
        annual_bal = next(b for b in balances if b["leave_type"] == "annual")
        assert annual_bal["allocated_days"] == 20
        assert annual_bal["remaining_days"] == 20
        print(f"Default leave balances verified: {len(balances)} categories initialized.")

        # Apply for leave (3 business days: next Monday to Wednesday)
        today = date.today()
        # Find next Monday
        days_until_monday = (7 - today.weekday()) % 7
        if days_until_monday == 0:
            days_until_monday = 7
        start_date = today + timedelta(days=days_until_monday)
        end_date = start_date + timedelta(days=2)  # Monday to Wednesday = 3 business days

        leave_req_payload = {
            "employee_id": emp_id,
            "leave_type": "annual",
            "start_date": start_date.isoformat(),
            "end_date": end_date.isoformat(),
            "reason": "Family vacation",
        }
        leave_res = await client.post("/api/v1/leave/requests", json=leave_req_payload)
        assert leave_res.status_code == 201, f"Apply leave failed: {leave_res.text}"
        req_data = leave_res.json()["data"]
        req_id = req_data["id"]
        assert req_data["days"] == 3
        assert req_data["status"] == "pending"
        print(f"Applied for leave request id={req_id}, days={req_data['days']}")

        # Overlapping leave conflict test
        overlap_res = await client.post("/api/v1/leave/requests", json=leave_req_payload)
        assert overlap_res.status_code == 409, f"Expected 409 for overlap, got {overlap_res.status_code}"
        print("Overlapping leave request rejected with 409 conflict.")

        # Approve leave request
        approve_payload = {
            "status": "approved",
            "manager_note": "Approved, enjoy your vacation!",
        }
        appr_res = await client.patch(f"/api/v1/leave/requests/{req_id}/status", json=approve_payload)
        assert appr_res.status_code == 200
        assert appr_res.json()["data"]["status"] == "approved"

        # Check that used_days increased and remaining_days decreased
        bal_res_after = await client.get(f"/api/v1/leave/balances/{emp_id}")
        annual_after = next(b for b in bal_res_after.json()["data"] if b["leave_type"] == "annual")
        assert annual_after["used_days"] == 3
        assert annual_after["remaining_days"] == 17
        print("Leave approved: balance deducted correctly (used=3, remaining=17).")

        # Cancel approved leave request -> verify days restored
        cancel_payload = {"status": "cancelled", "manager_note": "Employee cancelled trip."}
        cancel_res = await client.patch(f"/api/v1/leave/requests/{req_id}/status", json=cancel_payload)
        assert cancel_res.status_code == 200
        bal_res_restored = await client.get(f"/api/v1/leave/balances/{emp_id}")
        annual_restored = next(b for b in bal_res_restored.json()["data"] if b["leave_type"] == "annual")
        assert annual_restored["used_days"] == 0
        assert annual_restored["remaining_days"] == 20
        print("Leave cancelled: balance restored correctly (used=0, remaining=20).")

        print("\n=== 3. Testing Conversation & Chat APIs ===")
        # Create conversation
        conv_payload = {
            "employee_id": emp_id,
            "title": "Onboarding & Leave Policy Questions",
        }
        conv_res = await client.post("/api/v1/conversations", json=conv_payload)
        assert conv_res.status_code == 201
        conv_id = conv_res.json()["data"]["id"]
        print(f"Created conversation id='{conv_id}'")

        # Add message turns
        user_msg = {
            "role": "user",
            "content": "How many days of annual leave do I have?",
            "token_count": 10,
        }
        msg1_res = await client.post(f"/api/v1/conversations/{conv_id}/messages", json=user_msg)
        assert msg1_res.status_code == 201

        asst_msg = {
            "role": "assistant",
            "content": "You currently have 20 days of annual leave remaining.",
            "token_count": 12,
        }
        msg2_res = await client.post(f"/api/v1/conversations/{conv_id}/messages", json=asst_msg)
        assert msg2_res.status_code == 201

        # Get conversation detail with messages
        conv_detail_res = await client.get(f"/api/v1/conversations/{conv_id}")
        assert conv_detail_res.status_code == 200
        detail_data = conv_detail_res.json()["data"]
        assert len(detail_data["messages"]) == 2
        print(f"Conversation verified with {len(detail_data['messages'])} messages.")

        print("\n=== 4. Testing Document APIs ===")
        # Register document
        doc_payload = {
            "filename": "Employee_Handbook_2026.pdf",
            "file_path": "/uploads/documents/Employee_Handbook_2026.pdf",
            "file_size_bytes": 1048576,
            "meta_data": {"department": "HR", "version": "2.0"},
        }
        doc_res = await client.post("/api/v1/documents", json=doc_payload)
        assert doc_res.status_code == 201
        doc_id = doc_res.json()["data"]["id"]
        print(f"Registered document id='{doc_id}'")

        # List documents
        doc_list_res = await client.get("/api/v1/documents")
        assert doc_list_res.status_code == 200
        assert doc_list_res.json()["data"]["pagination"]["total_items"] >= 1
        print("List documents verified.")

        # Cleanup test entities
        await client.delete(f"/api/v1/documents/{doc_id}")
        await client.delete(f"/api/v1/conversations/{conv_id}")
        await client.delete(f"/api/v1/employees/{emp_id}")
        print("Cleaned up test entities.")

    print("\n=======================================================")
    print(" ALL PHASE 2 API TESTS COMPLETED & PASSED SUCCESSFULLY!")
    print("=======================================================")


if __name__ == "__main__":
    asyncio.run(run_phase2_tests())
