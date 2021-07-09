from enum import Enum


class Source(str, Enum):
    OVERRIDE = "override"
    COMMAND_LINE = "command-line"
    ENVIRONMENT = "environment"
    CONFIG_FILE = "config-file"
    KV_STORE = "kv-store"
    DEFAULT = "default"
