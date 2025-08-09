import re
import spacy
from typing import List, Dict, Any, Optional
from transformers import pipeline, AutoTokenizer, AutoModelForSequenceClassification
import nltk
from nltk.corpus import stopwords
from nltk.tokenize import word_tokenize, sent_tokenize
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity
import numpy as np
import logging
import os

logger = logging.getLogger(__name__)

class JobAnalyzer:
    """NLP analyzer for job descriptions and requirements"""
    
    def __init__(self):
        self.nlp = None
        self.sentiment_analyzer = None
        self.classifier = None
        self.skill_extractor = None
        self.tfidf_vectorizer = TfidfVectorizer(max_features=1000, stop_words='english')
        self._initialize_models()
    
    def _initialize_models(self):
        """Initialize NLP models and tools"""
        try:
            # Download required NLTK data
            nltk.download('punkt', quiet=True)
            nltk.download('stopwords', quiet=True)
            nltk.download('averaged_perceptron_tagger', quiet=True)
            
            # Load spaCy model
            model_name = os.getenv('SPACY_MODEL', 'en_core_web_sm')
            try:
                self.nlp = spacy.load(model_name)
                logger.info(f"Loaded spaCy model: {model_name}")
            except OSError:
                logger.warning(f"spaCy model {model_name} not found, using basic tokenizer")
                self.nlp = None
            
            # Initialize sentiment analysis
            self.sentiment_analyzer = pipeline(
                "sentiment-analysis",
                model="cardiffnlp/twitter-roberta-base-sentiment-latest",
                device=-1  # Use CPU
            )
            
            # Initialize job category classifier
            # Note: In production, you'd want to train a custom model
            self.classifier = pipeline(
                "zero-shot-classification",
                model="facebook/bart-large-mnli",
                device=-1
            )
            
            logger.info("NLP models initialized successfully")
            
        except Exception as e:
            logger.error(f"Error initializing NLP models: {e}")
    
    def analyze_job_description(self, description: str) -> Dict[str, Any]:
        """
        Comprehensive analysis of job description
        
        Args:
            description: Job description text
            
        Returns:
            Dictionary containing analysis results
        """
        analysis = {
            "skills": [],
            "requirements": [],
            "benefits": [],
            "sentiment_score": 0.0,
            "urgency_score": 0.0,
            "quality_score": 0.0,
            "job_category": None,
            "experience_level": None,
            "salary_mentioned": False,
            "remote_friendly": False,
            "company_size": None
        }
        
        if not description or len(description.strip()) < 50:
            return analysis
        
        try:
            # Extract skills
            analysis["skills"] = self.extract_skills(description)
            
            # Extract requirements
            analysis["requirements"] = self.extract_requirements(description)
            
            # Extract benefits
            analysis["benefits"] = self.extract_benefits(description)
            
            # Sentiment analysis
            analysis["sentiment_score"] = self.analyze_sentiment(description)
            
            # Urgency analysis
            analysis["urgency_score"] = self.analyze_urgency(description)
            
            # Quality assessment
            analysis["quality_score"] = self.assess_quality(description)
            
            # Job categorization
            analysis["job_category"] = self.categorize_job(description)
            
            # Experience level detection
            analysis["experience_level"] = self.detect_experience_level(description)
            
            # Additional features
            analysis["salary_mentioned"] = self.has_salary_info(description)
            analysis["remote_friendly"] = self.is_remote_friendly(description)
            analysis["company_size"] = self.estimate_company_size(description)
            
        except Exception as e:
            logger.error(f"Error analyzing job description: {e}")
        
        return analysis
    
    def extract_skills(self, text: str) -> List[str]:
        """Extract technical and soft skills from text"""
        skills = set()
        
        # Predefined skill lists
        technical_skills = {
            # Programming languages
            "python", "java", "javascript", "typescript", "c++", "c#", "php", "ruby", "go", "rust", "scala", "kotlin",
            "swift", "objective-c", "r", "matlab", "perl", "shell", "bash", "powershell",
            
            # Web technologies
            "html", "css", "sass", "scss", "less", "bootstrap", "tailwind", "react", "angular", "vue.js", "vue",
            "node.js", "express", "django", "flask", "fastapi", "spring", "laravel", "rails", "asp.net",
            
            # Databases
            "sql", "mysql", "postgresql", "oracle", "mongodb", "redis", "elasticsearch", "cassandra", "dynamodb",
            "sqlite", "mariadb", "neo4j", "influxdb",
            
            # Cloud and DevOps
            "aws", "azure", "gcp", "docker", "kubernetes", "jenkins", "gitlab", "github", "bitbucket",
            "terraform", "ansible", "chef", "puppet", "nginx", "apache", "linux", "windows", "macos",
            
            # Data Science and ML
            "machine learning", "deep learning", "ai", "neural networks", "pandas", "numpy", "scikit-learn",
            "tensorflow", "pytorch", "keras", "opencv", "nlp", "computer vision", "data science", "analytics",
            "tableau", "power bi", "excel", "r", "stata", "spss",
            
            # Mobile Development
            "android", "ios", "react native", "flutter", "xamarin", "ionic", "cordova",
            
            # Testing
            "selenium", "cypress", "jest", "junit", "pytest", "mocha", "chai", "cucumber",
            
            # Other tools
            "git", "svn", "jira", "confluence", "slack", "teams", "figma", "sketch", "photoshop",
            "illustrator", "agile", "scrum", "kanban", "devops", "ci/cd"
        }
        
        soft_skills = {
            "leadership", "communication", "teamwork", "problem solving", "analytical thinking",
            "creativity", "adaptability", "time management", "project management", "mentoring",
            "collaboration", "critical thinking", "attention to detail", "customer service"
        }
        
        all_skills = technical_skills.union(soft_skills)
        
        # Convert text to lowercase for matching
        text_lower = text.lower()
        
        # Find skills in text
        for skill in all_skills:
            if skill.lower() in text_lower:
                skills.add(skill)
        
        # Use spaCy for entity recognition if available
        if self.nlp:
            doc = self.nlp(text)
            
            # Extract organizations and technologies
            for ent in doc.ents:
                if ent.label_ in ["ORG", "PRODUCT"]:
                    skills.add(ent.text.lower())
        
        return list(skills)
    
    def extract_requirements(self, text: str) -> List[str]:
        """Extract job requirements from text"""
        requirements = []
        
        # Look for requirement sections
        requirement_patterns = [
            r"requirements?:?\s*(.+?)(?:\n\n|\n[A-Z]|\n•|\n\d+\.|\nNote:|\nBenefits?:|\nWe offer:|\nWhat we offer:|\nSalary:|\nLocation:|$)",
            r"qualifications?:?\s*(.+?)(?:\n\n|\n[A-Z]|\n•|\n\d+\.|\nNote:|\nBenefits?:|\nWe offer:|\nWhat we offer:|\nSalary:|\nLocation:|$)",
            r"must have:?\s*(.+?)(?:\n\n|\n[A-Z]|\n•|\n\d+\.|\nNote:|\nBenefits?:|\nWe offer:|\nWhat we offer:|\nSalary:|\nLocation:|$)",
            r"essential:?\s*(.+?)(?:\n\n|\n[A-Z]|\n•|\n\d+\.|\nNote:|\nBenefits?:|\nWe offer:|\nWhat we offer:|\nSalary:|\nLocation:|$)"
        ]
        
        for pattern in requirement_patterns:
            matches = re.finditer(pattern, text, re.IGNORECASE | re.DOTALL)
            for match in matches:
                req_text = match.group(1).strip()
                
                # Split by bullet points or line breaks
                req_items = re.split(r'\n\s*[•·*-]\s*|\n\s*\d+\.?\s*', req_text)
                
                for item in req_items:
                    item = item.strip()
                    if len(item) > 10 and len(item) < 200:  # Filter reasonable length requirements
                        requirements.append(item)
        
        return requirements[:10]  # Limit to top 10 requirements
    
    def extract_benefits(self, text: str) -> List[str]:
        """Extract job benefits from text"""
        benefits = []
        
        # Look for benefits sections
        benefit_patterns = [
            r"benefits?:?\s*(.+?)(?:\n\n|\n[A-Z]|\nRequirements?:|\nQualifications?:|\nSalary:|\nLocation:|$)",
            r"we offer:?\s*(.+?)(?:\n\n|\n[A-Z]|\nRequirements?:|\nQualifications?:|\nSalary:|\nLocation:|$)",
            r"what we offer:?\s*(.+?)(?:\n\n|\n[A-Z]|\nRequirements?:|\nQualifications?:|\nSalary:|\nLocation:|$)",
            r"perks:?\s*(.+?)(?:\n\n|\n[A-Z]|\nRequirements?:|\nQualifications?:|\nSalary:|\nLocation:|$)"
        ]
        
        for pattern in benefit_patterns:
            matches = re.finditer(pattern, text, re.IGNORECASE | re.DOTALL)
            for match in matches:
                benefit_text = match.group(1).strip()
                
                # Split by bullet points or line breaks
                benefit_items = re.split(r'\n\s*[•·*-]\s*|\n\s*\d+\.?\s*', benefit_text)
                
                for item in benefit_items:
                    item = item.strip()
                    if len(item) > 5 and len(item) < 150:  # Filter reasonable length benefits
                        benefits.append(item)
        
        return benefits[:8]  # Limit to top 8 benefits
    
    def analyze_sentiment(self, text: str) -> float:
        """Analyze sentiment of job description"""
        try:
            if self.sentiment_analyzer:
                # Truncate text to model's max length
                text = text[:512]
                result = self.sentiment_analyzer(text)[0]
                
                # Convert to score between -1 and 1
                if result['label'] == 'LABEL_2':  # Positive
                    return result['score']
                elif result['label'] == 'LABEL_0':  # Negative
                    return -result['score']
                else:  # Neutral
                    return 0.0
            
        except Exception as e:
            logger.error(f"Error in sentiment analysis: {e}")
        
        return 0.0
    
    def analyze_urgency(self, text: str) -> float:
        """Analyze urgency indicators in job posting"""
        urgency_keywords = [
            "urgent", "asap", "immediately", "urgent requirement", "immediate joining",
            "walk-in", "same day", "quick", "fast", "rush", "emergency",
            "limited time", "deadline", "expires soon", "closing soon"
        ]
        
        text_lower = text.lower()
        urgency_score = 0.0
        
        for keyword in urgency_keywords:
            if keyword in text_lower:
                urgency_score += 0.2
        
        # Cap at 1.0
        return min(urgency_score, 1.0)
    
    def assess_quality(self, text: str) -> float:
        """Assess quality of job posting"""
        quality_score = 0.0
        
        # Length check (good descriptions are detailed)
        if len(text) > 500:
            quality_score += 0.2
        if len(text) > 1000:
            quality_score += 0.1
        
        # Check for key sections
        sections = ["requirements", "responsibilities", "benefits", "experience", "skills"]
        for section in sections:
            if section in text.lower():
                quality_score += 0.15
        
        # Check for contact information
        if re.search(r'\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}\b', text):
            quality_score += 0.1
        
        # Check for salary information
        if any(term in text.lower() for term in ["salary", "compensation", "pay", "₹", "lakh", "lpa"]):
            quality_score += 0.1
        
        return min(quality_score, 1.0)
    
    def categorize_job(self, text: str) -> Optional[str]:
        """Categorize job based on description"""
        try:
            if self.classifier:
                categories = [
                    "Software Development", "Data Science", "Marketing", "Sales", "HR",
                    "Finance", "Operations", "Customer Service", "Design", "Engineering",
                    "Healthcare", "Education", "Consulting", "Legal", "Administration"
                ]
                
                # Truncate text for classification
                text = text[:1024]
                result = self.classifier(text, categories)
                
                if result['scores'][0] > 0.3:  # Confidence threshold
                    return result['labels'][0]
        
        except Exception as e:
            logger.error(f"Error in job categorization: {e}")
        
        return None
    
    def detect_experience_level(self, text: str) -> Optional[str]:
        """Detect required experience level from job description"""
        text_lower = text.lower()
        
        # Experience patterns
        if any(term in text_lower for term in ["fresher", "0 year", "0-1 year", "entry level", "no experience"]):
            return "fresher"
        elif any(term in text_lower for term in ["1-3 year", "2-4 year", "junior", "associate"]):
            return "entry_level"
        elif any(term in text_lower for term in ["3-5 year", "4-6 year", "mid level", "intermediate"]):
            return "mid_level"
        elif any(term in text_lower for term in ["5+ year", "6+ year", "senior", "lead", "principal"]):
            return "senior_level"
        elif any(term in text_lower for term in ["manager", "director", "head", "vp", "cto", "ceo"]):
            return "executive"
        
        return None
    
    def has_salary_info(self, text: str) -> bool:
        """Check if job posting mentions salary information"""
        salary_patterns = [
            r'\d+\s*(?:lakh|lpa|k|thousand)',
            r'₹\s*\d+',
            r'\d+\s*-\s*\d+\s*(?:lakh|lpa)',
            r'salary\s*:',
            r'compensation\s*:',
            r'ctc\s*:'
        ]
        
        text_lower = text.lower()
        return any(re.search(pattern, text_lower) for pattern in salary_patterns)
    
    def is_remote_friendly(self, text: str) -> bool:
        """Check if job is remote-friendly"""
        remote_keywords = [
            "remote", "work from home", "wfh", "telecommute", "distributed",
            "anywhere", "flexible location", "home office", "virtual"
        ]
        
        text_lower = text.lower()
        return any(keyword in text_lower for keyword in remote_keywords)
    
    def estimate_company_size(self, text: str) -> Optional[str]:
        """Estimate company size based on job description"""
        text_lower = text.lower()
        
        if any(term in text_lower for term in ["startup", "early stage", "growing team", "small team"]):
            return "startup"
        elif any(term in text_lower for term in ["enterprise", "multinational", "global", "fortune", "large organization"]):
            return "large"
        elif any(term in text_lower for term in ["mid-size", "medium", "established"]):
            return "medium"
        
        return None
    
    def calculate_job_match_score(self, job_description: str, user_profile: Dict[str, Any]) -> float:
        """Calculate how well a job matches user profile"""
        try:
            # Extract job skills and requirements
            job_analysis = self.analyze_job_description(job_description)
            job_skills = set(skill.lower() for skill in job_analysis.get("skills", []))
            
            # Get user skills
            user_skills = set(skill.lower() for skill in user_profile.get("skills", []))
            
            # Calculate skill match
            if job_skills and user_skills:
                skill_overlap = len(job_skills.intersection(user_skills))
                skill_match = skill_overlap / len(job_skills.union(user_skills))
            else:
                skill_match = 0.0
            
            # Experience level match
            job_exp_level = job_analysis.get("experience_level")
            user_exp_level = user_profile.get("experience_level", "").lower()
            
            exp_match = 1.0 if job_exp_level and job_exp_level.lower() == user_exp_level else 0.5
            
            # Location preference match
            location_match = 1.0  # Default to 1.0, can be enhanced with location matching
            
            # Calculate overall match score
            match_score = (skill_match * 0.6) + (exp_match * 0.3) + (location_match * 0.1)
            
            return round(match_score, 2)
            
        except Exception as e:
            logger.error(f"Error calculating job match score: {e}")
            return 0.0
