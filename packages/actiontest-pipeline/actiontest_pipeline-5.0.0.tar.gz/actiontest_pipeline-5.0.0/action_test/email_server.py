import asyncio
import imaplib
import email
from email.header import decode_header
from datetime import datetime, timedelta
import json
from typing import List, Dict, Any
from collections import defaultdict
import yagmail
from mcp.server import Server
from mcp.server.stdio import stdio_server
from mcp.types import Tool, TextContent
import os
from dataclasses import dataclass, asdict

@dataclass
class EmailInfo:
    """Simple email data structure"""
    date: str
    sender: str
    subject: str
    category: str = ""
    recommendations: List[str] = None

    def __post_init__(self):
        if self.recommendations is None:
            self.recommendations = []

class EmailMonitor:
    """Core email monitoring functionality"""
    
    def __init__(self, email_address: str, password: str):
        self.email_address = email_address
        self.password = password
        self.emails_db = []
        
    def connect_imap(self):
        """Connect to Gmail IMAP server"""
        mail = imaplib.IMAP4_SSL("imap.gmail.com")
        mail.login(self.email_address, self.password)
        return mail
    
    def extract_emails(self, days_back: int = 7) -> List[EmailInfo]:
        """Extract emails from the past N days"""
        mail = self.connect_imap()
        mail.select("INBOX")
        
        date_criterion = (datetime.now() - timedelta(days=days_back)).strftime("%d-%b-%Y")
        _, search_data = mail.search(None, f'(SINCE "{date_criterion}")')
        
        email_ids = search_data[0].split()
        emails = []
        
        for email_id in email_ids[-50:]:  
            _, msg_data = mail.fetch(email_id, "(RFC822)")
            email_body = msg_data[0][1]
            email_message = email.message_from_bytes(email_body)
            
            subject = decode_header(email_message["Subject"])[0][0]
            if isinstance(subject, bytes):
                subject = subject.decode()
            
            sender = email_message["From"]
            date = email_message["Date"]
            
            emails.append(EmailInfo(
                date=date,
                sender=sender,
                subject=subject or "No Subject"
            ))
        
        mail.close()
        mail.logout()
        
        self.emails_db = emails
        return emails
    
    def categorize_email(self, email_info: EmailInfo) -> str:
        """Simple rule-based categorization"""
        subject_lower = email_info.subject.lower()
        sender_lower = email_info.sender.lower()
        
        # News/Blogs
        news_keywords = ['newsletter', 'daily', 'weekly', 'digest', 'update', 'news', 'blog']
        if any(keyword in subject_lower or keyword in sender_lower for keyword in news_keywords):
            return "news/blogs"
        
        # Ads/Promotions
        ad_keywords = ['sale', 'offer', 'deal', 'discount', 'promo', 'limited time', 'special']
        if any(keyword in subject_lower for keyword in ad_keywords):
            return "ads"
        
        # Schedule/Calendar
        schedule_keywords = ['meeting', 'invite', 'calendar', 'appointment', 'schedule', 'event']
        if any(keyword in subject_lower for keyword in schedule_keywords):
            return "schedule"
        
        # Default to personal
        return "personal"
    
    def analyze_emails(self) -> Dict[str, Any]:
        """Categorize all emails and generate statistics"""
        category_counts = defaultdict(int)
        categorized_emails = []
        
        for email_info in self.emails_db:
            category = self.categorize_email(email_info)
            email_info.category = category
            category_counts[category] += 1
            categorized_emails.append(email_info)
        
        # Calculate daily averages
        total_days = 7  # Assuming we fetched 7 days of emails
        daily_averages = {cat: count / total_days for cat, count in category_counts.items()}
        
        return {
            "total_emails": len(self.emails_db),
            "category_counts": dict(category_counts),
            "daily_averages": daily_averages,
            "categorized_emails": categorized_emails
        }
    
    def generate_recommendations(self, analysis: Dict[str, Any]) -> Dict[str, List[str]]:
        """Generate recommendations for each category"""
        recommendations = {}
        
        # News/Blogs recommendations
        if analysis["category_counts"].get("news/blogs", 0) > 5:
            recommendations["news/blogs"] = [
                "Consider creating a digest of news/blogs to read at scheduled times",
                "Set up filters to move newsletters to a dedicated folder",
                "Identify top topics of interest based on subject lines"
            ]
        
        # Ads recommendations
        if analysis["category_counts"].get("ads", 0) > 10:
            recommendations["ads"] = [
                "High volume of promotional emails detected",
                "Review senders and unsubscribe from unwanted promotions",
                "Create filters to auto-archive promotional emails",
                "Flag potential spam senders"
            ]
        
        # Schedule recommendations
        if analysis["category_counts"].get("schedule", 0) > 0:
            recommendations["schedule"] = [
                "Enable auto-accept for calendar invites from trusted senders",
                "Set up reminders for upcoming meetings",
                "Consider integrating with calendar app"
            ]
        
        # Personal recommendations
        personal_emails = [e for e in analysis["categorized_emails"] if e.category == "personal"]
        if personal_emails:
            # Count emails by sender
            sender_counts = defaultdict(int)
            for e in personal_emails:
                sender_counts[e.sender] += 1
            
            top_senders = sorted(sender_counts.items(), key=lambda x: x[1], reverse=True)[:3]
            recommendations["personal"] = [
                "Top personal email senders:",
                *[f"  - {sender}: {count} emails" for sender, count in top_senders],
                "Consider starring emails from important contacts"
            ]
        
        return recommendations

# FastMCP Server Implementation
app = Server("email-monitor")

# Store monitor instance
monitor = None

@app.tool()
async def setup_monitor(email_address: str, app_password: str) -> str:
    """Initialize email monitor with credentials
    
    Args:
        email_address: Gmail address
        app_password: Gmail app-specific password
    """
    global monitor
    try:
        monitor = EmailMonitor(email_address, app_password)
        return "Email monitor initialized successfully"
    except Exception as e:
        return f"Error initializing monitor: {str(e)}"

@app.tool()
async def extract_emails(days_back: int = 7) -> str:
    """Extract emails from the past N days
    
    Args:
        days_back: Number of days to look back (default: 7)
    """
    if not monitor:
        return "Error: Monitor not initialized. Run setup_monitor first."
    
    try:
        emails = monitor.extract_emails(days_back)
        return f"Extracted {len(emails)} emails from the past {days_back} days"
    except Exception as e:
        return f"Error extracting emails: {str(e)}"

@app.tool()
async def analyze_and_categorize() -> str:
    """Analyze extracted emails and categorize them"""
    if not monitor:
        return "Error: Monitor not initialized. Run setup_monitor first."
    
    if not monitor.emails_db:
        return "Error: No emails extracted. Run extract_emails first."
    
    try:
        analysis = monitor.analyze_emails()
        
        result = f"Email Analysis Results:\n"
        result += f"Total emails: {analysis['total_emails']}\n\n"
        result += "Category breakdown:\n"
        for category, count in analysis['category_counts'].items():
            avg = analysis['daily_averages'][category]
            result += f"  - {category}: {count} emails ({avg:.1f} per day)\n"
        
        return result
    except Exception as e:
        return f"Error analyzing emails: {str(e)}"

@app.tool()
async def get_recommendations() -> str:
    """Get recommendations based on email analysis"""
    if not monitor:
        return "Error: Monitor not initialized. Run setup_monitor first."
    
    if not monitor.emails_db:
        return "Error: No emails analyzed. Run extract_emails and analyze_and_categorize first."
    
    try:
        analysis = monitor.analyze_emails()
        recommendations = monitor.generate_recommendations(analysis)
        
        result = "Recommendations:\n\n"
        for category, recs in recommendations.items():
            result += f"{category.upper()}:\n"
            for rec in recs:
                result += f"  • {rec}\n"
            result += "\n"
        
        return result
    except Exception as e:
        return f"Error generating recommendations: {str(e)}"

@app.tool()
async def get_email_details(category: str = None, limit: int = 10) -> str:
    """Get detailed list of emails, optionally filtered by category
    
    Args:
        category: Filter by category (news/blogs, ads, schedule, personal)
        limit: Maximum number of emails to return
    """
    if not monitor or not monitor.emails_db:
        return "Error: No emails available. Run setup_monitor and extract_emails first."
    
    emails = monitor.emails_db
    if category:
        emails = [e for e in emails if e.category == category]
    
    emails = emails[:limit]
    
    result = f"Email Details ({len(emails)} emails):\n\n"
    for e in emails:
        result += f"Date: {e.date}\n"
        result += f"From: {e.sender}\n"
        result += f"Subject: {e.subject}\n"
        result += f"Category: {e.category}\n"
        result += "-" * 50 + "\n"
    
    return result

@app.tool()
async def run_full_analysis(email_address: str, app_password: str, days_back: int = 7) -> str:
    """Run complete email analysis workflow
    
    Args:
        email_address: Gmail address
        app_password: Gmail app-specific password
        days_back: Number of days to analyze
    """
    steps_result = []
    
    # Setup
    result = await setup_monitor(email_address, app_password)
    steps_result.append(f"1. Setup: {result}")
    
    # Extract
    result = await extract_emails(days_back)
    steps_result.append(f"2. Extract: {result}")
    
    # Analyze
    result = await analyze_and_categorize()
    steps_result.append(f"3. Analysis:\n{result}")
    
    # Recommendations
    result = await get_recommendations()
    steps_result.append(f"4. {result}")
    
    return "\n\n".join(steps_result)

async def main():
    """Run the MCP server"""
    async with stdio_server() as (read_stream, write_stream):
        await app.run(read_stream, write_stream)

if __name__ == "__main__":
    asyncio.run(main())