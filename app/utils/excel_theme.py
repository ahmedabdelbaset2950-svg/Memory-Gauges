import xlsxwriter




class ExcelTheme:

    def __init__(self, workbook):

        self.workbook = workbook

        self._create_formats()

    def _create_formats(self):

        # ==========================
        # COLORS
        # ==========================

        self.NAVY = "#173B68"
        self.BLUE = "#2D5E9C"
        self.LIGHT = "#EEF3F8"
        self.WHITE = "#FFFFFF"
        self.GRAY = "#6B7280"
        self.GREEN = "#27AE60"
        self.YELLOW = "#F4B400"
        self.RED = "#DB4437"

        # ==========================
        # REPORT TITLE
        # ==========================

        self.title = self.workbook.add_format({
            "bold": True,
            "font_size": 22,
            "font_color": self.WHITE,
            "bg_color": self.NAVY,
            "align": "center",
            "valign": "vcenter"
        })

        # ==========================
        # SUB TITLE
        # ==========================

        self.subtitle = self.workbook.add_format({
            "italic": True,
            "font_size": 11,
            "font_color": self.GRAY
        })

        # ==========================
        # TABLE HEADER
        # ==========================

        self.header = self.workbook.add_format({
            "bold": True,
            "bg_color": self.NAVY,
            "font_color": self.WHITE,
            "border": 1,
            "align": "center",
            "valign": "vcenter"
        })

        # ==========================
        # NORMAL CELL
        # ==========================

        self.cell = self.workbook.add_format({
            "border": 1,
            "align": "center",
            "valign": "vcenter"
        })

        # ==========================
        # TEXT CELL
        # ==========================

        self.text = self.workbook.add_format({
            "border": 1,
            "align": "left",
            "valign": "vcenter"
        })

        # ==========================
        # NUMBER
        # ==========================

        self.number = self.workbook.add_format({
            "border": 1,
            "align": "center",
            "num_format": "#,##0.00"
        })

        # ==========================
        # INTEGER
        # ==========================

        self.integer = self.workbook.add_format({
            "border": 1,
            "align": "center",
            "num_format": "#,##0"
        })

        # ==========================
        # KPI TITLE
        # ==========================

        self.kpi_title = self.workbook.add_format({
            "bold": True,
            "font_color": self.WHITE,
            "bg_color": self.BLUE,
            "align": "center",
            "border": 1
        })

        # ==========================
        # KPI VALUE
        # ==========================

        self.kpi_value = self.workbook.add_format({
            "bold": True,
            "font_size": 20,
            "bg_color": self.LIGHT,
            "align": "center",
            "valign": "vcenter",
            "border": 1
        })

        # ==========================
        # SUCCESS
        # ==========================

        self.success = self.workbook.add_format({
            "bg_color": "#E8F5E9",
            "font_color": self.GREEN,
            "bold": True,
            "align": "center",
            "border": 1
        })

        # ==========================
        # WARNING
        # ==========================

        self.warning = self.workbook.add_format({
            "bg_color": "#FFF8E1",
            "font_color": self.YELLOW,
            "bold": True,
            "align": "center",
            "border": 1
        })

        # ==========================
        # DANGER
        # ==========================

        self.danger = self.workbook.add_format({
            "bg_color": "#FDECEC",
            "font_color": self.RED,
            "bold": True,
            "align": "center",
            "border": 1
        })