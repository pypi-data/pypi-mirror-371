"""Calculator dialog for book production.

This dialog allows users to calculate spine width based on page count
and document type (cover or dustjacket), and displays total document
dimensions for all book formats.
"""

from typing import Optional

from PySide6.QtCore import Qt
from PySide6.QtWidgets import (
    QDialog,
    QDialogButtonBox,
    QGroupBox,
    QHBoxLayout,
    QHeaderView,
    QLabel,
    QRadioButton,
    QSpinBox,
    QTableWidget,
    QTableWidgetItem,
    QVBoxLayout,
    QWidget,
)

from momovu.lib.constants import (
    COVER_BLEED,
    DUSTJACKET_BLEED,
    DUSTJACKET_FLAP_WIDTH,
    DUSTJACKET_FOLD_SAFETY_MARGIN,
    MINIMUM_COVER_PAGES,
    SPINE_WIDTH_DIVISOR,
    SPINE_WIDTH_OFFSET,
)
from momovu.lib.logger import get_logger
from momovu.lib.sizes.book_interior_sizes import BOOK_INTERIOR_SIZES
from momovu.lib.sizes.dustjacket_spine_widths import get_dustjacket_spine_width

logger = get_logger(__name__)


def format_spine_width(width: float) -> str:
    """Format spine width removing unnecessary trailing zeros.

    Args:
        width: Spine width in millimeters

    Returns:
        Formatted string without trailing zeros
    """
    # Format to 3 decimal places, then remove trailing zeros
    formatted = f"{width:.3f}".rstrip("0").rstrip(".")
    return formatted


# Constants for spine width calculation are imported from momovu.lib.constants


def calculate_cover_spine_width(page_count: int) -> float:
    """Calculate spine width for covers using official Lulu formula.

    Formula from Lulu PDF: (number of interior pages / 17.48) + 1.524 mm

    Args:
        page_count: Number of pages in the book

    Returns:
        Spine width in millimeters, rounded to 3 decimal places
    """
    spine_width = (page_count / SPINE_WIDTH_DIVISOR) + SPINE_WIDTH_OFFSET
    return round(spine_width, 3)


class SpineWidthCalculatorDialog(QDialog):
    """Dialog for calculating spine width based on page count and document type.

    Uses official Lulu formulas:
    - Covers (Paperback): (pages / 17.48) + 1.524 mm
    - Dustjackets (Hardcover): Lookup table based on page ranges
    """

    def __init__(
        self, parent: Optional[QWidget] = None, initial_pages: int = 100
    ) -> None:
        """Initialize the calculator dialog.

        Args:
            parent: Parent widget for the dialog
            initial_pages: Initial page count to display
        """
        super().__init__(parent)
        self.setWindowTitle(self.tr("Calculator"))
        self.setModal(True)
        self.setMinimumWidth(700)
        self.setMinimumHeight(800)
        # Set a reasonable default size to avoid scrollbars
        self.resize(750, 850)
        self.initial_pages = initial_pages

        self._setup_ui()
        self._connect_signals()

        # Calculate initial values
        self._calculate_spine_width()
        self._update_document_sizes()

        logger.debug(f"Calculator dialog initialized with {initial_pages} pages")

    def _setup_ui(self) -> None:
        """Build the dialog layout with input controls and result display."""
        layout = QVBoxLayout(self)
        layout.setSpacing(15)

        # Instructions
        instructions = QLabel(
            self.tr(
                "Calculate spine width based on page count and document type.\n"
                "Enter the number of pages and select the document type."
            )
        )
        instructions.setWordWrap(True)
        layout.addWidget(instructions)

        # Page count input
        page_layout = QHBoxLayout()
        page_layout.addWidget(QLabel(self.tr("Number of Pages:")))

        self.page_spinbox = QSpinBox()
        self.page_spinbox.setMinimum(1)
        self.page_spinbox.setMaximum(999)
        self.page_spinbox.setValue(self.initial_pages)
        self.page_spinbox.setToolTip(self.tr("Enter the total number of pages (1-999)"))
        page_layout.addWidget(self.page_spinbox)
        page_layout.addStretch()

        layout.addLayout(page_layout)

        # Document type selection
        type_group = QGroupBox(self.tr("Document Type"))
        type_layout = QVBoxLayout()

        self.cover_radio = QRadioButton(self.tr("Cover"))
        self.cover_radio.setChecked(True)  # Default selection
        type_layout.addWidget(self.cover_radio)

        self.dustjacket_radio = QRadioButton(self.tr("Dustjacket"))
        type_layout.addWidget(self.dustjacket_radio)

        type_group.setLayout(type_layout)
        layout.addWidget(type_group)

        # Result display
        result_group = QGroupBox(self.tr("Calculated Spine Width"))
        result_layout = QVBoxLayout()

        self.result_label = QLabel(
            self.tr("Spine Width: {width}mm").format(width="0.000")
        )
        self.result_label.setStyleSheet("font-size: 16px; font-weight: bold;")
        self.result_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        result_layout.addWidget(self.result_label)

        # Additional info label
        self.info_label = QLabel("")
        self.info_label.setStyleSheet("font-size: 11px; color: #666;")
        self.info_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        result_layout.addWidget(self.info_label)

        result_group.setLayout(result_layout)
        layout.addWidget(result_group)

        # Document dimensions table
        dimensions_group = QGroupBox(self.tr("Document Dimensions"))
        dimensions_layout = QVBoxLayout()

        self.dimensions_table = self._setup_document_size_table()
        dimensions_layout.addWidget(self.dimensions_table)

        dimensions_group.setLayout(dimensions_layout)
        layout.addWidget(dimensions_group)

        # Dialog buttons
        button_box = QDialogButtonBox(QDialogButtonBox.StandardButton.Ok)
        button_box.accepted.connect(self.accept)
        layout.addWidget(button_box)

        # Set focus to OK button
        button_box.button(QDialogButtonBox.StandardButton.Ok).setFocus()

    def _connect_signals(self) -> None:
        """Connect UI signals to calculation methods."""
        self.page_spinbox.valueChanged.connect(self._calculate_spine_width)
        self.page_spinbox.valueChanged.connect(self._update_document_sizes)
        self.cover_radio.toggled.connect(self._calculate_spine_width)
        self.cover_radio.toggled.connect(self._update_document_sizes)
        self.dustjacket_radio.toggled.connect(self._calculate_spine_width)
        self.dustjacket_radio.toggled.connect(self._update_document_sizes)

    def _calculate_spine_width(self) -> None:
        """Calculate and display spine width based on current inputs."""
        page_count = self.page_spinbox.value()

        if self.cover_radio.isChecked():
            # Check minimum page count for covers
            if page_count < MINIMUM_COVER_PAGES:
                self.info_label.setText(
                    self.tr("Minimum {pages} pages required for covers").format(
                        pages=MINIMUM_COVER_PAGES
                    )
                )
                self.result_label.setText(self.tr("Spine Width: --"))
                return

            # Use official Lulu formula for covers
            spine_width = calculate_cover_spine_width(page_count)
            self.info_label.setText("")
        else:
            # Use lookup table for dustjackets
            if page_count < 24 or page_count > 800:
                self.info_label.setText(
                    self.tr("Note: Page count outside standard range")
                )
                self.result_label.setText(self.tr("Spine Width: --"))
                return
            else:
                spine_width = get_dustjacket_spine_width(page_count)
                self.info_label.setText("")

        # Update result display with proper formatting
        formatted_width = format_spine_width(spine_width)
        self.result_label.setText(
            self.tr("Spine Width: {width}mm").format(width=formatted_width)
        )

        logger.debug(
            f"Calculated spine width: {spine_width}mm for {page_count} pages "
            f"({'cover' if self.cover_radio.isChecked() else 'dustjacket'})"
        )

    def _setup_document_size_table(self) -> QTableWidget:
        """Create and configure the document dimensions table.

        Returns:
            Configured QTableWidget for displaying document dimensions
        """
        # Count actual number of formats to avoid empty rows
        num_formats = len(BOOK_INTERIOR_SIZES)
        table = QTableWidget(num_formats, 3)  # Exact number of formats, 3 columns
        table.setHorizontalHeaderLabels(
            [
                self.tr("Book Format"),
                self.tr("Trim Size"),
                self.tr("Total Document Size"),
            ]
        )

        # Hide row numbers (vertical header)
        table.verticalHeader().setVisible(False)

        # Make table read-only and improve appearance
        table.setEditTriggers(QTableWidget.EditTrigger.NoEditTriggers)
        table.setAlternatingRowColors(True)
        table.setSelectionBehavior(QTableWidget.SelectionBehavior.SelectRows)

        # Make columns fill the table width proportionally
        header = table.horizontalHeader()
        header.setSectionResizeMode(0, QHeaderView.ResizeMode.Stretch)
        header.setSectionResizeMode(1, QHeaderView.ResizeMode.Stretch)
        header.setSectionResizeMode(2, QHeaderView.ResizeMode.Stretch)

        # Set relative stretch factors (all equal for 1/3 each)
        header.setStretchLastSection(False)

        # Populate format names (rows)
        for row, format_key in enumerate(BOOK_INTERIOR_SIZES):
            format_name = self._format_book_name(format_key)
            table.setItem(row, 0, QTableWidgetItem(format_name))

        return table

    def _format_book_name(self, key: str) -> str:
        """Convert book format key to display name.

        Args:
            key: Format key from BOOK_INTERIOR_SIZES (e.g., 'POCKET_BOOK')

        Returns:
            Formatted display name (e.g., 'Pocket Book')
        """
        # Special handling for US formats to keep "US" uppercase
        if key.startswith("US_"):
            return "US " + key[3:].replace("_", " ").title()
        else:
            return key.replace("_", " ").title()

    def _get_spine_width_for_table(self) -> float:
        """Get spine width for table calculations.

        Always returns a valid spine width, even when page count
        is outside normal ranges.

        Returns:
            Spine width in millimeters
        """
        page_count = self.page_spinbox.value()

        if self.cover_radio.isChecked():
            # Always calculate for covers, even below minimum
            return calculate_cover_spine_width(page_count)
        else:
            # For dustjackets, use lookup or minimum
            if 24 <= page_count <= 800:
                return get_dustjacket_spine_width(page_count)
            else:
                return 6.0  # Minimum dustjacket spine width

    def _calculate_document_size(
        self, trim_width: float, trim_height: float
    ) -> tuple[float, float]:
        """Calculate total document dimensions for a book format.

        Args:
            trim_width: Trim width in millimeters
            trim_height: Trim height in millimeters

        Returns:
            Tuple of (total_width, total_height) in millimeters
        """
        spine_width = self._get_spine_width_for_table()

        if self.cover_radio.isChecked():
            # Cover calculation: front + spine + back + bleeds
            total_width = (trim_width * 2) + spine_width + (COVER_BLEED * 2)
            total_height = trim_height + (COVER_BLEED * 2)
        else:
            # Dustjacket calculation: flaps + front + spine + back + bleeds + fold safety margins
            # There are 3 fold lines that need safety margins: flap-to-cover, cover-to-spine (x2)
            # Plus 1 fold margin on height
            total_width = (
                (trim_width * 2)
                + spine_width
                + (DUSTJACKET_FLAP_WIDTH * 2)
                + (DUSTJACKET_BLEED * 2)
                + (DUSTJACKET_FOLD_SAFETY_MARGIN * 3)
            )
            total_height = (
                trim_height + (DUSTJACKET_BLEED * 2) + DUSTJACKET_FOLD_SAFETY_MARGIN
            )

        return (total_width, total_height)

    def _format_dimension(self, width: float, height: float) -> str:
        """Format dimensions as a display string.

        Args:
            width: Width in millimeters
            height: Height in millimeters

        Returns:
            Formatted string like '210.00 × 297.00 mm'
        """
        return f"{width:.2f} × {height:.2f} mm"

    def _update_document_sizes(self) -> None:
        """Update all rows in the document dimensions table."""
        for row, (_format_key, (trim_width, trim_height)) in enumerate(
            BOOK_INTERIOR_SIZES.items()
        ):
            # Set trim size column
            trim_size_str = self._format_dimension(trim_width, trim_height)
            self.dimensions_table.setItem(row, 1, QTableWidgetItem(trim_size_str))

            # Calculate and set total document size
            total_width, total_height = self._calculate_document_size(
                trim_width, trim_height
            )
            total_size_str = self._format_dimension(total_width, total_height)
            self.dimensions_table.setItem(row, 2, QTableWidgetItem(total_size_str))

        logger.debug(
            f"Updated document sizes for all formats "
            f"({'cover' if self.cover_radio.isChecked() else 'dustjacket'} mode)"
        )
