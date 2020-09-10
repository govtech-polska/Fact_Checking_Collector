from enum import Enum, unique

COMMENT_LENGTH = 1000
TEXT_LENGTH = 20000
URL_LENGTH = 2000


@unique
class NewsOrigin(Enum):
    PLUGIN = "plugin"
    CHATBOT = "chatbot"
    MOBILE = "mobile"
