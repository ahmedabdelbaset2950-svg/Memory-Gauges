from app.utils.excel_theme import ExcelTheme


class DashboardReport:

    def __init__(self, workbook):

        self.workbook = workbook
        self.theme = ExcelTheme(workbook)

    # ==========================================================
    # MONTHLY ANALYSIS SHEET
    # ==========================================================

    def _create_monthly_sheet(self, data):

        ws = self.workbook.add_worksheet("Monthly Analysis")

        ws.hide_gridlines(2)
        ws.set_zoom(90)

        ws.set_column("A:G", 18)

        headers = [
            "Month",
            "Jobs",
            "Working Days",
            "Actual Gauges",
            "Wells",
            "Changes",
            "Average Days"
        ]

        for col, title in enumerate(headers):
            ws.write(0, col, title, self.theme.header)

        monthly = data.get("monthly_table", [])

        row = 1

        for item in monthly:

            ws.write(row, 0, item["month"], self.theme.cell)
            ws.write(row, 1, item["jobs"], self.theme.integer)
            ws.write(row, 2, item["days"], self.theme.number)
            ws.write(row, 3, item["gauges"], self.theme.integer)
            ws.write(row, 4, item["wells"], self.theme.integer)
            ws.write(row, 5, item["changes"], self.theme.integer)
            ws.write(row, 6, item["avg_days"], self.theme.number)

            row += 1
            print(monthly)
            print(len(monthly))

        chart = self.workbook.add_chart({"type": "column"})

        chart.add_series({

            "name": "Jobs",

            "categories": [
                "Monthly Analysis",
                1,
                0,
                row - 1,
                0
            ],

            "values": [
                "Monthly Analysis",
                1,
                1,
                row - 1,
                1
            ]

        })

        chart.set_title({"name": "Jobs per Month"})
        chart.set_style(10)
        chart.set_legend({"none": True})

        ws.insert_chart("I2", chart)
    # ==========================================================
    # DASHBOARD SHEET
    # ==========================================================

    def build(self, data):
        self._create_cover_page(data.get("year", ""))

        ws = self.workbook.add_worksheet("Dashboard")

        # ------------------------------------
        # Page Setup
        # ------------------------------------
        ws.hide_gridlines(2)
        ws.set_zoom(90)
        ws.set_landscape()
        ws.set_paper(9)
        ws.fit_to_pages(1, 0)
        ws.set_margins(0.3, 0.3, 0.4, 0.4)

        # ------------------------------------
        # Columns
        # ------------------------------------
        ws.set_column("A:A", 3)
        for c in "BCDEFGHIJKLM":
            ws.set_column(f"{c}:{c}", 16)

        # ------------------------------------
        # Title
        # ------------------------------------
        ws.merge_range("B2:M3", "MGMS Executive Dashboard", self.theme.title)
        ws.write("B5", "Memory Gauge Management System", self.theme.subtitle)

        # ------------------------------------
        # KPI Cards
        # ------------------------------------
        cards = [
            ("Total Jobs", data.get("total_jobs", 0)),
            ("Working Days", data.get("total_days", 0)),
            ("Actual Gauges", data.get("actual_gauges", 0)),
            ("Wells", data.get("wells", 0)),
            ("Changes", data.get("changes", 0)),
            ("Average Days", data.get("avg_job_duration", 0))
        ]

        row = 7
        col = 1

        for title, value in cards:
            ws.merge_range(row, col, row, col + 1, title, self.theme.kpi_title)
            ws.merge_range(row + 1, col, row + 3, col + 1, value, self.theme.kpi_value)
            col += 2

        monthly = data.get("monthly_table", [])
        data_len = len(monthly) if monthly else 1

        # ------------------------------------
        # Chart 1: Monthly Jobs (قراءة البيانات مباشرة من شيت Monthly Analysis)
        # ------------------------------------
        chart1 = self.workbook.add_chart({"type": "column"})

        chart1.add_series({
            "name": "Jobs",
            "categories": [
                "Monthly Analysis",
                1,
                0,
                data_len,
                0
            ],
            "values": [
                "Monthly Analysis",
                1,
                1,
                data_len,
                1
            ],
        })

        chart1.set_x_axis({"name": "Month"})
        chart1.set_y_axis({"name": "Jobs"})
        chart1.set_title({"name": "Monthly Jobs Overview"})
        chart1.set_style(10)
        chart1.set_legend({"none": True})
        chart1.set_size({"width": 480, "height": 260})

        ws.insert_chart("B14", chart1)

        # ------------------------------------
        # Chart 2: Survey Distribution (قراءة البيانات من شيت Survey Analysis)
        # ------------------------------------
        survey_labels = data.get("survey_labels", [])
        survey_len = len(survey_labels) if survey_labels else 1

        chart2 = self.workbook.add_chart({"type": "pie"})

        chart2.add_series({
            "name": "Survey Distribution",
            "categories": [
                "Survey Analysis",
                1,
                0,
                survey_len,
                0
            ],
            "values": [
                "Survey Analysis",
                1,
                1,
                survey_len,
                1
            ],
            "data_labels": {"percentage": True}
        })

        chart2.set_title({"name": "Survey Type Distribution"})
        chart2.set_style(10)
        chart2.set_size({"width": 480, "height": 260})

        ws.insert_chart("H14", chart2)

        # استدعاء وبناء باقي الشيتات الفرعية
        self._create_monthly_sheet(data)
        self._create_survey_sheet(data)
        self._create_job_type_sheet(data)
        self._create_gauge_sheet(data)
        self._create_rig_sheet(data)
        self._create_well_sheet(data)

        return ws
    # ==========================================================
    # SURVEY ANALYSIS SHEET
    # ==========================================================

    def _create_survey_sheet(self, data):

        ws = self.workbook.add_worksheet("Survey Analysis")

        ws.hide_gridlines(2)
        ws.set_zoom(90)

        ws.set_column("A:B", 25)

        ws.write(0, 0, "Survey Type", self.theme.header)
        ws.write(0, 1, "Jobs", self.theme.header)

        labels = data.get("survey_labels", [])
        values = data.get("survey_values", [])

        row = 1

        for label, value in zip(labels, values):

            ws.write(row, 0, label, self.theme.cell)
            ws.write(row, 1, value, self.theme.integer)

            row += 1
        

        chart = self.workbook.add_chart({
            "type": "pie"
        })

        chart.add_series({

            "name": "Survey Distribution",

            "categories": [
                "Survey Analysis",
                1,
                0,
                row - 1,
                0
            ],

            "values": [
                "Survey Analysis",
                1,
                1,
                row - 1,
                1
            ],

            "data_labels": {
                "percentage": True
            }

        })

        chart.set_title({
            "name": "Survey Distribution"
        })

        chart.set_style(10)

        chart.set_size({
            "width": 650,
            "height": 380
        })

        ws.insert_chart("D2", chart)
            # ==========================================================
    # JOB TYPE ANALYSIS
    # ==========================================================

    def _create_job_type_sheet(self, data):

        ws = self.workbook.add_worksheet("Job Type Analysis")

        ws.hide_gridlines(2)
        ws.set_zoom(90)

        ws.set_column("A:B", 25)

        ws.write(0, 0, "Job Type", self.theme.header)
        ws.write(0, 1, "Jobs", self.theme.header)

        labels = data.get("type_labels", [])
        values = data.get("type_values", [])

        row = 1

        for label, value in zip(labels, values):

            ws.write(row, 0, label, self.theme.cell)
            ws.write(row, 1, value, self.theme.integer)

            row += 1

        chart = self.workbook.add_chart({
            "type": "pie"
        })

        chart.add_series({

            "name": "Job Type Distribution",

            "categories": [
                "Job Type Analysis",
                1,
                0,
                row - 1,
                0
            ],

            "values": [
                "Job Type Analysis",
                1,
                1,
                row - 1,
                1
            ],

            "data_labels": {
                "percentage": True
            }

        })

        chart.set_title({
            "name": "Job Type Distribution"
        })

        chart.set_style(10)

        chart.set_size({
            "width": 650,
            "height": 380
        })

        ws.insert_chart("D2", chart)
            # ==========================================================
    # GAUGE UTILIZATION
    # ==========================================================

    def _create_gauge_sheet(self, data):

        ws = self.workbook.add_worksheet("Gauge Utilization")

        ws.hide_gridlines(2)
        ws.set_zoom(90)

        ws.set_column("A:B", 25)

        ws.write(0, 0, "Gauge", self.theme.header)
        ws.write(0, 1, "Working Days", self.theme.header)

        labels = data.get("gauge_labels", [])
        values = data.get("gauge_values", [])

        row = 1

        for label, value in zip(labels, values):

            ws.write(row, 0, label, self.theme.cell)
            ws.write(row, 1, value, self.theme.number)

            row += 1

        chart = self.workbook.add_chart({
            "type": "bar"
        })

        chart.add_series({

            "name": "Working Days",

            "categories": [
                "Gauge Utilization",
                1,
                0,
                row - 1,
                0
            ],

            "values": [
                "Gauge Utilization",
                1,
                1,
                row - 1,
                1
            ],

            "data_labels": {
                "value": True
            }

        })

        chart.set_title({
            "name": "Top Gauges by Working Days"
        })

        chart.set_style(10)

        chart.set_size({
            "width": 700,
            "height": 420
        })

        chart.set_legend({
            "none": True
        })

        ws.insert_chart("D2", chart)
            # ==========================================================
    # RIG ANALYSIS
    # ==========================================================

    def _create_rig_sheet(self, data):

        ws = self.workbook.add_worksheet("Rig Analysis")

        ws.hide_gridlines(2)
        ws.set_zoom(90)

        ws.set_column("A:B", 28)

        ws.write(0, 0, "Rig", self.theme.header)
        ws.write(0, 1, "Jobs", self.theme.header)

        labels = data.get("rig_labels", [])
        values = data.get("rig_values", [])

        row = 1

        for label, value in zip(labels, values):

            ws.write(row, 0, label, self.theme.cell)
            ws.write(row, 1, value, self.theme.integer)

            row += 1

        chart = self.workbook.add_chart({"type": "bar"})

        chart.add_series({

            "name": "Jobs",

            "categories": [
                "Rig Analysis",
                1,
                0,
                row - 1,
                0
            ],

            "values": [
                "Rig Analysis",
                1,
                1,
                row - 1,
                1
            ]

        })

        chart.set_title({"name": "Top Rigs by Jobs"})
        chart.set_style(10)
        chart.set_legend({"none": True})

        ws.insert_chart("D2", chart)
            # ==========================================================
    # WELL ANALYSIS
    # ==========================================================

    def _create_well_sheet(self, data):

        ws = self.workbook.add_worksheet("Well Analysis")

        ws.hide_gridlines(2)
        ws.set_zoom(90)

        ws.set_column("A:B", 28)

        ws.write(0, 0, "Well", self.theme.header)
        ws.write(0, 1, "Jobs", self.theme.header)

        labels = data.get("well_labels", [])
        values = data.get("well_values", [])

        row = 1

        for label, value in zip(labels, values):

            ws.write(row, 0, label, self.theme.cell)
            ws.write(row, 1, value, self.theme.integer)

            row += 1

        chart = self.workbook.add_chart({"type": "bar"})

        chart.add_series({

            "name": "Jobs",

            "categories": [
                "Well Analysis",
                1,
                0,
                row - 1,
                0
            ],

            "values": [
                "Well Analysis",
                1,
                1,
                row - 1,
                1
            ]

        })

        chart.set_title({"name": "Top Wells by Jobs"})
        chart.set_style(10)
        chart.set_legend({"none": True})

        ws.insert_chart("D2", chart)
            # ==========================================================
    # COVER PAGE
    # ==========================================================

    def _create_cover_page(self, year):

        ws = self.workbook.add_worksheet("Cover")

        ws.hide_gridlines(2)
        ws.set_zoom(100)

        ws.set_landscape()

        ws.set_column("A:L", 18)

        ws.merge_range(
            "B3:J5",
            "MGMS Executive Report",
            self.theme.title
        )

        ws.merge_range(
            "B8:J9",
            f"Operations Report - {year}",
            self.theme.kpi_value
        )

        ws.write(
            "B12",
            "Memory Gauge Management System",
            self.theme.subtitle
        )

        ws.write(
            "B14",
            "Generated automatically by MGMS",
            self.theme.subtitle
        )