import sys
import os

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "bin")))
from dependencies import *



class Calendar(QWidget):
    def __init__(self, parent=None, translator=None, lang_code="en"):
        super().__init__(parent)
        self.tr = translator if translator else lambda x: x
        self.lang_code = lang_code  # Сохраняем переданный язык
        # self.setWindowTitle("Календарь в стиле Windows 11")
        self.resize(350, 350)
        self.setStyleSheet("""
            QWidget {
                background-color: rgba(30, 30, 30, 0.9);
                color: white;
                border-radius: 8px;
            }
            QPushButton {
                background-color: transparent;
                color: white;
                font-size: 18px;
                border: none;
                padding: 5px;
                border-radius: 4px;
            }
            QPushButton:hover {
                background-color: rgba(255, 255, 255, 0.1);
            }
            QPushButton:pressed {
                background-color: rgba(255, 255, 255, 0.2);
            }
            #header {
                background-color: transparent;
                color: white;
                border-top-left-radius: 8px;
                border-top-right-radius: 8px;
                padding: 10px;
            }
            #monthYearLabel {
                font-size: 16px;
                font-weight: bold;
                color: white;
            }
            #weekdays {
                font-size: 12px;
                font-weight: bold;
                color: rgba(255, 255, 255, 0.8);
                padding: 5px 0;
            }
            .day {
                font-size: 14px;
                border-radius: 4px;
                min-width: 30px;
                min-height: 30px;
                color: white;
            }
            .day:hover {
                background-color: rgba(255, 255, 255, 0.1);
            }
            .current-day {
                background-color: rgba(255, 255, 255, 0.3);
                color: white;
                font-weight: bold;
            }
            .selected-day {
                background-color: rgba(255, 255, 255, 0.4);
                color: white;
                font-weight: bold;
            }
            .other-month {
                color: rgba(255, 255, 255, 0.5);
            }
            .nav-button {
                border-radius: 4px;
                padding: 5px 10px;
                font-size: 16px;
            }
            .nav-button:hover {
                background-color: rgba(255, 255, 255, 0.2);
            }
        """)
        
        # Добавляем эффект тени
        shadow = QGraphicsDropShadowEffect()
        shadow.setBlurRadius(20)
        shadow.setColor(QColor(0, 0, 0, 150))
        shadow.setOffset(0, 4)
        self.setGraphicsEffect(shadow)
        
        self.current_date = QDate.currentDate()
        self.selected_date = None
        self.initUI()
        
    def mousePressEvent(self, event):
        # Если клик был за пределами виджета, закрываем его
        if not self.rect().contains(event.pos()):
            self.close()
        super().mousePressEvent(event)
        
    def initUI(self):
        main_layout = QVBoxLayout(self)
        main_layout.setContentsMargins(0, 0, 0, 0)
        main_layout.setSpacing(0)
        
        # Header with month/year and navigation
        header = QWidget()
        header.setObjectName("header")
        header_layout = QHBoxLayout(header)
        
        self.prev_month_btn = QPushButton("◀")
        self.prev_month_btn.setObjectName("nav-button")
        self.prev_month_btn.clicked.connect(self.prev_month)
        
        self.month_year_label = QLabel()
        self.month_year_label.setObjectName("monthYearLabel")
        self.month_year_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        
        self.next_month_btn = QPushButton("▶")
        self.next_month_btn.setObjectName("nav-button")
        self.next_month_btn.clicked.connect(self.next_month)
        
        header_layout.addWidget(self.prev_month_btn)
        header_layout.addWidget(self.month_year_label, 1)
        header_layout.addWidget(self.next_month_btn)
        
        main_layout.addWidget(header)
        
        # Weekdays header
        weekdays = [self.tr("Mon"), self.tr("Tue"), self.tr("Wed"), self.tr("Thu"), 
                   self.tr("Fri"), self.tr("Sat"), self.tr("Sun")]
        weekdays_widget = QWidget()
        weekdays_widget.setObjectName("weekdays")
        weekdays_layout = QHBoxLayout(weekdays_widget)
        weekdays_layout.setContentsMargins(0, 5, 0, 5)
        weekdays_layout.setSpacing(0)
        
        for day in weekdays:
            label = QLabel(day)
            label.setAlignment(Qt.AlignmentFlag.AlignCenter)
            weekdays_layout.addWidget(label)
        
        main_layout.addWidget(weekdays_widget)
        
        # Calendar grid - 6 строк
        self.calendar_grid = QGridLayout()
        self.calendar_grid.setHorizontalSpacing(0)
        self.calendar_grid.setVerticalSpacing(0)
        self.calendar_grid.setContentsMargins(5, 5, 5, 5)
        
        main_layout.addLayout(self.calendar_grid)
        
        self.update_calendar()
        
    def update_calendar(self):
        # Update month/year label
        month = self.current_date.toString("MMMM")
        year = self.current_date.toString("yyyy")
        self.month_year_label.setText(f"{month} {year}")
        
        # Clear previous days
        for i in reversed(range(self.calendar_grid.count())): 
            self.calendar_grid.itemAt(i).widget().setParent(None)
        
        # Get first day of month and days in month
        first_day = QDate(self.current_date.year(), self.current_date.month(), 1)
        days_in_month = first_day.daysInMonth()
        
        # Get the weekday of the first day (1 = Monday, 7 = Sunday)
        start_day = first_day.dayOfWeek()
        
        # Get days from previous month to show
        prev_month = first_day.addMonths(-1)
        days_in_prev_month = prev_month.daysInMonth()
        
        # Fill the grid with exactly 6 weeks (42 days)
        day_counter = 1
        current_row = 0
        
        # Previous month days
        prev_month_days_to_show = start_day - 1
        prev_month_start_day = days_in_prev_month - prev_month_days_to_show + 1
        
        for i in range(prev_month_days_to_show):
            day = prev_month_start_day + i
            btn = QPushButton(str(day))
            btn.setProperty("class", "other-month")
            btn.setCursor(Qt.CursorShape.ArrowCursor)
            self.calendar_grid.addWidget(btn, current_row, i % 7)
            
            if (i + 1) % 7 == 0:
                current_row += 1
        
        # Current month days
        current_day = QDate.currentDate()
        for day in range(1, days_in_month + 1):
            btn = QPushButton(str(day))
            btn.setProperty("class", "day")
            
            # Check if this day is selected
            is_selected = (self.selected_date and 
                          day == self.selected_date.day() and 
                          self.current_date.month() == self.selected_date.month() and 
                          self.current_date.year() == self.selected_date.year())
            
            # Check if this is current day
            is_current = (day == current_day.day() and 
                         self.current_date.month() == current_day.month() and 
                         self.current_date.year() == current_day.year())
            
            if is_selected:
                btn.setProperty("class", "selected-day")
            elif is_current:
                btn.setProperty("class", "current-day")
            
            btn.clicked.connect(lambda _, d=day: self.day_clicked(d))
            
            col = (prev_month_days_to_show + day - 1) % 7
            row = (prev_month_days_to_show + day - 1) // 7
            
            self.calendar_grid.addWidget(btn, row, col)
            day_counter += 1
        
        # Next month days to fill exactly 6 weeks (42 cells)
        next_month_days_needed = 42 - (prev_month_days_to_show + days_in_month)
        next_month = first_day.addMonths(1)
        
        for i in range(1, next_month_days_needed + 1):
            btn = QPushButton(str(i))
            btn.setProperty("class", "other-month")
            btn.setCursor(Qt.CursorShape.ArrowCursor)
            
            total_days_shown = prev_month_days_to_show + days_in_month + i - 1
            col = total_days_shown % 7
            row = total_days_shown // 7
            
            self.calendar_grid.addWidget(btn, row, col)
    
    def day_clicked(self, day):
        self.selected_date = QDate(self.current_date.year(), self.current_date.month(), day)
        self.update_calendar()
    
    def prev_month(self):
        self.current_date = self.current_date.addMonths(-1)
        self.update_calendar()
    
    def next_month(self):
        self.current_date = self.current_date.addMonths(1)
        self.update_calendar()
    
    def paintEvent(self, event):
        painter = QPainter(self)
        painter.setRenderHint(QPainter.RenderHint.Antialiasing)
        
        # Draw rounded corners
        rect = self.rect()
        painter.setBrush(QBrush(QColor(30, 30, 30, 230)))
        painter.setPen(Qt.PenStyle.NoPen)
        painter.drawRoundedRect(rect, 8, 8)