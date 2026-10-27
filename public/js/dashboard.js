(() => {
const T = {
 ar:{total:"إجمالي الجهات",hospitals:"المستشفيات",gov:"المحافظات",cat:"التصنيفات",tUnit:"جهة مسجلة",hUnit:"مستشفى ومركز طبي",gUnit:"محافظة / منطقة",cUnit:"نوع مختلف",
  byGov:"توزيع الجهات حسب المحافظات",byCat:"توزيع الجهات حسب التصنيف",other:"أخرى",map:"توزيع الجهات على الخريطة",mapBtn:"عرض الخريطة",mapNote:"عرض توضيحي للمواقع وليس خريطة جغرافية دقيقة.",
  recent:"أحدث الجهات المضافة",add:"+ إضافة جهة جديدة",name:"اسم الجهة",g:"المحافظة",area:"المنطقة",c:"التصنيف",ph:"رقم الهاتف",hl:"الخط الساخن",hrs:"مواعيد العمل",addr:"العنوان",svc:"الخدمات المقدمة",
  act:"الإجراءات",view:"عرض",edit:"تعديل",del:"حذف",save:"حفظ",cancel:"إلغاء",close:"إغلاق",confirm:"هل أنت متأكد من حذف هذه الجهة؟ لا يمكن التراجع.",
  showing:(a,b,n)=>`عرض (${a}-${b} من ${n} جهة)`,prev:"السابق",next:"التالي",all:"عرض جميع الجهات",less:"عرض أحدث 5 فقط",empty:"لا توجد نتائج.",
  count:"عدد الجهات",share:"النسبة",govT:"المحافظات والمناطق",govS:"توزيع الجهات المسجلة حسب المحافظة",catT:"التصنيفات",catS:"أنواع الجهات وعدد كل نوع",
  impT:"استيراد البيانات",impS:"ارفع ملف CSV لإضافة جهات جديدة دفعة واحدة",impHint:"يجب أن يحتوي الملف (UTF-8) على العمود service_name_ar على الأقل، ويمكن إضافة: governorate, city_area, phone_number, hotline, category, address, available_hours, services_provided",
  choose:"اختيار ملف CSV",upload:"رفع واستيراد",imported:n=>`تم استيراد ${n} جهة بنجاح.`,err:"حدث خطأ، حاول مرة أخرى.",saved:"تم الحفظ."},
 en:{total:"Total entities",hospitals:"Hospitals",gov:"Governorates",cat:"Categories",tUnit:"registered entities",hUnit:"hospitals & medical centers",gUnit:"governorates / regions",cUnit:"different types",
  byGov:"Entities by governorate",byCat:"Entities by category",other:"Other",map:"Entities on the map",mapBtn:"View map",mapNote:"Illustrative plot of locations, not an accurate geographic map.",
  recent:"Recently added entities",add:"+ Add new entity",name:"Entity name",g:"Governorate",area:"Area",c:"Category",ph:"Phone",hl:"Hotline",hrs:"Working hours",addr:"Address",svc:"Services provided",
  act:"Actions",view:"View",edit:"Edit",del:"Delete",save:"Save",cancel:"Cancel",close:"Close",confirm:"Delete this entity? This cannot be undone.",
  showing:(a,b,n)=>`Showing ${a}-${b} of ${n} entities`,prev:"Previous",next:"Next",all:"View all entities",less:"Show latest 5 only",empty:"No results.",
  count:"Entities",share:"Share",govT:"Governorates & Areas",govS:"Registered entities by governorate",catT:"Categories",catS:"Entity types and how many of each",
  impT:"Import Data",impS:"Upload a CSV file to add many entities at once",impHint:"The UTF-8 file needs at least the column service_name_ar; optional: governorate, city_area, phone_number, hotline, category, address, available_hours, services_provided",
  choose:"Choose CSV file",upload:"Upload & import",imported:n=>`Imported ${n} entities successfully.`,err:"Something went wrong, please try again.",saved:"Saved."}
};
const COLORS=["#E91443","#2f7be5","#f5b82e","#1fa463","#8b5cf6","#d4b483"];
const FIELDS=[["service_name_ar","name"],["governorate","g"],["city_area","area"],["category","c"],["phone_number","ph"],["hotline","hl"],["available_hours","hrs"],["address","addr"],["services_provided","svc"]];
const S={sum:null,ent:{rows:[],total:0},page:1,per:5,q:""};
const L=()=>T[document.documentElement.lang==="en"?"en":"ar"];
const $=s=>document.querySelector(s);
const esc=s=>String(s??"").replace(/[&<>"]/g,c=>({"&":"&amp;","<":"&lt;",">":"&gt;",'"':"&quot;"}[c]));
const csrf=()=>document.querySelector('meta[name="csrf-token"]')?.content??"";
async function api(url,opt={}){const r=await fetch(url,{...opt,headers:{"X-CSRF-Token":csrf(),...(opt.headers||{})}});const d=await r.json().catch(()=>({}));if(!r.ok)throw new Error(d.message||"error");return d;}
const goto=id=>document.querySelector(`.nav-link[data-target="${id}"]`)?.click();

function mapSvg(pts){
 if(!pts.length)return"";
 const la=pts.map(p=>p.lat),lo=pts.map(p=>p.lon),a=Math.min(...la),b=Math.max(...la),c=Math.min(...lo),d=Math.max(...lo);
 const W=400,H=210,P=14,sx=(W-2*P)/((d-c)||1),sy=(H-2*P)/((b-a)||1),k=Math.min(sx,sy);
 return `<svg class="vd-map" viewBox="0 0 ${W} ${H}" preserveAspectRatio="xMidYMid meet">${pts.map(p=>`<circle cx="${P+(p.lon-c)*k+((W-2*P)-(d-c)*k)/2}" cy="${P+(b-p.lat)*k+((H-2*P)-(b-a)*k)/2}" r="3.2"><title>${esc(p.name)}</title></circle>`).join("")}</svg>`;
}
function renderDash(){
 const root=$("#vd-root"),s=S.sum;if(!root||!s)return;const t=L();
 const max=Math.max(...s.by_governorate.map(x=>x[1]),1),tot=s.by_category.reduce((n,x)=>n+x[1],0)||1;
 let acc=0;const stops=s.by_category.map((x,i)=>{const p=acc/tot*100;acc+=x[1];return`${COLORS[i%6]} ${p}% ${acc/tot*100}%`}).join(",");
 const card=(cls,ico,l,v,u)=>`<article class="vd-card ${cls}"><div><span>${l}</span><h3>${v}</h3><small>${u}</small></div><span class="vd-ico">${ico}</span></article>`;
 root.innerHTML=`<div class="vd-cards">${card("vd-c1","✚",t.total,s.total,t.tUnit)}${card("vd-c2","▣",t.hospitals,s.hospitals,t.hUnit)}${card("vd-c3","⌖",t.gov,s.governorates,t.gUnit)}${card("vd-c4","▤",t.cat,s.categories,t.cUnit)}</div>
 <div class="vd-charts">
 <div class="vd-panel"><h3>${t.byGov}</h3><div class="vd-bars">${s.by_governorate.map(([n,v])=>`<div class="vd-bar"><span>${v}</span><i style="height:${v/max*140}px"></i><span>${esc(n)}</span></div>`).join("")}</div></div>
 <div class="vd-panel"><h3>${t.byCat}</h3><div class="vd-donut-wrap"><div class="vd-donut" style="background:conic-gradient(${stops})"><b>${tot}</b></div><ul class="vd-legend">${s.by_category.map(([n,v],i)=>`<li><i style="background:${COLORS[i%6]}"></i><span>${n==="__other__"?t.other:esc(n)}</span><small>${(v/tot*100).toFixed(1)}%</small></li>`).join("")}</ul></div></div>
 <div class="vd-panel"><h3>${t.map}</h3>${mapSvg(s.points)}<p class="vd-note">${t.mapNote}</p><button class="vd-pill" data-go="clinics" style="margin-top:8px">${t.mapBtn}</button></div>
 </div>
 <div class="section-title"><div><h2>${t.recent}</h2></div><button type="button" class="primary-button" id="vdAdd">${t.add}</button></div>
 <div class="table-wrapper"><table><thead><tr><th>#</th><th>${t.name}</th><th>${t.g}</th><th>${t.area}</th><th>${t.c}</th><th>${t.ph}</th><th>${t.hl}</th><th>${t.hrs}</th><th>${t.act}</th></tr></thead><tbody id="vdRows"></tbody></table></div>
 <div class="vd-foot" id="vdFoot"></div>`;
 renderRows();
}
function renderRows(){
 const body=$("#vdRows"),foot=$("#vdFoot");if(!body)return;const t=L(),{rows,total}=S.ent;
 body.innerHTML=rows.length?rows.map(r=>`<tr><td>${esc(r.contact_id)}</td><td>${esc(r.service_name_ar)}</td><td>${esc(r.governorate)}</td><td>${esc(r.city_area)}</td><td>${esc(r.category)}</td><td dir="ltr">${esc(r.phone_number)}</td><td dir="ltr">${esc(r.hotline)}</td><td>${esc(r.available_hours)}</td>
  <td><div class="vd-actions"><button data-a="view" data-id="${esc(r.contact_id)}">${t.view}</button><button data-a="edit" data-id="${esc(r.contact_id)}">${t.edit}</button><button class="del" data-a="del" data-id="${esc(r.contact_id)}">${t.del}</button></div></td></tr>`).join(""):`<tr><td colspan="9">${t.empty}</td></tr>`;
 const from=total?(S.page-1)*S.per+1:0,to=Math.min(S.page*S.per,total);
 foot.innerHTML=`<span>${t.showing(from,to,total)}</span><span><button data-p="-1" ${S.page<=1?"disabled":""}>${t.prev}</button> <button data-p="1" ${to>=total?"disabled":""}>${t.next}</button></span><button data-all="1">${S.per===5?t.all:t.less}</button>`;
}
function renderTable(id,title,sub,list){
 const el=$("#vd-"+id);if(!el)return;const t=L(),tot=list.reduce((n,x)=>n+x[1],0)||1;
 el.innerHTML=`<div class="section-title"><div><h2>${title}</h2><p>${sub}</p></div></div><div class="table-wrapper"><table><thead><tr><th>#</th><th>${id==="governorates"?t.g:t.c}</th><th>${t.count}</th><th>${t.share}</th></tr></thead><tbody>${list.map(([n,v],i)=>`<tr><td>${i+1}</td><td>${esc(n)}</td><td>${v}</td><td>${(v/tot*100).toFixed(1)}%</td></tr>`).join("")}</tbody></table></div>`;
}
function renderImport(){
 const el=$("#vd-import");if(!el)return;const t=L();
 el.innerHTML=`<div class="section-title"><div><h2>${t.impT}</h2><p>${t.impS}</p></div></div><div class="vd-panel"><label class="vd-drop"><strong>${t.choose}</strong><br><input type="file" id="vdFile" accept=".csv,text/csv"></label><p class="vd-note">${t.impHint}</p><button class="primary-button" id="vdUpload" style="margin-top:12px">${t.upload}</button><p class="vd-msg" id="vdImpMsg"></p></div>`;
}
function renderAll(){renderDash();if(S.sum){renderTable("governorates",L().govT,L().govS,S.sum.gov_all);renderTable("categories",L().catT,L().catS,S.sum.cat_all);}renderImport();}

function openDialog(mode,row={}){
 const t=L(),f=$("#entityForm"),ro=mode==="view";
 f.innerHTML=`<div class="dialog-heading"><h2>${t[mode==="add"?"add":mode].replace("+ ","")}</h2><button type="button" class="icon-button" data-close>×</button></div>
 <div class="dialog-grid">${FIELDS.map(([k,l])=>`<label class="${k==="services_provided"||k==="address"?"dialog-wide":""}"><span>${t[l]}</span>${k==="services_provided"?`<textarea name="${k}" rows="3" ${ro?"readonly":""}>${esc(row[k])}</textarea>`:`<input name="${k}" value="${esc(row[k])}" ${ro?"readonly":""} ${k==="service_name_ar"?"required":""}>`}</label>`).join("")}</div>
 <p class="feedback-message" id="entityMsg"></p>
 <div class="dialog-actions"><button type="button" class="secondary-button" data-close>${ro?t.close:t.cancel}</button>${ro?"":`<button type="submit" class="primary-button">${t.save}</button>`}</div>`;
 f.dataset.mode=mode;f.dataset.id=row.contact_id||"";$("#entityDialog").showModal();
}
async function loadSum(){try{S.sum=await api("/api/dashboard/summary");renderAll();}catch(e){}}
async function loadEnt(){try{S.ent=await api(`/api/entities?page=${S.page}&per_page=${S.per}&q=${encodeURIComponent(S.q)}`);renderRows();}catch(e){}}
async function loadBell(){try{const d=await (await fetch("/api/analytics")).json();const n=d.analytics?.total_searches||0,b=$("#bellCount");if(b){b.textContent=n;b.hidden=!n;}}catch(e){}}
const reload=()=>{loadSum();loadEnt();loadBell();};

document.addEventListener("DOMContentLoaded",()=>{
 reload();
 new MutationObserver(renderAll).observe(document.documentElement,{attributes:true,attributeFilter:["lang"]});
 $("#refreshButton")?.addEventListener("click",reload);
 $("#bellButton")?.addEventListener("click",()=>goto("analytics"));
 $("#globalSearchForm")?.addEventListener("submit",e=>{e.preventDefault();S.q=$("#globalSearch").value.trim();S.page=1;goto("dashboard");loadEnt();});
 $("#entityDialog").addEventListener("click",e=>{if(e.target.hasAttribute("data-close"))$("#entityDialog").close();});
 $("#entityForm").addEventListener("submit",async e=>{
  e.preventDefault();const f=e.target,m=f.dataset.mode;if(m==="view")return;
  const body=Object.fromEntries(new FormData(f));
  try{await api(m==="add"?"/api/entities":`/api/entities/${f.dataset.id}`,{method:m==="add"?"POST":"PUT",headers:{"Content-Type":"application/json"},body:JSON.stringify(body)});$("#entityDialog").close();reload();}
  catch(err){$("#entityMsg").textContent=L().err;}
 });
 document.addEventListener("click",async e=>{
  const b=e.target.closest("button");if(!b)return;
  if(b.id==="vdAdd")return openDialog("add");
  if(b.dataset.go)return goto(b.dataset.go);
  if(b.dataset.p){S.page=Math.max(1,S.page+Number(b.dataset.p));return loadEnt();}
  if(b.dataset.all){S.per=S.per===5?25:5;S.page=1;return loadEnt();}
  if(b.dataset.a){
   const row=S.ent.rows.find(r=>r.contact_id===b.dataset.id);if(!row)return;
   if(b.dataset.a==="del"){if(confirm(L().confirm)){try{await api(`/api/entities/${row.contact_id}`,{method:"DELETE"});reload();}catch(x){alert(L().err);}}return;}
   return openDialog(b.dataset.a,row);
  }
  if(b.id==="vdUpload"){
   const file=$("#vdFile").files[0],msg=$("#vdImpMsg");if(!file)return;const fd=new FormData();fd.append("file",file);
   try{const d=await api("/api/import",{method:"POST",body:fd});msg.textContent=L().imported(d.imported);reload();}catch(x){msg.textContent=x.message||L().err;}
  }
 });
});
})();
