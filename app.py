from io import BytesIO
import json
from flask import Flask, jsonify,render_template, request, send_file,redirect, url_for
import pandas as pd
from discounted_cashflow import calculate_discounted_cashflow
from werkzeug.exceptions import MethodNotAllowed

pd.options.display.float_format = '{:.2f}'.format
app = Flask(__name__)

@app.route('/')
def index():
    return render_template('index.html')

@app.errorhandler(MethodNotAllowed)
def handle_method_not_allowed(e):
    return redirect(url_for('index'))

@app.route('/calculate', methods=['POST'])
def calculate():
    try:
        # future_file = request.files['futureFile']
        # cashflow_file = request.files['cashflowFile']
        # interest_file = request.files['interestFile']
        # df_future = pd.read_excel(future_file)
        # df_cashflow = pd.read_excel(cashflow_file)
        # df_interest = pd.read_excel(interest_file)

        effect = request.form.get('rate-display',default=0,type=float)
        df_interest = pd.read_excel("QUOTES.xlsx")
        df_cashflow = pd.read_excel("cashflow.xlsx")
        df_future = pd.read_excel("future_value.xlsx")
        present_values = calculate_discounted_cashflow(df_interest,df_cashflow,df_future,effect)
        pv_df = pd.DataFrame(present_values)
        sum_of_cf = pv_df.groupby(["Group"]).sum().reset_index()
        sum_of_cf["Period"] = 'Total'
        sum_of_cf["Amount"] = sum_of_cf["Amount"].round(2)
        

        # output = BytesIO()
        # with pd.ExcelWriter(output, engine="xlsxwriter") as writer:
        #     present_values.to_excel(writer, sheet_name="Sheet1")
        # output.seek(0)

        return render_template('result.html',column_names=pv_df.columns.values, 
        present_values=present_values,sum_of_cf=list(sum_of_cf.values.tolist()))
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
                         attachment_filename='discounted_cash_flows.xlsx',
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
