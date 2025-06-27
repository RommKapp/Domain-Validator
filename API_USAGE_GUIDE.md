# Email Domain Validator - Complete Usage Guide

## 🚀 Quick Start

### Web Interface
Access the user-friendly web interface at: **http://localhost:8000/**

### API Documentation
Interactive API docs available at: **http://localhost:8000/docs**

## 📖 Web Interface Guide

### Single Domain Validation
1. **Navigate** to the main page
2. **Enter** domain or email in the input field (e.g., `example.com` or `user@company.com`)
3. **Click** "Validate" or press Enter
4. **View** results with detailed metadata and recommendations

**Quick Examples Available:**
- Click pre-loaded examples: `google.com`, `gmail.com`, `harvard.edu`, `tempmail.org`
- Results show domain type, quality score, and technical details

### Batch Domain Validation
1. **Switch** to the "Batch Domain Validation" section
2. **Enter** multiple domains/emails (one per line) in the text area
3. **Alternative**: Upload a CSV/TXT file using the file upload area
4. **Click** "Validate Batch" 
5. **View** summary statistics and individual results
6. **Export** results as CSV or JSON

**File Upload Support:**
- Accepts `.csv` and `.txt` files
- Automatically parses domains separated by commas or newlines
- Displays domain count as you type

### Results Export
- **CSV Export**: Structured data for spreadsheets
- **JSON Export**: Complete API response data
- Files named with current date for organization

## 🔧 API Usage Guide

### Base URL
```
http://localhost:8000/api/v1
```

### 1. Single Domain Validation

#### Endpoint
```http
POST /domain/validate
```

#### Request Body
```json
{
  "domain": "example.com"
}
```

#### Response
```json
{
  "domain": "example.com",
  "domain_type": "corporate",
  "validation_status": "valid",
  "quality_score": 8.5,
  "recommendation": "accept",
  "metadata": {
    "has_mx_record": true,
    "has_a_record": true,
    "mx_servers": ["mail.example.com"],
    "website_accessible": true,
    "has_ssl_certificate": true
  },
  "checked_at": "2024-01-01T12:00:00Z"
}
```

#### cURL Example
```bash
curl -X POST "http://localhost:8000/api/v1/domain/validate" \
  -H "Content-Type: application/json" \
  -d '{"domain": "example.com"}'
```

### 2. Batch Domain Validation

#### Endpoint
```http
POST /domain/validate-batch
```

#### Request Body
```json
{
  "domains": [
    "example.com",
    "user@company.com",
    "university.edu",
    "tempmail.org"
  ]
}
```

#### Response
```json
{
  "results": [
    {
      "domain": "example.com",
      "domain_type": "corporate",
      "validation_status": "valid",
      "quality_score": 8.5,
      "recommendation": "accept",
      "metadata": { ... },
      "checked_at": "2024-01-01T12:00:00Z"
    }
  ],
  "total_processed": 4,
  "processing_time_seconds": 2.35
}
```

#### cURL Example
```bash
curl -X POST "http://localhost:8000/api/v1/domain/validate-batch" \
  -H "Content-Type: application/json" \
  -d '{
    "domains": [
      "example.com",
      "test@company.com",
      "university.edu"
    ]
  }'
```

### 3. System Status

#### Cache Statistics
```bash
curl "http://localhost:8000/api/v1/domain/cache/stats"
```

#### Health Check
```bash
curl "http://localhost:8000/health"
```

## 💻 Programming Examples

### JavaScript (Node.js/Browser)

#### Single Domain Validation
```javascript
const API_BASE = 'http://localhost:8000/api/v1';

async function validateDomain(domain) {
  try {
    const response = await fetch(`${API_BASE}/domain/validate`, {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
      },
      body: JSON.stringify({ domain })
    });
    
    if (!response.ok) {
      throw new Error(`HTTP error! status: ${response.status}`);
    }
    
    const result = await response.json();
    return result;
  } catch (error) {
    console.error('Validation error:', error);
    throw error;
  }
}

// Usage
validateDomain('example.com')
  .then(result => {
    console.log('Domain type:', result.domain_type);
    console.log('Quality score:', result.quality_score);
    console.log('Recommendation:', result.recommendation);
    
    if (result.recommendation === 'accept') {
      console.log('✅ Domain is safe to use');
    } else if (result.recommendation === 'reject') {
      console.log('❌ Domain should be blocked');
    } else {
      console.log('⚠️ Domain requires manual review');
    }
  })
  .catch(error => {
    console.error('Failed to validate domain:', error);
  });
```

#### Batch Validation
```javascript
async function validateBatch(domains) {
  try {
    const response = await fetch(`${API_BASE}/domain/validate-batch`, {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
      },
      body: JSON.stringify({ domains })
    });
    
    const result = await response.json();
    
    // Process results
    const summary = {
      accept: result.results.filter(r => r.recommendation === 'accept').length,
      reject: result.results.filter(r => r.recommendation === 'reject').length,
      review: result.results.filter(r => r.recommendation === 'manual_review').length,
    };
    
    console.log('Batch Summary:', summary);
    return result;
  } catch (error) {
    console.error('Batch validation error:', error);
    throw error;
  }
}

// Usage
const domains = ['example.com', 'gmail.com', 'tempmail.org'];
validateBatch(domains);
```

### Python

#### Simple Client
```python
import requests
import json
from typing import List, Dict

class EmailDomainValidator:
    def __init__(self, base_url: str = "http://localhost:8000/api/v1"):
        self.base_url = base_url
        
    def validate_domain(self, domain: str) -> Dict:
        """Validate a single domain"""
        try:
            response = requests.post(
                f"{self.base_url}/domain/validate",
                json={"domain": domain},
                timeout=30
            )
            response.raise_for_status()
            return response.json()
        except requests.exceptions.RequestException as e:
            print(f"Error validating domain {domain}: {e}")
            raise
    
    def validate_batch(self, domains: List[str]) -> Dict:
        """Validate multiple domains"""
        try:
            response = requests.post(
                f"{self.base_url}/domain/validate-batch",
                json={"domains": domains},
                timeout=60
            )
            response.raise_for_status()
            return response.json()
        except requests.exceptions.RequestException as e:
            print(f"Error validating batch: {e}")
            raise
    
    def filter_domains(self, domains: List[str], accept_only: bool = True) -> List[str]:
        """Filter domains based on recommendations"""
        batch_result = self.validate_batch(domains)
        
        if accept_only:
            return [
                result['domain'] 
                for result in batch_result['results'] 
                if result['recommendation'] == 'accept'
            ]
        else:
            return [
                result['domain'] 
                for result in batch_result['results'] 
                if result['recommendation'] != 'reject'
            ]

# Usage Examples
validator = EmailDomainValidator()

# Single validation
result = validator.validate_domain("example.com")
print(f"Domain: {result['domain']}")
print(f"Type: {result['domain_type']}")
print(f"Score: {result['quality_score']}/10")
print(f"Recommendation: {result['recommendation']}")

# Batch validation
domains = ["example.com", "gmail.com", "tempmail.org", "harvard.edu"]
batch_result = validator.validate_batch(domains)

print(f"\nProcessed {batch_result['total_processed']} domains in {batch_result['processing_time_seconds']:.2f}s")

for result in batch_result['results']:
    status_emoji = {
        'accept': '✅',
        'reject': '❌', 
        'manual_review': '⚠️'
    }
    emoji = status_emoji.get(result['recommendation'], '❓')
    print(f"{emoji} {result['domain']}: {result['domain_type']} (Score: {result['quality_score']:.1f})")

# Filter for safe domains only
safe_domains = validator.filter_domains(domains, accept_only=True)
print(f"\nSafe domains: {safe_domains}")
```

#### CSV Processing Example
```python
import csv
import pandas as pd

def process_email_list_csv(csv_file_path: str, output_file: str):
    """Process a CSV file with email addresses and validate domains"""
    validator = EmailDomainValidator()
    
    # Read email list
    df = pd.read_csv(csv_file_path)
    
    # Extract unique domains
    domains = df['email'].str.split('@').str[1].unique().tolist()
    
    # Validate all domains
    print(f"Validating {len(domains)} unique domains...")
    batch_result = validator.validate_batch(domains)
    
    # Create domain lookup
    domain_lookup = {
        result['domain']: result 
        for result in batch_result['results']
    }
    
    # Add validation results to dataframe
    df['domain'] = df['email'].str.split('@').str[1]
    df['domain_type'] = df['domain'].map(lambda d: domain_lookup.get(d, {}).get('domain_type', 'unknown'))
    df['quality_score'] = df['domain'].map(lambda d: domain_lookup.get(d, {}).get('quality_score', 0))
    df['recommendation'] = df['domain'].map(lambda d: domain_lookup.get(d, {}).get('recommendation', 'unknown'))
    
    # Save results
    df.to_csv(output_file, index=False)
    
    # Print summary
    summary = df['recommendation'].value_counts()
    print(f"\nValidation Summary:")
    print(f"Accept: {summary.get('accept', 0)}")
    print(f"Reject: {summary.get('reject', 0)}")
    print(f"Manual Review: {summary.get('manual_review', 0)}")

# Usage
process_email_list_csv('email_list.csv', 'validated_emails.csv')
```

### PHP

```php
<?php
class EmailDomainValidator {
    private $baseUrl;
    
    public function __construct($baseUrl = 'http://localhost:8000/api/v1') {
        $this->baseUrl = $baseUrl;
    }
    
    public function validateDomain($domain) {
        $ch = curl_init();
        curl_setopt($ch, CURLOPT_URL, $this->baseUrl . '/domain/validate');
        curl_setopt($ch, CURLOPT_POST, true);
        curl_setopt($ch, CURLOPT_POSTFIELDS, json_encode(['domain' => $domain]));
        curl_setopt($ch, CURLOPT_HTTPHEADER, [
            'Content-Type: application/json',
        ]);
        curl_setopt($ch, CURLOPT_RETURNTRANSFER, true);
        curl_setopt($ch, CURLOPT_TIMEOUT, 30);
        
        $response = curl_exec($ch);
        $httpCode = curl_getinfo($ch, CURLINFO_HTTP_CODE);
        curl_close($ch);
        
        if ($httpCode !== 200) {
            throw new Exception("HTTP Error: $httpCode");
        }
        
        return json_decode($response, true);
    }
    
    public function validateBatch($domains) {
        $ch = curl_init();
        curl_setopt($ch, CURLOPT_URL, $this->baseUrl . '/domain/validate-batch');
        curl_setopt($ch, CURLOPT_POST, true);
        curl_setopt($ch, CURLOPT_POSTFIELDS, json_encode(['domains' => $domains]));
        curl_setopt($ch, CURLOPT_HTTPHEADER, [
            'Content-Type: application/json',
        ]);
        curl_setopt($ch, CURLOPT_RETURNTRANSFER, true);
        curl_setopt($ch, CURLOPT_TIMEOUT, 60);
        
        $response = curl_exec($ch);
        $httpCode = curl_getinfo($ch, CURLINFO_HTTP_CODE);
        curl_close($ch);
        
        if ($httpCode !== 200) {
            throw new Exception("HTTP Error: $httpCode");
        }
        
        return json_decode($response, true);
    }
}

// Usage
$validator = new EmailDomainValidator();

try {
    // Single validation
    $result = $validator->validateDomain('example.com');
    echo "Domain: " . $result['domain'] . "\n";
    echo "Type: " . $result['domain_type'] . "\n";
    echo "Score: " . $result['quality_score'] . "/10\n";
    echo "Recommendation: " . $result['recommendation'] . "\n";
    
    // Batch validation
    $domains = ['example.com', 'gmail.com', 'tempmail.org'];
    $batchResult = $validator->validateBatch($domains);
    
    echo "\nBatch Results:\n";
    foreach ($batchResult['results'] as $result) {
        $emoji = $result['recommendation'] === 'accept' ? '✅' : 
                ($result['recommendation'] === 'reject' ? '❌' : '⚠️');
        echo "$emoji {$result['domain']}: {$result['domain_type']}\n";
    }
    
} catch (Exception $e) {
    echo "Error: " . $e->getMessage() . "\n";
}
?>
```

## 📝 Domain Classification Guide

### Domain Types

| Type | Description | Quality Score | Recommendation |
|------|-------------|---------------|----------------|
| **Corporate** | Business domains with proper infrastructure | 7-10 | Accept |
| **Educational** | Universities and schools (.edu, .ac.uk) | 8-9 | Accept |
| **Government** | Government organizations (.gov, .gov.uk) | 9-10 | Accept |
| **Public Provider** | Gmail, Yahoo, Outlook, etc. | 5-7 | Manual Review |
| **Disposable** | Temporary email services | 1-3 | Reject |
| **Suspicious** | Potential fraud or malicious domains | 2-4 | Reject |
| **Unreachable** | No DNS records or inaccessible | 0 | Reject |

### Quality Score Factors

**Positive Factors (+):**
- Valid MX records
- Working website
- SSL certificate
- Proper DNS configuration
- Established domain age
- Corporate/Educational classification

**Negative Factors (-):**
- Missing infrastructure
- Suspicious TLDs (.tk, .ml, .ga)
- Disposable email patterns
- Security blacklists
- Recent registration

### Recommendation Logic

- **Accept**: Corporate, Educational, Government domains with scores ≥7
- **Reject**: Disposable, Suspicious, Unreachable domains with scores <3
- **Manual Review**: Edge cases, Public providers, moderate scores 3-7

## 🛠 Advanced Usage

### Integration Patterns

#### CRM Integration
```javascript
// Example: HubSpot integration
async function validateHubSpotContacts() {
  const contacts = await hubspot.crm.contacts.getAll();
  const domains = contacts.results.map(c => 
    c.properties.email?.split('@')[1]
  ).filter(Boolean);
  
  const validation = await validateBatch([...new Set(domains)]);
  
  // Update contact properties based on validation
  for (const result of validation.results) {
    const contactsToUpdate = contacts.results.filter(c =>
      c.properties.email?.endsWith(`@${result.domain}`)
    );
    
    for (const contact of contactsToUpdate) {
      await hubspot.crm.contacts.basicApi.update(contact.id, {
        properties: {
          domain_type: result.domain_type,
          domain_quality: result.quality_score,
          domain_recommendation: result.recommendation
        }
      });
    }
  }
}
```

#### Email Marketing Filter
```python
def filter_email_list(email_list: List[str], min_quality: float = 6.0) -> List[str]:
    """Filter email list removing low-quality domains"""
    validator = EmailDomainValidator()
    
    # Extract unique domains
    domains = list(set([email.split('@')[1] for email in email_list]))
    
    # Validate domains
    results = validator.validate_batch(domains)
    
    # Create domain quality lookup
    domain_quality = {
        result['domain']: result['quality_score']
        for result in results['results']
    }
    
    # Filter emails
    filtered_emails = [
        email for email in email_list
        if domain_quality.get(email.split('@')[1], 0) >= min_quality
    ]
    
    print(f"Filtered {len(email_list)} -> {len(filtered_emails)} emails")
    return filtered_emails
```

## 🚨 Error Handling

### Common HTTP Status Codes

- **200**: Success
- **400**: Bad Request (invalid domain format)
- **429**: Rate Limit Exceeded
- **500**: Internal Server Error (DNS/HTTP check failed)

### Python Error Handling
```python
try:
    result = validator.validate_domain(domain)
except requests.exceptions.HTTPError as e:
    if e.response.status_code == 429:
        print("Rate limit exceeded, please wait")
        time.sleep(1)
        # Retry logic here
    elif e.response.status_code == 400:
        print(f"Invalid domain format: {domain}")
    else:
        print(f"HTTP error: {e.response.status_code}")
except requests.exceptions.Timeout:
    print("Request timeout - domain validation taking too long")
except requests.exceptions.RequestException as e:
    print(f"Request failed: {e}")
```

## 📊 Performance Tips

### Batch Processing
- Use batch endpoint for multiple domains (more efficient)
- Limit batches to 100 domains for optimal performance
- Implement retry logic for rate limits

### Caching
- Results are cached for 1 hour by default
- Subsequent requests for same domain return immediately
- Clear cache via admin endpoint if needed

### Rate Limits
- Standard endpoints: 10 requests/second
- Batch endpoints: 1 request/second
- Implement exponential backoff for rate limit handling

This comprehensive guide covers all aspects of using the Email Domain Validator through both the web interface and API. The service is ready for production use with robust validation, caching, and error handling.