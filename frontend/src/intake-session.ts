import type {Draft, SaveDraft, SuppliedClaim} from './api-schema';
export type ClaimForm={source:SuppliedClaim;precision:'unknown'|'day'|'month'|'year';value:string};
export type Form={name:string;aliases:string;description:string;claims:ClaimForm[];research_subject_id:string|null};
export type Editor={version:2;editor_id:string;form:Form;draft_id:string|null;base_revision:number|null;pending:{path:string;body:SaveDraft}|null;legacy:boolean};
export const storageKey='vee:intake-editor:2';
export const blank:Form={name:'',aliases:'',description:'',claims:[],research_subject_id:null};
export function newEditor(form:Form={...blank},draft:Draft|null=null):Editor{return {version:2,editor_id:crypto.randomUUID(),form,draft_id:draft?.draft_id||null,base_revision:draft?.revision_number||null,pending:null,legacy:false};}
export function draftForm(d:Draft):Form{return {name:d.content.name,aliases:(d.content.aliases||[]).join(', '),description:d.content.description||'',research_subject_id:d.content.research_subject_id||null,claims:(d.content.claims||[]).map(source=>({source,precision:source.published_date.precision,value:source.published_date.lower_bound?.slice(0,source.published_date.precision==='year'?4:source.published_date.precision==='month'?7:10)||''}))};}
export function readEditor():Editor{
 try{
  const raw=localStorage.getItem(storageKey);
  if(raw){const e=JSON.parse(raw) as Editor;if(e.version===2&&typeof e.editor_id==='string'&&e.form&&typeof e.form.name==='string'&&Array.isArray(e.form.claims)&&((e.draft_id===null&&e.base_revision===null)||(typeof e.draft_id==='string'&&Number.isInteger(e.base_revision)&&Number(e.base_revision)>0)))return e;}
  const old=JSON.parse(localStorage.getItem('vee:intake-form:1')||'null');
  if(old){const form={...blank,...old} as Form;return {...newEditor(form),legacy:!!(form.name||form.description||form.aliases||form.claims.length)};}
 }catch{/* Original recovery entries remain available; no automatic writes on mount. */}
 return newEditor();
}
