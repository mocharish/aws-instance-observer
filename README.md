# AWS Instance Performance Monitor

Web app that fetches **CPU utilization** for an EC2 instance from CloudWatch and displays it as a time-series chart.

## Inputs

1. **IP address** — Private IP of the EC2 instance to query
2. **Time period** — How far back to fetch (minutes)
3. **Interval** — Sampling interval in seconds between datapoints

## Requirements

- Python 3.7+
- AWS credentials with access to EC2 (describe) and CloudWatch (get metric statistics).

## Setup

1. **Clone or download** this repo.

2. **Install dependencies:**

   ```bash
   pip install flask flask-cors python-dotenv boto3
   ```

3. **Configure AWS credentials** via a `.env` file in the project root:
   ```
   AWS_ACCESS_KEY=your_access_key_id
   AWS_SECRET_KEY=your_secret_access_key
   AWS_REGION=us-east-1
   ```

## Run

1. Start the server:

   ```bash
   python app.py
   ```

   By default it runs on **http://127.0.0.1:5050**. 

2. Open in a browser:
   ```
   http://127.0.0.1:5050/
   ```
   Use the form to enter IP, period, and interval, then click **Show CPU Chart**.

## API

- **GET /** — Serves the web UI (`index.html`).
- **GET /api/metrics?ip=&lt;private_ip&gt;&period=&lt;minutes&gt;&interval=&lt;seconds&gt;**  
  Returns JSON: `instance_id`, `safety_status`, `datapoints` (CloudWatch CPU utilization).  
  Example: `http://127.0.0.1:5050/api/metrics?ip=172.31.88.161&period=60&interval=300`

## Safety: Termination Protection

The app includes a flag **`ALLOW_TERMINATION`** in `app.py` (default: `False`). When it is `False`, the server attempts to enable **termination protection** on the instance before returning metrics, so the machine is not accidentally terminated. If the IAM user lacks `ec2:ModifyInstanceAttribute`, the UI shows a short note and the chart still loads.
