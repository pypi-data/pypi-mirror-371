# coding:utf-8
from PySide6.QtWidgets import QWidget, QHBoxLayout
from PySide6.QtGui import QColor, QPainter
from PySide6.QtCore import Qt, Signal

from .button import TransparentToolButton
from ...common.icon import FluentIcon
from ...common.color import themeColor, isDarkTheme
from .label import BodyLabel
from .line_edit import LineEdit


class PageButton(QWidget):
    clicked = Signal(int)

    def __init__(self, page: int, selected=False, parent=None):
        super().__init__(parent)
        self.page: int = page
        self._text = str(page)
        self._isSelected: bool = selected
        self.setFixedSize(32, 32)

    def setSelected(self, isSelected: bool) -> None:
        if self._isSelected == isSelected:
            return
        self._isSelected = isSelected
        self.update()

    def isSelected(self) -> bool:
        return self._isSelected

    def mouseReleaseEvent(self, event):
        if event.button() is Qt.LeftButton:
            self.clicked.emit(self.page)
        self._isSelected = not self._isSelected
        self.update()
        super().mouseReleaseEvent(event)

    def paintEvent(self, event):
        painter = QPainter(self)
        painter.setRenderHints(QPainter.Antialiasing | QPainter.TextAntialiasing)
        painter.setPen(Qt.NoPen)
        rect = self.rect()
        isDark = isDarkTheme()
        c = 0 if isDark else 255
        if self._isSelected:
            painter.setBrush(themeColor())
        else:
            painter.setBrush(QColor(32, 32, 32) if isDark else QColor(255, 255, 255))
        painter.drawRoundedRect(rect, 6, 6)
        
        painter.setPen(QColor(c, c, c) if self._isSelected else (QColor(255, 255, 255) if isDark else QColor(0, 0, 0)))
        painter.drawText(rect, Qt.AlignCenter, self._text)


class Pager(QWidget):
    currentPageChanged = Signal(int)
    
    def __init__(self, pages: int, maxVisible: int, parent=None):
        super().__init__(parent)
        self.__pages: int = pages
        self.__currentPage: int = 0
        self.__maxVisible: int = maxVisible

        self._widgetLayout: QHBoxLayout = QHBoxLayout(self)
        self.__initWidget()
        self.__connectSignalSlot()
        self.__updateButtons()

    def __initWidget(self):
        self.topLabel: BodyLabel = BodyLabel("...")
        self.topLabel.setFixedWidth(20)
        self.topLabel.setAlignment(Qt.AlignCenter)

        self.bottomLabel: BodyLabel = BodyLabel("...")
        self.bottomLabel.setFixedWidth(20)
        self.bottomLabel.setAlignment(Qt.AlignCenter)

        self.topButton: TransparentToolButton = TransparentToolButton(FluentIcon.LEFT_ARROW, self)
        self.bottomButton: TransparentToolButton = TransparentToolButton(FluentIcon.RIGHT_ARROW, self)

        self.previousButton: TransparentToolButton = TransparentToolButton(FluentIcon.CARE_LEFT_SOLID, self)
        self.nextButton: TransparentToolButton = TransparentToolButton(FluentIcon.CARE_RIGHT_SOLID, self)

        self.jumpLabel: BodyLabel = BodyLabel("跳转到")
        self.countLabel: BodyLabel = BodyLabel(f"页 共计 {self.__pages} 页")

        self.jumpEdit: LineEdit = LineEdit(self)
        self.jumpEdit.setFixedWidth(50)

    def __connectSignalSlot(self) -> None:
        self.topButton.clicked.connect(lambda: self._onClicked(1))
        self.bottomButton.clicked.connect(lambda: self._onClicked(self.__pages))
        self.previousButton.clicked.connect(lambda: self._onClicked(self.__currentPage - 1))
        self.nextButton.clicked.connect(lambda: self._onClicked(self.__currentPage + 1))
        self.jumpEdit.returnPressed.connect(self.jumpToPage)

    def __updateButtons(self) -> None:
        for i in reversed(range(self._widgetLayout.count())):
            widget = self._widgetLayout.itemAt(i).widget()
            if widget:
                widget.setParent(None)
            self.topLabel.setParent(self)
            self.bottomLabel.setParent(self)

        self._widgetLayout.addWidget(self.topButton)
        self._widgetLayout.addWidget(self.previousButton)
        enable = self.__currentPage > 1
        self.topButton.setEnabled(enable)
        self.previousButton.setEnabled(enable)

        start = max(1, self.__currentPage - self.__maxVisible // 2)
        end = min(self.__pages, start + self.__maxVisible - 1)
        if end - start + 1 < self.__maxVisible:
            start = max(1, end - self.__maxVisible + 1)

        if start > 2:
            self._addButtonToPage(1)
            self.topLabel.setParent(self)
            self._widgetLayout.addWidget(self.topLabel)
        elif start == 2:
            self._addButtonToPage(1)

        for i in range(start, end + 1):
            self._addButtonToPage(i, selected=(i == self.__currentPage))

        if end < self.__pages - 1:
            self.bottomLabel.setParent(self)
            self._widgetLayout.addWidget(self.bottomLabel)
            self._addButtonToPage(self.__pages)
        elif end == self.__pages - 1:
            self._addButtonToPage(self.__pages)

        enable = self.__currentPage < self.__pages
        self._widgetLayout.addWidget(self.nextButton)
        self._widgetLayout.addWidget(self.bottomButton)
        self.nextButton.setEnabled(enable)
        self.bottomButton.setEnabled(enable)

        self._widgetLayout.addWidget(self.jumpLabel)
        self._widgetLayout.addWidget(self.jumpEdit)
        self._widgetLayout.addWidget(self.countLabel)
        
        self.currentPageChanged.emit(self.__currentPage)

    def currentPage(self) -> int:
        return self.__currentPage

    def pages(self) -> int:
        return self.__pages

    def maxVisible(self) -> int:
        return self.__maxVisible

    def setPages(self, number: int) -> None:
        if self.__pages == number:
            return
        self.__pages = number
        self.countLabel.setText(f"页 共计 {self.__pages} 页")
        self.__updateButtons()

    def setCurrentPage(self, page: int) -> None:
        if page > self.__pages:
            return
        self.__currentPage = page
        self._onClicked(page)
    
    def setMaxVisible(self, number: int) -> None:
        if self.__maxVisible == number or self.__maxVisible > self.__pages:
            return
        self.__maxVisible = number
        self.__updateButtons()

    def _addButtonToPage(self, number: int, selected=False) -> None:
        button = PageButton(number, selected, self)
        button.clicked.connect(self._onClicked)
        self._widgetLayout.addWidget(button)

    def _onClicked(self, page: int) -> None:
        self.__currentPage = page
        self.__updateButtons()

    def jumpToPage(self) -> None:
        try:
            page = int(self.jumpEdit.text())
            if 1 <= page <= self.__pages:
                self.__currentPage = page
                self.__updateButtons()
        except ValueError: ...