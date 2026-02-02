import boto3
from datetime import datetime, timedelta
import os

def get_aws_client(service):
    """Initializes an AWS client using environment variables."""
    return boto3.client(
        service,
        aws_access_key_id=os.getenv('AWS_ACCESS_KEY'),
        aws_secret_access_key=os.getenv('AWS_SECRET_KEY'),
        region_name=os.getenv('AWS_REGION')
    )

def get_instance_id_by_ip(ip_address):
    """Translates a Private IP address into an AWS Instance ID."""
    ec2 = get_aws_client('ec2')
    # We filter specifically for the private IP provided in the assignment
    response = ec2.describe_instances(
        Filters=[{'Name': 'private-ip-address', 'Values': [ip_address]}]
    )
    
    for reservation in response['Reservations']:
        for instance in reservation['Instances']:
            return instance['InstanceId']
    return None

def set_termination_protection(instance_id, enabled=True):
    """Enables or disables termination protection for the instance."""
    ec2 = get_aws_client('ec2')
    ec2.modify_instance_attribute(
        InstanceId=instance_id,
        DisableApiTermination={'Value': bool(enabled)}
    )

def get_termination_protection(instance_id):
    """Returns True if termination protection is enabled."""
    ec2 = get_aws_client('ec2')
    attr = ec2.describe_instance_attribute(
        InstanceId=instance_id,
        Attribute='disableApiTermination'
    )
    return bool(attr.get('DisableApiTermination', {}).get('Value'))

def get_cpu_metrics(instance_id, time_period_mins, interval_seconds):
    """Fetches the CPU utilization data points from CloudWatch."""
    cw = get_aws_client('cloudwatch')
    
    end_time = datetime.utcnow()
    start_time = end_time - timedelta(minutes=int(time_period_mins))
    
    stats = cw.get_metric_statistics(
        Namespace='AWS/EC2',
        MetricName='CPUUtilization',
        Dimensions=[{'Name': 'InstanceId', 'Value': instance_id}],
        StartTime=start_time,
        EndTime=end_time,
        Period=int(interval_seconds),
        Statistics=['Average'],
        Unit='Percent'
    )
    
    return sorted(stats['Datapoints'], key=lambda x: x['Timestamp'])