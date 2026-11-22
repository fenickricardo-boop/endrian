(() => {
  const $ = (s) => document.querySelector(s);
  const els = {
    history: $('#history'), special: $('#specialPanel'), input: $('#messageInput'), send: $('#sendButton'),
    desktopSummary: $('#desktopSummary'), mobileSummary: $('#mobileSummary'),
    servicesDrawer: $('#servicesDrawer'), drawer: $('#priceDrawer'), contactDrawer: $('#contactDrawer'), backdrop: $('#drawerBackdrop'),
    mobileNav: $('#mobileNav'), summaryToggle: $('#summaryToggle'),
    composer: $('#composerZone'),
    conversationScroll: $('#conversationScroll')
  };
  let cfg = null, session = null, busy = false;
  let billingCountries=[], phoneCountries=[], editingContact=false;
  let followLatest=true;
  const escapeHtml = (s='') => String(s).replace(/[&<>'"]/g, c => ({'&':'&amp;','<':'&lt;','>':'&gt;',"'":'&#39;','"':'&quot;'}[c]));

  async function api(path, options={}) {
    const opts = {credentials:'same-origin', ...options};
    opts.headers = {'Content-Type':'application/json','X-ENDRIAN-QA':'1',...(options.headers||{})};
    const res = await fetch(path, opts); let body={}; try{body=await res.json()}catch(_){ }
    if(!res.ok) { const e=new Error(typeof body.message==='string'?body.message:`HTTP ${res.status}`); e.body=body; throw e; }
    return body;
  }
  function flow(){ return session?.full_flow || {state:'S0'}; }
  function pickerDisplay(item){return item?.calling_code?`${item.code} ${item.calling_code}`:item?.name||''}
  function pickerControlMarkup(id,placeholder,items,selected=null,required=false){const value=pickerDisplay(selected);return `<div class="country-picker ${items.some(x=>x.calling_code)?'phone-prefix-picker':'billing-country-picker'}" id="${id}" data-code="${escapeHtml(selected?.code||'')}" data-calling-code="${escapeHtml(selected?.calling_code||'')}"><input class="country-picker-input" value="${escapeHtml(value)}" placeholder="${escapeHtml(placeholder)}" autocomplete="off" ${required?'required':''} role="combobox" aria-autocomplete="list" aria-controls="${id}List" aria-expanded="false"><div class="country-picker-list" id="${id}List" role="listbox" hidden>${items.map(x=>x.calling_code?`<button type="button" role="option" aria-label="${escapeHtml(x.name)}, ${escapeHtml(x.code)} ${escapeHtml(x.calling_code)}" data-code="${escapeHtml(x.code)}" data-name="${escapeHtml(x.name)}" data-calling-code="${escapeHtml(x.calling_code)}"><span>${escapeHtml(x.code)}</span><small>${escapeHtml(x.calling_code)}</small></button>`:`<button type="button" role="option" data-code="${escapeHtml(x.code)}" data-name="${escapeHtml(x.name)}" data-calling-code=""><span>${escapeHtml(x.name)}</span></button>`).join('')}</div></div>`}
  function pickerMarkup(id,label,placeholder,items,selected=null,required=false,errorId=''){const visibleLabel=String(label).replace(/\s*\*$/,'');return `<label class="field-block"><span class="field-label">${escapeHtml(visibleLabel)}${required?' <span aria-hidden="true">*</span>':''}</span>${pickerControlMarkup(id,placeholder,items,selected,required)}${errorId?`<small class="field-error" id="${errorId}" role="alert"></small>`:''}</label>`}
  function phoneGroupMarkup(prefixId,numberId,selected=null,number=''){return `<div class="phone-field field-block"><span class="field-label">Teléfono (opcional)</span><div class="phone-controls">${pickerControlMarkup(prefixId,'Prefijo',phoneCountries,selected)}<label class="phone-number-label"><span class="sr-only">Número de teléfono</span><input id="${numberId}" value="${escapeHtml(number)}" placeholder="Número de teléfono" inputmode="tel" autocomplete="tel-national"></label></div><small class="field-error phone-error" id="${numberId}Error" role="alert"></small></div>`}
  function normalizedSearch(value){return String(value||'').normalize('NFD').replace(/[\u0300-\u036f]/g,'').toLocaleLowerCase('es').trim()}
  function setupPicker(id,items){const root=$('#'+id);if(!root)return;const input=root.querySelector('input'),list=root.querySelector('.country-picker-list'),buttons=()=>[...list.querySelectorAll('button:not([hidden])')];const show=()=>{list.hidden=false;input.setAttribute('aria-expanded','true')};const hide=()=>{list.hidden=true;input.setAttribute('aria-expanded','false')};const choose=(b)=>{const item=items.find(x=>x.code===b.dataset.code);input.value=pickerDisplay(item);root.dataset.code=b.dataset.code;root.dataset.callingCode=b.dataset.callingCode||'';hide();input.focus()};const filter=()=>{const q=normalizedSearch(input.value);root.dataset.code='';root.dataset.callingCode='';list.querySelectorAll('button').forEach(b=>b.hidden=Boolean(q)&&!normalizedSearch(`${b.dataset.name} ${b.dataset.code} ${b.dataset.callingCode}`).includes(q));show()};input.addEventListener('focus',show);input.addEventListener('input',filter);input.addEventListener('keydown',e=>{if(e.key==='Escape'){hide();return}if(e.key==='ArrowDown'){e.preventDefault();show();buttons()[0]?.focus();return}if(e.key==='Enter'&&!list.hidden){const first=buttons()[0];if(first){e.preventDefault();choose(first)}}});input.addEventListener('blur',()=>setTimeout(hide,150));list.addEventListener('keydown',e=>{const visible=buttons(),index=visible.indexOf(document.activeElement);if(e.key==='ArrowDown'){e.preventDefault();visible[(index+1)%visible.length]?.focus()}if(e.key==='ArrowUp'){e.preventDefault();(index<=0?input:visible[index-1])?.focus()}if(e.key==='Escape'){e.preventDefault();hide();input.focus()}if(e.key==='Enter'&&document.activeElement?.matches('button')){e.preventDefault();choose(document.activeElement)}});list.querySelectorAll('button').forEach(b=>b.onclick=()=>choose(b))}
  function pickerSelection(id,items){const root=$('#'+id);if(!root)return null;const item=items.find(x=>x.code===root.dataset.code);return item&&root.querySelector('input').value.trim()===pickerDisplay(item)?item:null}
  function normalizedPhoneNumber(value){return String(value||'').replace(/[\s().-]/g,'')}
  function validatedPhone(prefixId,numberId){const country=pickerSelection(prefixId,phoneCountries),raw=$('#'+numberId)?.value.trim()||'',number=normalizedPhoneNumber(raw),error=$('#'+numberId+'Error');if(Boolean(country)!==Boolean(number)){if(error)error.textContent='Completa el prefijo y el número, o borra ambos para omitir el teléfono.';return {valid:false}}if(!country&&!number){if(error)error.textContent='';return {valid:true,country:null,number:''}}if(!/^\d{4,15}$/.test(number)){if(error)error.textContent='Ingresa un número válido o borra ambos campos para omitir el teléfono.';return {valid:false}}if(error)error.textContent='';return {valid:true,country,number}}
  function phoneLabel(phone){return phone?.international_number||''}
  function nearChatBottom(){const el=els.conversationScroll;return el.scrollHeight-el.scrollTop-el.clientHeight<96}
  function revealLatest(force=false){requestAnimationFrame(()=>requestAnimationFrame(()=>{if(!force&&!followLatest)return;const target=els.special.lastElementChild||els.history.lastElementChild;if(target)target.scrollIntoView({block:'nearest',behavior:'smooth'});else els.conversationScroll.scrollTop=els.conversationScroll.scrollHeight}))}
  function appendMessage(role,text){if(!text)return;const row=document.createElement('div');row.className=`message ${role}`;if(role==='assistant'){row.innerHTML=`<div class="agent-mark" aria-hidden="true">✦</div><div><div class="bubble"><p>${escapeHtml(text)}</p></div><div class="message-meta">${new Date().toLocaleTimeString([], {hour:'2-digit',minute:'2-digit'})}</div></div>`}else{row.innerHTML=`<div><div class="bubble"><p>${escapeHtml(text)}</p></div><div class="message-meta">${new Date().toLocaleTimeString([], {hour:'2-digit',minute:'2-digit'})}</div></div>`}els.history.appendChild(row)}
  function appendRegistrationForm(){
    const row=document.createElement('div');
    row.className='message assistant registration-form-row';
    row.innerHTML=`<div class="agent-mark" aria-hidden="true">✦</div><div class="bubble registration-form">
      <p class="flow-note">Utiliza únicamente datos ficticios durante esta prueba. No se enviarán correos, SMS ni verificaciones externas.</p>
      <div class="form-grid" style="grid-template-columns:1fr">
        <label class="field-block">Nombre completo<input id="regName" placeholder="Escribe tu nombre completo" autocomplete="name"></label>
        <label class="field-block">Correo<input id="regEmail" type="email" placeholder="Escribe tu correo" autocomplete="email"></label>
      </div>
      <small class="field-error" id="regFormError" role="alert"></small>
      <p class="flow-note">Al continuar, aceptas el tratamiento de tus datos y las comunicaciones operativas de esta prueba.</p>
      <div class="card-actions"><button type="button" id="regSubmit" class="primary-cta">Continuar <span>→</span></button></div>
    </div>`;
    els.history.appendChild(row);
    const submit=row.querySelector('#regSubmit'), nameInput=row.querySelector('#regName'), emailInput=row.querySelector('#regEmail'), errorEl=row.querySelector('#regFormError');
    submit.onclick=async()=>{
      const name=nameInput.value.trim(), email=emailInput.value.trim();
      errorEl.textContent='';
      if(!name||!email){errorEl.textContent='Completa el nombre y el correo para continuar.';return}
      submit.disabled=true;
      try{
        const out=await api('/api/chat/register',{method:'POST',body:JSON.stringify({name,email,data_processing:true,operational_comms:true})});
        row.remove();
        appendMessage('user',`${name} · ${email}`);
        appendMessage('assistant',out.message||'');
        if(out.summary)session=out.summary;
        renderAll();
        revealLatest(true);
      }catch(e){
        submit.disabled=false;
        errorEl.textContent=e.body?.message||e.message||'No fue posible completar el registro.';
      }
    };
    revealLatest(true);
  }
  let quickReplySeq=0;
  function appendQuickReply(label,value,secondaryLabel){
    const uid=`qr${++quickReplySeq}`;
    const row=document.createElement('div');
    row.className='message assistant quick-reply-row';
    row.innerHTML=`<div class="agent-mark" aria-hidden="true">✦</div><div class="bubble quick-reply"><div class="card-actions">${actionButton(uid+'p',label)}${secondaryLabel?actionButton(uid+'s',secondaryLabel,true):''}</div></div>`;
    els.history.appendChild(row);
    row.querySelector('#'+uid+'p').onclick=()=>{row.remove();send(value)};
    if(secondaryLabel)row.querySelector('#'+uid+'s').onclick=()=>{row.remove();els.input.focus()};
    revealLatest(true);
  }
  function loading(on){busy=on;els.send.disabled=on;els.input.disabled=on;const old=$('#typingRow');if(old)old.remove();if(on){const row=document.createElement('div');row.id='typingRow';row.className='message assistant';row.setAttribute('role','status');row.setAttribute('aria-label','ENDRIAN está preparando la respuesta');row.innerHTML='<div class="agent-mark">✦</div><div class="bubble"><span class="loading-dot"><span></span><span></span><span></span></span></div>';els.history.appendChild(row);$('#conversationScroll').scrollTop=$('#conversationScroll').scrollHeight}}

  const journeySteps=[
    {title:'Conversación',description:'Cuéntanos qué necesitas.',states:['S0','S1']},
    {title:'Definición de tu solicitud',description:'Aclaramos contigo el alcance y lo que recibirás.',states:['S3','S4','SH']},
    {title:'Revisión y pago',description:'Revisas tu propuesta y confirmas los datos antes de pagar.',states:['S2','S5','S6']},
    {title:'Pedido recibido',description:'Confirmamos tu pago y registramos tu pedido.',states:['S7','S8']}
  ];
  // The free-text conversational path (real/gemini model) advances through its
  // own internal state machine (session.state) and never moves full_flow past
  // S1, so the journey panel would otherwise look frozen on "Conversación" for
  // the whole exchange even as registration/orientation/payment progress.
  // Map that state onto the same 4 stages as a fallback when full_flow hasn't
  // moved yet.
  const coreStateJourney={
    'CONVERSACIÓN INICIAL':0,'COMPRENSIÓN PRELIMINAR':0,'REGISTRO PENDIENTE':0,
    'DIMENSIONAMIENTO INCOMPLETO':1,'ORIENTACIÓN EN REVISIÓN':1,'REVISIÓN HUMANA REQUERIDA':1,
    'PRECIO PENDIENTE':2,'PROPUESTA DISPONIBLE':2,'PAGO DISPONIBLE':2,'PAGO PENDIENTE':2,
    'ORDEN CONFIRMADA':3,'MATRIZ QA COMPLETA / APTA PARA EVALUACIÓN':3,'MATRIZ EN REVISIÓN':3,
    'REEMBOLSO CONFIRMADO':3,'REEMBOLSO PENDIENTE':3
  };
  function summaryMarkup(s){
    const state=s?.full_flow?.state||'S0';
    let currentIndex=Math.max(0,journeySteps.findIndex(step=>step.states.includes(state)));
    let journeyCompleted=['S7','S8'].includes(state);
    if(['S0','S1'].includes(state) && coreStateJourney[s?.state]!==undefined){
      currentIndex=coreStateJourney[s.state];
      journeyCompleted=currentIndex>=journeySteps.length-1;
    }
    return `<div class="journey-heading" data-panel-mode="journey"><h2>Tu recorrido</h2></div><div class="summary-list">${journeySteps.map((step,i)=>{const status=journeyCompleted||i<currentIndex?'done':i===currentIndex?'current':'pending';const statusLabel=status==='done'?'Completado':status==='current'?'Etapa actual':'Pendiente';return `<div class="summary-step ${status}"${status==='current'?' aria-current="step"':''}><span class="step-dot">${status==='done'?'✓':''}</span><strong>${escapeHtml(step.title)}</strong><p>${escapeHtml(step.description)}</p><small>${statusLabel}</small></div>`}).join('')}</div>${state==='SH'?`<div class="journey-notice">Necesitamos revisar un punto antes de continuar.</div>`:''}`;
  }
  function renderSummary(s){session=s||session||{};const html=summaryMarkup(session);els.desktopSummary.innerHTML=html;els.mobileSummary.innerHTML=html}

  function currentQuote(f){return (f.quotations||[]).find(q=>q.quotation_ref===f.current_quotation_ref)||(f.quotations||[]).at(-1)||{}}
  function actionButton(id,label,secondary=false){return `<button type="button" id="${id}" class="${secondary?'secondary-cta':'primary-cta'}">${escapeHtml(label)} <span>→</span></button>`}
  function bind(id,fn){const el=$('#'+id);if(el)el.onclick=fn}
  function errorBox(message){return `<div class="flow-error" role="alert">${escapeHtml(message)}</div>`}
  function setFieldError(id,message=''){const el=$('#'+id);if(el)el.textContent=message}
  function clearContactErrors(ids){['nameError','emailError','countryError','phoneError'].forEach(key=>setFieldError(ids[key],''));const box=$('#flowError');if(box)box.innerHTML=''}
  function validEmailFormat(email){return /^[^\s@]+@[^\s@]+\.[^\s@]{2,}$/.test(email)}
  function validateContact(ids){clearContactErrors(ids);const name=$('#'+ids.name)?.value.trim()||'',email=$('#'+ids.email)?.value.trim()||'',country=pickerSelection(ids.country,billingCountries),phone=validatedPhone(ids.phoneCountry,ids.phoneNumber);let valid=true;if(name.length<2||!/^[A-Za-zÁÉÍÓÚÜÑáéíóúüñ .'-]+$/.test(name)){setFieldError(ids.nameError,'Revisa el nombre completo ingresado.');valid=false}if(!validEmailFormat(email)){setFieldError(ids.emailError,'Revisa el formato del correo.');valid=false}if(!country){setFieldError(ids.countryError,'Selecciona tu país de facturación.');valid=false}if(!phone.valid)valid=false;return {valid,name,email,country,phone}}
  function detailFields(detail){return Array.isArray(detail)?detail.map(item=>{const loc=Array.isArray(item?.loc)?item.loc:[];return loc[loc.length-1]}).filter(Boolean):[]}
  function contactErrorMessage(detail){if(typeof detail==='string')return detail;const fields=detailFields(detail);if(fields.some(x=>x==='email'))return 'Revisa el correo ingresado.';if(fields.some(x=>x==='name'))return 'Revisa el nombre completo ingresado.';if(fields.some(x=>String(x).startsWith('country_')))return 'Selecciona tu país de facturación.';if(fields.some(x=>String(x).startsWith('phone_')))return 'Revisa el teléfono ingresado o déjalo vacío.';return fields.length?'Revisa los campos indicados para continuar.':''}
  function applyContactApiError(body,ids){const event=body?.event||'';let message=typeof body?.message==='string'?body.message:contactErrorMessage(body?.detail);if(event==='SYNTHETIC_NAME_REQUIRED'){setFieldError(ids.nameError,'Revisa el nombre completo ingresado.');return}if(event==='EMAIL_FORMAT_INVALID'){setFieldError(ids.emailError,'Revisa el formato del correo.');return}if(event==='BILLING_COUNTRY_REQUIRED'){setFieldError(ids.countryError,'Selecciona tu país de facturación.');return}if(['PHONE_COUNTRY_INVALID','PHONE_NUMBER_INVALID'].includes(event)){setFieldError(ids.phoneError,message||'Revisa el teléfono ingresado o déjalo vacío.');return}const fields=detailFields(body?.detail);if(fields.some(x=>x==='email'))setFieldError(ids.emailError,message);else if(fields.some(x=>x==='name'))setFieldError(ids.nameError,message);else if(fields.some(x=>String(x).startsWith('country_')))setFieldError(ids.countryError,message);else if(fields.some(x=>String(x).startsWith('phone_')))setFieldError(ids.phoneError,message);else{const box=$('#flowError');if(box)box.innerHTML=errorBox(message||'Revisa los campos indicados para continuar.')}}
  async function runAction(path,payload={},options={}){const shouldFollow=nearChatBottom();try{const out=await api(path,{method:'POST',body:JSON.stringify(payload)});session=out.summary||session;renderAll();if(!options.silent&&out.message)appendMessage('assistant',out.message);revealLatest(shouldFollow);return out}catch(e){const body=e.body||{};if(options.preserveForm){options.onError?.(body);return null}if(body.summary){session=body.summary;renderAll()}const box=$('#flowError');if(box)box.innerHTML=errorBox(typeof body.message==='string'?body.message:contactErrorMessage(body.detail)||e.message);revealLatest(shouldFollow);return null}}

  function renderFlow(){
    const f=flow(), state=f.state||'S0'; let html='';
    if(state==='S0') html='';
    if(state==='S1'){
      html='';
    } else if(state==='S2'){
      const identity=f.qa_identity||{}, billing=identity.billing_country||{}, phone=identity.phone||{};
      const billingSelected=billing.country_code?billingCountries.find(x=>x.code===billing.country_code):null, phoneSelected=phone.country_code?phoneCountries.find(x=>x.code===phone.country_code):null;
      html=`<section class="flow-card"><h2>Datos del cliente</h2><p>Indícanos dónde enviarte la información de tu solicitud.</p><p class="flow-note">Utiliza únicamente datos ficticios durante esta prueba. No se enviarán correos, SMS ni verificaciones externas.</p><div class="form-grid contact-form-grid"><label class="field-block">Nombre completo<input id="contactName" value="${escapeHtml(identity.name||'')}" placeholder="Escribe tu nombre completo" autocomplete="name"><small class="field-error" id="contactNameError" role="alert"></small></label><label class="field-block">Correo<input id="contactEmail" type="email" value="${escapeHtml(identity.email||'')}" placeholder="Escribe tu correo" autocomplete="email"><small class="field-error" id="contactEmailError" role="alert"></small></label>${pickerMarkup('billingCountry','País de facturación*','Selecciona tu país',billingCountries,billingSelected,true,'billingCountryError')}${phoneGroupMarkup('phoneCountry','contactPhoneNumber',phoneSelected,phone.national_number||'')}</div><div id="flowError"></div><div class="card-actions">${actionButton('completeRegistration','Continuar')}</div></section>`;
    } else if(state==='S3'){
      html='';
    } else if(state==='S4'){
      const pc=f.product_conformity;
      html=pc&&!pc.accepted?`<section class="flow-card"><h2>Confirmación de la solución</h2><p>La preferencia inicial fue <strong>${escapeHtml(pc.previous_product||'')}</strong>, pero la solicitud definida corresponde a <strong>${escapeHtml(pc.proposed_product||'')}</strong>.</p><p>Confirma este cambio para continuar con el servicio validado.</p><div id="flowError"></div><div class="card-actions">${actionButton('proposalReturn','Volver a la conversación',true)}${actionButton('confirmProductChange','Confirmar cambio')}</div></section>`:`<section class="flow-card confirmation-actions"><p>¿Esto refleja bien lo que necesitas o quieres cambiar algo?</p><div id="flowError"></div><div class="card-actions">${actionButton('correctUnderstanding','Quiero corregir algo',true)}${actionButton('confirmUnderstanding','Sí, preparar mi resumen')}</div></section>`;
    } else if(state==='S5'){
      const p=currentQuote(f), c=f.client_output||{}, contracting=f.microstate==='S5.CONTRACT-DATA', expired=p.status==='EXPIRED'||Boolean(p.force_expired_qa), special=(f.solution_request_versions||[]).find(x=>x.solution_request_version_id===f.current_solution_request_version_id)?.route==='SPECIAL_REVIEW';
      const list=(items)=>`<ul>${(items||[]).map(x=>`<li>${escapeHtml(x)}</li>`).join('')}</ul>`;
      const unique=(items)=>[...new Map((items||[]).filter(Boolean).map(x=>[String(x).trim().toLocaleLowerCase('es'),String(x).trim()])).values()];
      const deliverables=unique(c.deliverables||[]);
      const specificConditions=[];
      if(c.information_input&&c.information_input!=='No registrado'){
        const inputSentence=String(c.information_input).split(/\.\s+(?:Esta prueba|No se)/i)[0].trim();
        if(inputSentence)specificConditions.push(inputSentence.replace(/\.$/,'' )+'.');
      }
      const draftSource=[...(c.commitments||[]),...(c.limits||[]),c.scope||''].join(' ').toLocaleLowerCase('es');
      if(draftSource.includes('borrador'))specificConditions.push('La solución prepara borradores; tu equipo los revisa y realiza el envío.');
      const requestDetails=`<div class="request-summary-group"><div class="flow-kv"><strong>Servicio recomendado</strong><span>${escapeHtml(c.service||c.agent||'')}</span></div><div class="flow-kv"><strong>Qué incluye</strong>${c.request_description?`<span>${escapeHtml(c.request_description)}</span>`:''}${deliverables.length?list(deliverables):''}${unique(specificConditions).length?`<small>${escapeHtml(unique(specificConditions).join(' '))}</small>`:''}</div><div class="flow-kv"><strong>Plataforma de uso</strong><span>${escapeHtml(c.environment_label||'')}</span>${c.environment_notice?`<small>${escapeHtml(c.environment_notice)}</small>`:''}</div></div>`;
      const offerDetails=p.amount_label?`<div class="flow-kv"><strong>Precio</strong><span>${escapeHtml(p.amount_label)} · Precio de prueba, sin cobro real</span></div><div class="flow-kv"><strong>Plazo estimado de entrega</strong><span>${escapeHtml(c.delivery_window||'2 a 5 días hábiles desde la confirmación del pago')}</span>${c.delivery_notice?`<small>${escapeHtml(c.delivery_notice)}</small>`:''}</div>`:'<p>La cotización se preparará después de la revisión.</p>';
      const identity=f.qa_identity||{}, billing=identity.billing_country||{}, phone=identity.phone||{};
      const contactReview=`<div class="flow-grid"><div class="flow-kv"><strong>Nombre completo</strong><span>${escapeHtml(identity.name||'')}</span></div><div class="flow-kv"><strong>Correo</strong><span>${escapeHtml(identity.email||'')}</span></div>${phone.international_number?`<div class="flow-kv"><strong>Teléfono</strong><span>${escapeHtml(phone.international_number)}</span></div>`:''}<div class="flow-kv"><strong>País de facturación</strong><span>${escapeHtml(billing.country_name||'')}</span></div></div>`;
      const billingSelected=billing.country_code?billingCountries.find(x=>x.code===billing.country_code):null, phoneSelected=phone.country_code?phoneCountries.find(x=>x.code===phone.country_code):null;
      const contactEdit=`<p class="flow-note">Utiliza únicamente datos ficticios durante esta prueba. No se enviarán correos, SMS ni verificaciones externas.</p><div class="form-grid contact-form-grid"><label class="field-block">Nombre completo<input id="prepaymentName" value="${escapeHtml(identity.name||'')}" placeholder="Escribe tu nombre completo"><small class="field-error" id="prepaymentNameError" role="alert"></small></label><label class="field-block">Correo<input id="prepaymentEmail" type="email" value="${escapeHtml(identity.email||'')}" placeholder="Escribe tu correo"><small class="field-error" id="prepaymentEmailError" role="alert"></small></label>${pickerMarkup('prepaymentCountry','País de facturación*','Selecciona tu país',billingCountries,billingSelected,true,'prepaymentCountryError')}${phoneGroupMarkup('prepaymentPhoneCountry','prepaymentPhoneNumber',phoneSelected,phone.national_number||'')}</div>`;
      html=contracting?`<section class="flow-card"><h2>Antes de pagar</h2><p>Revisa la solución, tus datos y las condiciones aplicables antes de continuar.</p><div class="flow-grid"><div class="flow-kv"><strong>Solución</strong><span>${escapeHtml(c.request_title||c.agent||'')}</span></div><div class="flow-kv"><strong>Servicio recomendado</strong><span>${escapeHtml(c.service||c.agent||'')}</span></div><div class="flow-kv"><strong>Importe</strong><span>${escapeHtml(p.amount_label||'')} · Precio de prueba, sin cobro real</span></div><div class="flow-kv"><strong>Plazo estimado de entrega</strong><span>${escapeHtml(c.delivery_window||'')}</span></div><div class="flow-kv"><strong>Plataforma de uso</strong><span>${escapeHtml(c.environment_label||'')}</span></div></div><h3>Datos del cliente</h3>${editingContact?contactEdit:contactReview}<p class="flow-note">Usaremos este correo para gestionar tu solicitud y enviarte las confirmaciones relacionadas con tu contratación.</p><p class="document-note">Documentos de prueba, no válidos para contratación real.</p><details><summary>Resumen de tu solicitud</summary><h3>${escapeHtml(c.request_title||'')}</h3>${requestDetails}</details><details><summary>Términos y Condiciones de ENDRIAN</summary><p>Documento QA-TERMS-0.1. No constituye términos legales definitivos.</p></details><details><summary>Política de Privacidad</summary><p>Aviso QA-PRIVACY-0.1. Utiliza únicamente datos ficticios; no existe envío a servicios externos.</p></details><label class="check-row"><input type="checkbox" id="contractTermsAccepted"> Acepto los Términos y Condiciones de ENDRIAN y confirmo mi pedido según el Resumen de tu solicitud.</label><label class="check-row"><input type="checkbox" id="privacyAccepted"> Autorizo a ENDRIAN a tratar mis datos personales para gestionar mi pedido y prestar el servicio contratado, conforme a la Política de Privacidad.</label><p>Continuarás a una simulación de pago. No se realizarán cobros ni se solicitarán datos financieros.</p><div id="flowError"></div><div class="card-actions">${actionButton('proposalReturn','Volver a la conversación',true)}${actionButton(editingContact?'saveContact':'modifyPrepayment',editingContact?'Guardar datos':'Modificar datos',true)}${actionButton('goToPayment','Continuar al pago')}</div></section>`:`<section class="flow-card"><h2>Resumen de tu solicitud</h2><h3>${escapeHtml(c.request_title||'')}</h3>${requestDetails}${offerDetails}${expired?'<p class="flow-error">La cotización de prueba venció. Actualízala antes de continuar.</p>':''}<div id="flowError"></div><div class="card-actions">${actionButton('proposalReturn','Volver a la conversación',true)}${actionButton(expired?'refreshOffer':special?'sendForReview':'proposalAccept',expired?'Actualizar cotización de prueba':special?'Enviar mi solicitud para revisión':'Continuar con mi solicitud')}</div></section>`;
    } else if(state==='S6'){
      const p=f.payment_qa||{}, gate=session.payment_gate||{};
      const cond=gate.conditions||{};
      html=p.status==='RECHAZADO'?`<section class="flow-card"><h2>El pago no fue confirmado</h2><p>Tu solicitud se conserva. Puedes revisar los datos y volver a intentarlo mientras la oferta siga vigente.</p><div class="card-actions">${actionButton('recoverPayment','Revisar antes de pagar')}</div></section>`:session.ui_state==='payment_verifying'?`<section class="flow-card"><h2>Estamos verificando tu pago</h2><p>Conservamos tu solicitud. No necesitas intentar pagar nuevamente.</p><p class="flow-note">Esta verificación es simulada y no valida un pago real.</p></section>`:`<section class="flow-card"><h2>Simulación de pago</h2><p>Este entorno no procesa pagos reales ni solicita datos financieros.</p><div class="flow-kv"><strong>Servicio</strong><span>${escapeHtml(p.service_label||'')}</span></div><div class="flow-kv"><strong>Importe</strong><span>${escapeHtml(p.currency||'')} ${escapeHtml(p.amount||'')}</span></div><div class="card-actions">${actionButton('returnFromCheckout','Volver al Laboratorio')}</div></section>`;
    } else if(state==='S7'){
      const o=f.order_qa||{};
      const snapshot=o.construction_request_snapshot||{}, solutionTitle=snapshot.solution_title;
      const solutionTitleMarkup=solutionTitle?`<span>${escapeHtml(solutionTitle)}</span>`:'<span class="flow-error" role="alert">El título del agente no está disponible en el snapshot de esta orden.</span>';
      html=`<section class="flow-card"><h2>Pago confirmado</h2><p>Tu pedido fue recibido correctamente.</p><div class="flow-grid"><div class="flow-kv"><strong>Número de orden</strong><code>${escapeHtml(o.order_id||'')}</code></div><div class="flow-kv"><strong>Solución</strong>${solutionTitleMarkup}</div><div class="flow-kv"><strong>Servicio contratado</strong><span>${escapeHtml(snapshot.service_label||snapshot.agent||'')}</span></div><div class="flow-kv"><strong>Estado</strong><span>Pedido recibido</span></div><div class="flow-kv"><strong>Importe</strong><span>${escapeHtml(`${snapshot.currency||''} ${snapshot.amount||''}`.trim())} · Pago de prueba, sin cobro real</span></div><div class="flow-kv"><strong>Plataforma</strong><span>${escapeHtml(snapshot.platform_label||'')}</span></div><div class="flow-kv"><strong>Plazo acordado</strong><span>${escapeHtml(snapshot.delivery_window||'')}</span></div></div><div class="flow-kv"><strong>¿Qué ocurre ahora?</strong><span>ENDRIAN preparará, comprobará y entregará tu solución según el alcance y las condiciones confirmadas.</span></div><p class="flow-note">Esta simulación no inicia una construcción real ni habilita acceso a la solución.</p><div id="flowError"></div><div class="card-actions">${actionButton('finalizeConversation','Finalizar conversación')}</div></section>`;
    } else if(state==='S8'){
      const o=f.order_qa||{}, p=f.payment_qa||{};
      html=`<section class="flow-card"><h2>Tu solicitud / seguimiento</h2><div class="flow-kv"><strong>Referencia</strong><code>${escapeHtml(f.qa_identity?.qa_identity_ref||'')}</code></div><div class="flow-kv"><strong>Pago</strong><span>${escapeHtml(p.status||'')}</span></div><div class="flow-kv"><strong>Solicitud</strong><span>${escapeHtml(o.order_id||'Todavía no creada')}</span></div><p>Puedes volver al último estado guardado sin repetir el pago ni crear otra solicitud.</p><div id="flowError"></div><div class="card-actions">${actionButton('trackingReturn','Volver al estado anterior')}${actionButton('copyRecoveryRef','Copiar referencia',true)}</div></section>`;
    } else if(state==='SH'){
      const h=f.human_review||{};
      html=session.ui_state==='special_review_waiting'?`<section class="flow-card human-review-card"><h2>Solicitud enviada para revisión</h2><p>Recibimos tus datos y el resumen confirmado. Antes de preparar una cotización revisaremos las dependencias y responsables de este caso.</p><p>No existe un precio ni un pago habilitado mientras esta revisión esté pendiente.</p></section>`:`<section class="flow-card human-review-card"><h2>Necesitamos revisar un punto</h2><p>${escapeHtml(h.reason||'Existe una incertidumbre material que impide continuar responsablemente.')}</p><div id="flowError"></div><div class="card-actions">${actionButton('reviewToS3','Volver a la conversación')}${actionButton('reviewToS4','Revisar la definición',true)}</div></section>`;
    }
    els.special.innerHTML=html; bindFlowHandlers(state);
  }

  function bindFlowHandlers(state){
    if(state==='S1'){}
    if(state==='S2'){setupPicker('billingCountry',billingCountries);setupPicker('phoneCountry',phoneCountries);bind('completeRegistration',()=>{const ids={name:'contactName',email:'contactEmail',country:'billingCountry',phoneCountry:'phoneCountry',phoneNumber:'contactPhoneNumber',nameError:'contactNameError',emailError:'contactEmailError',countryError:'billingCountryError',phoneError:'contactPhoneNumberError'},data=validateContact(ids);if(!data.valid)return;runAction('/api/full-flow/registration',{name:data.name,email:data.email,country_code:data.country.code,country_name:data.country.name,phone_country_code:data.phone.number?(data.phone.country?.code||''):'',phone_country_name:data.phone.number?(data.phone.country?.name||''):'',phone_calling_code:data.phone.number?(data.phone.country?.calling_code||''):'',phone_national_number:data.phone.number,data_processing:false,operational_comms:false,marketing:false},{preserveForm:true,onError:body=>applyContactApiError(body,ids)})})}
    if(state==='S3'){}
    if(state==='S4'){bind('confirmProductChange',()=>runAction('/api/full-flow/product-change/confirm'));bind('proposalReturn',()=>runAction('/api/full-flow/orientation/action',{action:'request_correction'}));bind('confirmUnderstanding',()=>runAction('/api/full-flow/confirmation/action',{action:'confirm'}));bind('correctUnderstanding',()=>runAction('/api/full-flow/confirmation/action',{action:'correct'}))}
    if(state==='S5'){bind('proposalAccept',()=>runAction('/api/full-flow/proposal/action',{action:'continue'}));bind('refreshOffer',()=>runAction('/api/full-flow/proposal/action',{action:'revalidate'}));bind('sendForReview',()=>runAction('/api/full-flow/proposal/action',{action:'send_for_review'}));bind('proposalReturn',()=>runAction('/api/full-flow/proposal/action',{action:'return_to_chat'}));bind('modifyPrepayment',()=>{editingContact=true;renderAll()});if(editingContact){setupPicker('prepaymentCountry',billingCountries);setupPicker('prepaymentPhoneCountry',phoneCountries);bind('saveContact',async()=>{const ids={name:'prepaymentName',email:'prepaymentEmail',country:'prepaymentCountry',phoneCountry:'prepaymentPhoneCountry',phoneNumber:'prepaymentPhoneNumber',nameError:'prepaymentNameError',emailError:'prepaymentEmailError',countryError:'prepaymentCountryError',phoneError:'prepaymentPhoneNumberError'},data=validateContact(ids);if(!data.valid)return;const out=await runAction('/api/full-flow/contact/edit',{name:data.name,email:data.email,country_code:data.country.code,country_name:data.country.name,phone_country_code:data.phone.number?(data.phone.country?.code||''):'',phone_country_name:data.phone.number?(data.phone.country?.name||''):'',phone_calling_code:data.phone.number?(data.phone.country?.calling_code||''):'',phone_national_number:data.phone.number},{preserveForm:true,onError:body=>applyContactApiError(body,ids)});if(out){editingContact=false;renderAll()}})}bind('goToPayment',preparePayment)}
    if(state==='S6'){bind('returnFromCheckout',()=>runAction('/api/full-flow/payment/return'));bind('recoverPayment',()=>runAction('/api/full-flow/payment/recovery'))}
    if(state==='S7'){bind('finalizeConversation',finalizeConversation)}
    if(state==='S8'){bind('trackingReturn',()=>runAction('/api/full-flow/tracking/return'));bind('copyRecoveryRef',()=>navigator.clipboard?.writeText(flow().qa_identity?.qa_identity_ref||''))}
    if(state==='SH'){bind('reviewToS3',()=>runAction('/api/full-flow/human-review/resolve',{target:'S3'}));bind('reviewToS4',()=>runAction('/api/full-flow/human-review/resolve',{target:'S4'}))}
  }

  function renderAll(){renderSummary(session);renderFlow();const state=flow().state;const correctionChat=state==='S3'&&session.ui_state==='scope_correction_chat';const confirmationChat=state==='S4'&&session.ui_state==='needs_confirmation_chat';const chatAllowed=['S0','S1','SH'].includes(state)||correctionChat||confirmationChat;els.composer.classList.toggle('composer--compact',!chatAllowed);els.input.disabled=!chatAllowed;els.send.disabled=!chatAllowed;els.input.placeholder=correctionChat?'Escribe qué quieres agregar o cambiar…':confirmationChat?'Escribe tu respuesta…':chatAllowed?cfg.copy.placeholder:state==='S7'?'La conversación está cerrada para este pedido. Finalízala cuando termines de revisar.':'El cuadro de escritura está inactivo mientras completas este paso.'}

  let paymentPreparing=false;
  async function preparePayment(){if(paymentPreparing||editingContact)return;paymentPreparing=true;const button=$('#goToPayment');if(button)button.disabled=true;try{const contracted=await runAction('/api/full-flow/contracting',{contract_terms_accepted:Boolean($('#contractTermsAccepted')?.checked),privacy_authorization_accepted:Boolean($('#privacyAccepted')?.checked)},{silent:true});if(contracted)await runAction('/api/full-flow/payment/start',{}, {silent:true})}finally{paymentPreparing=false;if(button?.isConnected)button.disabled=false}}

  async function loadSession(){session=await api('/api/session');els.history.innerHTML='';(session.history||[]).forEach(m=>appendMessage(m.role,m.text));renderAll();followLatest=true;revealLatest(true)}
  async function finalizeConversation(){const out=await api('/api/full-flow/conversation/finalize',{method:'POST',body:'{}'});session=out.summary;editingContact=false;els.history.innerHTML='';renderAll();history.replaceState(null,'',location.pathname)}
  async function send(text){const value=(text??els.input.value).trim();if(!value||busy)return;const shouldFollow=nearChatBottom();appendMessage('user',value);els.input.value='';loading(true);try{const out=await api('/api/chat',{method:'POST',body:JSON.stringify({message:value})});loading(false);appendMessage('assistant',out.message||'');if(out.summary)session=out.summary;renderAll();const quickReplyByEvent={ORIENTATION_READY:['Confirmar, esto es lo que necesito','confirmo la orientación','Quiero ajustar algo'],PROPOSAL_READY_QA:['Acepto la propuesta','acepto la propuesta'],PAYMENT_AVAILABLE_QA:['Iniciar el pago','inicia el pago'],PAYMENT_STATUS_QA:['Confirmar que ya pagué','pago confirmado']};if(out.event==='REGISTRATION_REQUIRED')appendRegistrationForm();else if(quickReplyByEvent[out.event])appendQuickReply(...quickReplyByEvent[out.event]);revealLatest(shouldFollow)}catch(e){loading(false);appendMessage('assistant',e.body?.message||e.message||'No fue posible procesar el mensaje.');revealLatest(shouldFollow)}}

  let lastDrawerTrigger=null;
  const publicDrawers=()=>[els.servicesDrawer,els.drawer,els.contactDrawer];
  function drawerIsOpen(drawer){return drawer?.classList.contains('open')}
  function hideDrawer(drawer){if(!drawer)return;drawer.classList.remove('open');drawer.setAttribute('aria-hidden','true')}
  function syncBackdrop(){setTimeout(()=>{els.backdrop.hidden=!publicDrawers().some(drawerIsOpen)},260)}
  function closeDrawer(drawer,{restoreFocus=true}={}){hideDrawer(drawer);syncBackdrop();if(restoreFocus&&lastDrawerTrigger){const trigger=lastDrawerTrigger;lastDrawerTrigger=null;trigger.focus()}}
  function openDrawer(drawer,closeButton,trigger){publicDrawers().forEach(hideDrawer);lastDrawerTrigger=trigger||document.activeElement;els.backdrop.hidden=false;drawer.classList.add('open');drawer.setAttribute('aria-hidden','false');closeButton.focus()}
  let lastServiceCardTrigger=null;
  let servicesListScrollTop=0;
  function resetServicesPanel(){
    const list=$('#servicesListView'),detail=$('#serviceDetailView'),content=$('#serviceDetailContent');
    if(list)list.hidden=false;
    if(detail)detail.hidden=true;
    if(content)content.innerHTML='';
    lastServiceCardTrigger=null;
    servicesListScrollTop=0;
  }
  function openServiceDetail(id,trigger){
    const template=document.querySelector(`template[data-service-detail="${id}"]`);
    if(!template)return;
    lastServiceCardTrigger=trigger||null;
    servicesListScrollTop=$('#servicesListView')?.scrollTop||0;
    $('#serviceDetailContent').innerHTML=template.innerHTML;
    $('#servicesListView').hidden=true;
    $('#serviceDetailView').hidden=false;
    $('#serviceDetailView').scrollTop=0;
    $('#serviceBack').focus();
  }
  function backToServices(){
    $('#serviceDetailView').hidden=true;
    $('#servicesListView').hidden=false;
    $('#serviceDetailContent').innerHTML='';
    const target=lastServiceCardTrigger;
    lastServiceCardTrigger=null;
    requestAnimationFrame(()=>{
      const list=$('#servicesListView');
      if(list)list.scrollTop=servicesListScrollTop;
      if(target?.focus)target.focus({preventScroll:true});
    });
  }
  function openServices(trigger){resetServicesPanel();openDrawer(els.servicesDrawer,$('#closeServices'),trigger)}
  function openPrices(trigger){openDrawer(els.drawer,$('#closePrices'),trigger)}
  function closeServices(options){resetServicesPanel();closeDrawer(els.servicesDrawer,options)}
  function closePrices(options){closeDrawer(els.drawer,options)}
  function openContact(trigger){openDrawer(els.contactDrawer,$('#closeContact'),trigger)}
  function closeContact(options){closeDrawer(els.contactDrawer,options)}
  function returnToConversation(drawer){closeDrawer(drawer,{restoreFocus:false});lastDrawerTrigger=null;els.input.focus()}
  function openInfo(title,html){$('#dialogTitle').textContent=title;$('#dialogBody').innerHTML=html;$('#infoDialog').showModal()}
  function returnToEndrian(){
    const localHome=new URLSearchParams(location.search).get('home');
    if(localHome&&localHome.startsWith('/')&&!localHome.startsWith('//')){location.href=localHome;return}
    const ref=document.referrer;
    if(ref&&ref!==location.href){location.href=ref;return}
    openInfo('Volver a ENDRIAN','<p>La Home pública no forma parte de este candidato local. Si el Laboratorio se abre desde la Home local autorizada, este acceso vuelve a esa referencia; también puede recibir una ruta local relativa mediante el parámetro home. No se ha inventado una URL pública.</p>');
  }
  async function newConversation(){await api('/api/session/new',{method:'POST',body:'{}'});location.reload()}
  async function recoverSession(){const ref=prompt('Ingresa el qa_identity_ref sintético (QID-XXXXXXXXXXXX). No ingreses datos personales.');if(!ref)return;try{await api('/api/full-flow/recover',{method:'POST',body:JSON.stringify({qa_identity_ref:ref})});location.reload()}catch(e){alert(e.body?.message||e.message)}}

  function renderGeneralContactControls(){
    $('#generalContactCountrySlot').innerHTML=pickerMarkup('generalContactCountry','País','Selecciona tu país',billingCountries,null,true,'generalContactCountryError');
    $('#generalContactPhoneSlot').innerHTML=phoneGroupMarkup('generalContactPhoneCountry','generalContactPhoneNumber');
    setupPicker('generalContactCountry',billingCountries);setupPicker('generalContactPhoneCountry',phoneCountries);
  }
  function clearGeneralContactErrors(){['generalContactNameError','generalContactLastNameError','generalContactEmailError','generalContactCountryError','generalContactPhoneNumberError','generalContactSubjectError','generalContactMessageError'].forEach(id=>setFieldError(id,''));$('#contactStatus').textContent=''}
  function validateGeneralContact(){
    clearGeneralContactErrors();
    const name=$('#generalContactName').value.trim(),lastName=$('#generalContactLastName').value.trim(),email=$('#generalContactEmail').value.trim(),subject=$('#generalContactSubject').value.trim(),message=$('#generalContactMessage').value.trim();
    const countryRoot=$('#generalContactCountry'),countryInput=countryRoot.querySelector('input'),country=pickerSelection('generalContactCountry',billingCountries),phone=validatedPhone('generalContactPhoneCountry','generalContactPhoneNumber');
    let valid=true;
    if(name.length<2){setFieldError('generalContactNameError','Escribe tu nombre.');valid=false}
    if(!validEmailFormat(email)){setFieldError('generalContactEmailError','Revisa el formato del correo.');valid=false}
    if(!country){setFieldError('generalContactCountryError','Selecciona un país de la lista.');valid=false}
    if(subject.length<2){setFieldError('generalContactSubjectError','Escribe el asunto.');valid=false}
    if(message.length<2){setFieldError('generalContactMessageError','Escribe tu mensaje.');valid=false}
    if(!phone.valid)valid=false;
    return {valid,name,lastName,email,country,phone,subject,message};
  }

  async function init(){
    cfg=await api('/api/config');const regionNames=new Intl.DisplayNames(['es'],{type:'region'});billingCountries=(cfg.billing_country_codes||[]).map(code=>({code,name:regionNames.of(code)})).sort((a,b)=>a.name.localeCompare(b.name,'es'));phoneCountries=(cfg.phone_country_prefixes||[]).map(x=>({code:x.country_code,name:regionNames.of(x.country_code),calling_code:x.calling_code})).sort((a,b)=>a.name.localeCompare(b.name,'es'));$('#greeting').textContent=cfg.copy.greeting;els.input.placeholder=cfg.copy.placeholder;$('#composerHelp').textContent=cfg.copy.composer_help;$('#qaWarning').textContent='Entorno de prueba · Sin operaciones reales';renderGeneralContactControls();
    await loadSession();
  }

  els.send.onclick=()=>send();
  els.input.addEventListener('keydown',e=>{if(e.key==='Enter'&&!e.shiftKey){e.preventDefault();send()}});
  $('#returnEndrian').onclick=returnToEndrian;
  $('#servicesButton').onclick=e=>openServices(e.currentTarget);
  $('#priceButton').onclick=e=>openPrices(e.currentTarget);
  $('#contactButton').onclick=e=>openContact(e.currentTarget);
  $('#newConversation').onclick=newConversation;
  $('#closeServices').onclick=()=>closeServices();
  $('#closePrices').onclick=()=>closePrices();
  $('#closeContact').onclick=()=>closeContact();
  document.querySelectorAll('.service-open-detail').forEach(button=>button.onclick=()=>openServiceDetail(button.dataset.serviceDetailOpen,button));
  $('#serviceBack').onclick=backToServices;
  els.backdrop.onclick=()=>{const open=publicDrawers().find(drawerIsOpen);if(open)closeDrawer(open)};
  $('#contactForm').addEventListener('submit',e=>{e.preventDefault();const result=validateGeneralContact();if(!result.valid)return;$('#contactStatus').textContent='Datos validados en esta prueba local. El mensaje no fue enviado ni almacenado.'});
  $('#privacyFooter').onclick=()=>openInfo('Política de Privacidad','<p>No introduzcas datos personales, confidenciales o sensibles reales. La información utilizada en este entorno tiene retención temporal.</p>');
  $('#contactPrivacyLink').onclick=()=>$('#privacyFooter').click();
  $('#recoverSession').onclick=recoverSession;
  $('#closeDialog').onclick=()=>$('#infoDialog').close();
  $('#homeLink').onclick=e=>{e.preventDefault();returnToEndrian()};
  $('#mobileMenu').onclick=()=>{els.mobileNav.hidden=!els.mobileNav.hidden;$('#mobileMenu').setAttribute('aria-expanded',String(!els.mobileNav.hidden))};
  els.mobileNav.querySelectorAll('button').forEach(b=>b.onclick=()=>{const a=b.dataset.mobileAction;els.mobileNav.hidden=true;$('#mobileMenu').setAttribute('aria-expanded','false');const mobileTrigger=$('#mobileMenu');if(a==='home')returnToEndrian();if(a==='services')openServices(mobileTrigger);if(a==='prices')openPrices(mobileTrigger);if(a==='contact')openContact(mobileTrigger);if(a==='new')newConversation()});
  $('#summaryToggle').onclick=()=>{const hidden=els.mobileSummary.hidden;els.mobileSummary.hidden=!hidden;$('#summaryToggle').setAttribute('aria-expanded',String(hidden))};
  document.addEventListener('keydown',e=>{if(e.key==='Escape'){const open=publicDrawers().find(drawerIsOpen);if(open)closeDrawer(open)}});
  els.conversationScroll.addEventListener('scroll',()=>{followLatest=nearChatBottom()},{passive:true});
  init().catch(e=>appendMessage('assistant','No fue posible iniciar el Laboratorio: '+e.message));
})();
