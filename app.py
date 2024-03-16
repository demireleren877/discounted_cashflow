from io import BytesIO
import json
from flask import Flask, jsonify,render_template, request, send_file
import pandas as pd
from discounted_cashflow import calculate_discounted_cashflow


app = Flask(__name__)

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/calculate', methods=['POST'])
def calculate():
    try:
        future_file = request.files['futureFile']
        cashflow_file = request.files['cashflowFile']
        interest_file = request.files['interestFile']
        df_future = pd.read_excel(future_file)
        df_cashflow = pd.read_excel(cashflow_file)
        df_interest = pd.read_excel(interest_file)
        present_values = calculate_discounted_cashflow(df_interest,df_cashflow,df_future)

        # output = BytesIO()
        # with pd.ExcelWriter(output, engine="xlsxwriter") as writer:
        #     present_values.to_excel(writer, sheet_name="Sheet1")
        # output.seek(0)

        return render_template('result.html', present_values=present_values)
    except Exception as e:
        return render_template('index.html',error=str(e))

@app.route('/export/<present_values>', methods=['GET'])
def export_to_excel(present_values):
    try:
        present_values_json = present_values.replace("'", '"')
        if not present_values_json:
            raise ValueError("Present values not found in the URL parameter.")
        present_values = json.loads(present_values_json)
        df = pd.DataFrame(present_values)
        df=df[["Group","Period","Amount"]]
        excel_output = BytesIO()
        df.to_excel(excel_output, index=False, sheet_name='Discounted_Cash_Flows')
        excel_output.seek(0)
        return send_file(excel_output,
                         download_name='discounted_cash_flows.xlsx',
                         as_attachment=True)

    except Exception as e:
        return jsonify({'error': str(e)})

@app.route('/download_example/<filename>', methods=['GET'])
def download_example(filename):
    example_files_dir = 'example_files'  # Directory containing example files
    example_file_path = f'{filename}'

    return send_file(example_file_path,
                     as_attachment=True)

if __name__ == '__main__':
    app.run(debug=True)
