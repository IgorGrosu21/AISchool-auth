from datetime import datetime, timezone
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
import hashlib
from html.parser import HTMLParser
import re
import secrets
import smtplib

from jinja2 import Template

from core.settings import (
    BASE_DIR,
    EMAIL_HOST,
    EMAIL_HOST_PASSWORD,
    EMAIL_HOST_USER,
    EMAIL_PORT,
    EMAIL_USE_TLS,
    HOST,
)
from models.models import User


class HTMLToTextConverter(HTMLParser):
    """Convert HTML to plain text with proper formatting"""

    def __init__(self):
        super().__init__()
        self.text = []
        self.current_url = None
        self.in_link = False
        self.link_text = []
        # Block elements that should have line breaks before/after
        self.block_elements = {
            'h1', 'h2', 'h3', 'h4', 'h5', 'h6', 'p', 'div', 'li', 
            'tr', 'td', 'th', 'blockquote', 'pre', 'br'
        }
        self.last_tag = None

    def handle_starttag(self, tag, attrs):
        """Handle opening tags"""
        attrs_dict = dict(attrs)

        # Handle links - extract href
        if tag == 'a' and 'href' in attrs_dict:
            self.current_url = attrs_dict['href']
            self.in_link = True
            self.link_text = []

        # Add line breaks for block elements
        if tag in self.block_elements and self.text and self.text[-1] not in ['\n', '\n\n']:
            if tag == 'br':
                self.text.append('\n')
            elif self.last_tag not in self.block_elements or tag in ['h1', 'h2', 'h3', 'h4', 'h5', 'h6']:
                self.text.append('\n')

        self.last_tag = tag

    def handle_endtag(self, tag):
        """Handle closing tags"""
        if tag == 'a' and self.in_link:
            # Add link text and URL
            link_content = ''.join(self.link_text).strip()
            if link_content:
                if self.current_url and self.current_url != link_content:
                    self.text.append(f"{link_content} ({self.current_url})")
                else:
                    self.text.append(link_content)
            elif self.current_url:
                self.text.append(self.current_url)
            self.in_link = False
            self.current_url = None
            self.link_text = []

        # Add line breaks after block elements
        if tag in self.block_elements:
            if tag in ['h1', 'h2', 'h3', 'h4', 'h5', 'h6', 'p']:
                self.text.append('\n\n')
            elif tag in ['li', 'tr']:
                self.text.append('\n')
            elif tag in ['td', 'th']:
                self.text.append(' ')

        self.last_tag = tag

    def handle_data(self, data):
        """Handle text content"""
        # Skip text in style/script tags
        if self.last_tag in ['style', 'script']:
            return

        text = data.strip()
        if text:
            if self.in_link:
                self.link_text.append(text)
            else:
                self.text.append(text)

    def handle_entityref(self, name):
        """Handle named entities like &copy;"""
        from html import entities
        if name in entities.name2codepoint:
            char = chr(entities.name2codepoint[name])
            if self.in_link:
                self.link_text.append(char)
            else:
                self.text.append(char)

    def handle_charref(self, name):
        """Handle numeric entities like &#169;"""
        try:
            if name.startswith('x'):
                char = chr(int(name[1:], 16))
            else:
                char = chr(int(name))
            if self.in_link:
                self.link_text.append(char)
            else:
                self.text.append(char)
        except (ValueError, OverflowError):
            pass

    def get_text(self):
        """Get the final text content"""
        result = ''.join(self.text)
        # Clean up multiple consecutive newlines (max 2)
        result = re.sub(r'\n{3,}', '\n\n', result)
        # Clean up excessive whitespace
        result = re.sub(r'[ \t]+', ' ', result)
        # Strip leading/trailing whitespace from each line
        lines = [line.strip() for line in result.split('\n')]
        return '\n'.join(lines)


def _html_to_text(html_content: str) -> str:
    """
    Convert HTML content to plain text with proper formatting.

    Features:
    - Extracts URLs from links and appends them
    - Handles block elements with proper line breaks
    - Decodes HTML entities
    - Preserves meaningful structure
    - Removes style/script tags
    """
    converter = HTMLToTextConverter()
    converter.feed(html_content)
    return converter.get_text()

def generate_verification_token(user: User) -> str:
    """Generate a simple verification token (could be enhanced with proper token generation)"""
    token_data = f"{user.email}{secrets.token_urlsafe(16)}"
    return hashlib.sha256(token_data.encode()).hexdigest()[:32]

def send_verification_email(user: User, token: str):
    """Send verification email to user"""
    verify_link = f"{HOST}/verify?pk={user.email}&token={token}"

    template_path = BASE_DIR / "templates" / "verify_email.html"
    with open(template_path, "r", encoding="utf-8") as f:
        template_content = f.read()

    template = Template(template_content)
    now = datetime.now(timezone.utc)
    html_content = template.render(
        username=user.email.split("@")[0],
        verify_url=verify_link,
        now=now
    )

    msg = MIMEMultipart("alternative")
    msg["Subject"] = "Подтвердите свой аккаунт"
    msg["From"] = EMAIL_HOST_USER
    msg["To"] = user.email

    text_content = _html_to_text(html_content)

    part1 = MIMEText(text_content, "plain", "utf-8")
    part2 = MIMEText(html_content, "html", "utf-8")

    msg.attach(part1)
    msg.attach(part2)

    with smtplib.SMTP(EMAIL_HOST, EMAIL_PORT) as server:
        server.starttls(EMAIL_USE_TLS)
        server.login(EMAIL_HOST_USER, EMAIL_HOST_PASSWORD)
        server.send_message(msg)
