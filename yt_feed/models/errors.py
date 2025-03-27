class BadChannelException(Exception):
    def __init__(self, message, errors):
        super().__init__(message)
        self.errors = errors


class InvalidConfigException(Exception):
    def __init__(self, domain, key):
        domain_part, key_part = "", ""
        if not domain:
            domain_part = "DOMAIN not set in env vars"
        if not key:
            key_part = "YOUTUBE_API_KEY not set in env vars"
        message = f"\n\n{domain_part}\n{key_part}"

        super().__init__(message)
        self.errors = ""
