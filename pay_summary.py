from info_extra import PDFPayslipReader

# Example usage:
if __name__ == '__main__':
    json_file = 'payslip_data.json'
    start_date = '2022-05'
    end_date = '2023-04'

    PDFPayslipReader.check_date_range_gaps(json_file)

    summary_from_json, _, _ = PDFPayslipReader.summarize_payments_from_json(json_file, start_date, end_date)
    print("Summary of payments from JSON file:")
    for payment, total_amount in summary_from_json.items():
        print(f"{payment}: {total_amount:.2f}")

    # Summarize additional payments for different sets
    additional_payments_list = [['Overtimes', 'NOC Shift Differential', 'Bonus'],
                               ['RTC', 'RCA'],
                               ['Overtimes', 'NOC Shift Differential', 'Bonus', 'RTC', 'RCA'],
                                ['NOC Shift Differential', 'Bonus', 'RTC', 'RCA']]
    for additional_payments in additional_payments_list:
        total_additional_payments_from_json, _, _ = PDFPayslipReader.summarize_additional_payments_from_json(json_file,
                                                                                                             start_date,
                                                                                                             end_date,
                                                                                                             additional_payments)
        output_string = "Total of " + " + ".join(payment for payment in additional_payments) + " from JSON file: "
        # Use the output_string in the print statement
        print(f"{output_string}{total_additional_payments_from_json:.2f}")
