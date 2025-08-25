"""
Functions and routines associated with Enasis Network Remote Connect.

This file is part of Enasis Network software eco-system. Distribution
is permitted, for more information consult the project license file.
"""



from typing import Annotated
from typing import Any
from typing import Optional

from encommon.types import BaseModel

from pydantic import Field



class BridgeParams(BaseModel, extra='forbid'):
    """
    Process and validate the class configuration parameters.
    """

    server: Annotated[
        str,
        Field(...,
              description='Server address for connection',
              min_length=1)]

    timeout: Annotated[
        int,
        Field(30,
              description='Timeout connecting to server',
              ge=1, le=300)]

    appid: Annotated[
        int,
        Field(...,
              description='Parameter for the integration',
              ge=0)]

    token: Annotated[
        str,
        Field(...,
              description='Parameter for the integration',
              min_length=1)]

    ssl_verify: Annotated[
        bool,
        Field(False,
              description='Verify the ceritifcate valid')]

    ssl_capem: Annotated[
        Optional[str],
        Field(None,
              description='Verify the ceritifcate valid',
              min_length=1)]


    def __init__(
        self,
        /,
        **data: Any,
    ) -> None:
        """
        Initialize instance for class using provided parameters.
        """

        super().__init__(**data)
