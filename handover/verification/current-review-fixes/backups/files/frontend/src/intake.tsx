import { useEffect, useRef, useState } from "react";
import type { Draft, DraftPage, DraftContent, DuplicatePage, IntakeComparison, SuppliedClaim, ResearchSubjectsResponse } from "./api-schema";
import { useResource } from "./hooks";
import { Status } from "./shared";

type ClaimForm={source:SuppliedClaim;precision:"unknown"|"day"|"month"|"year";value:string};
type Form={name:string;aliases:string;description:string;claims:ClaimForm[];research_subject_id:string|null};
const unknown={precision:"unknown" as const,lower_bound:null,upper_bound:null};
const blank:Form={name:"",aliases:"",description:"",claims:[],research_subject_id:null};
const newClaim=():ClaimForm=>({source:{field:"solution",text:"",source_url:"",source_title:"",publisher:"",locator:"",source_relationship:"other_identified",retrieved_on:"",published_date:unknown,effective_date:unknown},precision:"unknown",value:""});
function toDate(c:ClaimForm) {
 if(c.precision==="unknown")return unknown;
 if(c.precision==="day")return {precision:c.precision,lower_bound:c.value,upper_bound:c.value};
 if(c.precision==="year"){if(!/^\d{4}$/.test(c.value))throw Error("Publication year must be YYYY");return {precision:c.precision,lower_bound:c.value+"-01-01",upper_bound:c.value+"-12-31"};}
 if(!/^\d{4}-\d{2}$/.test(c.value))throw Error("Publication month must be YYYY-MM");
 const [y,m]=c.value.split("-").map(Number);const last=new Date(Date.UTC(y,m,0)).getUTCDate();
 return {precision:c.precision,lower_bound:c.value+"-01",upper_bound:c.value+"-"+String(last).padStart(2,"0")};
}
async function post<T>(path:string,body:unknown):Promise<T>{
 const response=await fetch("/api"+path,{method:"POST",headers:{"Content-Type":"application/json"},body:JSON.stringify(body)});
 if(!response.ok){const d=await response.json().catch(()=>null);throw Error(typeof d?.detail==="string"?d.detail:response.status===503?"Saving unavailable. Your input is retained; retry later.":"Check required fields, source URLs and dates. Your input is retained.");}return response.json();
}
export function IntakeWorkspace(){
 const [form,setForm]=useState<Form>(()=>{try{return {...blank,...JSON.parse(localStorage.getItem("vee:intake-form:1")||"{}")} as Form;}catch{return blank;}});
 const [saved,setSaved]=useState<Draft|null>(null);const [comparison,setComparison]=useState<IntakeComparison|null>(null);
 const [error,setError]=useState("");const [busy,setBusy]=useState(false);const [retry,setRetry]=useState(0);const [policy,setPolicy]=useState<"exploration"|"accepted">("exploration");
 const requestID=useRef(crypto.randomUUID());const pending=useRef(0);
 const {data:research}=useResource<ResearchSubjectsResponse>("/research/subjects");
 const {data:list,error:listError}=useResource<DraftPage>("/intake/drafts",retry);
 const {data:duplicates}=useResource<DuplicatePage>("/intake/duplicates?q="+encodeURIComponent(form.name)+"&aliases="+encodeURIComponent(form.aliases)+"&exclude_draft="+encodeURIComponent(saved?.draft_id||""),0,150);
 useEffect(()=>{localStorage.setItem("vee:intake-form:1",JSON.stringify(form));requestID.current=crypto.randomUUID();pending.current++;setComparison(null);},[form]);
 useEffect(()=>{pending.current++;setComparison(null);return()=>{pending.current++;};},[policy]);
 function open(d:Draft){setSaved(d);setError("");setForm({name:d.content.name,aliases:(d.content.aliases||[]).join(", "),description:d.content.description||"",research_subject_id:d.content.research_subject_id||null,claims:(d.content.claims||[]).map(source=>({source,precision:source.published_date.precision,value:source.published_date.lower_bound?.slice(0,source.published_date.precision==="year"?4:source.published_date.precision==="month"?7:10)||""}))});}
 function claim(i:number,key:keyof SuppliedClaim,value:string){setForm(f=>({...f,claims:f.claims.map((c,n)=>n===i?{...c,source:{...c.source,[key]:value}}:c)}));}
 async function save(e:React.FormEvent){e.preventDefault();setBusy(true);setError("");try{
  const content:DraftContent={format_version:"venture-intake:1",name:form.name,aliases:form.aliases.split(",").map(s=>s.trim()).filter(Boolean),description:form.description,research_subject_id:form.research_subject_id,claims:form.claims.map(c=>({...c.source,published_date:toDate(c)}))};
  const d=await post<Draft>(saved?`/intake/drafts/${saved.draft_id}/revisions`:"/intake/drafts",{...content,request_id:requestID.current,expected_revision:saved?.revision_number||null});setSaved(d);setRetry(n=>n+1);requestID.current=crypto.randomUUID();
 }catch(e){setError((e as Error).message);}finally{setBusy(false);}}
 async function compare(){if(!saved)return;const id=++pending.current;setBusy(true);setError("");try{const result=await post<IntakeComparison>(`/intake/drafts/${saved.draft_id}/compare`,{policy,mode:"product_customer"});if(id===pending.current)setComparison(result);}catch(e){if(id===pending.current)setError((e as Error).message);}finally{setBusy(false);}}
 return <section className="intake-workspace"><p className="notice">Saved drafts are local user assertions. Supplied source attributions remain unreviewed. Saving never accepts identity, legal facts or retrieval evidence.</p>
 <div className="intake-layout"><section><h2>{saved?"Edit saved draft":"Add venture"}</h2><form onSubmit={save}><fieldset disabled={busy} className="intake-form">
 <label>Venture or project name<input aria-label="Venture or project name" required maxLength={300} value={form.name} onChange={e=>setForm({...form,name:e.target.value})}/></label>
 <label>Aliases (comma separated)<input value={form.aliases} onChange={e=>setForm({...form,aliases:e.target.value})}/></label>
 <label>Description<textarea aria-label="Description" maxLength={5000} value={form.description} onChange={e=>setForm({...form,description:e.target.value})}/></label>
 <label>Existing research query subject (optional)<select value={form.research_subject_id||''} onChange={e=>setForm({...form,research_subject_id:e.target.value||null})}><option value=''>Unresolved new subject</option>{research?.items.map(s=><option key={s.subject_id} value={s.subject_id}>{s.display_name} · {s.identity_link_status}</option>)}</select></label>
 {!!duplicates?.items.length&&<aside className="notice"><strong>Possible identity duplicates — unresolved</strong><ul>{duplicates.items.map(d=><li key={d.kind+d.subject_id}>{d.display_name} · {d.kind} · {d.basis}</li>)}</ul>No name-based merge.</aside>}
 {form.claims.map((c,i)=><fieldset key={i}><legend>Optional source attribution {i+1} · unreviewed</legend>
 {([['text','Attributed claim'],['source_url','Source URL'],['source_title','Source title'],['publisher','Publisher'],['locator','Passage locator'],['retrieved_on','Retrieval date']] as const).map(([key,title])=><label key={key}>{title}<input required type={key==='source_url'?'url':key==='retrieved_on'?'date':'text'} value={c.source[key]} onChange={e=>claim(i,key,e.target.value)}/></label>)}
 <label>Assertion field<select value={c.source.field} onChange={e=>claim(i,'field',e.target.value)}>{['problem','solution','intended_user','buyer','technology','business_model','validation','deployment','other'].map(s=><option key={s}>{s}</option>)}</select></label>
 <label>Claim responsibility<select value={c.source.source_relationship} onChange={e=>claim(i,'source_relationship',e.target.value)}>{['entrant','company','university','customer','regulator','investor','project_team','other_identified'].map(s=><option key={s}>{s}</option>)}</select></label>
 <label>Publication precision<select value={c.precision} onChange={e=>setForm({...form,claims:form.claims.map((v,n)=>n===i?{...v,precision:e.target.value as ClaimForm['precision']}:v)})}>{['unknown','year','month','day'].map(s=><option key={s}>{s}</option>)}</select></label>
 {c.precision!=='unknown'&&<label>Publication value<input required value={c.value} onChange={e=>setForm({...form,claims:form.claims.map((v,n)=>n===i?{...v,value:e.target.value}:v)})}/></label>}
 <p className="muted">User-supplied attribution, not authenticated publisher evidence. Occurrence dates stay unknown unless supplied separately through the versioned API.</p>
 <button type="button" onClick={()=>setForm({...form,claims:form.claims.filter((_,n)=>n!==i)})}>Remove attribution {i+1}</button></fieldset>)}
 <button type="button" onClick={()=>setForm({...form,claims:[...form.claims,newClaim()]})}>Add optional source attribution</button>
 <button type="submit">{busy?'Working…':saved?'Save revision':'Save draft'}</button><button type="button" onClick={()=>{setSaved(null);setForm(blank);setComparison(null);setError('');}}>Start another draft</button>
 </fieldset></form>{error&&<Status error>{error}</Status>}
 {saved&&<section className="saved-draft"><h3>Saved: {saved.content.name}</h3><p>Draft / unreviewed · revision {saved.revision_number} · identity unresolved</p><p>Unknown / unverified: {saved.unknowns.join(', ')}</p><label>Candidate evidence policy<select value={policy} onChange={e=>setPolicy(e.target.value as typeof policy)}><option value="exploration">Exploration</option><option value="accepted">Accepted only</option></select></label><button disabled={busy} type="button" onClick={compare}>Compare saved draft</button><p className="muted">Uses the last saved revision. Unsaved edits remain in the form.</p></section>}
 </section><aside><h2>Saved local drafts</h2>{listError&&<Status error>{listError}</Status>}{list?.items.map(d=><p key={d.draft_id}><button type="button" onClick={()=>open(d)}>{d.content.name} · revision {d.revision_number}</button></p>)}{list?.total===0&&<p>No saved drafts.</p>}</aside></div>
 {comparison&&<section className="intake-comparison"><h2>Saved-draft comparison</h2><p>{comparison.identity_limitation}</p><p>Query inputs: {comparison.query_fields.join(', ')||'No descriptive evidence supplied'} · {comparison.wrapper_version} · base {comparison.baseline_version}</p><div className="table-scroll" tabIndex={0}><table><thead><tr><th>Record</th><th>Disposition</th><th>Matching evidence</th><th>Unknown / unverified</th></tr></thead><tbody><tr><th>{comparison.draft.content.name}</th><td>Saved draft · query only</td><td>{comparison.effective_query||'No informative input'}</td><td>{comparison.draft.unknowns.join(', ')}</td></tr>{comparison.results.map(r=><tr key={r.venture.venture_id}><th>{r.venture.display_name}</th><td>Lexical score {r.ranking_score.toFixed(3)}</td><td>{r.matched_terms.join(', ')}{r.evidence.map(e=><p key={e.observation.observation_id}><a href={e.observation.url} target="_blank" rel="noreferrer">{e.observation.source_title}</a> · {e.observation.locator} · {e.observation.review_status}</p>)}</td><td>{r.unavailable_evidence.join(', ')}</td></tr>)}</tbody></table></div>{comparison.abstention_reason&&<Status>{comparison.abstention_reason}</Status>}</section>}
 </section>;
}
