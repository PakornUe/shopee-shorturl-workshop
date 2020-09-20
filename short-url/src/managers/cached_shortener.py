from utils.redis import redis_client
from accessors import UrlsTabAccessor
from managers import ShortUrlManager, NotFoundException
from managers.generators import UniqueShortKeyGenerator


class CachedShortUrlManager(ShortUrlManager):

    def __init__(self, urls_tab_accessor: UrlsTabAccessor, short_key_generator: UniqueShortKeyGenerator):
        super().__init__(urls_tab_accessor, short_key_generator)

    def resolve(self, short_key: str) -> str:
        """
        Return the latest source url for the short key.
        """
        redis = redis_client()


        # Attempt to retrieve short key from cache
        url = redis.get(short_key)

        if (url):
            return url

        # Database lookup if not found
        url = self.urls_tab_accessor.find_last_by_short_key(short_key)

        if (url):
            redis.set(short_key, url, ex = 10)
        else:
            raise NotFoundException(f'url not found for short_key: {short_key}')

        return url

    def create(self, url: str) -> str:
        """
        Return a short key for the url.
        """
        redis = redis_client()

        # Cache lookup
        short_key = redis.get(url)
        
        if (short_key):
            return short_key

        # Database lookup
        short_key, matched = self.urls_tab_accessor.find_match_by_url(url)

        # If not in database, create a shortkey
        if matched != url:
            short_key = self._generate_new_short_key(url)

        # Store in cache and return
        redis.set(url, short_key, ex = 10)
        return short_key

    def _generate_new_short_key(self, url):
        short_key = self.short_key_generator.generate(url)
        self.urls_tab_accessor.create(short_key, url)
        return short_key
