PRAGMA foreign_keys = ON;

CREATE TABLE IF NOT EXISTS profiles (
  id TEXT PRIMARY KEY,
  slug TEXT NOT NULL UNIQUE,
  profile_type TEXT NOT NULL DEFAULT 'advocate',
  status TEXT NOT NULL DEFAULT 'pending' CHECK(status IN ('pending','under_review','approved','rejected','suspended')),
  full_name TEXT NOT NULL,
  designation TEXT NOT NULL DEFAULT 'Advocate',
  state_bar_council TEXT NOT NULL,
  enrolment_number TEXT NOT NULL,
  enrolment_year INTEGER,
  qualification TEXT NOT NULL,
  city TEXT NOT NULL,
  state TEXT NOT NULL,
  bio TEXT NOT NULL,
  practice_areas_json TEXT NOT NULL DEFAULT '[]',
  courts_json TEXT NOT NULL DEFAULT '[]',
  professional_website TEXT,
  linkedin_url TEXT,
  photo_url TEXT,
  submitted_email TEXT NOT NULL,
  accuracy_confirmed INTEGER NOT NULL DEFAULT 0,
  publication_consent INTEGER NOT NULL DEFAULT 0,
  conduct_confirmed INTEGER NOT NULL DEFAULT 0,
  review_notes TEXT,
  created_at TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP,
  updated_at TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP,
  published_at TEXT
);

CREATE INDEX IF NOT EXISTS idx_profiles_status_created ON profiles(status, created_at DESC);
CREATE INDEX IF NOT EXISTS idx_profiles_slug ON profiles(slug);
CREATE INDEX IF NOT EXISTS idx_profiles_state ON profiles(state);

CREATE TABLE IF NOT EXISTS audit_log (
  id TEXT PRIMARY KEY,
  profile_id TEXT,
  actor_type TEXT NOT NULL,
  actor_email TEXT,
  action TEXT NOT NULL,
  details_json TEXT,
  created_at TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP,
  FOREIGN KEY(profile_id) REFERENCES profiles(id) ON DELETE CASCADE
);

CREATE INDEX IF NOT EXISTS idx_audit_profile_time ON audit_log(profile_id, created_at DESC);

CREATE TABLE IF NOT EXISTS profile_submissions (
  id TEXT PRIMARY KEY,
  profile_id TEXT,
  submitted_email TEXT NOT NULL,
  ip_hash TEXT,
  created_at TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP,
  FOREIGN KEY(profile_id) REFERENCES profiles(id) ON DELETE CASCADE
);
CREATE INDEX IF NOT EXISTS idx_submissions_email_time ON profile_submissions(submitted_email, created_at DESC);
CREATE INDEX IF NOT EXISTS idx_submissions_ip_time ON profile_submissions(ip_hash, created_at DESC);
