"""
Copyright CNRS (https://www.cnrs.fr/index.php/en)
Contributor(s): Eric Debreuve (eric.debreuve@cnrs.fr) since 2023
SEE COPYRIGHT NOTICE BELOW
"""

import logging as l
import typing as h

from logger_36.catalog.config.optional import RICH_IS_AVAILABLE

if RICH_IS_AVAILABLE:
    from rich.console import Console as console_t  # noqa
    from rich.console import ConsoleOptions as console_options_t  # noqa
    from rich.markup import escape as EscapedForRich  # noqa
    from rich.terminal_theme import DEFAULT_TERMINAL_THEME  # noqa

    from logger_36.catalog.config.console_rich import DATE_TIME_COLOR
    from logger_36.catalog.handler.console_rich import HighlightedVersion
else:
    DATE_TIME_COLOR = HighlightedVersion = console_t = console_options_t = (
        EscapedForRich
    ) = DEFAULT_TERMINAL_THEME = None

from logger_36.task.format.rule import Rule, RuleAsText
from logger_36.type.handler import handler_t as base_t

LogAsIs_h = h.Callable[[str | h.Any], None]


@h.runtime_checkable
class EmitRule_p(h.Protocol):
    def __call__(self, /, *, text: str | None = None, color: str = "white") -> None: ...


class generic_handler_t(base_t):
    """
    alternating_logs:
    - 0: disabled
    - 1: enabled for dark background
    - 2: enabled for light background
    """

    def __init__(
        self,
        name: str | None,
        message_width: int,
        level: int,
        formatter: l.Formatter | None,
        kwargs,
    ) -> None:
        """
        EmitAsIs: By definition, the generic handler does not know how to output
        messages. If not passed, it defaults to output-ing messages in the console.
        """
        EmitAsIs = kwargs.pop("EmitAsIs", None)
        alternating_logs = kwargs.pop("alternating_logs", 0)
        supports_html = kwargs.pop("supports_html", False)

        assert alternating_logs in (0, 1, 2)

        base_t.__init__(self, name, message_width, level, formatter, kwargs)

        if EmitAsIs is not None:
            self.EmitAsIs = EmitAsIs
        self.console = None  # console_t | None.
        self.console_options = None  # console_options_t | None.
        self.alternating_logs = alternating_logs
        self._log_parity = False

        self.__post_init_local__(supports_html)

    def __post_init_local__(self, supports_html: bool) -> None:
        """"""
        if supports_html and (console_t is not None):
            self.console = console_t(highlight=False, force_terminal=True)
            self.console_options = self.console.options.update(
                overflow="ignore", no_wrap=True
            )
            self.EmitRule = self._EmitRichRule

    @classmethod
    def New(
        cls,
        /,
        *,
        name: str | None = None,
        message_width: int = -1,
        level: int = l.NOTSET,
        formatter: l.Formatter | None = None,
        **kwargs,
    ) -> h.Self:
        """"""
        return cls(name, message_width, level, formatter, kwargs)

    def emit(self, record: l.LogRecord, /) -> None:
        """"""
        if self.console is None:
            message = self.MessageFromRecord(
                record, RuleAsText, line_width=self.message_width
            )[0]
        else:
            message, is_not_a_rule = self.MessageFromRecord(
                record,
                Rule,
                line_width=self.message_width,
                color=DATE_TIME_COLOR,
                PreProcessed=EscapedForRich,
            )
            if is_not_a_rule:
                message = HighlightedVersion(
                    self.console,
                    message,
                    record.levelno,
                    self.alternating_logs,
                    self._log_parity,
                )
            segments = self.console.render(message, options=self.console_options)

            # Inspired from the code of: rich.console.export_html.
            html_segments = []
            for text, style, _ in segments:
                if text == "\n":
                    html_segments.append("\n")
                else:
                    if style is not None:
                        style = style.get_html_style(DEFAULT_TERMINAL_THEME)
                        if (style is not None) and (style.__len__() > 0):
                            text = f'<span style="{style}">{text}</span>'
                    html_segments.append(text)
            if html_segments[-1] == "\n":
                html_segments = html_segments[:-1]

            # /!\ For some reason, the widget splits the message into lines, place each
            # line inside a pre tag, and set margin-bottom of the first and list lines
            # to 12px. This can be seen by printing self.contents.toHtml(). To avoid the
            # unwanted extra margins, margin-bottom is set to 0 below.
            message = (
                "<pre style='margin-bottom:0px'>" + "".join(html_segments) + "</pre>"
            )

        self.EmitAsIs(message)
        self._log_parity = not self._log_parity

    def _EmitRichRule(
        self, /, *, text: str | None = None, color: str = "black"
    ) -> None:
        """"""
        self.EmitAsIs(Rule(text, color))


"""
COPYRIGHT NOTICE

This software is governed by the CeCILL  license under French law and
abiding by the rules of distribution of free software.  You can  use,
modify and/ or redistribute the software under the terms of the CeCILL
license as circulated by CEA, CNRS and INRIA at the following URL
"http://www.cecill.info".

As a counterpart to the access to the source code and  rights to copy,
modify and redistribute granted by the license, users are provided only
with a limited warranty  and the software's author,  the holder of the
economic rights,  and the successive licensors  have only  limited
liability.

In this respect, the user's attention is drawn to the risks associated
with loading,  using,  modifying and/or developing or reproducing the
software by the user in light of its specific status of free software,
that may mean  that it is complicated to manipulate,  and  that  also
therefore means  that it is reserved for developers  and  experienced
professionals having in-depth computer knowledge. Users are therefore
encouraged to load and test the software's suitability as regards their
requirements in conditions enabling the security of their systems and/or
data to be ensured and,  more generally, to use and operate it in the
same conditions as regards security.

The fact that you are presently reading this means that you have had
knowledge of the CeCILL license and that you accept its terms.

SEE LICENCE NOTICE: file README-LICENCE-utf8.txt at project source root.
"""
