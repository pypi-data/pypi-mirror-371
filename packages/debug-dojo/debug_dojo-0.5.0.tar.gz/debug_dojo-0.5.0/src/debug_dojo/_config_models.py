from __future__ import annotations

from enum import Enum
from typing import ClassVar

from pydantic import BaseModel, ConfigDict


class BaseConfig(BaseModel):
    """Base configuration class with extra fields forbidden."""

    model_config: ClassVar[ConfigDict] = ConfigDict(
        extra="forbid", validate_assignment=True
    )


class DebuggerType(Enum):
    """Enum for different types of debuggers."""

    DEBUGPY = "debugpy"
    IPDB = "ipdb"
    PDB = "pdb"
    PUDB = "pudb"


class Features(BaseModel):
    """Configuration for installing debug features."""

    model_config = ConfigDict(extra="forbid")  # pyright: ignore[reportUnannotatedClassAttribute]

    rich_inspect: bool = True
    """Install rich inspect as 'i' for enhanced object inspection."""
    rich_print: bool = True
    """Install rich print as 'p' for enhanced printing."""
    rich_traceback: bool = True
    """Install rich traceback for better error reporting."""
    comparer: bool = True
    """Install comparer as 'c' for side-by-side object comparison."""
    breakpoint: bool = True
    """Install breakpoint as 'b' for setting breakpoints in code."""


class DebugpyConfig(BaseConfig):
    """Configuration for debugpy debugger."""

    host: str = "localhost"
    """Host for debugpy debugger."""
    log_to_file: bool = False
    """Whether to log debugpy output to a file."""
    port: int = 1992
    """Port for debugpy debugger."""
    wait_for_client: bool = True
    """Whether to wait for the client to connect before starting debugging."""

    @property
    def set_trace_hook(self) -> str:
        return "debugpy.breakpoint"


class IpdbConfig(BaseConfig):
    """Configuration for ipdb debugger."""

    context_lines: int = 20
    """Number of context lines to show in ipdb."""

    @property
    def set_trace_hook(self) -> str:
        return "ipdb.set_trace"


class PdbConfig(BaseConfig):
    """Configuration for pdb debugger."""

    @property
    def set_trace_hook(self) -> str:
        return "pdb.set_trace"


class PudbConfig(BaseConfig):
    """Configuration for pudb debugger."""

    @property
    def set_trace_hook(self) -> str:
        return "pudb.set_trace"


class DebuggersConfig(BaseConfig):
    """Configuration for debuggers."""

    default: DebuggerType = DebuggerType.IPDB
    """Default debugger to use."""
    prompt_name: str = "debug-dojo> "
    """Prompt name for the debugger, used in the REPL."""

    debugpy: DebugpyConfig = DebugpyConfig()
    """Configuration for debugpy debugger."""
    ipdb: IpdbConfig = IpdbConfig()
    """Configuration for ipdb debugger."""
    pdb: PdbConfig = PdbConfig()
    """Configuration for pdb debugger."""
    pudb: PudbConfig = PudbConfig()
    """Configuration for pudb debugger."""


class ExceptionsConfig(BaseConfig):
    """Configuration for exceptions handling."""

    locals_in_traceback: bool = False
    """Include local variables in traceback."""
    post_mortem: bool = True
    """Enable post-mortem debugging after an exception."""
    rich_traceback: bool = True
    """Enable rich traceback for better error reporting."""


class FeaturesConfig(BaseConfig):
    """Configuration for installing debug features."""

    breakpoint: str = "b"
    """Install breakpoint as 'b' for setting breakpoints in code."""
    comparer: str = "c"
    """Install comparer as 'c' for side-by-side object comparison."""
    rich_inspect: str = "i"
    """Install rich inspect as 'i' for enhanced object inspection."""
    rich_print: str = "p"
    """Install rich print as 'p' for enhanced printing."""


class DebugDojoConfigV1(BaseModel):
    """Configuration for Debug Dojo."""

    model_config = ConfigDict(extra="forbid")  # pyright: ignore[reportUnannotatedClassAttribute]

    debugger: DebuggerType = DebuggerType.PUDB
    """The type of debugger to use."""
    features: Features = Features()
    """Features to install for debugging."""

    def update(self) -> DebugDojoConfigV2:
        """Update the configuration to the latest version."""
        v2_exceptions = ExceptionsConfig(
            rich_traceback=self.features.rich_traceback,
        )
        v2_debuggers = DebuggersConfig(default=self.debugger)
        v2_features = FeaturesConfig(
            rich_inspect="i" if self.features.rich_inspect else "",
            rich_print="p" if self.features.rich_print else "",
            comparer="c" if self.features.comparer else "",
            breakpoint="b" if self.features.breakpoint else "",
        )
        return DebugDojoConfigV2(
            exceptions=v2_exceptions,
            debuggers=v2_debuggers,
            features=v2_features,
        )


class DebugDojoConfigV2(BaseModel):
    """Configuration for Debug Dojo."""

    model_config = ConfigDict(extra="forbid")  # pyright: ignore[reportUnannotatedClassAttribute]

    exceptions: ExceptionsConfig = ExceptionsConfig()
    """Better exception messages."""
    debuggers: DebuggersConfig = DebuggersConfig()
    """Default debugger and configs."""
    features: FeaturesConfig = FeaturesConfig()
    """Features mnemonics."""


DebugDojoConfig = DebugDojoConfigV2
