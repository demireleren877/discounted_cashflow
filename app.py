from io import BytesIO
import io
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
        sum_of_cf["Amount"] = sum_of_cf["Amount"].round(4)
        

        # output = BytesIO()
        # with pd.ExcelWriter(output, engine="xlsxwriter") as writer:
        #     present_values.to_excel(writer, sheet_name="Sheet1")
        # output.seek(0)

        return render_template('result.html',column_names=pv_df.columns.values, 
        present_values=present_values,sum_of_cf=list(sum_of_cf.values.tolist()))
    except Exception as e:
        return render_template('index.html',error=str(e))

@app.route('/export_to_excel', methods=['POST'])
def export_to_excel():
    filtered_data = request.form.get('filtered_data')
    all_data = json.loads(request.form.get('all_data'))

    if filtered_data and filtered_data != "[]":
        data = pd.DataFrame(json.loads(filtered_data),columns=["Group","Period","Amount"])  
        print(data)  
    else:
        data = pd.DataFrame(all_data)
        data=data[["Group","Period","Amount"]]

    data['Amount'] = data['Amount'].astype(float)
    output = io.BytesIO()
    writer = pd.ExcelWriter(output, engine='xlsxwriter')
    data.to_excel(writer, index=False, sheet_name='Sheet1',header=True)
    writer.close()
    output.seek(0)
    
    return send_file(output, download_name='discounted_cashflow.xlsx', as_attachment=True)


@app.route('/download_example/<filename>', methods=['GET'])
def download_example(filename):
    example_file_path = f'{filename}'

    return send_file(example_file_path,
                     as_attachment=True)

if __name__ == '__main__':
    app.run(debug=True)
