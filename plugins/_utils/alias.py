import typing as T

from graia.application import MessageChain
from graia.application.message.elements import ExternalElement

MESSAGE_T = T.Union[
    MessageChain,
    ExternalElement,
    str
]
