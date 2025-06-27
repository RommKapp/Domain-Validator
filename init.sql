-- Initial database setup for Email Domain Validator

-- Create extensions
CREATE EXTENSION IF NOT EXISTS "uuid-ossp";

-- Create indexes for better performance
CREATE INDEX IF NOT EXISTS idx_domains_domain_name ON domains(domain_name);
CREATE INDEX IF NOT EXISTS idx_domains_type ON domains(domain_type);
CREATE INDEX IF NOT EXISTS idx_domains_whitelisted ON domains(is_whitelisted);
CREATE INDEX IF NOT EXISTS idx_domains_blacklisted ON domains(is_blacklisted);
CREATE INDEX IF NOT EXISTS idx_domains_last_checked ON domains(last_checked_at);

CREATE INDEX IF NOT EXISTS idx_disposable_domains_name ON disposable_domains(domain_name);
CREATE INDEX IF NOT EXISTS idx_public_provider_domains_name ON public_provider_domains(domain_name);