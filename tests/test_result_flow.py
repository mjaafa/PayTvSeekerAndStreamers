from Engine.results import dedupe_results, normalize_legacy_result, normalized_result
from Reporting.report_writer import ReportWriter


def test_normalize_legacy_url():
    item = normalize_legacy_result("https://192.0.2.10:443", engine="test", query="demo")
    assert item["engine"] == "test"
    assert item["query"] == "demo"
    assert item["ip"] == "192.0.2.10"
    assert item["port"] == 443
    assert item["protocol"] == "https"


def test_dedupe_result_dicts():
    a = normalized_result(engine="shodan", query="dreambox", ip="192.0.2.1", port=80)
    b = dict(a)
    assert len(dedupe_results([a, b])) == 1


def test_report_writer(tmp_path):
    writer = ReportWriter(tmp_path)
    result = normalized_result(engine="shodan", query="dreambox", ip="192.0.2.1", port=80)
    paths = writer.write([result], [{"engine": "shodan", "status": "ok", "result_count": 1, "error": ""}])
    assert set(paths) >= {"json", "csv", "html", "latest_html"}
    assert (tmp_path / "latest.json").exists()
    assert (tmp_path / "latest.csv").exists()
    assert (tmp_path / "latest.html").exists()


def test_censys_extract_handles_string_result_and_string_services():
    from Engine.censys_api import censys

    engine = censys("censys@id@secret", "dreambox")
    assert engine._extract_results("dreambox", {"result": "not-a-dict"}) == []

    payload = {
        "result": {
            "hits": [
                {
                    "ip": "192.0.2.20",
                    "services": ["HTTP", {"port": 443, "extended_service_name": "HTTPS"}],
                }
            ]
        }
    }
    results = engine._extract_results("dreambox", payload)
    assert len(results) == 2
    assert results[0]["ip"] == "192.0.2.20"


def test_zoomeye_extract_handles_nested_data():
    from Engine.zoomeye_api import zoomeye

    engine = zoomeye("zoomeye@test", "dreambox")
    payload = {"data": {"matches": [{"ip": "192.0.2.30", "portinfo": {"port": 443, "service": "https"}}]}}
    results = engine._extract_results("dreambox", payload)
    assert len(results) == 1
    assert results[0]["protocol"] == "https"
