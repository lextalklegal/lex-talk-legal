import { json, text, list, validEmail, safeUrl, slugify, hashIp, requestOriginAllowed } from "../_lib.js";

function bad(message, field = null) { return json({ ok:false, error:message, field }, 400); }

export async function onRequestPost(context) {
  if (!requestOriginAllowed(context.request, context.env)) return json({ok:false,error:"Invalid request origin."},403);
  if (!context.env.DB) return json({ok:false,error:"Profile system is not configured yet. Please try again later."},503);
  const len = Number(context.request.headers.get("content-length") || 0);
  if (len && len > 26000) return bad("Submission is too large.");
  let body;
  try { body = await context.request.json(); } catch { return bad("Invalid submission format."); }
  if (text(body.website,40)) return bad("Spam check failed.");

  const full_name=text(body.full_name,100);
  const state_bar_council=text(body.state_bar_council,160);
  const enrolment_number=text(body.enrolment_number,80);
  const qualification=text(body.qualification,160);
  const city=text(body.city,80);
  const state=text(body.state,80);
  const bio=text(body.bio,1400);
  const email=validEmail(body.email);
  const enrolment_year=body.enrolment_year ? Number(body.enrolment_year) : null;
  const practice_areas=list(body.practice_areas,12,70);
  const courts=list(body.courts,12,90);
  const professional_website=safeUrl(body.professional_website,[]);
  const photo_url=safeUrl(body.photo_url,[]);
  const linkedin_url=safeUrl(body.linkedin_url,['www.linkedin.com','linkedin.com','in.linkedin.com']);

  if(full_name.length<3) return bad("Please enter the full professional name.","full_name");
  if(!state_bar_council) return bad("State Bar Council is required.","state_bar_council");
  if(!enrolment_number) return bad("Enrolment number is required.","enrolment_number");
  if(!qualification) return bad("Qualification is required.","qualification");
  if(!city || !state) return bad("City and State are required.");
  if(bio.length<40) return bad("Please provide a meaningful professional bio.","bio");
  if(!email) return bad("Please enter a valid email address.","email");
  if(![true,"true",1,"1"].includes(body.accuracy_confirmed) || ![true,"true",1,"1"].includes(body.publication_consent) || ![true,"true",1,"1"].includes(body.conduct_confirmed)) return bad("Please confirm all required declarations.");
  if(enrolment_year && (enrolment_year<1950 || enrolment_year>new Date().getFullYear())) return bad("Please enter a valid enrolment year.","enrolment_year");

  const ip=context.request.headers.get("CF-Connecting-IP") || "unknown";
  const ip_hash=await hashIp(ip, text(context.env.RATE_LIMIT_SALT,200) || "lex-talk-legal-rate");
  const recent=await context.env.DB.prepare(`SELECT COUNT(*) AS count FROM profile_submissions WHERE (ip_hash=? OR submitted_email=?) AND created_at >= strftime('%Y-%m-%dT%H:%M:%fZ','now','-1 hour')`).bind(ip_hash,email).first();
  if(Number(recent?.count||0)>=3) return json({ok:false,error:"Too many submissions from this source. Please try again later."},429);

  let base=slugify(`${full_name} ${city}`), slug=base, n=0;
  while((await context.env.DB.prepare(`SELECT id FROM profiles WHERE slug=? LIMIT 1`).bind(slug).first())) { n++; slug=`${base}-${n}`; if(n>20) slug=`${base}-${crypto.randomUUID().slice(0,6)}`; }
  const id=crypto.randomUUID();
  const now=new Date().toISOString();
  const details={full_name,state_bar_council,enrolment_number,enrolment_year,qualification,city,state,practice_areas,courts,professional_website,linkedin_url};
  await context.env.DB.batch([
    context.env.DB.prepare(`INSERT INTO profiles (id,slug,profile_type,status,full_name,designation,state_bar_council,enrolment_number,enrolment_year,qualification,city,state,bio,practice_areas_json,courts_json,professional_website,linkedin_url,photo_url,submitted_email,accuracy_confirmed,publication_consent,conduct_confirmed,created_at,updated_at) VALUES (?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?)`).bind(id,slug,"advocate","pending",full_name,"Advocate",state_bar_council,enrolment_number,enrolment_year,qualification,city,state,bio,JSON.stringify(practice_areas),JSON.stringify(courts),professional_website,linkedin_url,null,email,1,1,1,now,now),
    context.env.DB.prepare(`INSERT INTO profile_submissions (id,profile_id,submitted_email,ip_hash,created_at) VALUES (?,?,?,?,?)`).bind(crypto.randomUUID(),id,email,ip_hash,now),
    context.env.DB.prepare(`INSERT INTO audit_log (id,profile_id,actor_type,action,details_json,created_at) VALUES (?,?,?,?,?,?)`).bind(crypto.randomUUID(),id,"profile_owner","submitted",JSON.stringify(details),now)
  ]);
  return json({ok:true,message:"Profile submitted successfully. It is pending administrative review and will not be publicly listed until approved.",reference_id:id},201);
}
