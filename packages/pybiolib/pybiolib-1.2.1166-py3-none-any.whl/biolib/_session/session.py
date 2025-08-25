from biolib import utils
from biolib._internal.types import Optional
from biolib.api.client import ApiClient, ApiClientInitDict
from biolib._internal.auth_utils import exchange_username_password_for_tokens
from biolib.app import BioLibApp


class Session:
    def __init__(self, _init_dict: ApiClientInitDict) -> None:
        self._api = ApiClient(_init_dict=_init_dict)

    @staticmethod
    def get_session(
        refresh_token: Optional[str] = None, 
        base_url: Optional[str] = None, 
        client_type: Optional[str] = None,
        username: Optional[str] = None,
        password: Optional[str] = None
    ) -> 'Session':
        if refresh_token and (username or password):
            raise ValueError("Cannot specify both refresh_token and username/password authentication")
        
        if (username and not password) or (password and not username):
            raise ValueError("Both username and password must be provided for username/password authentication")
        
        if not refresh_token and not (username and password):
            raise ValueError("Must provide either refresh_token or username/password for authentication")

        base_url_resolved = base_url or utils.load_base_url_from_env()
        
        if username and password:
            tokens = exchange_username_password_for_tokens(
                username,
                password,
                base_url_resolved,
            )
            refresh_token = tokens['refresh']

        init_dict = ApiClientInitDict(
            refresh_token=str(refresh_token),
            base_url=base_url_resolved,
            client_type=client_type,
        )
            
        return Session(_init_dict=init_dict)

    def load(self, uri: str, suppress_version_warning: bool = False) -> BioLibApp:
        r"""Load a BioLib application by its URI or website URL.

        Args:
            uri (str): The URI or website URL of the application to load. Can be either:
                - App URI (e.g., 'biolib/myapp:1.0.0')
                - Website URL (e.g., 'https://biolib.com/biolib/myapp/')
            suppress_version_warning (bool): If True, don't print a warning when no version is specified.
                Defaults to False.

        Returns:
            BioLibApp: The loaded application object

        Example::

            >>> # Load by URI
            >>> app = biolib.load('biolib/myapp:1.0.0')
            >>> # Load by website URL
            >>> app = biolib.load('https://biolib.com/biolib/myapp/')
            >>> result = app.cli('--help')
        """
        return BioLibApp(uri=uri, _api_client=self._api, suppress_version_warning=suppress_version_warning)
