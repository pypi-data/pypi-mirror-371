"""
Functions and routines associated with Enasis Network Homie Automate.

This file is part of Enasis Network software eco-system. Distribution
is permitted, for more information consult the project license file.
"""



from copy import deepcopy
from dataclasses import dataclass
from typing import TYPE_CHECKING

from encommon.types import LDictStrAny

from ..homie.threads import HomieUpdate
from ..homie.threads import HomieUpdateItem

if TYPE_CHECKING:
    from ..homie.childs import HomieOrigin



@dataclass
class HubiUpdateItem(HomieUpdateItem):
    """
    Contain information for sharing using the Python queue.
    """

    fetch: LDictStrAny


    def __init__(
        self,
        origin: 'HomieOrigin',
        fetch: LDictStrAny,
    ) -> None:
        """
        Initialize instance for class using provided parameters.
        """

        fetch = deepcopy(fetch)

        self.fetch = fetch

        super().__init__(origin)



class HubiUpdate(HomieUpdate):
    """
    Common methods and routines for Homie Automate threads.
    """
