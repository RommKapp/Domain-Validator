#!/usr/bin/env python3
"""
Test dataset for Email Domain Validator
This script creates a known dataset and tests our algorithm's accuracy
"""

import asyncio
import json
import time
from typing import Dict, List, Tuple
from app.services.domain_validator import DomainValidator
from app.models.schemas import DomainType, ValidationStatus, Recommendation

# Known test dataset with expected classifications
TEST_DOMAINS = {
    # Corporate domains - should be classified as CORPORATE
    "corporate": [
        {"domain": "microsoft.com", "expected_type": DomainType.CORPORATE, "expected_recommendation": Recommendation.ACCEPT},
        {"domain": "apple.com", "expected_type": DomainType.CORPORATE, "expected_recommendation": Recommendation.ACCEPT},
        {"domain": "google.com", "expected_type": DomainType.CORPORATE, "expected_recommendation": Recommendation.ACCEPT},
        {"domain": "amazon.com", "expected_type": DomainType.CORPORATE, "expected_recommendation": Recommendation.ACCEPT},
        {"domain": "stripe.com", "expected_type": DomainType.CORPORATE, "expected_recommendation": Recommendation.ACCEPT},
        {"domain": "shopify.com", "expected_type": DomainType.CORPORATE, "expected_recommendation": Recommendation.ACCEPT},
        {"domain": "salesforce.com", "expected_type": DomainType.CORPORATE, "expected_recommendation": Recommendation.ACCEPT},
    ],
    
    # Public email providers - should be classified as PUBLIC_PROVIDER
    "public_providers": [
        {"domain": "gmail.com", "expected_type": DomainType.PUBLIC_PROVIDER, "expected_recommendation": Recommendation.MANUAL_REVIEW},
        {"domain": "yahoo.com", "expected_type": DomainType.PUBLIC_PROVIDER, "expected_recommendation": Recommendation.MANUAL_REVIEW},
        {"domain": "outlook.com", "expected_type": DomainType.PUBLIC_PROVIDER, "expected_recommendation": Recommendation.MANUAL_REVIEW},
        {"domain": "hotmail.com", "expected_type": DomainType.PUBLIC_PROVIDER, "expected_recommendation": Recommendation.MANUAL_REVIEW},
        {"domain": "icloud.com", "expected_type": DomainType.PUBLIC_PROVIDER, "expected_recommendation": Recommendation.MANUAL_REVIEW},
        {"domain": "protonmail.com", "expected_type": DomainType.PUBLIC_PROVIDER, "expected_recommendation": Recommendation.MANUAL_REVIEW},
    ],
    
    # Educational domains - should be classified as EDUCATIONAL
    "educational": [
        {"domain": "harvard.edu", "expected_type": DomainType.EDUCATIONAL, "expected_recommendation": Recommendation.ACCEPT},
        {"domain": "mit.edu", "expected_type": DomainType.EDUCATIONAL, "expected_recommendation": Recommendation.ACCEPT},
        {"domain": "stanford.edu", "expected_type": DomainType.EDUCATIONAL, "expected_recommendation": Recommendation.ACCEPT},
        {"domain": "oxford.ac.uk", "expected_type": DomainType.EDUCATIONAL, "expected_recommendation": Recommendation.ACCEPT},
        {"domain": "cambridge.ac.uk", "expected_type": DomainType.EDUCATIONAL, "expected_recommendation": Recommendation.ACCEPT},
    ],
    
    # Government domains - should be classified as GOVERNMENT
    "government": [
        {"domain": "whitehouse.gov", "expected_type": DomainType.GOVERNMENT, "expected_recommendation": Recommendation.ACCEPT},
        {"domain": "nasa.gov", "expected_type": DomainType.GOVERNMENT, "expected_recommendation": Recommendation.ACCEPT},
        {"domain": "irs.gov", "expected_type": DomainType.GOVERNMENT, "expected_recommendation": Recommendation.ACCEPT},
        {"domain": "gov.uk", "expected_type": DomainType.GOVERNMENT, "expected_recommendation": Recommendation.ACCEPT},
    ],
    
    # Disposable domains - should be classified as DISPOSABLE
    "disposable": [
        {"domain": "10minutemail.com", "expected_type": DomainType.DISPOSABLE, "expected_recommendation": Recommendation.REJECT},
        {"domain": "guerrillamail.com", "expected_type": DomainType.DISPOSABLE, "expected_recommendation": Recommendation.REJECT},
        {"domain": "mailinator.com", "expected_type": DomainType.DISPOSABLE, "expected_recommendation": Recommendation.REJECT},
        {"domain": "tempmail.org", "expected_type": DomainType.DISPOSABLE, "expected_recommendation": Recommendation.REJECT},
        {"domain": "throwaway.email", "expected_type": DomainType.DISPOSABLE, "expected_recommendation": Recommendation.REJECT},
    ],
    
    # Suspicious domains - should be classified as SUSPICIOUS
    "suspicious": [
        {"domain": "fake-bank-site.tk", "expected_type": DomainType.SUSPICIOUS, "expected_recommendation": Recommendation.REJECT},
        {"domain": "test-spam-domain.ml", "expected_type": DomainType.SUSPICIOUS, "expected_recommendation": Recommendation.REJECT},
        {"domain": "temporary-scam.ga", "expected_type": DomainType.SUSPICIOUS, "expected_recommendation": Recommendation.REJECT},
        {"domain": "gooogle.com", "expected_type": DomainType.SUSPICIOUS, "expected_recommendation": Recommendation.REJECT},
        {"domain": "microsft.com", "expected_type": DomainType.SUSPICIOUS, "expected_recommendation": Recommendation.REJECT},
    ],
    
    # Unreachable domains - should be classified as UNREACHABLE
    "unreachable": [
        {"domain": "this-domain-does-not-exist-12345.com", "expected_type": DomainType.UNREACHABLE, "expected_recommendation": Recommendation.REJECT},
        {"domain": "nonexistent-test-domain-67890.net", "expected_type": DomainType.UNREACHABLE, "expected_recommendation": Recommendation.REJECT},
        {"domain": "fake-unreachable-domain.invalid", "expected_type": DomainType.UNREACHABLE, "expected_recommendation": Recommendation.REJECT},
    ]
}

class TestResults:
    def __init__(self):
        self.total_tests = 0
        self.correct_classifications = 0
        self.correct_recommendations = 0
        self.results_by_category = {}
        self.detailed_results = []
        
    def add_result(self, category: str, domain: str, expected_type: DomainType, 
                   actual_type: DomainType, expected_rec: Recommendation, 
                   actual_rec: Recommendation, quality_score: float):
        self.total_tests += 1
        
        type_correct = expected_type == actual_type
        rec_correct = expected_rec == actual_rec
        
        if type_correct:
            self.correct_classifications += 1
        if rec_correct:
            self.correct_recommendations += 1
            
        if category not in self.results_by_category:
            self.results_by_category[category] = {
                'total': 0,
                'type_correct': 0,
                'rec_correct': 0
            }
            
        self.results_by_category[category]['total'] += 1
        if type_correct:
            self.results_by_category[category]['type_correct'] += 1
        if rec_correct:
            self.results_by_category[category]['rec_correct'] += 1
            
        self.detailed_results.append({
            'category': category,
            'domain': domain,
            'expected_type': expected_type.value,
            'actual_type': actual_type.value,
            'expected_recommendation': expected_rec.value,
            'actual_recommendation': actual_rec.value,
            'quality_score': quality_score,
            'type_correct': type_correct,
            'recommendation_correct': rec_correct
        })

async def run_validation_tests():
    """Run validation tests on our known dataset"""
    
    print("🧪 Starting Email Domain Validator Testing")
    print("=" * 60)
    
    # Initialize the validator
    validator = DomainValidator()
    
    # Initialize domain lists (add known disposable domains for testing)
    validator.domain_lists.disposable_domains.update([
        "10minutemail.com", "guerrillamail.com", "mailinator.com", 
        "tempmail.org", "throwaway.email"
    ])
    
    # Initialize cache connection
    try:
        await validator.cache_service.connect()
        print("✅ Cache service connected")
    except Exception as e:
        print(f"⚠️  Cache service not available: {e}")
    
    results = TestResults()
    
    # Test each category
    for category, domains in TEST_DOMAINS.items():
        print(f"\n📁 Testing {category.upper()} domains:")
        print("-" * 40)
        
        for test_case in domains:
            domain = test_case["domain"]
            expected_type = test_case["expected_type"]
            expected_rec = test_case["expected_recommendation"]
            
            try:
                print(f"🔍 Testing {domain}...", end=" ")
                
                # Run validation
                start_time = time.time()
                result = await validator.validate_domain(domain)
                end_time = time.time()
                
                # Check results
                type_match = "✅" if result.domain_type == expected_type else "❌"
                rec_match = "✅" if result.recommendation == expected_rec else "❌"
                
                print(f"({end_time - start_time:.2f}s)")
                print(f"   Type: {result.domain_type.value} {type_match} | Rec: {result.recommendation.value} {rec_match} | Score: {result.quality_score:.1f}")
                
                # Record results
                results.add_result(
                    category, domain, expected_type, result.domain_type,
                    expected_rec, result.recommendation, result.quality_score
                )
                
            except Exception as e:
                print(f"❌ ERROR: {e}")
                # For errors, assume UNREACHABLE classification
                results.add_result(
                    category, domain, expected_type, DomainType.UNREACHABLE,
                    expected_rec, Recommendation.REJECT, 0.0
                )
    
    # Print summary results
    print("\n" + "=" * 60)
    print("📊 TEST RESULTS SUMMARY")
    print("=" * 60)
    
    classification_accuracy = (results.correct_classifications / results.total_tests) * 100
    recommendation_accuracy = (results.correct_recommendations / results.total_tests) * 100
    
    print(f"Total tests: {results.total_tests}")
    print(f"Classification accuracy: {results.correct_classifications}/{results.total_tests} ({classification_accuracy:.1f}%)")
    print(f"Recommendation accuracy: {results.correct_recommendations}/{results.total_tests} ({recommendation_accuracy:.1f}%)")
    
    print("\n📈 RESULTS BY CATEGORY:")
    print("-" * 40)
    
    for category, stats in results.results_by_category.items():
        type_acc = (stats['type_correct'] / stats['total']) * 100
        rec_acc = (stats['rec_correct'] / stats['total']) * 100
        print(f"{category.upper():15} | Type: {stats['type_correct']}/{stats['total']} ({type_acc:.1f}%) | Rec: {stats['rec_correct']}/{stats['total']} ({rec_acc:.1f}%)")
    
    # Show detailed failures
    print("\n❌ DETAILED FAILURES:")
    print("-" * 40)
    
    failures = [r for r in results.detailed_results if not (r['type_correct'] and r['recommendation_correct'])]
    
    if not failures:
        print("🎉 No failures! All tests passed perfectly!")
    else:
        for failure in failures:
            print(f"Domain: {failure['domain']}")
            print(f"  Expected: {failure['expected_type']} -> {failure['expected_recommendation']}")
            print(f"  Actual:   {failure['actual_type']} -> {failure['actual_recommendation']}")
            print(f"  Score:    {failure['quality_score']:.1f}")
            print()
    
    # Save detailed results to JSON
    with open('test_results.json', 'w') as f:
        json.dump({
            'summary': {
                'total_tests': results.total_tests,
                'classification_accuracy': classification_accuracy,
                'recommendation_accuracy': recommendation_accuracy,
                'results_by_category': results.results_by_category
            },
            'detailed_results': results.detailed_results
        }, f, indent=2, default=str)
    
    print(f"💾 Detailed results saved to test_results.json")
    
    # Clean up
    if validator.cache_service.redis_client:
        await validator.cache_service.disconnect()
    
    return results

async def test_performance():
    """Test performance with a batch of domains"""
    print("\n⚡ PERFORMANCE TEST")
    print("=" * 60)
    
    validator = DomainValidator()
    
    # Test batch of mixed domains
    test_batch = [
        "google.com", "gmail.com", "harvard.edu", "whitehouse.gov",
        "mailinator.com", "nonexistent.domain", "fake.tk"
    ]
    
    print(f"Testing batch of {len(test_batch)} domains...")
    
    start_time = time.time()
    results = []
    
    for domain in test_batch:
        try:
            result = await validator.validate_domain(domain)
            results.append(result)
        except Exception as e:
            print(f"Error validating {domain}: {e}")
    
    end_time = time.time()
    total_time = end_time - start_time
    avg_time = total_time / len(test_batch)
    
    print(f"✅ Processed {len(results)}/{len(test_batch)} domains")
    print(f"⏱️  Total time: {total_time:.2f}s")
    print(f"📊 Average time per domain: {avg_time:.3f}s")
    print(f"🚀 Throughput: {len(test_batch)/total_time:.1f} domains/second")

if __name__ == "__main__":
    async def main():
        # Run validation tests
        await run_validation_tests()
        
        # Run performance tests
        await test_performance()
        
        print("\n🎯 Testing complete!")
    
    asyncio.run(main())