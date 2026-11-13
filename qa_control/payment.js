(() => {
  const reference=document.querySelector('#reference');
  const result=document.querySelector('#result');
  const referenceStatus=document.querySelector('#referenceStatus');
  async function loadPendingReference(){
    try{
      const response=await fetch('/api/session',{credentials:'same-origin'});
      const body=await response.json();
      const payment=body?.full_flow?.payment_qa||{};
      if(payment.status==='PENDIENTE'&&payment.reference){reference.value=payment.reference;referenceStatus.textContent='Intento pendiente cargado para esta sesión.'}
      else{referenceStatus.textContent='No encontramos un intento pendiente en esta sesión. Vuelve al Laboratorio y completa primero la simulación de pago.'}
    }catch(error){referenceStatus.textContent='No fue posible cargar automáticamente la referencia. Puedes copiarla desde /api/session.'}
  }
  async function resolve(outcome){
    const value=reference.value.trim();
    if(!value){result.textContent='Ingresa una referencia válida.';return}
    document.querySelectorAll('button').forEach(button=>button.disabled=true);
    try{
      const response=await fetch('/api/qa-control/payment/resolve',{method:'POST',credentials:'same-origin',headers:{'Content-Type':'application/json'},body:JSON.stringify({reference:value,outcome})});
      const body=await response.json();
      result.textContent=JSON.stringify({ok:response.ok,event:body.event,message:body.message,state:body.summary?.full_flow?.state,order_id:body.summary?.full_flow?.order_qa?.order_id||null},null,2);
      if(response.ok&&outcome==='confirmed')referenceStatus.textContent='Pago QA confirmado. Vuelve al Laboratorio para ver la orden.';
    }catch(error){result.textContent='No fue posible aplicar el resultado: '+error.message}
    finally{document.querySelectorAll('button').forEach(button=>button.disabled=false)}
  }
  document.querySelectorAll('[data-outcome]').forEach(button=>button.addEventListener('click',()=>resolve(button.dataset.outcome)));
  loadPendingReference();
})();
