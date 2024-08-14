import pdfplumber

class PDFPayslipReader:

    def __init__(self, filepath):
        self.filepath = filepath

    def read_pdf(self):
        with pdfplumber.open(self.filepath) as pdf:
            first_page = pdf.pages[0]
            text = first_page.extract_text()
        print(text)
        return text

    def extract_rows(self):
        text = self.read_pdf()
        rows = text.split('\n')
        print(rows[9])
        print(rows[10])
        return rows

    def extract_info(self):
        rows = self.extract_rows()
        payslip_info = {}
        for row in rows:
            key_value = row.split(':', 1)
            if len(key_value) == 2:
                key, value = key_value
                payslip_info[key.strip()] = value.strip()
        return payslip_info

    def print_extracted_info(self):
        payslip_info = self.extract_info()
        for key, value in payslip_info.items():
            print(f"{key}: {value}")

# Example usage:
if __name__ == '__main__':
    payslip_reader = PDFPayslipReader('payslips/UK_Payslip2_Apr2023.pdf')
    payslip_reader.print_extracted_info()
