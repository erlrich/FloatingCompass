# ============================================================
# Floating Compass - QGIS Plugin
#
# Author   : Achmad Amrulloh
# Email    : achmad.amrulloh@gmail.com
# LinkedIn : https://www.linkedin.com/in/achmad-amrulloh/
#
# © 2026 Dinzo. All rights reserved.
#
# This software is provided as freeware.
# Redistribution, modification, or reuse without
# proper attribution is not permitted.
# ============================================================
# floating_compass_news_manager.py

import json
from datetime import datetime, timedelta

from qgis.PyQt.QtCore import QSettings, QUrl
from qgis.PyQt.QtNetwork import QNetworkRequest
from qgis.core import (
    QgsBlockingNetworkRequest,
    QgsMessageLog,
    Qgis,
)


# ============================================================
# CONSTANTS
# ============================================================

# GitHub raw URL untuk news.json (Floating Compass)
NEWS_JSON_URL = (
    "https://raw.githubusercontent.com/erlrich/"
    "FloatingCompass/main/news.json"
)

# Interval fetch (7 hari = 168 jam)
FETCH_INTERVAL_HOURS = 168

# Log tag
LOG_TAG = "Floating Compass"

# QSettings keys
KEY_LAST_FETCH  = "FloatingCompass/news_last_fetch"
KEY_CACHED_NEWS = "FloatingCompass/news_cached"
KEY_READ_IDS    = "FloatingCompass/news_read_ids"


# ============================================================
# NEWS MANAGER
# ============================================================

class NewsManager:
    """
    Manage news fetching & caching from GitHub JSON.

    Behavior:
    - Fetch hanya jika sudah lewat FETCH_INTERVAL_HOURS
    - Cache hasil fetch di QSettings
    - Track news yang sudah dibaca (by id)
    """

    def __init__(self):
        self.settings = QSettings()

    # ---------------------------------------------------------
    # PUBLIC API
    # ---------------------------------------------------------

    def should_fetch(self):
        """
        Cek apakah perlu fetch news (interval 7 hari).
        """
        last_fetch_str = self.settings.value(KEY_LAST_FETCH, "", str)

        if not last_fetch_str:
            return True

        try:
            last_fetch = datetime.fromisoformat(last_fetch_str)
            elapsed = datetime.now() - last_fetch
            return elapsed >= timedelta(hours=FETCH_INTERVAL_HOURS)
        except (ValueError, TypeError):
            return True

    def fetch(self):
        """
        Fetch news.json dari GitHub.

        Returns:
            dict | None: Parsed JSON kalau sukses, None kalau gagal
        """
        try:
            # Pakai QNetworkRequest (dari Qt), BUKAN urllib/requests
            request = QNetworkRequest(QUrl(NEWS_JSON_URL))
            blocking = QgsBlockingNetworkRequest()
            error_code = blocking.get(request)

            # Cek ErrorCode enum (long-form, Qt5 & Qt6 safe)
            if error_code != QgsBlockingNetworkRequest.ErrorCode.NoError:
                QgsMessageLog.logMessage(
                    f"News fetch failed: {blocking.errorMessage()}",
                    LOG_TAG,
                    Qgis.MessageLevel.Warning,
                )
                return None

            # Ambil konten dari reply
            reply = blocking.reply()
            if not reply:
                return None

            # Konversi QByteArray ke bytes lalu decode
            raw = bytes(reply.content())
            data = json.loads(raw.decode("utf-8"))

            # Update last fetch timestamp
            self.settings.setValue(
                KEY_LAST_FETCH,
                datetime.now().isoformat(),
            )

            # Cache raw JSON
            self.settings.setValue(
                KEY_CACHED_NEWS,
                json.dumps(data),
            )

            return data

        except Exception as e:
            QgsMessageLog.logMessage(
                f"News fetch exception: {e}",
                LOG_TAG,
                Qgis.MessageLevel.Warning,
            )
            return None

    def get_cached(self):
        """
        Ambil cached news dari QSettings.
        """
        cached_str = self.settings.value(KEY_CACHED_NEWS, "", str)
        if not cached_str:
            return None

        try:
            return json.loads(cached_str)
        except (ValueError, TypeError):
            return None

    def get_unread_news(self):
        """
        Ambil list news yang BELUM dibaca.
        """
        data = self.get_cached()
        if not data:
            return []

        news_list = data.get("news", [])
        read_ids = self._get_read_ids()

        unread = [
            item for item in news_list
            if item.get("id") not in read_ids
        ]

        # Sort by priority (high first), lalu by date
        priority_order = {"high": 0, "medium": 1, "low": 2}
        unread.sort(
            key=lambda x: (
                priority_order.get(x.get("priority", "low"), 2),
                x.get("date", ""),
            )
        )

        return unread

    def mark_as_read(self, news_id):
        """
        Tandai news sebagai sudah dibaca.
        """
        read_ids = self._get_read_ids()
        if news_id not in read_ids:
            read_ids.append(news_id)
            self.settings.setValue(KEY_READ_IDS, json.dumps(read_ids))

    def mark_all_as_read(self):
        """Tandai semua news sebagai sudah dibaca."""
        data = self.get_cached()
        if not data:
            return

        news_list = data.get("news", [])
        read_ids = [item.get("id") for item in news_list if item.get("id")]
        self.settings.setValue(KEY_READ_IDS, json.dumps(read_ids))

    # ---------------------------------------------------------
    # INTERNAL HELPERS
    # ---------------------------------------------------------

    def _get_read_ids(self):
        """Ambil list ID news yang sudah dibaca."""
        raw = self.settings.value(KEY_READ_IDS, "[]", str)
        try:
            return json.loads(raw)
        except (ValueError, TypeError):
            return []