from celery import current_task
from typing import List, Dict, Any, Optional
import logging
from datetime import datetime
import asyncio
import aiohttp

from app.services.celery_app import celery_app
from app.nlp.contact_extractor import ContactExtractor

logger = logging.getLogger(__name__)

@celery_app.task(bind=True, name="app.tasks.verify_email_addresses")
def verify_email_addresses_task(self, email_addresses: List[str]):
    """
    Verify email addresses for deliverability
    """
    task_id = self.request.id
    
    try:
        logger.info(f"Starting email verification for {len(email_addresses)} addresses")
        
        contact_extractor = ContactExtractor()
        verified_emails = []
        
        total_emails = len(email_addresses)
        
        for i, email in enumerate(email_addresses):
            try:
                # Verify email
                verification_result = contact_extractor.verify_email_deliverability(email)
                
                verified_emails.append({
                    'email': email,
                    'is_deliverable': verification_result.get('is_deliverable'),
                    'confidence': verification_result.get('confidence'),
                    'reason': verification_result.get('reason'),
                    'verified_at': datetime.utcnow().isoformat()
                })
                
                # Update progress
                if (i + 1) % 10 == 0:
                    current_task.update_state(
                        state='PROGRESS',
                        meta={
                            'current': i + 1,
                            'total': total_emails,
                            'status': f'Verified {i + 1}/{total_emails} emails'
                        }
                    )
                
            except Exception as e:
                logger.error(f"Error verifying email {email}: {e}")
                verified_emails.append({
                    'email': email,
                    'is_deliverable': False,
                    'confidence': 0.0,
                    'reason': f'Verification failed: {str(e)}',
                    'verified_at': datetime.utcnow().isoformat()
                })
        
        result = {
            "verified_emails": verified_emails,
            "total_verified": len(verified_emails),
            "deliverable_count": sum(1 for e in verified_emails if e['is_deliverable']),
            "completed_at": datetime.utcnow().isoformat()
        }
        
        logger.info(f"Completed email verification for {len(verified_emails)} addresses")
        return result
        
    except Exception as e:
        logger.error(f"Error in email verification task: {e}")
        raise e

@celery_app.task(bind=True, name="app.tasks.extract_contacts_from_urls")
def extract_contacts_from_urls_task(self, urls: List[str]):
    """
    Extract contact information from multiple URLs
    """
    task_id = self.request.id
    
    try:
        logger.info(f"Starting contact extraction from {len(urls)} URLs")
        
        contact_extractor = ContactExtractor()
        all_contacts = []
        
        total_urls = len(urls)
        
        for i, url in enumerate(urls):
            try:
                # Extract contacts from webpage
                contacts = contact_extractor.extract_from_webpage(url)
                
                if contacts:
                    contacts['source_url'] = url
                    contacts['extracted_at'] = datetime.utcnow().isoformat()
                    all_contacts.append(contacts)
                
                # Update progress
                current_task.update_state(
                    state='PROGRESS',
                    meta={
                        'current': i + 1,
                        'total': total_urls,
                        'status': f'Processed {i + 1}/{total_urls} URLs'
                    }
                )
                
            except Exception as e:
                logger.error(f"Error extracting contacts from {url}: {e}")
                continue
        
        # Aggregate results
        aggregated_emails = []
        aggregated_phones = []
        aggregated_social = {}
        
        for contact_data in all_contacts:
            aggregated_emails.extend(contact_data.get('emails', []))
            aggregated_phones.extend(contact_data.get('phones', []))
            
            for platform, profile in contact_data.get('social_profiles', {}).items():
                if platform not in aggregated_social:
                    aggregated_social[platform] = []
                aggregated_social[platform].append(profile)
        
        # Remove duplicates
        unique_emails = []
        seen_emails = set()
        for email_data in aggregated_emails:
            email = email_data.get('email', '')
            if email not in seen_emails:
                seen_emails.add(email)
                unique_emails.append(email_data)
        
        unique_phones = []
        seen_phones = set()
        for phone_data in aggregated_phones:
            phone = phone_data.get('number', '')
            if phone not in seen_phones:
                seen_phones.add(phone)
                unique_phones.append(phone_data)
        
        result = {
            "extracted_contacts": all_contacts,
            "aggregated_emails": unique_emails,
            "aggregated_phones": unique_phones,
            "aggregated_social": aggregated_social,
            "total_urls_processed": len(all_contacts),
            "completed_at": datetime.utcnow().isoformat()
        }
        
        logger.info(f"Completed contact extraction from {len(all_contacts)} URLs")
        return result
        
    except Exception as e:
        logger.error(f"Error in URL contact extraction task: {e}")
        raise e

@celery_app.task(bind=True, name="app.tasks.validate_phone_numbers")
def validate_phone_numbers_task(self, phone_numbers: List[str]):
    """
    Validate phone numbers for format and carrier information
    """
    task_id = self.request.id
    
    try:
        logger.info(f"Starting phone validation for {len(phone_numbers)} numbers")
        
        contact_extractor = ContactExtractor()
        validated_phones = []
        
        total_phones = len(phone_numbers)
        
        for i, phone in enumerate(phone_numbers):
            try:
                # Validate phone number
                phone_info = contact_extractor.validate_phone_number(phone)
                
                if phone_info:
                    validated_phones.append(phone_info)
                else:
                    validated_phones.append({
                        'original_number': phone,
                        'is_valid': False,
                        'reason': 'Invalid format or number',
                        'validated_at': datetime.utcnow().isoformat()
                    })
                
                # Update progress
                if (i + 1) % 20 == 0:
                    current_task.update_state(
                        state='PROGRESS',
                        meta={
                            'current': i + 1,
                            'total': total_phones,
                            'status': f'Validated {i + 1}/{total_phones} phones'
                        }
                    )
                
            except Exception as e:
                logger.error(f"Error validating phone {phone}: {e}")
                validated_phones.append({
                    'original_number': phone,
                    'is_valid': False,
                    'reason': f'Validation error: {str(e)}',
                    'validated_at': datetime.utcnow().isoformat()
                })
        
        # Calculate statistics
        valid_count = sum(1 for p in validated_phones if p.get('is_valid', True))
        mobile_count = sum(1 for p in validated_phones if p.get('is_mobile', False))
        whatsapp_count = sum(1 for p in validated_phones if p.get('is_whatsapp_likely', False))
        
        result = {
            "validated_phones": validated_phones,
            "total_validated": len(validated_phones),
            "valid_count": valid_count,
            "mobile_count": mobile_count,
            "whatsapp_likely_count": whatsapp_count,
            "completed_at": datetime.utcnow().isoformat()
        }
        
        logger.info(f"Completed phone validation for {len(validated_phones)} numbers")
        return result
        
    except Exception as e:
        logger.error(f"Error in phone validation task: {e}")
        raise e

@celery_app.task(bind=True, name="app.tasks.enrich_contact_profiles")
def enrich_contact_profiles_task(self, contact_ids: List[str]):
    """
    Enrich contact profiles with additional information from social media
    """
    task_id = self.request.id
    
    try:
        logger.info(f"Starting contact profile enrichment for {len(contact_ids)} contacts")
        
        enriched_contacts = []
        total_contacts = len(contact_ids)
        
        for i, contact_id in enumerate(contact_ids):
            try:
                # In real implementation, fetch contact from database
                # Mock enrichment process
                
                enriched_data = {
                    'contact_id': contact_id,
                    'linkedin_profile': None,
                    'twitter_profile': None,
                    'company_info': None,
                    'additional_emails': [],
                    'additional_phones': [],
                    'enriched_at': datetime.utcnow().isoformat()
                }
                
                # Mock LinkedIn enrichment
                enriched_data['linkedin_profile'] = {
                    'url': f'https://linkedin.com/in/contact-{contact_id}',
                    'title': 'Senior Recruiter',
                    'company': 'Tech Company',
                    'location': 'Bangalore, India',
                    'connections': 500
                }
                
                # Mock company information
                enriched_data['company_info'] = {
                    'name': 'Tech Company',
                    'industry': 'Information Technology',
                    'size': '100-500 employees',
                    'website': 'https://techcompany.com'
                }
                
                enriched_contacts.append(enriched_data)
                
                # Update progress
                current_task.update_state(
                    state='PROGRESS',
                    meta={
                        'current': i + 1,
                        'total': total_contacts,
                        'status': f'Enriched {i + 1}/{total_contacts} contacts'
                    }
                )
                
            except Exception as e:
                logger.error(f"Error enriching contact {contact_id}: {e}")
                continue
        
        result = {
            "enriched_contacts": enriched_contacts,
            "total_enriched": len(enriched_contacts),
            "completed_at": datetime.utcnow().isoformat()
        }
        
        logger.info(f"Completed contact enrichment for {len(enriched_contacts)} contacts")
        return result
        
    except Exception as e:
        logger.error(f"Error in contact enrichment task: {e}")
        raise e

@celery_app.task(name="app.tasks.cleanup_duplicate_contacts")
def cleanup_duplicate_contacts_task():
    """
    Periodic task to identify and merge duplicate contacts
    """
    try:
        logger.info("Starting duplicate contact cleanup")
        
        # In real implementation, this would:
        # 1. Query database for potential duplicates
        # 2. Use fuzzy matching on names, emails, phones
        # 3. Merge duplicate records
        # 4. Update references in job records
        
        # Mock implementation
        duplicates_found = 25
        duplicates_merged = 20
        
        result = {
            "duplicates_found": duplicates_found,
            "duplicates_merged": duplicates_merged,
            "cleanup_completed_at": datetime.utcnow().isoformat()
        }
        
        logger.info(f"Completed duplicate contact cleanup: merged {duplicates_merged} duplicates")
        return result
        
    except Exception as e:
        logger.error(f"Error in duplicate contact cleanup: {e}")
        raise e

@celery_app.task(bind=True, name="app.tasks.generate_contact_insights")
def generate_contact_insights_task(self, contact_ids: List[str]):
    """
    Generate insights about contact data quality and trends
    """
    task_id = self.request.id
    
    try:
        logger.info(f"Generating insights for {len(contact_ids)} contacts")
        
        # Mock insights generation
        insights = {
            "contact_quality": {
                "high_quality_contacts": 75,
                "medium_quality_contacts": 20,
                "low_quality_contacts": 5
            },
            "contact_sources": {
                "linkedin": 45,
                "job_postings": 30,
                "company_websites": 15,
                "social_media": 10
            },
            "verification_status": {
                "verified_emails": 68,
                "unverified_emails": 32,
                "valid_phones": 82,
                "invalid_phones": 18
            },
            "response_rates": {
                "email_response_rate": 0.12,
                "phone_response_rate": 0.25,
                "linkedin_response_rate": 0.18
            },
            "contact_types": {
                "recruiters": 60,
                "hr_managers": 25,
                "hiring_managers": 10,
                "other": 5
            }
        }
        
        result = {
            "insights": insights,
            "total_contacts_analyzed": len(contact_ids),
            "generated_at": datetime.utcnow().isoformat()
        }
        
        logger.info("Completed contact insights generation")
        return result
        
    except Exception as e:
        logger.error(f"Error generating contact insights: {e}")
        raise e
