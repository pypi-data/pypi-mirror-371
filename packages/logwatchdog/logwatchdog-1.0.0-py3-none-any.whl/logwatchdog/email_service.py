"""
Email Service Module
====================

This module provides email notification functionality for the LogWatchdog system.
It handles sending alert emails when exceptions are detected in monitored log files.

The service uses SMTP to send emails and supports:
- TLS encryption for secure email transmission
- Configurable SMTP server settings
- Multiple recipient support
- Parameter-based configuration
- Error handling and logging

Configuration is passed as parameters for security and flexibility.
"""

import os
import smtplib
from email.mime.text import MIMEText

def send_email(subject: str, body: str, smtp_server: str, smtp_port: int, 
               email_user: str, email_password: str, receiver_group: str):
    """
    Send email to all recipients in the configured receiver group.
    
    This function creates and sends an email alert using the configured SMTP
    server. It supports TLS encryption and handles authentication automatically.
    
    Args:
        subject (str): The email subject line
        body (str): The email body content
        smtp_server (str): SMTP server address
        smtp_port (int): SMTP server port
        email_user (str): Email username/address
        email_password (str): Email password/app password
        receiver_group (str): Comma-separated list of recipient emails
        
    Returns:
        None
        
    Raises:
        smtplib.SMTPException: If there's an SMTP-related error
        Exception: For any other unexpected errors during email sending
        
    Note:
        - Uses TLS encryption for security
        - Sends to all recipients in receiver_group
        - Logs success/failure messages to console
    """
    # Split receiver group into list
    recipients = [email.strip() for email in receiver_group.split(",") if email.strip()]
    
    if not recipients:
        print("[EMAIL ERROR] No valid recipients found in receiver_group")
        return
    
    # Create the email message using MIMEText
    # This provides proper email formatting and headers
    msg = MIMEText(body)
    msg["Subject"] = subject
    msg["From"] = email_user
    msg["To"] = ", ".join(recipients)

    try:
        # Establish connection to SMTP server
        # Using 'with' statement ensures proper connection cleanup
        with smtplib.SMTP(smtp_server, smtp_port) as server:
            # Start TLS encryption for secure communication
            # This encrypts the connection between client and server
            server.starttls()
            
            # Authenticate with the SMTP server using provided credentials
            server.login(email_user, email_password)
            
            # Send the email to all recipients
            # The email is sent from email_user to all addresses in recipients
            server.sendmail(email_user, recipients, msg.as_string())
            
        # Log successful email transmission
        print("[EMAIL] Alert sent successfully.")
        print(f"[EMAIL] Recipients: {', '.join(recipients)}")
        
    except smtplib.SMTPAuthenticationError as e:
        # Handle authentication failures (wrong username/password)
        print(f"[EMAIL ERROR] Authentication failed: {e}")
        print("[EMAIL ERROR] Please check your email_user and email_password")
        
    except smtplib.SMTPConnectError as e:
        # Handle connection failures (server unreachable, wrong port)
        print(f"[EMAIL ERROR] Connection failed: {e}")
        print(f"[EMAIL ERROR] Please check smtp_server ({smtp_server}) and smtp_port ({smtp_port})")
        
    except smtplib.SMTPException as e:
        # Handle other SMTP-related errors
        print(f"[EMAIL ERROR] SMTP error: {e}")
        
    except Exception as e:
        # Handle any other unexpected errors
        print(f"[EMAIL ERROR] Unexpected error: {e}")
        print("[EMAIL ERROR] Please check your configuration and network connection")
