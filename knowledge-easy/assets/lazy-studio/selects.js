'use strict';
/* The hidden native select remains the data source; all visible menus use kit tokens. */
let selectMenu = null;
const selectBindings = [];
function closeSelectMenu(focus = false) {
  if (!selectMenu) return;
  const {button, popup} = selectMenu;
  popup.remove(); button.setAttribute('aria-expanded', 'false');
  if (focus) button.focus();
  selectMenu = null;
}
function syncSelects() {
  for (const {select, button, label} of selectBindings) {
    const value = select.selectedOptions[0]?.textContent || 'Choose an option';
    if (button.textContent !== value) button.textContent = value;
    button.setAttribute('aria-label', `${label}: ${value}`);
    button.disabled = select.disabled;
  }
}
function initSelects() {
  for (const select of document.querySelectorAll('select')) {
    if (select.dataset.enhanced) continue;
    select.dataset.enhanced = 'true';
    const label = select.getAttribute('aria-label') || document.querySelector(`label[for="${select.id}"]`)?.textContent || 'Select';
    const wrap = document.createElement('span'); wrap.className = `ui-select-wrap for-${select.id}`;
    const button = document.createElement('button'); button.type = 'button'; button.className = `${select.className} ui-select-button`;
    button.setAttribute('role','combobox'); button.setAttribute('aria-haspopup','listbox'); button.setAttribute('aria-expanded','false');
    select.before(wrap); wrap.append(button, select); select.hidden = true;
    const binding = {select, button, label}; selectBindings.push(binding);
    select.addEventListener('change', syncSelects);
    function open() {
      if (button.disabled) return;
      if (selectMenu?.button === button) {closeSelectMenu(true); return;}
      closeSelectMenu();
      const popup = document.createElement('div'); popup.className='choice-menu'; popup.id=`menu-${select.id}`;
      popup.setAttribute('role','listbox'); popup.setAttribute('aria-label',label); button.setAttribute('aria-controls',popup.id);
      const options = Array.from(select.options), rows=[];
      let active = Math.max(0, options.findIndex(o=>o.selected && !o.disabled));
      const pick = index => {if(options[index].disabled)return;select.value=options[index].value;select.dispatchEvent(new Event('change',{bubbles:true}));syncSelects();closeSelectMenu(true);};
      const highlight = index => {active=index;rows.forEach((r,i)=>r.classList.toggle('focused',i===active));button.setAttribute('aria-activedescendant',rows[active].id);rows[active].scrollIntoView({block:'nearest'});};
      options.forEach((option,index)=>{const row=document.createElement('div');row.className='choice-option';row.id=`option-${select.id}-${index}`;row.setAttribute('role','option');row.setAttribute('aria-selected',option.selected);row.setAttribute('aria-disabled',option.disabled);row.textContent=option.textContent;const tick=document.createElement('span');tick.textContent=option.selected?'✓':'';tick.setAttribute('aria-hidden','true');row.append(tick);row.onclick=()=>pick(index);row.onpointermove=()=>{if(!option.disabled)highlight(index);};rows.push(row);popup.append(row);});
      document.body.append(popup);const rect=button.getBoundingClientRect(),w=Math.max(160,rect.width);popup.style.width=`${Math.min(w,innerWidth-24)}px`;popup.style.left=`${Math.max(12,Math.min(rect.left,innerWidth-w-12))}px`;const h=Math.min(popup.scrollHeight,252);popup.style.top=`${rect.bottom+8+h>innerHeight-12?Math.max(12,rect.top-h-8):rect.bottom+8}px`;
      button.setAttribute('aria-expanded','true');selectMenu={button,popup,options,pick,highlight,get active(){return active;}};highlight(active);
    }
    button.onclick=open;
    button.onkeydown=e=>{if(['ArrowDown','ArrowUp','Home','End','Enter',' ','Escape'].includes(e.key)){e.preventDefault();e.stopPropagation();if(e.key==='Escape'){closeSelectMenu(true);return;}if(!selectMenu||selectMenu.button!==button){open();return;}const menu=selectMenu;if(e.key==='Enter'||e.key===' '){menu.pick(menu.active);return;}const enabled=menu.options.map((o,i)=>o.disabled?-1:i).filter(i=>i>=0);let i=enabled.indexOf(menu.active);i=e.key==='Home'?0:e.key==='End'?enabled.length-1:(i+(e.key==='ArrowDown'?1:-1)+enabled.length)%enabled.length;menu.highlight(enabled[i]);}else if(e.key==='Tab')closeSelectMenu();};
  }
  syncSelects();
}
document.addEventListener('pointerdown',e=>{if(selectMenu&&!selectMenu.popup.contains(e.target)&&!selectMenu.button.contains(e.target))closeSelectMenu();});
window.addEventListener('resize',()=>closeSelectMenu());
