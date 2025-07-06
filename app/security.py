import re
import hashlib
import time
from typing import List, Dict, Tuple, Optional
from dataclasses import dataclass
from collections import defaultdict
import logging

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

@dataclass
class SecurityViolation:
    """Represents a security violation detected."""
    violation_type: str
    severity: str  # 'low', 'medium', 'high', 'critical'
    description: str
    detected_pattern: str
    user_input: str
    timestamp: float

class SecurityGuardrails:
    """Comprehensive security guardrails for the chatbot."""
    
    def __init__(self):
        # Rate limiting
        self.rate_limit_window = 60  # seconds
        self.max_requests_per_window = 10
        self.request_history = defaultdict(list)
        
        # Suspicious patterns for prompt injection
        self.prompt_injection_patterns = [
            # System prompt attempts
            r'(?i)(system|assistant|user|role|ignore|forget|reset|new instructions)',
            r'(?i)(you are|act as|pretend to be|roleplay as)',
            r'(?i)(ignore previous|forget everything|start over)',
            r'(?i)(new system|override|bypass|hack)',
            
            # Jailbreak attempts
            r'(?i)(jailbreak|break free|ignore rules|ignore safety)',
            r'(?i)(do anything|no restrictions|unlimited)',
            r'(?i)(dangerous|harmful|illegal|unethical)',
            
            # Prompt extraction attempts
            r'(?i)(show me|display|print|output|reveal) (system|prompt|instructions)',
            r'(?i)(what are your|tell me your|show your) (instructions|rules|prompts)',
            r'(?i)(repeat|echo|copy) (your|the) (system|prompt|instructions)',
            
            # Context manipulation
            r'(?i)(modify|change|update|edit) (system|context|information)',
            r'(?i)(add|remove|delete) (information|data|context)',
            
            # Code injection attempts
            r'<script[^>]*>.*?</script>',
            r'javascript:',
            r'data:text/html',
            r'vbscript:',
            
            # SQL injection patterns
            r'(?i)(union|select|insert|update|delete|drop|create|alter)',
            r'(?i)(or\s+1\s*=\s*1|or\s+true|or\s+false)',
            
            # XSS patterns
            r'<[^>]*>',
            r'&[a-zA-Z]+;',
            r'&#[0-9]+;',
            
            # Command injection
            r'(?i)(exec|eval|system|shell|command)',
            r'[;&|`$(){}]',
            
            # File path traversal
            r'\.\./',
            r'\.\.\\',
            r'/etc/',
            r'/proc/',
            r'/sys/',
            
            # Sensitive data requests
            r'(?i)(password|secret|key|token|api|credential)',
            r'(?i)(private|confidential|internal|admin)',
            
            # Excessive repetition (potential DoS)
            r'(.)\1{50,}',  # Same character repeated 50+ times
            
            # Unicode normalization attacks
            r'[\u200B-\u200D\uFEFF]',  # Zero-width characters
            
            # Encoding attempts
            r'%[0-9A-Fa-f]{2}',
            r'\\x[0-9A-Fa-f]{2}',
            r'\\u[0-9A-Fa-f]{4}',
        ]
        
        # Compile patterns for efficiency
        self.compiled_patterns = [re.compile(pattern) for pattern in self.prompt_injection_patterns]
        
        # Conversation context limits
        self.max_conversation_history = 20
        self.max_message_length = 1000
        
        # Suspicious user agents
        self.suspicious_user_agents = [
            'curl', 'wget', 'python', 'scraper', 'bot', 'spider', 'crawler'
        ]
        
        # Violation tracking
        self.violations = []
        self.max_violations_per_ip = 5
        self.ip_violation_count = defaultdict(int)
        
        # IP blocking (in production, use Redis or database)
        self.blocked_ips = set()
        
    def check_rate_limit(self, client_ip: str) -> Tuple[bool, str]:
        """Check if client is within rate limits."""
        current_time = time.time()
        
        # Clean old requests
        self.request_history[client_ip] = [
            req_time for req_time in self.request_history[client_ip]
            if current_time - req_time < self.rate_limit_window
        ]
        
        # Check if limit exceeded
        if len(self.request_history[client_ip]) >= self.max_requests_per_window:
            return False, f"Rate limit exceeded. Max {self.max_requests_per_window} requests per {self.rate_limit_window} seconds."
        
        # Add current request
        self.request_history[client_ip].append(current_time)
        return True, "Rate limit OK"
    
    def detect_prompt_injection(self, message: str) -> List[SecurityViolation]:
        """Detect potential prompt injection attempts."""
        violations = []
        
        # Check for suspicious patterns
        for i, pattern in enumerate(self.compiled_patterns):
            matches = pattern.findall(message)
            if matches:
                severity = self._determine_severity(i, len(matches))
                violation = SecurityViolation(
                    violation_type="prompt_injection",
                    severity=severity,
                    description=f"Detected suspicious pattern: {pattern.pattern}",
                    detected_pattern=pattern.pattern,
                    user_input=message,
                    timestamp=time.time()
                )
                violations.append(violation)
                logger.warning(f"Prompt injection detected: {pattern.pattern} in message: {message[:100]}...")
        
        return violations
    
    def _determine_severity(self, pattern_index: int, match_count: int) -> str:
        """Determine severity based on pattern type and frequency."""
        # High severity patterns (first 10)
        if pattern_index < 10:
            return 'high' if match_count > 1 else 'medium'
        # Medium severity patterns (next 15)
        elif pattern_index < 25:
            return 'medium' if match_count > 2 else 'low'
        # Low severity patterns (rest)
        else:
            return 'low' if match_count > 3 else 'low'
    
    def validate_message_length(self, message: str) -> Tuple[bool, str]:
        """Validate message length."""
        if len(message) > self.max_message_length:
            return False, f"Message too long. Max {self.max_message_length} characters allowed."
        return True, "Message length OK"
    
    def validate_conversation_history(self, history: List[dict]) -> Tuple[bool, str]:
        """Validate conversation history length."""
        if len(history) > self.max_conversation_history:
            return False, f"Conversation history too long. Max {self.max_conversation_history} messages allowed."
        return True, "Conversation history OK"
    
    def check_suspicious_user_agent(self, user_agent: str) -> Tuple[bool, str]:
        """Check for suspicious user agents."""
        if not user_agent:
            return True, "No user agent provided"
        
        user_agent_lower = user_agent.lower()
        for suspicious in self.suspicious_user_agents:
            if suspicious in user_agent_lower:
                return False, f"Suspicious user agent detected: {suspicious}"
        
        return True, "User agent OK"
    
    def sanitize_input(self, message: str) -> str:
        """Sanitize user input to prevent injection attacks."""
        # Remove zero-width characters
        message = re.sub(r'[\u200B-\u200D\uFEFF]', '', message)
        
        # Normalize unicode
        message = message.encode('utf-8', errors='ignore').decode('utf-8')
        
        # Remove excessive whitespace
        message = re.sub(r'\s+', ' ', message).strip()
        
        # Truncate if still too long
        if len(message) > self.max_message_length:
            message = message[:self.max_message_length]
        
        return message
    
    def check_content_safety(self, message: str) -> List[SecurityViolation]:
        """Check for inappropriate or harmful content."""
        violations = []
        
        # Inappropriate content patterns
        inappropriate_patterns = [
            r'(?i)(hate|racist|sexist|discriminatory)',
            r'(?i)(violence|harm|kill|hurt)',
            r'(?i)(illegal|criminal|fraud|scam)',
            r'(?i)(personal|private|confidential) (information|data)',
        ]
        
        for pattern in inappropriate_patterns:
            if re.search(pattern, message):
                violation = SecurityViolation(
                    violation_type="inappropriate_content",
                    severity="medium",
                    description="Detected potentially inappropriate content",
                    detected_pattern=pattern,
                    user_input=message,
                    timestamp=time.time()
                )
                violations.append(violation)
        
        return violations
    
    def track_violation(self, client_ip: str, violation: SecurityViolation):
        """Track security violations per IP."""
        self.violations.append(violation)
        self.ip_violation_count[client_ip] += 1
        
        # Block IP if too many violations
        if self.ip_violation_count[client_ip] >= self.max_violations_per_ip:
            self.blocked_ips.add(client_ip)
            logger.warning(f"IP {client_ip} blocked due to multiple violations")
    
    def is_ip_blocked(self, client_ip: str) -> bool:
        """Check if IP is blocked."""
        return client_ip in self.blocked_ips
    
    def validate_request(self, message: str, conversation_history: List[dict], 
                        client_ip: str, user_agent: str = None) -> Tuple[bool, str, List[SecurityViolation]]:
        """Comprehensive request validation."""
        violations = []
        
        # Check if IP is blocked
        if self.is_ip_blocked(client_ip):
            return False, "Access denied due to security violations", violations
        
        # Rate limiting
        rate_ok, rate_msg = self.check_rate_limit(client_ip)
        if not rate_ok:
            return False, rate_msg, violations
        
        # Sanitize input
        sanitized_message = self.sanitize_input(message)
        
        # Message length validation
        length_ok, length_msg = self.validate_message_length(sanitized_message)
        if not length_ok:
            return False, length_msg, violations
        
        # Conversation history validation
        history_ok, history_msg = self.validate_conversation_history(conversation_history)
        if not history_ok:
            return False, history_msg, violations
        
        # Prompt injection detection (check before user agent)
        injection_violations = self.detect_prompt_injection(sanitized_message)
        violations.extend(injection_violations)
        
        # Content safety check
        content_violations = self.check_content_safety(sanitized_message)
        violations.extend(content_violations)
        
        # User agent validation (check after content analysis)
        if user_agent:
            ua_ok, ua_msg = self.check_suspicious_user_agent(user_agent)
            if not ua_ok:
                return False, ua_msg, violations
        
        # Track violations
        for violation in violations:
            self.track_violation(client_ip, violation)
        
        # Determine if request should be blocked
        critical_violations = [v for v in violations if v.severity == 'critical']
        high_violations = [v for v in violations if v.severity == 'high']
        medium_violations = [v for v in violations if v.severity == 'medium']
        
        # Block on any critical, 2+ high, or 3+ medium violations
        if critical_violations or len(high_violations) >= 2 or len(medium_violations) >= 3:
            return False, "Request blocked due to security violations", violations
        
        return True, "Request validated successfully", violations
    
    def get_security_stats(self) -> Dict:
        """Get security statistics."""
        return {
            "total_violations": len(self.violations),
            "blocked_ips": len(self.blocked_ips),
            "rate_limited_ips": len([ip for ip, history in self.request_history.items() 
                                   if len(history) >= self.max_requests_per_window]),
            "violation_types": defaultdict(int, {
                v.violation_type: sum(1 for v in self.violations if v.violation_type == v.violation_type)
                for v in self.violations
            })
        }

# Global security instance
security_guardrails = SecurityGuardrails() 