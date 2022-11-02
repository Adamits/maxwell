"""Classes for edit actions."""

import abc
import dataclasses
from typing import Any


class Edit(abc.ABC):
    pass


@dataclasses.dataclass(frozen=True, eq=True)
class Start(Edit):
    """Represents beginning of sequence action.

    Largely a dummy value for model to learn beginning of edits.
    """

    bos: str = "<BOS>"

    def __repr__(self) -> str:
        return self.bos


@dataclasses.dataclass(frozen=True, eq=True)
class End(Edit):
    """Represents end of sequence action.

    Used by model to predict end of edits.
    """

    eos: str = "<EOS>"

    def __repr__(self) -> str:
        return self.eos


class ConditionalEdit(Edit):
    """Parent class for actions generated by dataloader.

    Unlike GenerativeEdits, these don't map between source
    and target. Used for simple generation of possible actions.
    """

    def conditional_counterpart(self) -> Edit:
        return self


class GenerativeEdit(Edit):
    """Parent class for actions learned used by oracle.

    Generative edits map between source and target strings.
    """

    @abc.abstractmethod
    def conditional_counterpart(self) -> ConditionalEdit:
        """All generative edits should map to a conditional edit."""
        raise NotImplementedError


@dataclasses.dataclass(frozen=True, eq=True)
class ConditionalSub(ConditionalEdit):
    """Represents possible substitution action for observed target symbol."""

    new: Any


@dataclasses.dataclass(frozen=True, eq=True)
class ConditionalCopy(ConditionalEdit):
    """Represents possible copy action for observed target symbol."""

    pass


@dataclasses.dataclass(frozen=True, eq=True)
class ConditionalDel(ConditionalEdit):
    """Represents possible deletion for omission of target symbol."""

    # TODO: Verify this class needs to exist.
    pass


@dataclasses.dataclass(frozen=True, eq=True)
class ConditionalIns(ConditionalEdit):
    """Represents possible insertion for observed target symbol."""

    # TODO: Verify this class needs to exist.
    new: Any


@dataclasses.dataclass(frozen=True, eq=True)
class Sub(GenerativeEdit):
    """Represents substitution action.

    Maps substitutions between given prefix (old) and
    observed target (new).
    """

    old: Any
    new: Any

    def conditional_counterpart(self) -> ConditionalEdit:
        return ConditionalSub(self.new)


@dataclasses.dataclass(frozen=True, eq=True)
class Copy(Sub):
    """Represents copy action.

    Maps copy between given prefix (old) and observed target (new).
    """

    # TODO: Check use of this action. Old and new don't need to be separate.
    old: Any
    new: Any

    def __post_init__(self):
        if self.old != self.new:
            raise ValueError(f"Copy: old={self.old} != new={self.new}")

    def conditional_counterpart(self) -> ConditionalEdit:
        return ConditionalCopy()


@dataclasses.dataclass(frozen=True, eq=True)
class Del(GenerativeEdit):
    """Action represents deletion action."""

    old: Any

    def conditional_counterpart(self) -> ConditionalEdit:
        return ConditionalDel()


@dataclasses.dataclass(frozen=True, eq=True)
class Ins(GenerativeEdit):
    """Action represents insertion action."""

    new: Any

    def conditional_counterpart(self) -> ConditionalEdit:
        return ConditionalIns(self.new)
