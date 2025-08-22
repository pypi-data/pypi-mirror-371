from io import BytesIO
from copy import deepcopy
from typing import Any, Dict, Union
from urllib.parse import urlparse

import pandas as pd
from kedro.extras.datasets.pandas import ExcelDataSet
from kedro.io.core import PROTOCOL_DELIMITER, DataSetError, Version
from office365.sharepoint.client_context import ClientContext


class SharePointExcelDataSet(ExcelDataSet):
    def __init__(
        self,
        filepath: str,
        engine: str = "openpyxl",
        load_args: Dict[str, Any] = None,
        save_args: Dict[str, Any] = None,
        version: Version = None,
        credentials: Dict[str, Any] = None,
        fs_args: Dict[str, Any] = None,
    ) -> None:

        if not (
            credentials
            and "tenant" in credentials
            and credentials["tenant"]
            and "client_id" in credentials
            and credentials["client_id"]
            and "thumbprint" in credentials
            and credentials["thumbprint"]
            and "private_key" in credentials
            and credentials["private_key"]
        ):
            raise DataSetError(
                "'tenant', 'client_id', 'thumbprint' and 'private_key' arguments cannot be empty. Please "
                "provide valid SharePoint certificate credentials."
            )

        _credentials = deepcopy(credentials) or {}
        self._user_certificate_credentials = {
            "tenant": _credentials["tenant"],
            "client_id": _credentials["client_id"],
            "thumbprint": _credentials["thumbprint"],
            "private_key": _credentials["private_key"],
        }

        super().__init__(
            filepath, engine, load_args, save_args, version, credentials, fs_args
        )

    def _load(self) -> Union[pd.DataFrame, Dict[str, pd.DataFrame]]:
        load_path = str(self._get_load_path())
        if self._protocol == "file":
            return pd.read_excel(load_path, **self._load_args)

        load_path = f"{self._protocol}{PROTOCOL_DELIMITER}{load_path}"

        parsed = urlparse(load_path)

        parts = parsed.path.strip("/").split("/")

        if "sites" in parts:
            idx = parts.index("sites") + 2
            base_path = "/" + "/".join(parts[:idx])
            rest_path = "/" + "/".join(parts[idx:])
        else:
            base_path = ""
            rest_path = parsed.path

        base_url = f"{parsed.scheme}://{parsed.netloc}{base_path}"
        relative_url = f"{base_path}/{rest_path.lstrip('/')}" if rest_path else base_path

        ctx = ClientContext(base_url).with_client_certificate(**self._user_certificate_credentials)

        file = ctx.web.get_file_by_server_relative_url(relative_url)

        file_content = BytesIO()
        file.download(file_content)
        ctx.execute_query()

        file_content.seek(0)

        return pd.read_excel(
            file_content,
            **self._load_args
        )
