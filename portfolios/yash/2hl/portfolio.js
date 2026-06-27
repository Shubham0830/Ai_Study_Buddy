
/* THEME */
const html=document.documentElement;
const tb=document.getElementById('theme-toggle');
const ti=tb.querySelector('i');
tb.addEventListener('click',()=>{
  const d=html.getAttribute('data-theme')==='dark';
  html.setAttribute('data-theme',d?'light':'dark');
  ti.className=d?'fa-solid fa-sun':'fa-solid fa-moon';
});

/* HAMBURGER */
const ham=document.getElementById('hamburger');
const mob=document.getElementById('mobile-menu');
ham.addEventListener('click',()=>mob.classList.toggle('open'));
mob.querySelectorAll('.ml').forEach(l=>l.addEventListener('click',()=>mob.classList.remove('open')));

/* ACTIVE NAV */
const secs=document.querySelectorAll('section[id]');
const nls=document.querySelectorAll('.nl');
function setActive(){
  let cur='';
  secs.forEach(s=>{if(window.scrollY>=s.offsetTop-80)cur=s.id;});
  nls.forEach(l=>l.classList.toggle('active',l.getAttribute('href')==='#'+cur));
}
window.addEventListener('scroll',setActive,{passive:true});
setActive();

/* SCROLL REVEAL */
document.querySelectorAll('.reveal').forEach(el=>{
  new IntersectionObserver(([e])=>{if(e.isIntersecting)el.classList.add('vis');},{threshold:.1}).observe(el);
});

/* TYPEWRITER */
const phrases=['Competitive programmer','Backend Developer','API Builder','Full-Stack Developer','Problem solver'];
let pi=0,ci=0,del=false;
const tw=document.getElementById('typewriter');
function type(){
  const w=phrases[pi];
  if(!del){tw.textContent=w.slice(0,++ci);if(ci===w.length){del=true;setTimeout(type,2000);return;}}
  else{tw.textContent=w.slice(0,--ci);if(ci===0){del=false;pi=(pi+1)%phrases.length;}}
  setTimeout(type,del?50:90);
}
type();

/* CONTACT */
function sendMsg(){
  const n=document.getElementById('cn').value.trim();
  const e=document.getElementById('ce').value.trim();
  const m=document.getElementById('cm').value.trim();
  const fm=document.getElementById('fm');
  const btn=document.getElementById('send-btn');
  fm.className='';fm.innerHTML='';
  if(!n||!e||!m){fm.innerHTML='<i class="fa-solid fa-circle-exclamation"></i>&nbsp;Name, email and message are required.';fm.className='err';return;}
  if(!/\S+@\S+\.\S+/.test(e)){fm.innerHTML='<i class="fa-solid fa-circle-exclamation"></i>&nbsp;Invalid email address.';fm.className='err';return;}
  btn.disabled=true;btn.innerHTML='<i class="fa-solid fa-spinner fa-spin"></i>&nbsp;Sending…';
  setTimeout(()=>{
    fm.innerHTML='<i class="fa-solid fa-circle-check"></i>&nbsp;Message sent! Naresh will reply within 24 hours.';
    fm.className='ok';btn.disabled=false;
    btn.innerHTML='<i class="fa-solid fa-paper-plane"></i>&nbsp;Send Message';
    ['cn','ce','cs','cm'].forEach(id=>document.getElementById(id).value='');
  },1300);
}