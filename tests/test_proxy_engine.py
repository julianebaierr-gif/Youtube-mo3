import pytest
from fastapi.testclient import TestClient
from app.main import app, pick_best_proxy_country, get_dataimpulse_proxy_url, get_proxy_format_selector

client = TestClient(app)

def test_pick_best_proxy_country():
    # Mexico locked
    assert pick_best_proxy_country(["CR", "MX"]) == "mx"
    # France locked
    assert pick_best_proxy_country(["AD", "BL", "FR", "GF"]) == "fr"
    # Australia in list
    assert pick_best_proxy_country(["AE", "AR", "AU"]) == "au"
    # None or empty
    assert pick_best_proxy_country([]) is None

def test_proxy_format_selector_capped_at_720():
    audio_sel = get_proxy_format_selector(mode="audio")
    assert "140" in audio_sel or "bestaudio" in audio_sel

    video_sel = get_proxy_format_selector(mode="video", quality="1080")
    # Must contain height<=720
    assert "height<=720" in video_sel
    assert "1080" not in video_sel
    assert "2160" not in video_sel

def test_dataimpulse_proxy_url_format():
    url_base = get_dataimpulse_proxy_url()
    assert "gw.dataimpulse.com:823" in url_base
    assert "c8f15994b4066af9b4b9" in url_base

    url_geo = get_dataimpulse_proxy_url(country="mx", session_id="abc12345")
    assert "__cr.mx" in url_geo
    assert ";sid.abc12345" in url_geo

def test_video_resolutions_endpoint():
    # Test invalid id returns default safely
    res = client.get("/api/video-resolutions?id=invalid123")
    assert res.status_code == 200
    data = res.json()
    assert "max_height" in data
