import smtplib
import json
import csv
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from email.mime.base import MIMEBase
from email import encoders
from datetime import datetime
from pathlib import Path
import pandas as pd
import random
import os
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

def load_config():
    """Load configuration from config.json and override sensitive data with environment variables"""
    with open('config/config.json', 'r') as f:
        config = json.load(f)
    
    # Override sensitive data with environment variables
    config['email']['app_password'] = os.getenv('EMAIL_APP_PASSWORD')
    
    # Override sender email if provided
    if os.getenv('EMAIL_SENDER'):
        config['email']['sender_email'] = os.getenv('EMAIL_SENDER')
    
    # Override receiver emails if provided
    if os.getenv('EMAIL_RECEIVERS'):
        config['email']['receiver_emails'] = os.getenv('EMAIL_RECEIVERS').split(',')
    
    return config

def get_hedge_joke():
    """Generate a random funny joke about Hedge"""
    jokes = [
        "Why did Hedge cross the road? To check if that apartment had a Pool view! 🏊‍♂️",
        "Hedge is so picky about apartments, he once rejected one because it didn't have enough space for his collection of programming memes! 💻",
        "They say Hedge doesn't sleep, he just waits for apartment prices to drop! 😴",
        "Hedge's ideal apartment must have high-speed internet... How else will he debug code at 3 AM? 🌙",
        "Rumor has it, Hedge's perfect apartment needs a balcony big enough for his daily standup meetings... with himself! 🎭",
        "Hedge is so organized, he probably has a spreadsheet of spreadsheets to track his apartment search! 📊",
        "Why does Hedge prefer top floor apartments? Because he's already at the top of his game! 🎯",
        "Hedge's apartment checklist: Good WiFi ✓ Coffee maker space ✓ Debugging room ✓ 🏠",
        "They say Hedge doesn't need an elevator, he recursively takes the stairs! 🪜",
        "What's Hedge's favorite apartment feature? The bug-free windows! 🪟"
    ]
    return random.choice(jokes)

def generate_html_table():
    """Convert apartments.csv into a styled HTML table"""
    df = pd.read_csv('apartments.csv')
    
    # Sort by price
    df['PRICE'] = df['PRICE'].str.replace('$', '').str.replace(',', '').astype(float)
    df = df.sort_values('PRICE')
    df['PRICE'] = df['PRICE'].apply(lambda x: f"${x:,.0f}")
    
    # Style the table
    styled_table = df.to_html(index=False, classes='apartment-table', escape=False)
    
    # Add CSS styling
    css = """
    <style>
        body {
            font-family: Arial, sans-serif;
            line-height: 1.6;
            margin: 20px;
        }
        .apartment-table {
            border-collapse: collapse;
            width: 100%;
            margin: 25px 0;
            font-size: 14px;
            font-family: Arial, sans-serif;
        }
        .apartment-table th {
            background-color: #4CAF50;
            color: white;
            padding: 12px;
            text-align: left;
        }
        .apartment-table td {
            padding: 12px 8px;
            border-bottom: 1px solid #ddd;
        }
        .apartment-table tr:nth-child(even) {
            background-color: #f2f2f2;
        }
        .apartment-table tr:hover {
            background-color: #ddd;
        }
        .section-header {
            margin-top: 20px;
            margin-bottom: 10px;
            padding-bottom: 5px;
            border-bottom: 2px solid #4CAF50;
        }
    </style>
    """
    
    return css + styled_table

def generate_bot_message():
    """Generate a fun bot-like message"""
    current_time = datetime.now().strftime("%I:%M %p")
    
    messages = [
        f"🤖 *beep boop* PB-bot reporting for duty at {current_time}!",
        "<br><br>",
        "I've been scouting Crescent Village like a ninja robot! 🥷",
        "<br><br>",
        "😄 HEDGE HUMOR CIRCUIT ACTIVATED:",
        "--------------------------------<br>",
        get_hedge_joke(),
        "<br><br>",
        "🤔 ANALYSIS MODE ACTIVATED:",
        "--------------------------------<br>",
        "• I've sorted these by price (I'm a thoughtful bot!)<br>",
        "• All units are 2 Bed / 2 Bath (just as requested!)<br>",
        "• Prices range from {min_price} to {max_price}",
        "<br><br>",
        "💡 BOT WISDOM:",
        "--------------------------------<br>",
        "Remember: Time is of the essence in the apartment hunt! These units move faster than my processing speed! 🏃‍♂️",
        "<br><br>",
        "🏠 APARTMENT SCAN RESULTS 🏠",
        "--------------------------------<br>",
        "{table}",  # Table moved to the end
        "<br><br>",
        "🔄 I'll keep monitoring and alert you of any changes!",
        "<br><br>",
        "Beep boop,<br>",
        "PB-bot 🤖<br>",
        "Your Friendly Neighborhood Apartment Scanner",
        "<br><br>",
        "P.S. I've attached the CSV file for Hedge to add to his spreadsheet collection! 📎"
    ]
    
    return "\n".join(messages)

def send_email_alert():
    """Send email alert with apartment data"""
    config = load_config()
    email_config = config['email']
    
    # Create message with formatted date/time
    current_time = datetime.now().strftime("%b-%d-%Y %I:%M %p")
    msg = MIMEMultipart('alternative')
    msg['Subject'] = f"🏠 PB-bot's Apartment Update! ({current_time}) 🤖"
    msg['From'] = email_config['sender_email']
    msg['To'] = ', '.join(email_config['receiver_emails'])  # Join multiple emails with comma
    
    # Get apartment data
    df = pd.read_csv('apartments.csv')
    min_price = df['PRICE'].min()
    max_price = df['PRICE'].max()
    
    # Generate HTML content
    html_table = generate_html_table()
    bot_message = generate_bot_message()
    
    # Wrap the content in HTML structure
    html_content = f"""
    <html>
    <head></head>
    <body>
        {bot_message.format(
            table=html_table,
            min_price=min_price,
            max_price=max_price
        )}
    </body>
    </html>
    """
    
    # Attach HTML content
    msg.attach(MIMEText(html_content, 'html'))
    
    # Attach CSV file
    with open('apartments.csv', 'rb') as f:
        part = MIMEBase('application', 'octet-stream')
        part.set_payload(f.read())
        encoders.encode_base64(part)
        part.add_header(
            'Content-Disposition',
            f'attachment; filename=apartments_{datetime.now().strftime("%Y%m%d_%H%M")}.csv'
        )
        msg.attach(part)
    
    # Send email
    try:
        with smtplib.SMTP(email_config['smtp_server'], email_config['smtp_port']) as server:
            server.starttls()
            server.login(email_config['sender_email'], email_config['app_password'])
            server.send_message(msg, 
                              from_addr=email_config['sender_email'],
                              to_addrs=email_config['receiver_emails'])  # Send to multiple recipients
            print("🤖 PB-bot: Email alert sent successfully! *beep boop*")
            print(f"🤖 PB-bot: Sent to {len(email_config['receiver_emails'])} recipients")
    except Exception as e:
        print(f"🤖 PB-bot: ERROR! My circuits encountered an issue: {str(e)}")

if __name__ == "__main__":
    send_email_alert()
