from typing import Dict, Any, List
import logging
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
import requests
import json
from datetime import datetime

class AlertManager:
    """Manage and distribute system alerts."""
    
    def __init__(self, config: Dict[str, Any]):
        """Initialize alert manager with configuration.
        
        Args:
            config (Dict[str, Any]): Alert configuration including
                                    email and Slack settings
        """
        self.config = config
        self.logger = logging.getLogger(__name__)
    
    def send_alert(self, alert_type: str, message: str,
                  severity: str = "warning", data: Dict[str, Any] = None):
        """Send alert through configured channels.
        
        Args:
            alert_type (str): Type of alert
            message (str): Alert message
            severity (str): Alert severity (info/warning/critical)
            data (Dict[str, Any], optional): Additional alert data
        """
        try:
            alert = {
                'type': alert_type,
                'message': message,
                'severity': severity,
                'timestamp': datetime.utcnow().isoformat(),
                'data': data or {}
            }
            
            # Send through all configured channels
            if self.config.get('email', {}).get('enabled'):
                self._send_email_alert(alert)
            
            if self.config.get('slack', {}).get('enabled'):
                self._send_slack_alert(alert)
            
            # Log alert
            log_level = {
                'info': logging.INFO,
                'warning': logging.WARNING,
                'critical': logging.ERROR
            }.get(severity, logging.WARNING)
            
            self.logger.log(log_level, f"Alert: {message}")
            
        except Exception as e:
            self.logger.error(f"Error sending alert: {str(e)}")
    
    def _send_email_alert(self, alert: Dict[str, Any]):
        """Send alert via email.
        
        Args:
            alert (Dict[str, Any]): Alert information
        """
        try:
            msg = MIMEMultipart()
            msg['From'] = self.config['email']['sender']
            msg['To'] = ', '.join(self.config['email']['recipients'])
            msg['Subject'] = f"[{alert['severity'].upper()}] {alert['type']}"
            
            body = f"""
            Alert Type: {alert['type']}
            Severity: {alert['severity'].upper()}
            Time: {alert['timestamp']}
            
            Message:
            {alert['message']}
            
            Additional Data:
            {json.dumps(alert['data'], indent=2)}
            """
            
            msg.attach(MIMEText(body, 'plain'))
            
            # Connect to SMTP server and send
            server = smtplib.SMTP(self.config['email']['smtp_server'])
            server.starttls()
            server.login(
                self.config['email']['username'],
                self.config['email']['password']
            )
            server.send_message(msg)
            server.quit()
            
        except Exception as e:
            self.logger.error(f"Error sending email alert: {str(e)}")
    
    def _send_slack_alert(self, alert: Dict[str, Any]):
        """Send alert via Slack webhook.
        
        Args:
            alert (Dict[str, Any]): Alert information
        """
        try:
            # Format Slack message
            color = {
                'info': '#36a64f',
                'warning': '#ffcc00',
                'critical': '#ff0000'
            }.get(alert['severity'], '#cccccc')
            
            message = {
                'attachments': [{
                    'color': color,
                    'title': f"{alert['type']} - {alert['severity'].upper()}",
                    'text': alert['message'],
                    'fields': [
                        {
                            'title': 'Time',
                            'value': alert['timestamp'],
                            'short': True
                        }
                    ],
                    'footer': 'Fraud Detection System'
                }]
            }
            
            # Add data fields if present
            if alert['data']:
                for key, value in alert['data'].items():
                    message['attachments'][0]['fields'].append({
                        'title': key,
                        'value': str(value),
                        'short': True
                    })
            
            # Send to Slack
            response = requests.post(
                self.config['slack']['webhook_url'],
                json=message
            )
            response.raise_for_status()
            
        except Exception as e:
            self.logger.error(f"Error sending Slack alert: {str(e)}")