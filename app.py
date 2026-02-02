from flask import Flask, jsonify, request, send_from_directory
from flask_cors import CORS
from dotenv import load_dotenv
import aws_helper

load_dotenv()

app = Flask(__name__)
CORS(app) 

ALLOW_TERMINATION = False

@app.route('/api/metrics', methods=['GET'])
def metrics_endpoint():
    ip = request.args.get('ip')
    try:
        period = int(request.args.get('period', 60))   
        interval = int(request.args.get('interval', 300)) 
    except ValueError:
        return jsonify({"error": "period and interval must be integers"}), 400

    if not ip:
        return jsonify({"error": "IP address is required"}), 400

    try:
        instance_id = aws_helper.get_instance_id_by_ip(ip)
        if not instance_id:
            return jsonify({"error": "Instance not found"}), 404
        
        status_msg = "Termination Status Unknown"
        if not ALLOW_TERMINATION:
            try:
                aws_helper.set_termination_protection(instance_id, True)
                protection_enabled = aws_helper.get_termination_protection(instance_id)
                status_msg = "Termination Protected" if protection_enabled else "Termination Allowed"
            except Exception:
                status_msg = "Safety note: termination protection could not be enabled (IAM)"
        else:
            try:
                protection_enabled = aws_helper.get_termination_protection(instance_id)
                status_msg = "Termination Protected" if protection_enabled else "Termination Allowed"
            except Exception:
                status_msg = "Termination Status Unknown"

        data = aws_helper.get_cpu_metrics(instance_id, period, interval)
        
        return jsonify({
            "instance_id": instance_id,
            "safety_status": status_msg,
            "datapoints": data
        })
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route('/')
def home():
    return send_from_directory('.', 'index.html')

if __name__ == '__main__':
    import os
    port = int(os.getenv("PORT", "5050"))
    app.run(debug=True, port=port)