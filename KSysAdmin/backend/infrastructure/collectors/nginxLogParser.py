from __future__ import annotations
import json
from datetime import datetime
from pathlib import Path
from shared.backend.config.settings import settings
from shared.backend.loggingFactory import LoggerFactory

logger = LoggerFactory.getSystemLogger("KSysAdmin")


class NginxLogParser:
    """
    Parses nginx JSON access logs and extracts metric data.
    Reads new lines since last position (stateful parsing).
    """

    def __init__(self, log_path: str | None = None):
        self.log_path = Path(log_path or settings.nginx_access_log_path)
        self.last_position = 0

    def _extractServiceFromUrl(self, url: str) -> str:
        """Extract service name from URL path"""
        if url.startswith('/api/auth'):
            return 'kauth'
        elif url.startswith('/api/admin'):
            return 'ksysadmin'
        elif url.startswith('/api/payment'):
            return 'ksyspayment'
        else:
            return 'nginx_gateway'

    def _parseLogLine(self, line: str) -> dict | None:
        """Parse single JSON log line and extract metrics"""
        try:
            log_data = json.loads(line.strip())

            # Extract timestamp
            timestamp_str = log_data.get('timestamp', '')
            try:
                # Parse ISO format with timezone, then convert to naive UTC
                timestamp = datetime.fromisoformat(timestamp_str)
                # Remove timezone info (keep as UTC naive)
                if timestamp.tzinfo is not None:
                    timestamp = timestamp.replace(tzinfo=None)
            except Exception:
                timestamp = datetime.utcnow().replace(tzinfo=None)

            # Extract service from URL
            url = log_data.get('url', '')
            service = self._extractServiceFromUrl(url)

            # Convert latencies from seconds to milliseconds
            nginx_latency_s = log_data.get('nginx_latency_s', 0.0)
            backend_latency_s = log_data.get('backend_latency_s', '')

            nginx_latency_ms = float(nginx_latency_s) * 1000 if nginx_latency_s else 0.0
            backend_latency_ms = None
            if backend_latency_s and backend_latency_s != '':
                try:
                    backend_latency_ms = float(backend_latency_s) * 1000
                except (ValueError, TypeError):
                    backend_latency_ms = None

            # Extract user_id (empty string -> None)
            user_id = log_data.get('user_id', '')
            user_id = user_id if user_id else None

            return {
                'timestamp': timestamp,
                'service': service,
                'remote_ip': log_data.get('remote_ip', ''),
                'request_id': log_data.get('request_id', ''),
                'method': log_data.get('method', ''),
                'url': url,
                'status': int(log_data.get('status', 0)),
                'rate_limited': log_data.get('rate_limited', False),
                'user_agent': log_data.get('user_agent', ''),
                'nginx_latency_ms': nginx_latency_ms,
                'backend_latency_ms': backend_latency_ms,
                'user_id': user_id
            }

        except json.JSONDecodeError as e:
            logger.error(
                "nginx_log_parse_error",
                f"Failed to parse log line: {e}",
                line=line[:100]
            )
            return None
        except Exception as e:
            logger.error(
                "nginx_log_parse_unexpected_error",
                f"Unexpected error parsing log: {e}",
                error_type=type(e).__name__
            )
            return None

    def parseNewLogs(self) -> list[dict]:
        """
        Read and parse new log entries since last position.
        Maintains state to avoid re-processing.
        """
        if not self.log_path.exists():
            logger.application(
                "nginx_log_not_found",
                f"Nginx log file not found: {self.log_path}",
                level="warning"
            )
            return []

        metrics = []

        try:
            with open(self.log_path, 'r', encoding='utf-8') as f:
                # Seek to last position
                f.seek(self.last_position)

                # Read new lines
                for line in f:
                    if not line.strip():
                        continue

                    metric = self._parseLogLine(line)
                    if metric:
                        metrics.append(metric)

                # Update position
                self.last_position = f.tell()

            if metrics:
                logger.application(
                    "nginx_logs_parsed",
                    f"Parsed {len(metrics)} new log entries",
                    count=len(metrics)
                )

        except Exception as e:
            logger.error(
                "nginx_log_read_error",
                f"Failed to read nginx log: {e}",
                error_type=type(e).__name__
            )

        return metrics

    def resetPosition(self) -> None:
        """Reset read position to beginning of file"""
        self.last_position = 0
        logger.application(
            "nginx_log_position_reset",
            "Log parser position reset to beginning"
        )

    def getFileSize(self) -> int:
        """Get current log file size"""
        if self.log_path.exists():
            return self.log_path.stat().st_size
        return 0
