document.addEventListener("DOMContentLoaded",()=>{
"use strict";
const $=s=>document.querySelector(s), $$=s=>[...document.querySelectorAll(s)];
const sidebar=$("#sidebar"),scrim=$("#sidebarScrim");
function closeNav(){sidebar?.classList.remove("open");scrim?.classList.remove("show")}
$("#sidebarToggle")?.addEventListener("click",()=>{sidebar.classList.toggle("open");scrim.classList.toggle("show")});
scrim?.addEventListener("click",closeNav);
$$(".side-link").forEach(a=>a.addEventListener("click",closeNav));
$("#year").textContent=new Date().getFullYear();
const sections=$$(".studio-section[id]"),links=$$(".side-link");
if("IntersectionObserver"in window){const io=new IntersectionObserver(entries=>entries.forEach(e=>{if(e.isIntersecting)links.forEach(a=>a.classList.toggle("active",a.hash==="#"+e.target.id))}),{rootMargin:"-25% 0px -65% 0px"});sections.forEach(s=>io.observe(s))}
function message(out,text,ok=true){if(out){out.textContent=text;out.style.color=ok?"#7fffc4":"#ff9cae"}}
async function api(url,options={}){const r=await fetch(url,{...options,headers:{"Content-Type":"application/json",...(options.headers||{})}});const data=await r.json().catch(()=>({}));if(!r.ok)throw new Error(data.error||"در ارتباط با سرور مشکلی پیش آمد.");return data}
async function loadSite(){try{const d=await api("/api/site");const grid=$("#projectGrid");grid.replaceChildren();(d.projects||[]).forEach(p=>{const u=p.url||"",title=p.title||"ربات تلگرام";const type=u.includes("mohammad123alizadeh_bot")?"war":u.includes("mohammad12543778alizadeh_bot")?"dollar":u.includes("mohammad125437178alizadeh_bot")?"time":u.includes("mohammad127437178alizadeh_bot")?"hafez":u.includes("mohammad12543alizadeh_bot")?"age":title.includes("حافظ")?"hafez":title.includes("سن")?"age":title.includes("ساعت")?"time":title.includes("دلار")?"dollar":"war";const a=document.createElement("a");a.className="studio-card project-card";a.href=u;a.target="_blank";a.rel="noopener";const art=document.createElement("div");art.className="project-art";const img=document.createElement("img");img.className="project-cover";img.src="/images/bots/"+type+".svg?v=studio20261110";img.alt="تصویر "+title;img.onerror=()=>img.remove();art.append(img);const info=document.createElement("div");info.className="project-info";const desc=document.createElement("div");const h=document.createElement("h3");h.textContent=title;const pdesc=document.createElement("p");pdesc.textContent=p.description||"";desc.append(h,pdesc);const arrow=document.createElement("span");arrow.className="project-arrow";arrow.textContent="↗";info.append(desc,arrow);const tags=document.createElement("div");tags.className="project-tags";tags.innerHTML="<span>ربات تلگرام</span>";a.append(art,info,tags);grid.append(a)});$("#projectCount").textContent=(d.projects||[]).length+" ربات ثبت‌شده";}catch(e){$("#projectCount").textContent="دریافت اطلاعات ناموفق"}}
async function loadPortfolio(){const box=$("#portfolioGrid"),count=$("#portfolioCount");try{const d=await api("/api/site");const rows=Array.isArray(d.portfolio)?d.portfolio:[];box.replaceChildren();count.textContent=rows.length.toLocaleString("fa-IR")+" پروژه";if(!rows.length){const empty=document.createElement("div");empty.className="glass-panel portfolio-empty";empty.textContent="هنوز پروژه‌ای ثبت نشده است. پروژه‌های جدید به‌زودی در این بخش معرفی می‌شوند.";box.append(empty);return}rows.forEach(item=>{const card=document.createElement("article");card.className="studio-card portfolio-card";const art=document.createElement("div");art.className="portfolio-art";if(item.image){const img=document.createElement("img");img.src=item.image;img.alt="تصویر "+(item.title||"پروژه");img.loading="lazy";img.onerror=()=>{img.remove();art.classList.add("portfolio-art-empty")};art.append(img)}else{art.classList.add("portfolio-art-empty");const mark=document.createElement("span");mark.textContent="✦";art.append(mark)}const body=document.createElement("div");body.className="portfolio-body";const category=document.createElement("span");category.className="soft-tag";category.textContent=item.category||"پروژه";const title=document.createElement("h3");title.textContent=item.title||"پروژه بدون عنوان";const desc=document.createElement("p");desc.textContent=item.description||"توضیحی برای این پروژه ثبت نشده است.";body.append(category,title,desc);card.append(art,body);if(item.url){const link=document.createElement("a");link.className="portfolio-link";link.href=item.url;link.target="_blank";link.rel="noopener noreferrer";link.textContent="مشاهده پروژه ↗";card.append(link)}box.append(card)})}catch(e){box.replaceChildren();count.textContent="خطا در دریافت";const error=document.createElement("div");error.className="glass-panel";error.textContent="بارگذاری پروژه‌ها انجام نشد. لطفاً بعداً دوباره تلاش کن.";box.append(error)}}
async function loadStats(){try{const d=await api("/api/stats");$("#statBots").textContent=d.bots??"—";$("#statVisits").textContent=Number(d.visits||0).toLocaleString("fa-IR");$("#statProjects").textContent=d.projects??"نامشخص";$("#statUsers").textContent=d.users??"نامشخص";$("#statServices").textContent=d.services??"نامشخص"}catch{}}
async function loadStatus(){const box=$("#statusList");try{const rows=await api("/api/status");box.replaceChildren();rows.forEach(x=>{const card=document.createElement("article");card.className="studio-card status-unknown";const h=document.createElement("h3");h.textContent=x.name;const p=document.createElement("p");p.textContent=x.label;card.append(h,p);box.append(card)});if(!rows.length)box.textContent="سرویسی ثبت نشده است."}catch{box.textContent="دریافت وضعیت ممکن نشد."}}
$("#refreshStatus")?.addEventListener("click",loadStatus);
$("#makePassword")?.addEventListener("click",()=>{const n=Math.max(8,Math.min(64,Number($("#passwordLength").value)||16));const chars="ABCDEFGHJKLMNPQRSTUVWXYZabcdefghijkmnopqrstuvwxyz23456789!@#$%&*_-";const bytes=new Uint32Array(n);crypto.getRandomValues(bytes);let s="";for(let i=0;i<n;i++)s+=chars[bytes[i]%chars.length];$("#passwordOutput").textContent=s});
$$("[data-copy]").forEach(b=>b.addEventListener("click",async()=>{const t=$("#"+b.dataset.copy).textContent;if(!t)return;try{await navigator.clipboard.writeText(t);b.textContent="کپی شد";setTimeout(()=>b.textContent="کپی رمز",1200)}catch{message($("#passwordOutput"),"امکان کپی خودکار نیست؛ متن را دستی انتخاب کن.",false)}}));
function showQr(target,data,label){target.replaceChildren();if(label){const p=document.createElement("p");p.textContent=label;target.append(p)}if(data){const img=document.createElement("img");img.alt="کد QR";img.src=data;target.append(img);const a=document.createElement("a");a.href=data;a.download="mohammad-studio-qr.png";a.className="text-action";a.textContent="دانلود تصویر QR";target.append(a)}}
$("#makeQr")?.addEventListener("click",async()=>{const value=$("#qrText").value.trim(),out=$("#qrOutput");if(!value){message(out,"ابتدا متن یا لینک را وارد کن.",false);return}out.textContent="در حال ساخت QR…";try{const d=await api("/api/qr/generate",{method:"POST",body:JSON.stringify({text:value})});showQr(out,d.qr,"QR با موفقیت ساخته شد.")}catch(e){message(out,e.message,false)}});
$("#makeMediaQr")?.addEventListener("click",async()=>{const file=$("#qrMediaFile").files[0],out=$("#qrMediaOutput");if(!file){message(out,"ابتدا عکس یا ویدیو را انتخاب کن.",false);return}const form=new FormData();form.append("file",file);out.textContent="در حال بارگذاری فایل و ساخت QR…";try{const r=await fetch("/api/qr/upload",{method:"POST",body:form});const d=await r.json().catch(()=>({}));if(!r.ok)throw new Error(d.error||"بارگذاری فایل ناموفق بود.");showQr(out,d.qr,"QR فایل آماده شد. لینک مستقیم فایل:");const a=document.createElement("a");a.href=d.url;a.target="_blank";a.rel="noopener";a.textContent=d.url;a.className="text-action";out.append(a)}catch(e){message(out,e.message,false)}});
$("#decodeQr")?.addEventListener("click",async()=>{const file=$("#qrDecodeFile").files[0],out=$("#qrDecodeOutput");if(!file){message(out,"ابتدا تصویر QR را انتخاب کن.",false);return}const form=new FormData();form.append("file",file);out.textContent="در حال خواندن QR…";try{const r=await fetch("/api/qr/decode",{method:"POST",body:form});const d=await r.json().catch(()=>({}));if(!r.ok)throw new Error(d.error||"خواندن QR ناموفق بود.");out.replaceChildren();d.contents.forEach((value,index)=>{const p=document.createElement("p");p.textContent=(d.count>1?"کد "+(index+1)+": ":"محتوای QR: ")+value;out.append(p);if(value.startsWith("http://")||value.startsWith("https://")){const a=document.createElement("a");a.href=value;a.target="_blank";a.rel="noopener noreferrer";a.textContent="باز کردن لینک";a.className="text-action";out.append(a)}})}catch(e){message(out,e.message,false)}});

const aiMessages = [];
let aiBusy = false;
const AI_HISTORY_KEY = "mohammadStudioAiConversationsV1";
const AI_MODEL_KEY = "mohammadStudioAiModelV1";
const aiMessagesBox = $("#aiMessages"), aiWelcome = $("#aiWelcome"), aiInput = $("#aiInput"), aiSend = $("#aiSend"), aiNotice = $("#aiChatNotice");
const aiModelSelect = $("#aiModelSelect"), aiConversationSelect = $("#aiConversationSelect");
let aiConversations = [];
let activeConversationId = null;
let aiSelectedModel = localStorage.getItem(AI_MODEL_KEY) || "openrouter/free";
async function saveAiHistory(conversation) {
  if (!conversation) return;
  const snapshot = {
    title: conversation.title,
    model: conversation.model,
    messages: conversation.messages.slice(-40)
  };
  const previous = conversation._saveQueue || Promise.resolve();
  conversation._saveQueue = previous.catch(() => {}).then(() =>
    api("/api/ai/conversations/" + encodeURIComponent(conversation.id), {
      method: "PUT", body: JSON.stringify(snapshot)
    })
  );
  try {
    const data = await conversation._saveQueue;
    conversation.updatedAt = data.updatedAt || new Date().toISOString();
    aiConversations.sort((a,b) => Date.parse(b.updatedAt || 0) - Date.parse(a.updatedAt || 0));
    renderAiConversationList();
  } catch (error) {
    message(aiNotice, "ذخیره گفتگو روی سرور انجام نشد: " + error.message, false);
  }
}
function renderAiConversationList() {
  const current = activeConversationId || "";
  aiConversationSelect.replaceChildren();
  const placeholder = document.createElement("option");
  placeholder.value = "";
  placeholder.textContent = "انتخاب گفتگو";
  aiConversationSelect.append(placeholder);
  aiConversations.sort((a,b) => (b.updatedAt || 0) - (a.updatedAt || 0)).forEach(conversation => {
    const option = document.createElement("option");
    option.value = conversation.id;
    option.textContent = conversation.title || "گفتگوی بدون عنوان";
    aiConversationSelect.append(option);
  });
  aiConversationSelect.value = current;
}
function activeAiConversation() {
  return aiConversations.find(item => item.id === activeConversationId) || null;
}
function persistActiveAiConversation() {
  const conversation = activeAiConversation();
  if (!conversation) return;
  conversation.messages = aiMessages.slice(-40);
  conversation.model = aiSelectedModel;
  conversation.updatedAt = new Date().toISOString();
  saveAiHistory(conversation);
  renderAiConversationList();
}
function ensureAiConversation(firstPrompt) {
  let conversation = activeAiConversation();
  if (!conversation) {
    conversation = {id: (crypto.randomUUID ? crypto.randomUUID() : String(Date.now()) + Math.random().toString(16).slice(2)), title: firstPrompt.slice(0,42), model: aiSelectedModel, messages: [], updatedAt: Date.now()};
    aiConversations.unshift(conversation);
    activeConversationId = conversation.id;
  }
  if (!conversation.messages.length && firstPrompt) conversation.title = firstPrompt.replace(/\s+/g," ").slice(0,42);
  conversation.model = aiSelectedModel;
  renderAiConversationList();
  return conversation;
}
function addAiMessage(role, text) {
  const item = document.createElement("article");
  item.className = "ai-message " + (role === "user" ? "ai-user-message" : "ai-assistant-message");
  const label = document.createElement("span");
  label.className = "ai-message-label";
  label.textContent = role === "user" ? "شما" : "دستیار هوشمند";
  const body = document.createElement("p");
  body.textContent = text;
  item.append(label, body);
  if (role === "assistant") {
    const pdfButton = document.createElement("button");
    pdfButton.type = "button";
    pdfButton.className = "ai-manage-btn ai-pdf-export";
    pdfButton.textContent = "ذخیره پاسخ به PDF";
    pdfButton.addEventListener("click", () => {
      const printWindow = window.open("", "_blank");
      if (!printWindow) { message(aiNotice, "اجازه بازشدن پنجره چاپ را بده و دوباره تلاش کن.", false); return; }
      const doc = printWindow.document;
      doc.documentElement.lang = "fa";
      doc.documentElement.dir = "rtl";
      doc.title = "پاسخ دستیار محمد استودیو";
      const style = doc.createElement("style");
      style.textContent = "body{font-family:Tahoma,Arial,sans-serif;direction:rtl;text-align:right;line-height:2.1;padding:36px;color:#172033;white-space:pre-wrap}h1{font-size:20px;border-bottom:1px solid #ddd;padding-bottom:12px}main{font-size:14px}";
      const heading = doc.createElement("h1"); heading.textContent = "پاسخ دستیار هوشمند محمد استودیو";
      const main = doc.createElement("main"); main.textContent = body.textContent;
      doc.body.append(heading, main);
      doc.head.append(style);
      printWindow.focus();
      printWindow.print();
    });
    item.append(pdfButton);
  }
  aiMessagesBox.append(item);
  aiMessagesBox.scrollTop = aiMessagesBox.scrollHeight;
  return item;
}
function restoreAiConversation(id) {
  if (aiBusy) return;
  const conversation = aiConversations.find(item => item.id === id);
  if (!conversation) return;
  activeConversationId = conversation.id;
  aiMessages.splice(0, aiMessages.length, ...conversation.messages.slice(-40));
  aiMessagesBox.replaceChildren();
  aiMessages.forEach(item => addAiMessage(item.role, item.content));
  aiWelcome.hidden = aiMessages.length > 0;
  aiSelectedModel = conversation.model || "openrouter/free";
  aiModelSelect.value = aiSelectedModel;
  localStorage.setItem(AI_MODEL_KEY, aiSelectedModel);
  aiNotice.textContent = "";
  renderAiConversationList();
}
async function loadAiModels() {
  try {
    const data = await api("/api/ai/models");
    const models = Array.isArray(data.models) ? data.models : [];
    const previous = aiSelectedModel;
    aiModelSelect.replaceChildren();
    models.forEach(model => {
      if (!model || typeof model.id !== "string") return;
      const option = document.createElement("option");
      option.value = model.id;
      option.textContent = model.name || model.id;
      option.dataset.vision = model.vision ? "true" : "false";
      aiModelSelect.append(option);
    });
    if (![...aiModelSelect.options].some(option => option.value === previous)) aiSelectedModel = "openrouter/free";
    aiModelSelect.value = aiSelectedModel;
    localStorage.setItem(AI_MODEL_KEY, aiSelectedModel);
  } catch (error) {
    console.warn("AI model list could not be loaded", error);
  }
}
renderAiConversationList();
aiModelSelect.value = aiSelectedModel;
aiModelSelect.addEventListener("change", () => {
  aiSelectedModel = aiModelSelect.value || "openrouter/free";
  localStorage.setItem(AI_MODEL_KEY, aiSelectedModel);
  const conversation = activeAiConversation();
  if (conversation) { conversation.model = aiSelectedModel; persistActiveAiConversation(); }
});
aiConversationSelect.addEventListener("change", () => {
  if (aiConversationSelect.value) restoreAiConversation(aiConversationSelect.value);
});
let aiSelectedAttachment = null;
const aiFileInput = $("#aiFileInput");
const aiFileStatus = $("#aiFileStatus");
$("#aiAttachButton")?.addEventListener("click", () => aiFileInput?.click());
aiFileInput?.addEventListener("change", () => {
  const file = aiFileInput.files[0];
  if (!file) { aiSelectedAttachment = null; aiFileStatus.textContent = ""; return; }
  const allowed = ["application/pdf","image/png","image/jpeg","image/webp","image/gif"];
  if (!allowed.includes(file.type) || file.size > 10 * 1024 * 1024) {
    aiFileInput.value = ""; aiSelectedAttachment = null;
    message(aiNotice, "فقط PDF یا تصویر PNG/JPG/WEBP/GIF تا حجم ۱۰ مگابایت قابل ارسال است.", false);
    aiFileStatus.textContent = ""; return;
  }
  aiSelectedAttachment = file;
  aiFileStatus.textContent = "فایل انتخاب‌شده: " + file.name;
});
function fileAsDataUrl(file) {
  return new Promise((resolve, reject) => {
    const reader = new FileReader();
    reader.onload = () => resolve(reader.result);
    reader.onerror = () => reject(new Error("خواندن فایل ممکن نشد."));
    reader.readAsDataURL(file);
  });
}
async function sendAiMessage(text) {
  const prompt = String(text || "").trim();
  const attachmentFile = aiSelectedAttachment;
  if ((!prompt && !attachmentFile) || aiBusy) return;
  if (attachmentFile && attachmentFile.type.startsWith("image/") && aiModelSelect.selectedOptions[0]?.dataset.vision !== "true") {
    message(aiNotice, "برای بررسی تصویر، از فهرست مدل‌ها مدلی را انتخاب کن که پشتیبانی تصویر دارد.", false);
    return;
  }
  if (prompt.length > 6000) { message(aiNotice, "پیام حداکثر می‌تواند ۶۰۰۰ نویسه باشد.", false); return; }
  const visiblePrompt = prompt || "لطفاً فایل پیوست‌شده را بررسی کن.";
  ensureAiConversation(visiblePrompt);
  aiWelcome.hidden = true;
  aiNotice.textContent = "";
  aiMessages.push({role:"user",content:visiblePrompt + (attachmentFile ? "\\n[فایل پیوست: " + attachmentFile.name + "]" : "")});
  addAiMessage("user",visiblePrompt + (attachmentFile ? "\\n📎 " + attachmentFile.name : ""));
  persistActiveAiConversation();
  aiInput.value = "";
  aiBusy = true;
  aiSend.disabled = true;
  aiSend.textContent = "در حال پاسخ…";
  const pending = addAiMessage("assistant","در حال بررسی…");
  try {
    const attachment = attachmentFile ? {name:attachmentFile.name,type:attachmentFile.type,data:await fileAsDataUrl(attachmentFile)} : null;
    const data = await api("/api/ai/chat",{method:"POST",body:JSON.stringify({messages:aiMessages.slice(-20).map(m=>({role:m.role,content:m.content.replace(/\\n\\[فایل پیوست:.*?\\]$/,"")})),model:aiSelectedModel,attachment})});
    aiSelectedAttachment = null;
    if (aiFileInput) aiFileInput.value = "";
    if (aiFileStatus) aiFileStatus.textContent = "";
    if (!data.reply) throw new Error("پاسخ خالی از سرور دریافت شد.");
    aiMessages.push({role:"assistant",content:data.reply});
    pending.querySelector("p").textContent = data.reply;
    if (data.file && data.file.url) {
      const fileLink = document.createElement("a");
      fileLink.href = data.file.url;
      fileLink.download = data.file.filename || "Mohammad-Studio.docx";
      fileLink.textContent = "دانلود فایل Word آماده‌شده";
      fileLink.className = "ai-manage-btn";
      fileLink.style.display = "inline-block";
      fileLink.style.marginTop = "10px";
      pending.append(fileLink);
    }
    persistActiveAiConversation();
  } catch (error) {
    pending.remove();
    aiMessages.pop();
    persistActiveAiConversation();
    message(aiNotice,error.message,false);
  } finally {
    aiBusy = false;
    aiSend.disabled = false;
    aiSend.textContent = "ارسال ↗";
    aiInput.focus();
    aiMessagesBox.scrollTop = aiMessagesBox.scrollHeight;
  }
}
$("#aiChatForm")?.addEventListener("submit",event=>{event.preventDefault();sendAiMessage(aiInput.value);});
const aiImagePrompt = $("#aiImagePrompt"), aiImageButton = $("#aiImageButton"), aiImageOutput = $("#aiImageOutput");
aiImageButton?.addEventListener("click", async () => {
  const prompt = aiImagePrompt.value.trim();
  if (prompt.length < 3) { message(aiImageOutput, "توضیح تصویر را وارد کن.", false); return; }
  aiImageButton.disabled = true; aiImageButton.textContent = "در حال ساخت…"; aiImageOutput.replaceChildren();
  try {
    const result = await api("/api/ai/image", {method:"POST", body:JSON.stringify({prompt})});
    const img = document.createElement("img"); img.src = result.image; img.alt = prompt; img.className = "ai-generated-image";
    const link = document.createElement("a"); link.href = result.image; link.download = "mohammad-studio-image.png"; link.textContent = "باز کردن / ذخیره تصویر"; link.className = "ai-manage-btn";
    aiImageOutput.append(img, link);
  } catch (error) { message(aiImageOutput, error.message, false); }
  finally { aiImageButton.disabled = false; aiImageButton.textContent = "ساخت تصویر رایگان"; }
});
$("#aiInput")?.addEventListener("keydown",event=>{if(event.key==="Enter"&&!event.shiftKey){event.preventDefault();$("#aiChatForm").requestSubmit();}});
$$("[data-ai-prompt]").forEach(button=>button.addEventListener("click",()=>{aiInput.value=button.dataset.aiPrompt;aiInput.focus();}));
$("#aiNewChat")?.addEventListener("click",()=>{if(aiBusy)return;activeConversationId=null;aiMessages.length=0;aiMessagesBox.replaceChildren();aiWelcome.hidden=false;aiConversationSelect.value="";aiNotice.textContent="گفتگوی جدید شروع شد.";aiInput.value="";aiInput.focus();});
$("#aiRenameChat")?.addEventListener("click",()=>{const conversation=activeAiConversation();if(!conversation){message(aiNotice,"ابتدا یک گفتگوی ذخیره‌شده را انتخاب کن.",false);return;}const title=window.prompt("نام جدید گفتگو را وارد کن:",conversation.title||"گفتگوی جدید");if(title&&title.trim()){conversation.title=title.trim().slice(0,60);conversation.updatedAt=new Date().toISOString();saveAiHistory(conversation);renderAiConversationList();}});
$("#aiDeleteChat")?.addEventListener("click",async()=>{const conversation=activeAiConversation();if(!conversation){message(aiNotice,"ابتدا گفتگویی را برای حذف انتخاب کن.",false);return;}if(!window.confirm("این گفتگو و تاریخچه آن حذف شود؟"))return;try{await api("/api/ai/conversations/"+encodeURIComponent(conversation.id),{method:"DELETE"});aiConversations=aiConversations.filter(item=>item.id!==activeConversationId);activeConversationId=null;aiMessages.length=0;aiMessagesBox.replaceChildren();aiWelcome.hidden=false;aiNotice.textContent="گفتگو حذف شد.";renderAiConversationList();}catch(error){message(aiNotice,error.message,false);}});
loadAiModels();
(async () => {
  try {
    const history = await api("/api/ai/conversations");
    aiConversations = Array.isArray(history.conversations) ? history.conversations : [];
    // Migrate conversations saved by the previous browser-only version once.
    if (!aiConversations.length) {
      let legacy = [];
      try {
        const stored = JSON.parse(localStorage.getItem(AI_HISTORY_KEY) || "[]");
        if (Array.isArray(stored)) legacy = stored.filter(x => x && typeof x.id === "string" && Array.isArray(x.messages));
      } catch (_) {}
      for (const old of legacy.slice(0, 30)) {
        const migrated = {
          id: old.id,
          title: String(old.title || "گفتگوی قبلی").slice(0, 60),
          model: String(old.model || "openrouter/free"),
          messages: old.messages.filter(m => m && ["user", "assistant"].includes(m.role) && typeof m.content === "string").slice(-40),
          updatedAt: new Date(Number(old.updatedAt) || Date.now()).toISOString()
        };
        if (migrated.model !== "openrouter/free" && !migrated.model.endsWith(":free")) migrated.model = "openrouter/free";
        aiConversations.push(migrated);
        await saveAiHistory(migrated);
      }
      if (legacy.length) {
        try { localStorage.removeItem(AI_HISTORY_KEY); } catch (_) {}
      }
    }
    aiConversations.sort((a,b) => Date.parse(b.updatedAt || 0) - Date.parse(a.updatedAt || 0));
    renderAiConversationList();
    if (aiConversations.length) restoreAiConversation(aiConversations[0].id);
  } catch (error) {
    message(aiNotice, "دریافت تاریخچه گفتگوها از سرور ممکن نشد: " + error.message, false);
  }
})();
$("#shortenUrl")?.addEventListener("click",async()=>{const out=$("#shortUrlOutput");try{const d=await api("/api/shorten",{method:"POST",body:JSON.stringify({url:$("#longUrl").value.trim()})});out.textContent=d.url}catch(e){message(out,e.message,false)}});
$("#toUpper")?.addEventListener("click",()=>$("#convertOutput").textContent=$("#convertInput").value.toUpperCase());
$("#toLower")?.addEventListener("click",()=>$("#convertOutput").textContent=$("#convertInput").value.toLowerCase());
$("#contactForm")?.addEventListener("submit",async e=>{e.preventDefault();const form=new FormData(e.currentTarget);try{const d=await api("/api/contact",{method:"POST",body:JSON.stringify(Object.fromEntries(form))});message($("#contactResult"),d.message);e.currentTarget.reset()}catch(err){message($("#contactResult"),err.message,false)}});
async function loadIdeas(){const box=$("#ideasList");try{const rows=await api("/api/suggestions");box.replaceChildren();rows.forEach(x=>{const item=document.createElement("div");item.className="glass-panel idea-item";const content=document.createElement("div");const h=document.createElement("h4");h.textContent=x.title;const p=document.createElement("p");p.textContent=x.description||"";content.append(h,p);const b=document.createElement("button");b.className="vote-btn";b.textContent="♡ "+Number(x.votes).toLocaleString("fa-IR");b.addEventListener("click",async()=>{try{await api("/api/suggestions/"+x.id+"/vote",{method:"POST",body:"{}"});loadIdeas()}catch(e){b.textContent=e.message}});item.append(content,b);box.append(item)});if(!rows.length)box.textContent="هنوز پیشنهادی ثبت نشده است."}catch{box.textContent="دریافت پیشنهادها ممکن نشد."}}
$("#ideaForm")?.addEventListener("submit",async e=>{e.preventDefault();const f=new FormData(e.currentTarget);try{const d=await api("/api/suggestions",{method:"POST",body:JSON.stringify(Object.fromEntries(f))});message($("#ideaResult"),d.message);e.currentTarget.reset();loadIdeas()}catch(err){message($("#ideaResult"),err.message,false)}});
let target=Math.floor(Math.random()*20)+1,attempts=0;
$("#guessButton")?.addEventListener("click",()=>{const n=Number($("#guessInput").value),out=$("#guessResult");if(n<1||n>20||!Number.isInteger(n)){message(out,"عدد بین ۱ تا ۲۰ وارد کن.",false);return}attempts++;message(out,n===target?"آفرین! درست حدس زدی؛ تعداد تلاش: "+attempts:n<target?"عدد بزرگ‌تری انتخاب کن.":"عدد کوچک‌تری انتخاب کن.");if(n===target)$("#guessButton").disabled=true});
$("#resetGuess")?.addEventListener("click",()=>{target=Math.floor(Math.random()*20)+1;attempts=0;$("#guessInput").value="";$("#guessButton").disabled=false;$("#guessResult").textContent="بازی جدید شروع شد."});
$$("[data-rps]").forEach(b=>b.addEventListener("click",()=>{const opts=["سنگ","کاغذ","قیچی"],computer=opts[Math.floor(Math.random()*3)],you=b.dataset.rps;const result=you===computer?"مساوی شد!":(you==="سنگ"&&computer==="قیچی")||(you==="کاغذ"&&computer==="سنگ")||(you==="قیچی"&&computer==="کاغذ")?"تو بردی!":"این بار کامپیوتر برد.";$("#rpsResult").textContent="تو: "+you+" | کامپیوتر: "+computer+" — "+result}));
const saved=JSON.parse(localStorage.getItem("studioPrefs")||"{}");function applyPrefs(p){document.body.classList.toggle("theme-light",p.theme==="light");document.body.classList.toggle("accent-purple",p.accent==="purple");document.body.classList.toggle("accent-cyan",p.accent==="cyan");$("#themeSelect").value=p.theme||"dark";$("#accentSelect").value=p.accent||"blue"}applyPrefs(saved);
$("#saveSettings")?.addEventListener("click",()=>{const p={theme:$("#themeSelect").value,accent:$("#accentSelect").value};localStorage.setItem("studioPrefs",JSON.stringify(p));applyPrefs(p);message($("#settingsResult"),"تنظیمات در همین مرورگر ذخیره شد.")});
loadSite();loadPortfolio();loadStats();loadStatus();loadIdeas();
});