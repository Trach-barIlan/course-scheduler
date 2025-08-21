-- Migration: Create contact_submissions table
-- Date: 2025-08-21
-- Purpose: Store contact form submissions for feedback and bug reports

CREATE TABLE IF NOT EXISTS contact_submissions (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    name VARCHAR(100) NOT NULL,
    email VARCHAR(255) NOT NULL,
    subject VARCHAR(200) NOT NULL,
    type VARCHAR(50) NOT NULL, -- 'feedback', 'bug', 'feature', 'university', 'other'
    message TEXT NOT NULL,
    university VARCHAR(100),
    course VARCHAR(100),
    user_agent TEXT,
    ip_address INET,
    submitted_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    status VARCHAR(20) NOT NULL DEFAULT 'new', -- 'new', 'in_progress', 'resolved', 'closed'
    assigned_to VARCHAR(100),
    response_sent_at TIMESTAMPTZ,
    additional_data JSONB,
    created_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    updated_at TIMESTAMPTZ NOT NULL DEFAULT NOW()
);

-- Create indexes for better performance
CREATE INDEX IF NOT EXISTS idx_contact_submissions_type ON contact_submissions(type);
CREATE INDEX IF NOT EXISTS idx_contact_submissions_status ON contact_submissions(status);
CREATE INDEX IF NOT EXISTS idx_contact_submissions_submitted_at ON contact_submissions(submitted_at DESC);
CREATE INDEX IF NOT EXISTS idx_contact_submissions_email ON contact_submissions(email);

-- Enable Row Level Security (RLS)
ALTER TABLE contact_submissions ENABLE ROW LEVEL SECURITY;

-- Create policy to allow inserts from anyone (for form submissions)
CREATE POLICY "Allow contact form submissions" ON contact_submissions
    FOR INSERT TO anon, authenticated
    WITH CHECK (true);

-- Create policy to allow admin users to read all submissions
-- Note: You might want to adjust this based on your admin role system
CREATE POLICY "Allow admin to read submissions" ON contact_submissions
    FOR SELECT TO authenticated
    USING (true);

-- Create policy to allow admin users to update submissions (change status, assign, etc.)
CREATE POLICY "Allow admin to update submissions" ON contact_submissions
    FOR UPDATE TO authenticated
    USING (true)
    WITH CHECK (true);

-- Add some helpful comments
COMMENT ON TABLE contact_submissions IS 'Stores contact form submissions from users for feedback, bug reports, and feature requests';
COMMENT ON COLUMN contact_submissions.type IS 'Type of submission: feedback, bug, feature, university, other';
COMMENT ON COLUMN contact_submissions.status IS 'Current status: new, in_progress, resolved, closed';
COMMENT ON COLUMN contact_submissions.additional_data IS 'JSON field for storing additional form data and metadata';

-- Create a function to update the updated_at timestamp
CREATE OR REPLACE FUNCTION update_contact_submissions_updated_at()
RETURNS TRIGGER AS $$
BEGIN
    NEW.updated_at = NOW();
    RETURN NEW;
END;
$$ language 'plpgsql';

-- Create trigger to automatically update updated_at
DROP TRIGGER IF EXISTS trigger_update_contact_submissions_updated_at ON contact_submissions;
CREATE TRIGGER trigger_update_contact_submissions_updated_at
    BEFORE UPDATE ON contact_submissions
    FOR EACH ROW
    EXECUTE FUNCTION update_contact_submissions_updated_at();
