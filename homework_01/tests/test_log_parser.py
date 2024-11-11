import pytest
import datetime
from ..log_interpreter import get_requests_lex, LogEntry, Log, get_last_logfile, get_report_path, create_report, \
    default_cfg, get_config

# Sample log data for testing
sample_log_data = """
127.0.0.1 - - [10/Oct/2023:13:55:36 +0000] "GET /index.html HTTP/1.1" 200 615 "-" "Mozilla/5.0" "-" "-" "-" 0.123
127.0.0.1 - - [10/Oct/2023:13:55:36 +0000] "GET /about.html HTTP/1.1" 200 615 "-" "Mozilla/5.0" "-" "-" "-" 0.456
127.0.0.1 - - [10/Oct/2023:13:55:36 +0000] "GET /about.html HTTP/1.1" 200 615 "-" "Mozilla/5.0" "-" "-" "-" 0.789
"""


@pytest.fixture
def sample_log_file(tmp_path):
    log_file = tmp_path / "nginx-access-ui.log-20231010"
    log_file.write_text(sample_log_data)
    return log_file


def test_get_requests_lex(sample_log_file):
    log = Log(path=sample_log_file, date=datetime.date(2023, 10, 10), ext='')
    entry = LogEntry()
    errors_level = 30
    result = get_requests_lex(log, errors_level, entry)
    assert len(result) == 2
    assert result[0]['url'] == '/index.html'
    assert result[0]['count'] == 1
    assert result[0]['time_sum'] == 0.123


def test_get_last_logfile(tmp_path):
    log_dir = tmp_path / "logs"
    log_dir.mkdir()
    log_file = log_dir / "nginx-access-ui.log-20231010"
    log_file.write_text(sample_log_data)
    result = get_last_logfile(log_dir)
    assert result is not None
    assert result.path == log_file
    assert result.date == datetime.date(2023, 10, 10)
    assert result.ext == ''


def test_get_report_path(tmp_path):
    report_dir = tmp_path / "reports"
    report_dir.mkdir()
    log = Log(path=tmp_path / "nginx-access-ui.log-20231010", date=datetime.date(2023, 10, 10), ext='')
    result = get_report_path(report_dir, log)
    assert result == report_dir / "report-2023.10.10.html"


def test_create_report(tmp_path):
    report_dir = tmp_path / "reports"
    report_dir.mkdir()
    template_path = report_dir / "report.html"
    template_path.write_text("""
    <html>
    <body>
    <table>${table_json}</table>
    </body>
    </html>
    """)
    dest_path = report_dir / "report-2023.10.10.html"
    log_stat = [{'url': '/index.html', 'count': 1, 'count_perc': 100.0, 'time_sum': 0.123, 'time_perc': 100.0,
                 'time_avg': 0.123, 'time_max': 0.123, 'time_med': 0.123}]
    create_report(template_path, dest_path, log_stat)
    assert dest_path.exists()
    assert dest_path.read_text().strip() == """
    <html>
    <body>
    <table>[{"url": "/index.html", "count": 1, "count_perc": 100.0, "time_sum": 0.123, "time_perc": 100.0, "time_avg": 0.123, "time_max": 0.123, "time_med": 0.123}]</table>
    </body>
    </html>
    """.strip()


def test_get_config(tmp_path):
    config_path = tmp_path / "config.json"
    config_path.write_text('{"REPORT_SIZE": 50}')
    result = get_config(str(config_path), default_cfg)
    assert result['REPORT_SIZE'] == 50
    assert result['REPORT_DIR'] == "./reports"
