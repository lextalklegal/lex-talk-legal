import { json, profileData, text } from "../_lib.js";

export async function onRequestGet(context) {
  if (!context.env.DB) return json({ profiles: [], count: 0, setup_required: true }, 200);
  const url = new URL(context.request.url);
  const q = text(url.searchParams.get("q"), 80);
  const limit = Math.min(Math.max(parseInt(url.searchParams.get("limit") || "24", 10) || 24, 1), 60);
  const offset = Math.max(parseInt(url.searchParams.get("offset") || "0", 10) || 0, 0);
  let query = `SELECT id,slug,profile_type,status,full_name,designation,state_bar_council,enrolment_number,enrolment_year,qualification,city,state,bio,practice_areas_json,courts_json,professional_website,linkedin_url,photo_url,created_at,updated_at,published_at,review_notes,submitted_email,accuracy_confirmed,publication_consent,conduct_confirmed FROM profiles WHERE status='approved'`;
  const binds=[];
  if (q) { query += ` AND (full_name LIKE ? OR city LIKE ? OR state LIKE ? OR practice_areas_json LIKE ?)`; const like=`%${q}%`; binds.push(like,like,like,like); }
  query += ` ORDER BY published_at DESC, full_name ASC LIMIT ? OFFSET ?`;
  binds.push(limit,offset);
  const rows = await context.env.DB.prepare(query).bind(...binds).all();
  let countQuery = `SELECT COUNT(*) AS count FROM profiles WHERE status='approved'`;
  const countBinds=[];
  if(q){countQuery += ` AND (full_name LIKE ? OR city LIKE ? OR state LIKE ? OR practice_areas_json LIKE ?)`; const like=`%${q}%`; countBinds.push(like,like,like,like);}
  const countRow = await context.env.DB.prepare(countQuery).bind(...countBinds).first();
  return json({ profiles:(rows.results||[]).map(profileData).map(p=>{delete p.review_notes;delete p.submitted_email;delete p.accuracy_confirmed;delete p.publication_consent;delete p.conduct_confirmed;return p;}), count:Number(countRow?.count||0), offset, limit });
}
