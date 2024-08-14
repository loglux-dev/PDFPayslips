import json
import os
import re
from datetime import datetime
from dateutil.relativedelta import relativedelta
import pdfplumber


class PDFPayslipReader:
    def __init__(self, filepath):
        self.filepath = filepath

    def read_pdf(self):
        with pdfplumber.open(self.filepath) as pdf:
            first_page = pdf.pages[0]
            text = first_page.extract_text()
        return text

    def extract_rows(self):
        text = self.read_pdf()
        rows = text.split('\n')
        return rows

    def extract_info(self):
        rows = self.extract_rows()

        # Extract payment month
        date_range_pattern = r'\d{2}/\d{2}/\d{4}\s*-\s*\d{2}/\d{2}/\d{4}'
        payment_month = None
        for row in rows:
            if re.search(date_range_pattern, row):
                start_date, _ = re.findall(date_range_pattern, row)[0].split(' - ')
                _, start_month, start_year = start_date.split('/')
                payment_month = f"{start_year}-{start_month}"
                break

        if not payment_month:
            pay_period_pattern = r'Pay Period\s+([A-Za-z]{3})\s+(\d{2})'
            for row in rows:
                if re.search(pay_period_pattern, row):
                    month_str, year_str = re.findall(pay_period_pattern, row)[0]
                    month = datetime.strptime(month_str, "%b").month
                    year = 2000 + int(year_str)
                    payment_month = f"{year}-{month:02d}"

        # Extract salary, NOC Shift Differential, RCA, Overtime, RTC, Bonus
        payment_patterns = {
            'Salary': r'Salary\s+(\d+,\d+\.\d+)',
            'NOC Shift Differential': r'NOC Shift Differential\s+(\d+\.\d+)',
            'RCA': r'RCA\s+(\d+,\d+\.\d+)',
            'Overtimes': r'OT x 1\.5\s+\d+\.\d+\s+\d+\.\d+\s+(\d+\.\d+)',
            'RTC': r'RTC\s+(\d+,\d+\.\d+)',
            'Bonus': r'Bonus\s+(\d+,\d+\.\d+)'
        }

        payment_info = {}
        for row in rows:
            for payment, pattern in payment_patterns.items():
                match = re.search(pattern, row)
                if match:
                    amount = float(match.group(1).replace(',', ''))
                    payment_info[payment] = amount

        payslip_info = [{'payment_month': payment_month, 'payments': payment_info}]

        return payslip_info

    def save_to_json(self, payslip_info, output_file):
        with open(output_file, 'w') as f:
            json.dump(payslip_info, f, indent=2, ensure_ascii=False)

    @staticmethod
    def summarize_payments_from_json(json_file, start_date=None, end_date=None, print_output=True):
        with open(json_file, 'r') as f:
            payslip_data = json.load(f)

        if not payslip_data:
            print("Warning: The JSON file is empty.")
            return {}

        min_date = max_date = datetime.strptime(payslip_data[0]['payment_month'], "%Y-%m")
        summary = {}

        actual_start_date = None
        actual_end_date = None

        for payslip_info in payslip_data:
            date_str = payslip_info['payment_month']
            payslip_date = datetime.strptime(date_str, "%Y-%m")

            min_date = min(min_date, payslip_date)
            max_date = max(max_date, payslip_date)

            if start_date and payslip_date < datetime.strptime(start_date, "%Y-%m"):
                continue
            if end_date and payslip_date > datetime.strptime(end_date, "%Y-%m"):
                continue

            if actual_start_date is None or payslip_date < actual_start_date:
                actual_start_date = payslip_date

            if actual_end_date is None or payslip_date > actual_end_date:
                actual_end_date = payslip_date

            for payment, amount in payslip_info['payments'].items():
                if payment not in summary:
                    summary[payment] = 0
                summary[payment] += amount

        if print_output:
            if start_date or end_date:
                print(
                    f"Requested date range: {start_date or min_date.strftime('%Y-%m')} to {end_date or max_date.strftime('%Y-%m')}")
            print(
                f"Available date range in the JSON file: {min_date.strftime('%Y-%m')} to {max_date.strftime('%Y-%m')}")

            if actual_start_date and actual_end_date:
                print(
                    f"Actual output date range: {actual_start_date.strftime('%Y-%m')} to {actual_end_date.strftime('%Y-%m')}")
            else:
                print("No data found in the requested date range.")

        return summary, actual_start_date, actual_end_date

    @staticmethod
    def summarize_additional_payments_from_json(json_file, start_date=None, end_date=None, additional_payments = ['Overtimes', 'NOC Shift Differential', 'Bonus']):
        payments_summary, actual_start_date, actual_end_date = PDFPayslipReader.summarize_payments_from_json(json_file,
                                                                                                             start_date,
                                                                                                             end_date,
                                                                                                             print_output=False)
        # additional_payments = ['Overtimes', 'NOC Shift Differential', 'Bonus']
        total_additional_payments = 0

        for payment in additional_payments:
            if payment in payments_summary:
                total_additional_payments += payments_summary[payment]

        return total_additional_payments, actual_start_date, actual_end_date

    @staticmethod
    def check_date_range_gaps(json_file):
        with open(json_file, 'r') as f:
            payslip_data = json.load(f)

        if not payslip_data:
            print("Warning: The JSON file is empty.")
            return

        payslip_dates = [datetime.strptime(payslip_info['payment_month'], "%Y-%m") for payslip_info in payslip_data]
        payslip_dates.sort()

        min_date, max_date = payslip_dates[0], payslip_dates[-1]
        current_date = min_date
        missing_dates = []

        while current_date <= max_date:
            if current_date not in payslip_dates:
                missing_dates.append(current_date.strftime('%Y-%m'))
            current_date = current_date + relativedelta(months=1)

        if missing_dates:
            print(f"Warning: Payslip data is missing for the following month(s): {', '.join(missing_dates)}")
        else:
            print("No gaps found in the payslip data.")


    def print_extracted_info(self):
        payslip_info = self.extract_info()
        for employee_info in payslip_info:
            print(employee_info)


# Example usage:
if __name__ == '__main__':
    folder_path = 'payslips/'
    all_payslip_info = []

    payslip_reader = PDFPayslipReader(None)

    for filename in os.listdir(folder_path):
        if filename.lower().endswith('.pdf'):
            file_path = os.path.join(folder_path, filename)
            print(f"Processing {file_path}")
            payslip_reader = PDFPayslipReader(file_path)
            payslip_info = payslip_reader.extract_info()
            print(payslip_info)
            all_payslip_info.extend(payslip_info)

    output_file = 'payslip_data.json'
    payslip_reader.save_to_json(all_payslip_info, output_file)
    print(f"Saved payslip data to {output_file}")

    # Summarize payments from the JSON file
    json_file = 'payslip_data.json'
    summary_from_json, _, _ = PDFPayslipReader.summarize_payments_from_json(json_file)
    print("Summary of payments from JSON file:")
    for payment, total_amount in summary_from_json.items():
        print(f"{payment}: {total_amount:.2f}")

    # Summarize additional payments from the JSON file
    json_file = 'payslip_data.json'
    total_additional_payments_from_json, _, _ = PDFPayslipReader.summarize_additional_payments_from_json(json_file)
    print(f"Total of Overtimes + NOC Shift Differential + Bonus from JSON file: "
          f"{total_additional_payments_from_json:.2f}")
