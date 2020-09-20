import hashlib
from typing import Optional, Tuple

from sqlalchemy import desc

from accessors import UrlsTabAccessor
from db import session_ctx
from db.tables import UrlsTab
from utils.cache import RedisCache
from utils.time import current_timestamp


class MysqlUrlsTabAccessor(UrlsTabAccessor):

    def create(self, short_key: str, url: str) -> int:
        """
        :return: id of the created record
        """
        record = UrlsTab(
            url=url,
            short_key=short_key,
            hashed_url=self._url_hash(url),
            ctime=current_timestamp()
        )
        with session_ctx() as session:
            session.add(record)
        return record.id

    def find_last_by_short_key(self, short_key: str) -> Optional[str]:
        with session_ctx() as session:
            record = (
                session.query(UrlsTab)
                    .filter(UrlsTab.short_key == short_key)
                    .order_by(desc(UrlsTab.ctime))
                    .first()
            )
            url = record.url if record else None

        return url

    def find_match_by_url(self, url: str) -> Optional[Tuple[str, str]]:
        url_hash = self._url_hash(url)
        with session_ctx() as session:
            records = (
                session.query(UrlsTab)
                .filter(UrlsTab.hashed_url == url_hash)
                .order_by(desc(UrlsTab.ctime))
                .all()
            )
        match = next((record for record in records if record.url == url), None)
        if match is not None:
            return match.short_key, url
        return None, None

    @staticmethod
    def _url_hash(url):
        return bytearray.fromhex(hashlib.sha1(str.encode(url)).hexdigest())
