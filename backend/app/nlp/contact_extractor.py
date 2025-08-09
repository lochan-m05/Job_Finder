import re
import phonenumbers
from phonenumbers import geocoder, carrier, PhoneNumberType
from email_validator import validate_email, EmailNotValidError
from typing import List, Dict, Any, Optional, Tuple
import requests
from urllib.parse import urlparse, urljoin
import logging
from bs4 import BeautifulSoup
import whois
from datetime import datetime

logger = logging.getLogger(__name__)

class ContactExtractor:
    """Advanced contact information extraction and validation"""
    
    def __init__(self):
        self.common_email_domains = {
            'gmail.com', 'yahoo.com', 'hotmail.com', 'outlook.com', 'live.com',
            'aol.com', 'icloud.com', 'protonmail.com', 'tutanota.com'
        }
        
        self.business_email_indicators = {
            'hr', 'recruitment', 'careers', 'jobs', 'hiring', 'talent',
            'people', 'human', 'resources', 'contact', 'info', 'admin'
        }
        
        self.social_media_patterns = {
            'linkedin': r'(?:https?://)?(?:www\.)?linkedin\.com/(?:in/|company/|pub/)([a-zA-Z0-9\-_]+)',
            'twitter': r'(?:https?://)?(?:www\.)?twitter\.com/([a-zA-Z0-9_]+)',
            'facebook': r'(?:https?://)?(?:www\.)?facebook\.com/([a-zA-Z0-9\._-]+)',
            'instagram': r'(?:https?://)?(?:www\.)?instagram\.com/([a-zA-Z0-9\._]+)'
        }
    
    def extract_all_contacts(self, text: str, source_url: str = None) -> Dict[str, Any]:
        """
        Extract all contact information from text
        
        Args:
            text: Text to extract contacts from
            source_url: Source URL for context
            
        Returns:
            Dictionary containing all extracted contact information
        """
        contacts = {
            'emails': [],
            'phones': [],
            'social_profiles': {},
            'names': [],
            'addresses': [],
            'websites': []
        }
        
        # Extract emails
        contacts['emails'] = self.extract_emails(text)
        
        # Extract and validate phone numbers
        contacts['phones'] = self.extract_phones(text)
        
        # Extract social media profiles
        contacts['social_profiles'] = self.extract_social_profiles(text)
        
        # Extract names
        contacts['names'] = self.extract_names(text)
        
        # Extract addresses
        contacts['addresses'] = self.extract_addresses(text)
        
        # Extract websites
        contacts['websites'] = self.extract_websites(text)
        
        # Validate and score contacts
        contacts = self.validate_and_score_contacts(contacts, source_url)
        
        return contacts
    
    def extract_emails(self, text: str) -> List[Dict[str, Any]]:
        """Extract and validate email addresses"""
        email_pattern = r'\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}\b'
        found_emails = re.findall(email_pattern, text)
        
        validated_emails = []
        
        for email in set(found_emails):  # Remove duplicates
            email_info = self.validate_email_address(email)
            if email_info:
                validated_emails.append(email_info)
        
        # Sort by business relevance
        validated_emails.sort(key=lambda x: x['business_score'], reverse=True)
        
        return validated_emails
    
    def validate_email_address(self, email: str) -> Optional[Dict[str, Any]]:
        """Validate and analyze email address"""
        try:
            # Basic validation
            validated = validate_email(email)
            email = validated.email
            
            # Extract domain
            domain = email.split('@')[1].lower()
            
            # Determine if it's a business email
            is_business = domain not in self.common_email_domains
            
            # Calculate business score
            business_score = self.calculate_email_business_score(email)
            
            return {
                'email': email,
                'domain': domain,
                'is_business': is_business,
                'is_verified': False,  # Will be verified separately
                'business_score': business_score,
                'extracted_at': datetime.utcnow().isoformat()
            }
            
        except EmailNotValidError:
            return None
    
    def calculate_email_business_score(self, email: str) -> float:
        """Calculate how likely an email is to be business-related"""
        score = 0.0
        email_lower = email.lower()
        domain = email.split('@')[1].lower()
        
        # Personal email domains get lower score
        if domain in self.common_email_domains:
            score -= 0.3
        else:
            score += 0.4
        
        # Business-related keywords in email prefix
        email_prefix = email.split('@')[0].lower()
        for indicator in self.business_email_indicators:
            if indicator in email_prefix:
                score += 0.2
        
        # Common business patterns
        if any(pattern in email_prefix for pattern in ['hr', 'careers', 'jobs', 'recruitment']):
            score += 0.3
        
        # Avoid obvious personal patterns
        if any(pattern in email_prefix for pattern in ['personal', 'private', 'me', 'my']):
            score -= 0.2
        
        return max(0.0, min(1.0, score))
    
    def extract_phones(self, text: str) -> List[Dict[str, Any]]:
        """Extract and validate phone numbers"""
        # Enhanced phone patterns for Indian numbers
        phone_patterns = [
            r'\+91[\s\-]?[6-9]\d{9}',  # +91 format
            r'91[\s\-]?[6-9]\d{9}',    # 91 format without +
            r'[6-9]\d{9}',             # 10 digit Indian mobile
            r'\(\+91\)[\s\-]?[6-9]\d{9}',  # (+91) format
            r'0[1-9]\d{8,9}',          # Landline with STD code
            r'\d{3}[\s\-]\d{3}[\s\-]\d{4}',  # XXX-XXX-XXXX format
            r'\d{4}[\s\-]\d{3}[\s\-]\d{3}',  # XXXX-XXX-XXX format
        ]
        
        found_phones = set()
        
        for pattern in phone_patterns:
            matches = re.findall(pattern, text)
            found_phones.update(matches)
        
        validated_phones = []
        
        for phone in found_phones:
            phone_info = self.validate_phone_number(phone)
            if phone_info:
                validated_phones.append(phone_info)
        
        return validated_phones
    
    def validate_phone_number(self, phone: str) -> Optional[Dict[str, Any]]:
        """Validate and analyze phone number"""
        try:
            # Clean phone number
            clean_phone = re.sub(r'[\s\-\(\)]', '', phone)
            
            # Try to parse as Indian number
            try:
                parsed = phonenumbers.parse(clean_phone, "IN")
            except:
                # Try with +91 prefix
                parsed = phonenumbers.parse(f"+91{clean_phone}", "IN")
            
            if phonenumbers.is_valid_number(parsed):
                formatted = phonenumbers.format_number(parsed, phonenumbers.PhoneNumberFormat.E164)
                national = phonenumbers.format_number(parsed, phonenumbers.PhoneNumberFormat.NATIONAL)
                
                # Get carrier and location info
                carrier_name = carrier.name_for_number(parsed, "en")
                location = geocoder.description_for_number(parsed, "en")
                
                # Check if it's a mobile number
                number_type = phonenumbers.number_type(parsed)
                is_mobile = number_type in [PhoneNumberType.MOBILE, PhoneNumberType.FIXED_LINE_OR_MOBILE]
                
                # Check for WhatsApp likelihood (mobile numbers in India)
                is_whatsapp_likely = is_mobile and str(parsed.country_code) == "91"
                
                return {
                    'number': formatted,
                    'national_format': national,
                    'country_code': f"+{parsed.country_code}",
                    'is_mobile': is_mobile,
                    'is_whatsapp_likely': is_whatsapp_likely,
                    'carrier': carrier_name,
                    'location': location,
                    'is_verified': False,
                    'extracted_at': datetime.utcnow().isoformat()
                }
                
        except Exception as e:
            logger.debug(f"Phone validation failed for {phone}: {e}")
        
        return None
    
    def extract_social_profiles(self, text: str) -> Dict[str, str]:
        """Extract social media profile URLs"""
        profiles = {}
        
        for platform, pattern in self.social_media_patterns.items():
            matches = re.findall(pattern, text, re.IGNORECASE)
            if matches:
                # Take the first match for each platform
                username = matches[0]
                if platform == 'linkedin':
                    profiles[platform] = f"https://linkedin.com/in/{username}"
                elif platform == 'twitter':
                    profiles[platform] = f"https://twitter.com/{username}"
                elif platform == 'facebook':
                    profiles[platform] = f"https://facebook.com/{username}"
                elif platform == 'instagram':
                    profiles[platform] = f"https://instagram.com/{username}"
        
        return profiles
    
    def extract_names(self, text: str) -> List[Dict[str, Any]]:
        """Extract potential contact names"""
        names = []
        
        # Common name patterns in job postings
        name_patterns = [
            r'Contact:?\s+([A-Z][a-z]+\s+[A-Z][a-z]+)',
            r'HR:?\s+([A-Z][a-z]+\s+[A-Z][a-z]+)',
            r'Recruiter:?\s+([A-Z][a-z]+\s+[A-Z][a-z]+)',
            r'Manager:?\s+([A-Z][a-z]+\s+[A-Z][a-z]+)',
            r'([A-Z][a-z]+\s+[A-Z][a-z]+)\s*-\s*HR',
            r'([A-Z][a-z]+\s+[A-Z][a-z]+)\s*-\s*Recruiter',
        ]
        
        for pattern in name_patterns:
            matches = re.findall(pattern, text)
            for match in matches:
                if self.is_valid_name(match):
                    names.append({
                        'name': match.strip(),
                        'confidence': 0.8,
                        'context': 'recruiter',
                        'extracted_at': datetime.utcnow().isoformat()
                    })
        
        return names
    
    def is_valid_name(self, name: str) -> bool:
        """Check if extracted text is likely a valid name"""
        # Basic validation
        if len(name) < 4 or len(name) > 50:
            return False
        
        # Should contain only letters and spaces
        if not re.match(r'^[A-Za-z\s]+$', name):
            return False
        
        # Should have at least first and last name
        parts = name.split()
        if len(parts) < 2:
            return False
        
        # Common non-name words to exclude
        invalid_words = {
            'Team', 'Department', 'Manager', 'Director', 'Head', 'Lead',
            'Company', 'Organization', 'Group', 'Division', 'Office'
        }
        
        if any(word in invalid_words for word in parts):
            return False
        
        return True
    
    def extract_addresses(self, text: str) -> List[Dict[str, Any]]:
        """Extract physical addresses"""
        addresses = []
        
        # Indian address patterns
        address_patterns = [
            r'(\d+[^,\n]*(?:Road|Street|Lane|Avenue|Park|Nagar|Colony|Society)[^,\n]*,\s*[^,\n]*,\s*[^,\n]*\s*-?\s*\d{6})',
            r'([A-Z][^,\n]*(?:Bangalore|Mumbai|Delhi|Chennai|Hyderabad|Pune|Kolkata|Ahmedabad|Gurgaon|Noida)[^,\n]*\s*-?\s*\d{6})'
        ]
        
        for pattern in address_patterns:
            matches = re.findall(pattern, text, re.IGNORECASE)
            for match in matches:
                address_text = match.strip()
                if len(address_text) > 20:  # Reasonable address length
                    addresses.append({
                        'address': address_text,
                        'type': 'office',
                        'confidence': 0.7,
                        'extracted_at': datetime.utcnow().isoformat()
                    })
        
        return addresses
    
    def extract_websites(self, text: str) -> List[Dict[str, Any]]:
        """Extract website URLs"""
        url_pattern = r'https?://(?:[-\w.])+(?:[:\d]+)?(?:/(?:[\w/_.])*(?:\?(?:[\w&=%.])*)?(?:#(?:[\w.])*)?)?'
        
        found_urls = re.findall(url_pattern, text)
        websites = []
        
        for url in set(found_urls):
            parsed = urlparse(url)
            if parsed.netloc:
                websites.append({
                    'url': url,
                    'domain': parsed.netloc,
                    'type': self.classify_website_type(parsed.netloc),
                    'extracted_at': datetime.utcnow().isoformat()
                })
        
        return websites
    
    def classify_website_type(self, domain: str) -> str:
        """Classify website type based on domain"""
        domain_lower = domain.lower()
        
        if any(social in domain_lower for social in ['linkedin', 'twitter', 'facebook', 'instagram']):
            return 'social'
        elif any(job in domain_lower for job in ['naukri', 'indeed', 'monster', 'jobs']):
            return 'job_board'
        elif any(email in domain_lower for email in ['gmail', 'yahoo', 'outlook', 'hotmail']):
            return 'email_provider'
        else:
            return 'company'
    
    def validate_and_score_contacts(self, contacts: Dict[str, Any], source_url: str = None) -> Dict[str, Any]:
        """Validate and score all extracted contacts"""
        
        # Add overall confidence scores
        for email in contacts['emails']:
            email['overall_score'] = self.calculate_overall_email_score(email, source_url)
        
        for phone in contacts['phones']:
            phone['overall_score'] = self.calculate_overall_phone_score(phone, source_url)
        
        # Sort by overall scores
        contacts['emails'].sort(key=lambda x: x['overall_score'], reverse=True)
        contacts['phones'].sort(key=lambda x: x['overall_score'], reverse=True)
        
        return contacts
    
    def calculate_overall_email_score(self, email_info: Dict[str, Any], source_url: str = None) -> float:
        """Calculate overall score for email address"""
        score = email_info.get('business_score', 0.0)
        
        # Bonus for business domains
        if email_info.get('is_business', False):
            score += 0.2
        
        # Context bonus based on source
        if source_url:
            domain = email_info.get('domain', '')
            if domain in source_url:
                score += 0.3  # Same domain as source
        
        return min(1.0, score)
    
    def calculate_overall_phone_score(self, phone_info: Dict[str, Any], source_url: str = None) -> float:
        """Calculate overall score for phone number"""
        score = 0.5  # Base score
        
        # Mobile numbers get higher score
        if phone_info.get('is_mobile', False):
            score += 0.3
        
        # Valid carrier information
        if phone_info.get('carrier'):
            score += 0.1
        
        # WhatsApp likely numbers get bonus
        if phone_info.get('is_whatsapp_likely', False):
            score += 0.1
        
        return min(1.0, score)
    
    def extract_from_webpage(self, url: str) -> Dict[str, Any]:
        """Extract contacts from a webpage"""
        try:
            headers = {
                'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
            }
            
            response = requests.get(url, headers=headers, timeout=10)
            response.raise_for_status()
            
            soup = BeautifulSoup(response.content, 'html.parser')
            
            # Extract text from relevant sections
            contact_sections = soup.find_all(['div', 'section', 'footer'], 
                                           class_=re.compile(r'contact|about|footer', re.I))
            
            text = ""
            for section in contact_sections:
                text += section.get_text() + "\n"
            
            # If no specific sections found, use all text
            if not text.strip():
                text = soup.get_text()
            
            return self.extract_all_contacts(text, url)
            
        except Exception as e:
            logger.error(f"Error extracting contacts from webpage {url}: {e}")
            return {}
    
    def verify_email_deliverability(self, email: str) -> Dict[str, Any]:
        """Check email deliverability (basic implementation)"""
        # This is a basic implementation
        # In production, you'd use services like ZeroBounce, Hunter.io, etc.
        
        result = {
            'is_deliverable': None,
            'confidence': 0.0,
            'reason': None
        }
        
        try:
            # Basic format validation
            validated = validate_email(email)
            
            # Check if domain exists (basic DNS check)
            domain = email.split('@')[1]
            
            # This is a placeholder - implement actual verification
            result['is_deliverable'] = True
            result['confidence'] = 0.7
            result['reason'] = 'Format valid, domain exists'
            
        except EmailNotValidError as e:
            result['is_deliverable'] = False
            result['confidence'] = 0.9
            result['reason'] = str(e)
        
        return result
