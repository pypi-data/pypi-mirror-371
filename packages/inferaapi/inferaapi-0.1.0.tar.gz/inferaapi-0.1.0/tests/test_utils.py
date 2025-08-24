import asyncio

from inferaapi.utils import APIResponse, async_retry


def test_api_response_success():
    """Test APIResponse success method"""
    response = APIResponse.success({"test": "data"}, "Success message")
    assert response["status"] == "success"
    assert response["data"] == {"test": "data"}
    assert response["message"] == "Success message"


def test_api_response_error():
    """Test APIResponse error method"""
    response = APIResponse.error("Error message", 400, {"detail": "test"})
    assert response["status"] == "error"
    assert response["message"] == "Error message"
    assert response["code"] == 400
    assert response["details"] == {"detail": "test"}


def test_async_retry():
    """Test async_retry decorator - run synchronously"""
    call_count = 0

    @async_retry(max_attempts=3, delay=0.1)
    async def failing_function():
        nonlocal call_count
        call_count += 1
        if call_count < 3:
            raise ValueError("Temporary failure")
        return "success"

    # Run async function synchronously
    loop = asyncio.get_event_loop()
    result = loop.run_until_complete(failing_function())

    assert result == "success"
    assert call_count == 3
