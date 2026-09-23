from app.main import app


def test_only_id_image_verification_route_is_exposed():
    paths = app.openapi()["paths"]
    assert "/api/verification/id-image" in paths
    assert "/api/verification/id-live" not in paths
