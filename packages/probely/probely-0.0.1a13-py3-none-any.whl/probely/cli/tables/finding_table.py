from rich.table import Table

from probely.cli.renderers import (
    get_printable_date,
    get_printable_enum_value,
    get_printable_labels,
    get_printable_boolean,
)
from probely.cli.tables.base_table import BaseOutputTable
from probely.sdk.enums import FindingSeverityEnum
from probely.sdk.models import Finding

DEFAULT_LAST_FOUND_DATE_VALUE = "NO_DATE"


class FindingTable(BaseOutputTable):
    @classmethod
    def create_table(cls, show_header: bool = False) -> Table:
        table = Table(show_header=show_header, box=None)

        table.add_column("ID", width=18)
        table.add_column("TARGET_ID", width=12)
        table.add_column("SEVERITY", width=8)
        table.add_column("TITLE", width=48, no_wrap=True)
        table.add_column("LAST_FOUND", width=16)
        table.add_column("STATE", width=8)
        table.add_column("RETESTING", width=9)
        table.add_column("LABELS", width=16, no_wrap=True)

        return table

    @classmethod
    def add_row(cls, table: Table, finding: Finding) -> None:
        target = finding.target

        table.add_row(
            f"{target.id}-{finding.id}",  # Composite Finding ID
            target.id,
            get_printable_enum_value(FindingSeverityEnum, finding.severity),  # severity
            finding.definition.name,  # title
            get_printable_date(
                finding.last_found, DEFAULT_LAST_FOUND_DATE_VALUE
            ),  # last_found
            finding.state,
            get_printable_boolean(finding.retesting),
            get_printable_labels(finding.labels),
        )
