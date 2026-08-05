import io
import xlsxwriter

from app.utils.dashboard_report import DashboardReport


class ExcelReport:

    def __init__(self):

        self.output = io.BytesIO()

        self.workbook = xlsxwriter.Workbook(
            self.output,
            {"in_memory": True}
        )

    def dashboard(self, data):

        DashboardReport(self.workbook).build(data)

    def save(self):

        self.workbook.close()

        self.output.seek(0)

        return self.output