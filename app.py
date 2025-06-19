from flask import Flask, render_template, request, redirect, session, url_for
import boto3
import json
import requests

app = Flask(__name__)
app.secret_key = 'your_secret_key_here'

COGNITO_USER_POOL_ID = 'your_user_pool_id'
COGNITO_CLIENT_ID = 'your_app_client_id'
COGNITO_REGION = 'your_aws_region'
API_BASE_URL = 'https://your-api-id.execute-api.ap-south-1.amazonaws.com/prod'

cognito_client = boto3.client('cognito-idp', region_name=COGNITO_REGION)

@app.route('/')
def home():
    return render_template('home.html')

@app.route('/login', methods=['POST'])
def login():
    role = request.form['role']
    username = request.form['username']
    password = request.form['password']

    try:
        response = cognito_client.initiate_auth(
            ClientId=COGNITO_CLIENT_ID,
            AuthFlow='USER_PASSWORD_AUTH',
            AuthParameters={
                'USERNAME': username,
                'PASSWORD': password
            }
        )
        session['role'] = role
        session['username'] = username
        if role == 'admin':
            return redirect(url_for('admin_dashboard'))
        elif role == 'hr':
            return redirect(url_for('hr_dashboard'))
    except cognito_client.exceptions.NotAuthorizedException:
        return 'Login failed'

@app.route('/admin')
def admin_dashboard():
    return render_template('admin_dashboard.html')

@app.route('/admin/add_hr', methods=['POST'])
def add_hr():
    hr_id = request.form['hr_id']
    name = request.form['name']
    email = request.form['email']
    payload = {'hr_id': hr_id, 'name': name, 'email': email}
    response = requests.post(f'{API_BASE_URL}/hr', json=payload)
    return redirect(url_for('admin_dashboard')) if response.status_code == 200 else 'Error adding HR: ' + response.text

@app.route('/admin/delete_hr', methods=['POST'])
def delete_hr():
    hr_id = request.form['hr_id']
    response = requests.delete(f'{API_BASE_URL}/hr/{hr_id}')
    return redirect(url_for('admin_dashboard')) if response.status_code == 200 else 'Error deleting HR: ' + response.text

@app.route('/admin/list_hr')
def list_hr():
    response = requests.get(f'{API_BASE_URL}/hr')
    hr_list = response.json().get('hrs', []) if response.status_code == 200 else []
    return render_template('list_hr.html', hr_list=hr_list)

@app.route('/hr')
def hr_dashboard():
    return render_template('hr_dashboard.html')

@app.route('/hr/add_employee', methods=['POST'])
def add_employee():
    emp_id = request.form['emp_id']
    name = request.form['name']
    email = request.form['email']
    payload = {'emp_id': emp_id, 'name': name, 'email': email}
    response = requests.post(f'{API_BASE_URL}/employee', json=payload)
    return redirect(url_for('hr_dashboard')) if response.status_code == 200 else 'Error adding employee: ' + response.text

@app.route('/hr/delete_employee', methods=['POST'])
def delete_employee():
    emp_id = request.form['emp_id']
    response = requests.delete(f'{API_BASE_URL}/employee/{emp_id}')
    return redirect(url_for('hr_dashboard')) if response.status_code == 200 else 'Error deleting employee: ' + response.text

@app.route('/hr/list_employee')
def list_employee():
    response = requests.get(f'{API_BASE_URL}/employee')
    emp_list = response.json().get('employees', []) if response.status_code == 200 else []
    return render_template('list_employee.html', emp_list=emp_list)

@app.route('/hr/submit_leave', methods=['POST'])
def submit_leave():
    emp_id = request.form['emp_id']
    reason = request.form['reason']
    date = request.form['date']
    payload = {'emp_id': emp_id, 'reason': reason, 'date': date}
    response = requests.post(f'{API_BASE_URL}/leave', json=payload)
    return redirect(url_for('hr_dashboard')) if response.status_code == 200 else 'Error submitting leave: ' + response.text

@app.route('/hr/upload_document', methods=['POST'])
def upload_document():
    file = request.files['document']
    emp_id = request.form['emp_id']
    files = {'document': (file.filename, file.read())}
    data = {'emp_id': emp_id}
    response = requests.post(f'{API_BASE_URL}/document', files=files, data=data)
    return redirect(url_for('hr_dashboard')) if response.status_code == 200 else 'Error uploading document: ' + response.text

if __name__ == '__main__':
    app.run(debug=True)
