PRAGMA foreign_keys=ON;
CREATE TABLE IF NOT EXISTS profiles (id INTEGER PRIMARY KEY AUTOINCREMENT, slug TEXT NOT NULL UNIQUE, full_name TEXT NOT NULL, designation TEXT NOT NULL, state_bar_council TEXT, enrolment_number TEXT, enrolment_year INTEGER, qualification TEXT NOT NULL, city TEXT NOT NULL, state TEXT NOT NULL, photo_url TEXT, professional_url TEXT, practice_areas TEXT, courts_forums TEXT, bio TEXT, email TEXT NOT NULL, phone TEXT, email_hash TEXT, status TEXT NOT NULL DEFAULT 'pending' CHECK(status IN ('pending','under_review','approved','rejected','suspended')), created_at TEXT NOT NULL, updated_at TEXT NOT NULL);
CREATE INDEX IF NOT EXISTS idx_profiles_status ON profiles(status);
CREATE INDEX IF NOT EXISTS idx_profiles_name ON profiles(full_name);
CREATE INDEX IF NOT EXISTS idx_profiles_location ON profiles(city,state);
CREATE TABLE IF NOT EXISTS admin_audit (id INTEGER PRIMARY KEY AUTOINCREMENT, profile_id INTEGER, action TEXT NOT NULL, actor_email TEXT, note TEXT, created_at TEXT NOT NULL);
CREATE INDEX IF NOT EXISTS idx_admin_audit_profile ON admin_audit(profile_id);
