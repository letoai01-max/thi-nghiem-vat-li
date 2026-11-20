"use strict";
// Thí nghiệm khám phá Vật lí 10 (KNTT): nêu vấn đề → sơ đồ → thao tác → quan sát → phân tích → kết luận.
const $=s=>document.getElementById(s),cv=$("cv"),c=cv.getContext("2d"),W=720,H=360,g=9.8,D=Math.PI/180;
const col=n=>getComputedStyle(document.body).getPropertyValue(n).trim()||"#888";
const L=(a,b,x,y,w,s)=>{c.beginPath();c.moveTo(a,b);c.lineTo(x,y);c.lineWidth=w||2;c.strokeStyle=s||col("--c");c.stroke()};
const O=(x,y,r,f,s)=>{c.beginPath();c.arc(x,y,Math.max(r,.5),0,7);if(f){c.fillStyle=f;c.fill()}if(s!==0){c.strokeStyle=s||col("--c");c.lineWidth=1.5;c.stroke()}};
const T=(t,x,y,s,f)=>{c.fillStyle=f||col("--c");c.font=(s||13)+"px system-ui,sans-serif";c.fillText(t,x,y)};
const R=(x,y,w,h,f,s)=>{if(f){c.fillStyle=f;c.fillRect(x,y,w,h)}if(s){c.strokeStyle=s;c.lineWidth=1.5;c.strokeRect(x,y,w,h)}};
const A=(a,b,x,y,s)=>{L(a,b,x,y,2.5,s);const q=Math.atan2(y-b,x-a);c.beginPath();c.moveTo(x,y);c.lineTo(x-9*Math.cos(q-.4),y-9*Math.sin(q-.4));c.lineTo(x-9*Math.cos(q+.4),y-9*Math.sin(q+.4));c.closePath();c.fillStyle=s||col("--c");c.fill()};
const POLY=(pts,f,s)=>{c.beginPath();pts.forEach((p,i)=>i?c.lineTo(p[0],p[1]):c.moveTo(p[0],p[1]));c.closePath();if(f){c.fillStyle=f;c.fill()}c.strokeStyle=s||col("--c");c.lineWidth=1.5;c.stroke()};
const N=v=>v*(($("nhieu")&&$("nhieu").checked)?1+(Math.random()*2-1)*.03:1);                 // nhiễu đo tuỳ chọn
const F=(v,n)=>(+v).toFixed(n==null?2:n).replace(".",",");
function GR(x,y,w,h,pts,xl,yl,fit){                                                          // đồ thị thời gian thực
 R(x,y,w,h,col("--n"),col("--c"));T(yl,x+4,y+13,11);T(xl,x+w-70,y+h-4,11);
 if(!pts.length)return;const X=pts.map(p=>p[0]),Y=pts.map(p=>p[1]),mx=Math.max(1e-9,...X),my=Math.max(1e-9,...Y);
 const px=v=>x+8+(w-16)*v/mx,py=v=>y+h-8-(h-30)*v/my;
 if(fit)L(px(0),py(0),px(mx),py(fit*mx),1.5,col("--o"));
 c.beginPath();pts.forEach((p,i)=>i?c.lineTo(px(p[0]),py(p[1])):c.moveTo(px(p[0]),py(p[1])));c.strokeStyle=col("--m");c.lineWidth=2;c.stroke();
 pts.forEach(p=>O(px(p[0]),py(p[1]),2.5,col("--m"),0))}
function GR2(x,y,w,h,series,xl,yl){                                                          // nhiều đường
 R(x,y,w,h,col("--n"),col("--c"));T(yl,x+4,y+13,11);T(xl,x+w-70,y+h-4,11);const all=series.flatMap(s=>s.p);if(!all.length)return;
 const mx=Math.max(1e-9,...all.map(p=>p[0])),my=Math.max(1e-9,...all.map(p=>p[1]));
 series.forEach(s=>{c.beginPath();s.p.forEach((p,i)=>{const X=x+8+(w-16)*p[0]/mx,Y=y+h-8-(h-30)*p[1]/my;i?c.lineTo(X,Y):c.moveTo(X,Y)});c.strokeStyle=s.c;c.lineWidth=2;c.stroke()})}
const SIMS=[];let sim,S,P={},run=false,last=0;
function sliders(){const k=$("ctl");k.innerHTML="";(sim.P||[]).forEach(p=>{P[p[0]]=p[4];const d=document.createElement("div"),v=document.createElement("span");
 d.innerHTML=`<label>${p[1]}: <b id="v_${p[0]}"></b></label><input type="range" min="${p[2]}" max="${p[3]}" step="${p[5]||.1}" value="${p[4]}">`;
 const i=d.querySelector("input"),b=d.querySelector("b");b.textContent=F(p[4],p[5]>=1?0:2);i.oninput=()=>{P[p[0]]=+i.value;b.textContent=F(+i.value,p[5]>=1?0:2);reset()};k.appendChild(d)})}
function reset(){S={t:0,tb:[],fin:false,n:0};run=false;if(sim.init)sim.init(S,P);$("chay").textContent="▶ Bắt đầu";if(!sim.dom)paint()}
function paint(){c.clearRect(0,0,W,H);if(sim.draw)sim.draw(S,P);$("so").textContent=sim.info?sim.info(S,P):""}
function tick(ts){const dt=Math.min(.03,(ts-last)/1e3||0);last=ts;if(run&&sim.step&&!sim.dom){for(let i=0;i<4;i++)sim.step(S,P,dt/4);S.t+=dt;if(S.fin){run=false;$("chay").textContent="▶ Chạy lại"}}if(!sim.dom)paint();requestAnimationFrame(tick)}
function load(i){sim=SIMS[i];$("ten").textContent=`${sim.id.toUpperCase()}. ${sim.ten}`;$("chg").textContent=`Chương ${sim.ch}`;$("vd").textContent=sim.vd;$("kl").textContent=sim.kl;
 cv.hidden=!!sim.dom;$("dom").innerHTML="";$("nut").innerHTML="";sliders();(sim.btn||[]).forEach(b=>{const e=document.createElement("button");e.className="p";e.textContent=b[0];e.onclick=()=>{b[1](S,P);if(!run&&!sim.dom)paint()};$("nut").appendChild(e)});
 $("chay").hidden=$("dat").hidden=!!(sim.dom||sim.static);reset();if(sim.dom){sim.dom($("dom"));$("so").textContent=""}}
$("chay").onclick=()=>{if(S.fin||!run&&S.t>0&&sim.once)reset();run=!run;$("chay").textContent=run?"⏸ Tạm dừng":"▶ Tiếp tục"};$("dat").onclick=reset;
if(typeof document!=="undefined"&&cv.getContext){window.addEventListener("load",()=>{SIMS.forEach((s,i)=>$("ds").add(new Option(`${s.id.toUpperCase()} – ${s.ten}`,i)));$("ds").onchange=()=>load(+$("ds").value);
 const q=(location.hash.match(/k\d\d/)||[])[0],i=SIMS.findIndex(s=>s.id==q);$("ds").value=Math.max(i,0);load(Math.max(i,0));requestAnimationFrame(tick)})}
cv.onclick=e=>{if(sim&&sim.click){const r=cv.getBoundingClientRect();sim.click(S,P,(e.clientX-r.left)*W/r.width,(e.clientY-r.top)*H/r.height);if(!run)paint()}};
const GND=H-24,ground=()=>{R(0,GND,W,24,col("--v"));L(0,GND,W,GND,2)};
const tab=(h,rows)=>rows.length?"\n"+h.join(" | ")+"\n"+rows.slice(-8).map(r=>r.join(" | ")).join("\n"):"";

SIMS.push({id:"k01",ten:"An toàn phòng thực hành và nhận diện thiết bị",ch:"I",
 vd:"Trước khi làm thí nghiệm, em phải nhận ra các biển báo nguy hiểm và biết thao tác an toàn khi cắm nguồn điện. Nối từng biển báo với ý nghĩa, rồi sắp xếp đúng các bước cắm nguồn.",
 kl:"Biển báo giúp nhận biết rủi ro (điện, nhiệt, hoá chất) trước khi thao tác. Với nguồn điện: kiểm tra dây và ổ cắm → tắt công tắc thiết bị → cắm phích → rồi mới bật công tắc; không cắm hoặc rút phích khi tay ướt, không lắc chân cắm.",
 dom(el){const bb=[["⚡","Nguy cơ điện giật"],["🔥","Nguồn nhiệt, dễ cháy, dễ bỏng"],["☣","Hoá chất độc hại"],["👓","Bắt buộc đeo kính bảo hộ"],["⚠","Cảnh báo nguy hiểm chung"]],op=[2,0,4,3,1];
  const st=["Kiểm tra dây điện và ổ cắm không hỏng","Tắt công tắc nguồn của thiết bị","Cắm phích vào ổ cắm","Bật công tắc và quan sát"],mix=[2,0,3,1];let got=[];
  el.innerHTML="<p><b>1. Nối biển báo với ý nghĩa</b></p>"+bb.map((b,i)=>`<div style="font-size:30px">${b[0]} <select data-i="${i}" style="font-size:15px"><option value="">chọn ý nghĩa…</option>${op.map(j=>`<option value="${j}">${bb[j][1]}</option>`).join("")}</select></div>`).join("")+
   `<button id="k1a">Kiểm tra</button><p><b>2. Thứ tự cắm nguồn điện (bấm lần lượt)</b></p><div id="k1s">${mix.map(i=>`<button class="p" data-s="${i}">${st[i]}</button>`).join(" ")}</div><p id="k1o"></p><button id="k1b">Kiểm tra thứ tự</button><button class="p" id="k1c">Làm lại</button><pre id="k1r"></pre>`;
  el.querySelector("#k1a").onclick=()=>{let ok=0;el.querySelectorAll("select").forEach(s=>{if(s.value!==""&&+s.value===+s.dataset.i)ok++});$("k1r").textContent=`Nối đúng ${ok}/5 biển báo.`+(ok<5?" Xem lại những biển chưa khớp.":" Tốt!")};
  el.querySelectorAll("#k1s button").forEach(b=>b.onclick=()=>{if(!got.includes(+b.dataset.s)){got.push(+b.dataset.s);b.disabled=true;$("k1o").textContent=got.map((x,i)=>`${i+1}. ${st[x]}`).join(" → ")}});
  el.querySelector("#k1b").onclick=()=>{$("k1r").textContent=got.length<4?"Hãy bấm đủ 4 bước.":got.every((x,i)=>x===i)?"Đúng thứ tự an toàn.":"Chưa đúng: phải tắt công tắc thiết bị TRƯỚC khi cắm phích, và chỉ bật công tắc sau cùng."};
  el.querySelector("#k1c").onclick=()=>{got=[];$("k1o").textContent="";el.querySelectorAll("#k1s button").forEach(b=>b.disabled=false);$("k1r").textContent=""}}});

SIMS.push({id:"k02",ten:"Tháp nghiêng Pisa (Galilei)",ch:"I",
 vd:"Hai quả cầu có khối lượng chênh lệch lớn được thả cùng lúc từ đỉnh tháp. Quả nào chạm đất trước? Hãy đổi khối lượng, rồi bật/tắt lực cản không khí và quan sát.",
 kl:"Khi bỏ qua lực cản, mọi vật rơi với cùng gia tốc g nên chạm đất cùng lúc dù khác khối lượng (bác bỏ quan niệm của Aristotle). Có lực cản, vật nhẹ có gia tốc nhỏ hơn (a = g − k·v²/m) nên chạm đất sau: khác biệt đến từ lực cản, không phải từ khối lượng.",
 P:[["m1","Khối lượng quả cầu 1 (kg)",.5,20,10,.5],["m2","Khối lượng quả cầu 2 (kg)",.05,5,1,.05],["lc","Lực cản không khí (0 = không, 1 = có)",0,1,0,1]],
 init(S){S.b=[{y:0,v:0,t:null},{y:0,v:0,t:null}];S.tt=0},
 step(S,P,dt){S.tt+=dt;S.b.forEach((b,i)=>{if(b.t!=null)return;const m=i?P.m2:P.m1;b.v+=(g-(P.lc?.02/m*b.v*b.v:0))*dt;b.y+=b.v*dt;if(b.y>=20){b.y=20;b.t=S.tt}});S.fin=S.b.every(b=>b.t!=null)},
 draw(S,P){R(60,20,600,6,col("--o"));T("đỉnh tháp 20 m",64,16,11);ground();S.b.forEach((b,i)=>{const m=i?P.m2:P.m1,r=5+4*Math.cbrt(m),x=240+i*240;L(x,26,x,GND,1,col("--v"));O(x,26+b.y*14.5,r,i?col("--gr"):col("--m"));T(`m = ${F(m,2)} kg`,x-30,GND+16,12)})},
 info(S,P){const[a,b]=S.b;return `Lực cản: ${P.lc?"có":"không"}\nThời gian rơi: quả 1 = ${a.t==null?"…":F(a.t,2)+" s"};  quả 2 = ${b.t==null?"…":F(b.t,2)+" s"}`+(a.t!=null&&b.t!=null?`\nChênh lệch: ${F(Math.abs(a.t-b.t),2)} s`:"")}});

SIMS.push({id:"k03",ten:"Ống chân không Newton",ch:"II",
 vd:"Trong ống chứa không khí, viên bi chì rơi nhanh hơn chiếc lông chim. Điều gì xảy ra khi hút hết không khí? Chuyển môi trường rồi so sánh đồ thị vận tốc theo thời gian.",
 kl:"Trong không khí, lông chim chịu lực cản lớn so với trọng lượng nên rơi chậm và nhanh chóng đạt tốc độ ổn định. Trong chân không chỉ còn trọng lực nên cả hai có cùng gia tốc g: đồ thị v–t trùng nhau và hai vật chạm đáy cùng lúc.",
 P:[["cd","Môi trường (0 = không khí, 1 = chân không)",0,1,0,1]],
 init(S){S.b=[{y:0,v:0,k:.002,t:null,p:[]},{y:0,v:0,k:1.2,t:null,p:[]}];S.tt=0},
 step(S,P,dt){S.tt+=dt;S.b.forEach(b=>{if(b.t!=null)return;b.v+=(g-(P.cd?0:b.k*b.v*b.v))*dt;b.y+=b.v*dt;if(Math.round(S.tt*100)%2==0)b.p.push([S.tt,b.v]);if(b.y>=2){b.y=2;b.t=S.tt}});S.fin=S.b.every(b=>b.t!=null)},
 draw(S,P){R(80,30,70,300,col("--p"),col("--c"));R(80,30,70,300,P.cd?"rgba(120,120,120,.18)":"rgba(74,163,232,.10)");T(P.cd?"chân không":"không khí",70,350,12);
  S.b.forEach((b,i)=>{const x=i?130:100;O(x,45+b.y*140,i?7:9,i?col("--o"):col("--m"));T(i?"lông chim":"bi chì",x-20,24,11)});GR2(250,30,440,300,[{p:S.b[0].p,c:col("--m")},{p:S.b[1].p,c:col("--o")}],"t (s)","v (m/s)  — xanh: bi chì, cam: lông chim")},
 info(S){return S.b.map((b,i)=>`${i?"Lông chim":"Bi chì"}: v = ${F(b.v,2)} m/s`+(b.t!=null?`, chạm đáy sau ${F(b.t,2)} s`:"")).join("\n")}});

SIMS.push({id:"k04",ten:"Kiểm tra phương thẳng đứng của sự rơi",ch:"II",
 vd:"Dây dọi cho biết phương thẳng đứng. Thả viên bi từ đỉnh giá đỡ và dùng êke kiểm tra: bi rơi theo phương nào? Thử nghiêng giá đỡ để xem đường rơi có thay đổi không.",
 kl:"Dù giá đỡ nghiêng bao nhiêu, bi vẫn rơi dọc theo (song song với) dây dọi: quỹ đạo rơi tự do là đường thẳng đứng, vì lực tác dụng duy nhất là trọng lực hướng thẳng đứng xuống. Độ lệch so với giá đỡ nghiêng tăng dần, độ lệch so với dây dọi luôn bằng 0.",
 P:[["ng","Độ nghiêng của giá đỡ (độ)",0,30,12,1]],
 init(S){S.y=0;S.v=0;S.tr=[]},
 step(S,P,dt){if(S.y>=4)return;S.v+=g*dt;S.y+=S.v*dt;if(S.tr.length==0||S.y-S.tr[S.tr.length-1]>.2)S.tr.push(S.y);if(S.y>=4){S.y=4;S.fin=true}},
 draw(S,P){ground();const x0=360,y0=30,s=75,t=P.ng*D;L(x0-4-80,GND,x0-4-80+(GND-y0)*Math.tan(t),y0,6,col("--o"));L(x0,y0,x0,GND-5,1.5,col("--r"));O(x0,GND-5,6,col("--r"));T("dây dọi",x0+8,60,12,col("--r"));
  S.tr.forEach(y=>O(x0+14,y0+y*s,3,col("--m"),0));O(x0+14,y0+S.y*s,7,col("--m"));POLY([[x0+30,GND],[x0+30,GND-120],[x0+130,GND]],"rgba(42,157,74,.18)",col("--gr"));T("êke",x0+70,GND-22,12,col("--gr"));L(x0+30,y0,x0+30,GND,1,col("--gr"))},
 info(S,P){const dev=S.y*Math.tan(P.ng*D)*1000;return `Độ lệch của bi so với dây dọi: 0,0 mm\nĐộ lệch của bi so với trục giá đỡ nghiêng ${P.ng}°: ${F(dev,0)} mm\nQuãng rơi: ${F(S.y,2)} m`}});

SIMS.push({id:"k05",ten:"Chuyển động ném ngang",ch:"II",
 vd:"Búa đập giải phóng đồng thời bi A (ném ngang) và bi B (rơi tự do). Bi nào chạm đất trước? Chỉnh vận tốc ném v₀ và độ cao rồi phân tích toạ độ x, y.",
 kl:"Hai bi chạm đất cùng lúc: theo phương thẳng đứng bi A cũng rơi tự do (y = ½gt²), còn theo phương ngang chuyển động thẳng đều (x = v₀t). Quỹ đạo là một nhánh parabol; thời gian rơi t = √(2h/g) không phụ thuộc v₀, tầm xa L = v₀·t.",
 P:[["v0","Vận tốc ném v₀ (m/s)",1,15,8,.5],["h","Độ cao h (m)",5,25,15,1]],
 init(S){S.tt=0;S.A=[];S.B=[]},
 step(S,P,dt){S.tt+=dt;const T0=Math.sqrt(2*P.h/g);if(S.tt>=T0){S.tt=T0;S.fin=true}if(!S.A.length||S.tt-S.A[S.A.length-1][2]>=.099||S.fin){S.A.push([P.v0*S.tt,.5*g*S.tt*S.tt,S.tt])}},
 draw(S,P){ground();const s=12,x0=40,y0=GND-P.h*s,px=x=>x0+x*s,py=y=>y0+y*s;R(x0-30,y0,40,5,col("--o"));
  c.setLineDash([4,4]);c.beginPath();for(let t=0;t<=Math.sqrt(2*P.h/g);t+=.02)c.lineTo(px(P.v0*t),py(.5*g*t*t));c.strokeStyle=col("--m");c.stroke();c.setLineDash([]);
  S.A.forEach(p=>{O(px(p[0]),py(p[1]),3,col("--m"),0);O(x0+40,py(p[1]),3,col("--gr"),0);L(x0+40,py(p[1]),px(p[0]),py(p[1]),.5,col("--v"))});
  const q=S.A[S.A.length-1]||[0,0];O(px(q[0]),py(q[1]),8,col("--m"));O(x0+40,py(q[1]),8,col("--gr"));T("A",px(q[0])+10,py(q[1]),12);T("B",x0+52,py(q[1]),12)},
 info(S,P){const x=P.v0*S.tt,y=.5*g*S.tt*S.tt;return `t = ${F(S.tt,2)} s;  x = v₀t = ${F(x,2)} m;  y = ½gt² = ${F(y,2)} m\nvₓ = ${F(P.v0,2)} m/s;  v_y = gt = ${F(g*S.tt,2)} m/s\nDự đoán: t_rơi = √(2h/g) = ${F(Math.sqrt(2*P.h/g),2)} s (cả A và B);  tầm xa L = ${F(P.v0*Math.sqrt(2*P.h/g),2)} m`}});

SIMS.push({id:"k06",ten:"Chuyển động ném xiên",ch:"II",
 vd:"Vật được bắn lên với vận tốc v₀ hợp góc α với phương ngang. Thay đổi α và v₀: góc nào cho tầm xa lớn nhất? Quan sát vectơ vận tốc và tiếp tuyến quỹ đạo.",
 kl:"Quỹ đạo là parabol. Tầm bay cao H_max = v₀²sin²α/(2g), tầm bay xa L = v₀²sin2α/g đạt lớn nhất khi α = 45° (bỏ qua lực cản). Hai góc phụ nhau (ví dụ 30° và 60°) cho cùng tầm xa. Vectơ vận tốc luôn tiếp tuyến với quỹ đạo; thành phần ngang không đổi, thành phần đứng đổi dấu ở đỉnh.",
 P:[["a","Góc bắn α (độ)",5,85,45,1],["v0","Vận tốc ban đầu v₀ (m/s)",5,30,20,1]],
 init(S){S.tt=0;S.p=[]},
 step(S,P,dt){const T0=2*P.v0*Math.sin(P.a*D)/g;S.tt+=dt;if(S.tt>=T0){S.tt=T0;S.fin=true}S.p.push([P.v0*Math.cos(P.a*D)*S.tt,P.v0*Math.sin(P.a*D)*S.tt-.5*g*S.tt*S.tt])},
 draw(S,P){ground();const s=620/(P.v0*P.v0/g),x0=40,px=x=>x0+x*s,py=y=>GND-y*s,vx=P.v0*Math.cos(P.a*D),vy=P.v0*Math.sin(P.a*D)-g*S.tt,T0=2*P.v0*Math.sin(P.a*D)/g;
  c.setLineDash([4,4]);c.beginPath();for(let t=0;t<=T0;t+=T0/60)c.lineTo(px(vx*t),py(P.v0*Math.sin(P.a*D)*t-.5*g*t*t));c.strokeStyle=col("--v");c.lineWidth=2;c.stroke();c.setLineDash([]);
  S.p.forEach((p,i)=>{if(i%6==0)O(px(p[0]),py(p[1]),2.5,col("--m"),0)});const q=S.p[S.p.length-1]||[0,0],X=px(q[0]),Y=py(q[1]);
  L(X-vx*s*.5,Y+vy*s*.5,X+vx*s*.5,Y-vy*s*.5,1,col("--o"));A(X,Y,X+vx*4,Y-vy*4,col("--r"));A(X,Y,X+vx*4,Y,col("--gr"));A(X,Y,X,Y-vy*4,col("--gr"));O(X,Y,7,col("--m"))},
 info(S,P){const vx=P.v0*Math.cos(P.a*D),vy=P.v0*Math.sin(P.a*D)-g*S.tt;return `t = ${F(S.tt,2)} s;  vₓ = ${F(vx,2)} m/s;  v_y = ${F(vy,2)} m/s;  v = ${F(Math.hypot(vx,vy),2)} m/s\nH_max = ${F(Math.pow(P.v0*Math.sin(P.a*D),2)/(2*g),2)} m;  L = ${F(P.v0*P.v0*Math.sin(2*P.a*D)/g,2)} m  (L_max = ${F(P.v0*P.v0/g,2)} m khi α = 45°)`}});

SIMS.push({id:"k07",ten:"Máng nghiêng Galilei (Định luật 1 Newton)",ch:"III",
 vd:"Thả bi từ độ cao cố định xuống máng nghiêng rồi cho lên một máng nghiêng thứ hai. Giảm dần góc nghiêng β của máng thứ hai và hệ số ma sát: bi đi được quãng đường thế nào? Nếu β = 0 và không ma sát thì sao?",
 kl:"Ma sát càng nhỏ và máng càng thoải thì bi càng đi xa, vẫn lên gần tới độ cao ban đầu. Suy luận của Galilei: nếu không có ma sát và mặt phẳng nằm ngang thì bi chuyển động thẳng đều mãi mãi. Vật giữ nguyên trạng thái chuyển động khi không chịu lực (hoặc các lực cân bằng): Định luật 1 Newton.",
 P:[["b","Góc nghiêng máng thứ hai β (độ)",0,60,20,1],["mu","Hệ số ma sát μ",0,.3,0,.01]],
 init(S){S.s=0;S.v=0;S.hmax=0},
 step(S,P,dt){const l1=2/Math.sin(35*D),b=P.b*D;let sl,cs;if(S.s<l1){sl=-Math.sin(35*D);cs=Math.cos(35*D)}else if(S.s<l1+3){sl=0;cs=1}else{sl=Math.sin(b);cs=Math.cos(b)}
  let a=-g*sl;const ff=P.mu*g*cs;if(Math.abs(S.v)<1e-3&&Math.abs(a)<=ff&&S.t>.3){S.v=0;S.fin=true;return}a-=ff*Math.sign(S.v||-a);S.v+=a*dt;S.s+=S.v*dt;if(S.s<0){S.s=0;S.v=0}
  if(S.s>l1+3){S.hmax=Math.max(S.hmax,(S.s-l1-3)*Math.sin(b))}if(S.s>l1+3+25){S.fin=true}},
 draw(S,P){const b=P.b*D,l1=2/Math.sin(35*D),dx1=2/Math.tan(35*D),ext=12,tot=dx1+3+ext*Math.cos(b),s=Math.min(60,690/tot),x0=15,zb=GND-5,X=x=>x0+x*s,Z=z=>zb-z*s;
  const pts=[[X(0),Z(2)],[X(dx1),Z(0)],[X(dx1+3),Z(0)],[X(dx1+3+ext*Math.cos(b)),Z(ext*Math.sin(b))]];L(...pts[0],...pts[1],4);L(...pts[1],...pts[2],4);L(...pts[2],...pts[3],4);
  c.setLineDash([5,5]);L(0,Z(2),W,Z(2),1,col("--o"));c.setLineDash([]);T("độ cao ban đầu",W-110,Z(2)-4,11,col("--o"));
  let p;if(S.s<l1)p=[X(dx1*(1-S.s/l1)),Z(2-S.s*Math.sin(35*D))];else if(S.s<l1+3)p=[X(dx1+S.s-l1),Z(0)];else{const u=S.s-l1-3;p=[X(dx1+3+u*Math.cos(b)),Z(u*Math.sin(b))]}O(p[0],p[1]-7,7,col("--m"))},
 info(S,P){return `Vận tốc bi: ${F(S.v,2)} m/s;  độ cao lớn nhất đạt được trên máng 2: ${F(S.hmax,2)} m (ban đầu 2,00 m)`+(P.b==0&&P.mu==0&&S.t>3?"\nKhông ma sát, mặt phẳng ngang: v không đổi (chuyển động thẳng đều).":"")}});
SIMS.push({id:"k08",ten:"Khảo sát quán tính",ch:"III",
 vd:"Tình huống 1: xe chở khối gỗ bị chặn đột ngột. Tình huống 2: giật nhanh tờ giấy dưới cốc nước. Điều gì xảy ra với khối gỗ và cái cốc? Đổi vận tốc, thử có và không có dây an toàn.",
 kl:"Mọi vật có xu hướng giữ nguyên trạng thái chuyển động của mình (quán tính). Xe dừng đột ngột, khối gỗ vẫn tiến về trước; dây an toàn tạo lực hãm giữ người lại. Giật giấy thật nhanh thì lực ma sát tác dụng lên cốc chỉ trong thời gian rất ngắn nên cốc gần như đứng yên; kéo chậm thì cốc bị cuốn theo.",
 P:[["demo","Tình huống (0 = xe và khối gỗ, 1 = giật tờ giấy)",0,1,0,1],["v","Vận tốc xe / tốc độ giật giấy (m/s)",.2,6,3,.1],["dai","Dây an toàn cho khối gỗ (0 = không, 1 = có)",0,1,0,1]],
 init(S,P){S.tt=0;S.xc=1;S.vc=P.v;S.xb=2.5;S.vb=P.v;S.hit=false;S.xp=0;S.xcup=.25;S.vcup=0},
 step(S,P,dt){if(!P.demo){if(!S.hit&&S.xc+3>=15.5){S.hit=true;S.vc=0;S.xc=12.5;if(P.dai)S.vb=0}if(S.hit&&!P.dai)S.vb=Math.max(0,S.vb-1.5*dt);S.xc+=S.vc*dt;S.xb+=(S.hit?S.vb:S.vc)*dt;if(S.hit&&(S.vb==0||S.xb>16.5)&&S.t>1)S.fin=true}
  else{S.xp+=P.v*dt;const mg=.3*g;if(S.xp<S.xcup){S.vcup=Math.min(P.v,S.vcup+mg*dt)}else S.vcup=Math.max(0,S.vcup-mg*dt);S.xcup+=S.vcup*dt;if(S.xp>S.xcup+.5&&S.vcup==0)S.fin=true}},
 draw(S,P){if(!P.demo){ground();R(620,GND-120,10,120,col("--o"));T("tường",610,GND-126,12);const x=S.xc*40;R(x,GND-30,120,16,col("--m"));O(x+22,GND-10,9,col("--c"));O(x+98,GND-10,9,col("--c"));const bx=S.xb*40-16;R(bx,GND-62,32,32,col("--o"),col("--c"));if(P.dai)L(bx+16,GND-46,x+60,GND-30,3,col("--r"));if(S.hit&&!P.dai)T("quán tính: khối gỗ văng về phía trước",300,60,14,col("--r"))}
  else{const y=200;R(60,y,600,10,col("--v"));R(60+S.xp*300,y-4,150,4,"#e8d37a",col("--c"));const cx=60+S.xcup*300;R(cx-18,y-48,36,44,col("--w"),col("--c"));T(S.xp>S.xcup+.5?"giấy đã rút ra":"giấy đang bị kéo →",70,y+30,13)}},
 info(S,P){return P.demo?`Cốc dịch chuyển: ${F((S.xcup-.25)*100,1)} cm (giật càng nhanh, cốc càng ít dịch)`:`Vận tốc xe: ${F(S.vc,1)} m/s; vận tốc khối gỗ: ${F(S.vb,1)} m/s`}});

SIMS.push({id:"k09",ten:"Khảo sát Định luật 2 Newton",ch:"III",rec:[],
 vd:"Xe trượt trên đệm khí được kéo bởi quả cân treo qua ròng rọc. Thay đổi khối lượng xe M và quả nặng m, bấm 'Ghi số liệu' để vẽ đồ thị a theo F và a theo 1/(M+m). Gia tốc phụ thuộc thế nào vào lực và khối lượng?",
 kl:"Đồ thị a–F gần là đường thẳng qua gốc: a tỉ lệ thuận với lực F = mg (khi khối lượng hệ không đổi). Đồ thị a–1/(M+m) cũng là đường thẳng qua gốc: a tỉ lệ nghịch với khối lượng. Gộp lại: a = F/m_hệ, tức Định luật 2 Newton.",
 P:[["M","Khối lượng xe M (kg)",.2,2,.5,.05],["m","Quả nặng treo m (kg)",.02,.2,.05,.01]],
 btn:[["Ghi số liệu",(S,P)=>{const a=N(P.m*g/(P.M+P.m));SIMS[8].rec.push([P.m*g,a,1/(P.M+P.m),P.M,P.m])}],["Xoá bảng",()=>{SIMS[8].rec.length=0}]],
 init(S){S.x=0;S.v=0},
 step(S,P,dt){const a=P.m*g/(P.M+P.m);S.v+=a*dt;S.x+=S.v*dt;if(S.x>=1.2)S.fin=true},
 draw(S,P){const r=SIMS[8].rec;R(30,100,470,4,col("--c"));R(30+S.x*330,70,60,30,col("--m"));T(`M=${F(P.M,2)} kg`,36+S.x*330,88,11,"#fff");L(500,100,500,70,2);O(500,70,10,col("--v"));
  const ym=Math.min(250,100+(S.x/1.2)*60);L(490+0,70,90+S.x*330,70,1,col("--c"));L(510,70,510,ym,1);O(510,ym+10,8+P.m*40,col("--o"));T(`m=${F(P.m,2)} kg`,520,ym+14,11);
  const s1=r.map(p=>[p[0],p[1]]).sort((a,b)=>a[0]-b[0]),s2=r.map(p=>[p[2],p[1]]).sort((a,b)=>a[0]-b[0]);GR(20,150,330,190,s1,"F (N)","a (m/s²)");GR(370,150,330,190,s2,"1/(M+m) (1/kg)","a (m/s²)")},
 info(S,P){const r=SIMS[8].rec;return `Quãng đường xe đã đi: ${F(S.x,2)} m;  vận tốc: ${F(S.v,2)} m/s`+tab(["F (N)","a (m/s²)","1/(M+m)"],r.map(p=>[F(p[0],3),F(p[1],3),F(p[2],3)]))}});

SIMS.push({id:"k10",ten:"Khảo sát Định luật 3 Newton",ch:"III",
 vd:"Hai lực kế móc vào nhau, một lực kế bị kéo: số chỉ hai lực kế thế nào? Rồi hai xe nén lò xo ở giữa, đốt sợi chỉ: hai xe chuyển động ra sao khi khối lượng khác nhau?",
 kl:"Lực kế A kéo lực kế B bao nhiêu thì B kéo lại A bấy nhiêu: hai lực trực đối (F₁₂ = −F₂₁), cùng độ lớn, ngược hướng, đặt vào hai vật KHÁC nhau nên không triệt tiêu. Lò xo đẩy hai xe với hai lực bằng nhau nên xe nhẹ hơn thu gia tốc và vận tốc lớn hơn (m₁v₁ = m₂v₂ về độ lớn).",
 P:[["F","Lực kéo (N)",0,10,4,.5],["m1","Khối lượng xe 1 (kg)",.2,2,.5,.1],["m2","Khối lượng xe 2 (kg)",.2,2,1,.1]],static:false,
 btn:[["Đốt sợi chỉ",(S)=>{S.go=true;run=true;$("chay").textContent="⏸ Tạm dừng"}]],
 init(S){S.go=false;S.x1=0;S.x2=0;S.tg=0},
 step(S,P,dt){if(!S.go)return;S.tg+=dt;const u=2,v1=-u*P.m2/(P.m1+P.m2),v2=u*P.m1/(P.m1+P.m2);S.x1+=v1*dt;S.x2+=v2*dt;if(Math.abs(S.x1)>2.6||Math.abs(S.x2)>2.6)S.fin=true},
 draw(S,P){R(60,40,160,36,col("--v"),col("--c"));R(300,40,160,36,col("--v"),col("--c"));L(220,58,300,58,3);T(`A: ${F(P.F,1)} N`,100,63,15);T(`B: ${F(P.F,1)} N`,340,63,15);A(260,58,260+P.F*9,58,col("--gr"));A(260,58,260-P.F*9,58,col("--r"));T("lực A kéo B",262,100,12,col("--gr"));T("lực B kéo A",170,100,12,col("--r"));L(220,58,60,58,3);T("→ kéo",470,63,12);
  ground();const k=100,x1=300+S.x1*k,x2=420+S.x2*k;R(x1-60,GND-40,60,28,col("--m"));R(x2,GND-40,60,28,col("--o"));O(x1-45,GND-9,7,col("--c"));O(x1-15,GND-9,7,col("--c"));O(x2+15,GND-9,7,col("--c"));O(x2+45,GND-9,7,col("--c"));T(`m₁=${F(P.m1,1)}`,x1-50,GND-22,11,"#fff");T(`m₂=${F(P.m2,1)}`,x2+8,GND-22,11,"#fff");
  if(!S.go){L(x1,GND-26,x2,GND-26,3,col("--r"));T("lò xo nén, buộc chỉ",330,GND-50,12)}else if(S.tg<.6){A(x1-60,GND-60,x1-110,GND-60,col("--r"));A(x2+60,GND-60,x2+110,GND-60,col("--gr"));T("hai lực bằng nhau",300,GND-80,12)}},
 info(S,P){const u=2,v1=-u*P.m2/(P.m1+P.m2),v2=u*P.m1/(P.m1+P.m2);return `Hai lực kế: ${F(P.F,1)} N và ${F(P.F,1)} N (bằng nhau)`+(S.go?`\nSau khi đứt chỉ: v₁ = ${F(v1,2)} m/s, v₂ = ${F(v2,2)} m/s;  tỉ số |v₁|/|v₂| = ${F(Math.abs(v1/v2),2)}`:"")}});

(()=>{const V=[[0,0],[200,15],[235,95],[140,115],[115,205],[15,170]];let a=0,gx=0,gy=0;for(let i=0;i<6;i++){const p=V[i],q=V[(i+1)%6],w=p[0]*q[1]-q[0]*p[1];a+=w;gx+=(p[0]+q[0])*w;gy+=(p[1]+q[1])*w}a/=2;const G=[gx/(6*a),gy/(6*a)];
 const inside=b=>{let o=false;for(let i=0,j=5;i<6;j=i++){if((V[i][1]>b[1])!=(V[j][1]>b[1])&&b[0]<(V[j][0]-V[i][0])*(b[1]-V[i][1])/(V[j][1]-V[i][1])+V[i][0])o=!o}return o};
 const tr=(S,b)=>{const cs=Math.cos(S.phi),sn=Math.sin(S.phi),dx=b[0]-S.P[0],dy=b[1]-S.P[1];return[S.ps[0]+cs*dx-sn*dy,S.ps[1]+sn*dx+cs*dy]};
 SIMS.push({id:"k11",ten:"Xác định trọng tâm vật phẳng mỏng",ch:"III",static:true,
 vd:"Một tấm phẳng mỏng không đối xứng. Bấm vào tấm để treo nó ở một điểm: dây dọi chỉ ra đường thẳng đứng đi qua trọng tâm. Treo ở hai điểm khác nhau, giao của hai đường là trọng tâm G. Sau đó thử đỡ tấm bằng ngón tay.",
 kl:"Khi treo ở điểm bất kì và cân bằng, trọng tâm nằm trên đường thẳng đứng qua điểm treo. Hai điểm treo khác nhau cho hai đường cắt nhau tại trọng tâm G. Đỡ ngón tay đúng tại G thì tấm nằm cân bằng, đỡ chỗ khác thì tấm quay.",
 btn:[["Thử đỡ bằng ngón tay",(S)=>{S.finger=true;S.msg="Bấm vào điểm em muốn đỡ tấm."}]],
 init(S){S.P=[0,0];S.ps=[200,60];S.phi=0;S.tphi=0;S.lines=[];S.finger=false;S.msg="Bấm vào tấm để treo nó tại điểm đó."},
 click(S,P,x,y){const dx=x-S.ps[0],dy=y-S.ps[1],cs=Math.cos(S.phi),sn=Math.sin(S.phi),b=[S.P[0]+cs*dx+sn*dy,S.P[1]-sn*dx+cs*dy];
  if(S.finger){const d=Math.hypot(b[0]-G[0],b[1]-G[1]);S.finger=false;S.msg=d<14?"Tấm nằm cân bằng: đây đúng là trọng tâm G.":"Tấm bị xoay: điểm đỡ chưa phải trọng tâm (cách G khoảng "+F(d/10,1)+" cm).";if(d>=14){S.tphi=S.phi+(b[0]<G[0]?-.5:.5)}return}
  if(!inside(b))return;S.P=b;S.ps=[420,40];S.tphi=Math.PI/2-Math.atan2(G[1]-b[1],G[0]-b[0]);S.lines.push(b);S.msg=S.lines.length<2?"Đường dọi thứ nhất đã vẽ. Hãy treo tấm ở một điểm khác.":"Hai đường dọi cắt nhau tại trọng tâm G."},
 draw(S){S.phi+=(S.tphi-S.phi)*.18;POLY(V.map(v=>tr(S,v)),"rgba(74,163,232,.35)");S.lines.forEach(p=>{const d=[G[0]-p[0],G[1]-p[1]],l=Math.hypot(...d),u=[d[0]/l,d[1]/l];const a=tr(S,[p[0]-u[0]*30,p[1]-u[1]*30]),b=tr(S,[p[0]+u[0]*300,p[1]+u[1]*300]);L(a[0],a[1],b[0],b[1],1.5,col("--r"));const q=tr(S,p);O(q[0],q[1],4,col("--r"))});
  if(S.lines.length>=2){const g2=tr(S,G);O(g2[0],g2[1],6,col("--gr"));T("G",g2[0]+8,g2[1]-6,14,col("--gr"))}T(S.msg,20,H-14,13)},
 info(S){return `Số điểm treo đã dùng: ${S.lines.length}`+(S.lines.length>=2?"\nTrọng tâm G nằm ở giao điểm hai đường dọi.":"")}})})();

SIMS.push({id:"k12",ten:"Khảo sát lực ma sát trượt",ch:"III",rec:[],
 vd:"Kéo khối gỗ đều trên các bề mặt gỗ, giấy, nỉ và chồng thêm quả nặng. Lực kế điện tử cho biết lực ma sát trượt. Nó phụ thuộc vào những yếu tố nào: vật liệu, áp lực, diện tích tiếp xúc? Ghi số liệu và so sánh.",
 kl:"Lực ma sát trượt phụ thuộc vật liệu hai bề mặt (nỉ > gỗ > giấy trong mô hình này) và tỉ lệ thuận với áp lực N (đồ thị F–N là đường thẳng qua gốc), nhưng không phụ thuộc diện tích tiếp xúc: F = μN. Hệ số ma sát μ chỉ phụ thuộc cặp bề mặt tiếp xúc.",
 P:[["bm","Khối lượng chồng thêm (kg)",0,1,0,.1],["sf","Bề mặt (0 = gỗ, 1 = giấy, 2 = nỉ)",0,2,0,1],["dt","Cách đặt khối (0 = nằm, 1 = dựng đứng: diện tích nhỏ hơn)",0,1,0,1]],
 btn:[["Ghi số liệu",(S,P)=>{SIMS[11].rec.push([P.sf,(.5+P.bm)*g,P.dt?"nhỏ":"lớn",S.Fm])}],["Xoá bảng",()=>{SIMS[11].rec.length=0}]],
 init(S,P){S.x=0;S.k=0;S.Fm=N([.3,.2,.5][P.sf]*(.5+P.bm)*g)},
 step(S,P,dt){S.x=(S.x+90*dt)%500;S.k+=dt;if(S.k>.6){S.k=0;S.Fm=N([.3,.2,.5][P.sf]*(.5+P.bm)*g)}},
 draw(S,P){const cl=[col("--o"),"#e8d37a",col("--gr")],n=["gỗ","giấy","nỉ"];R(20,150,680,12,cl[P.sf]);T("bề mặt: "+n[P.sf],24,178,12);const w=P.dt?26:64,h=P.dt?64:26,x=60+S.x;R(x,150-h,w,h,col("--m"),col("--c"));L(x+w,150-h/2,x+w+60,150-h/2,2,col("--c"));R(x+w+60,150-h/2-14,70,28,col("--n"),col("--c"));T(F(S.Fm,2)+" N",x+w+64,150-h/2+5,13);
  const r=SIMS[11].rec,ser=[0,1,2].map(i=>({c:cl[i],p:r.filter(q=>q[0]==i).map(q=>[q[1],q[3]]).sort((a,b)=>a[0]-b[0])}));GR2(20,195,680,150,ser,"N (N)","F_mst (N) — cam: gỗ, vàng: giấy, xanh: nỉ")},
 info(S,P){return `Áp lực N = ${F((.5+P.bm)*g,2)} N;  lực kế chỉ ${F(S.Fm,2)} N`+tab(["bề mặt (0 gỗ,1 giấy,2 nỉ)","N (N)","diện tích","F (N)"],SIMS[11].rec.map(r=>[r[0],F(r[1],2),r[2],F(r[3],2)]))}});

SIMS.push({id:"k13",ten:"Quy tắc moment lực (đòn bẩy)",ch:"III",static:true,
 vd:"Một đòn bẩy có trục quay ở giữa, các lỗ cách đều 5 cm. Treo các quả cân (mỗi quả 50 g) ở hai phía rồi thay đổi số quả và vị trí. Khi nào đòn bẩy cân bằng?",
 kl:"Đòn bẩy cân bằng khi tổng moment làm quay theo chiều kim đồng hồ bằng tổng moment ngược chiều: F₁·d₁ = F₂·d₂ (moment M = F·d, d là cánh tay đòn, khoảng cách từ trục đến giá của lực). Bên nào có moment lớn hơn thì bên đó chìm xuống.",
 P:[["m1","Số quả cân bên trái",1,5,2,1],["d1","Lỗ bên trái (cách trục d×5 cm)",1,5,3,1],["m2","Số quả cân bên phải",1,5,3,1],["d2","Lỗ bên phải (cách trục d×5 cm)",1,5,2,1]],
 init(S){S.th=0},
 draw(S,P){const M1=P.m1*.49*P.d1*.05,M2=P.m2*.49*P.d2*.05,tg=Math.max(-18,Math.min(18,(M1-M2)*60));S.th+=(tg-S.th)*.1;const th=S.th*D,cx=360,cy=200,u=55;POLY([[cx-18,cy+90],[cx+18,cy+90],[cx,cy]],col("--v"));
  const pt=k=>[cx+k*u*Math.cos(th),cy+k*u*Math.sin(th)];const a=pt(-5.6),b=pt(5.6);L(a[0],a[1],b[0],b[1],8,col("--o"));for(let k=-5;k<=5;k++){const p=pt(k);O(p[0],p[1],2.5,col("--c"),0)}
  [[-P.d1,P.m1],[P.d2,P.m2]].forEach(([k,n])=>{const p=pt(k);for(let i=0;i<n;i++){R(p[0]-12,p[1]+6+i*13,24,12,col("--m"),col("--c"))}L(p[0],p[1],p[0],p[1]+6,1)});O(cx,cy,5,col("--c"))},
 info(S,P){const M1=P.m1*.49*P.d1*.05,M2=P.m2*.49*P.d2*.05;return `Moment trái = ${F(P.m1*.49,2)} N × ${F(P.d1*5,0)} cm = ${F(M1*100,2)} N·cm\nMoment phải = ${F(P.m2*.49,2)} N × ${F(P.d2*5,0)} cm = ${F(M2*100,2)} N·cm\n`+(Math.abs(M1-M2)<1e-9?"→ Cân bằng (F₁d₁ = F₂d₂)":M1>M2?"→ Quay về bên trái (moment trái lớn hơn)":"→ Quay về bên phải (moment phải lớn hơn)")}});

SIMS.push({id:"k14",ten:"Khảo sát lực hướng tâm",ch:"III",
 vd:"Quay đều một vật nặng buộc vào dây trên mặt phẳng ngang. Lực căng dây đóng vai trò gì? Tăng tốc độ quay ω rồi bấm 'Cắt dây': vật bay đi theo hướng nào?",
 kl:"Lực căng dây hướng vào tâm quỹ đạo, đóng vai trò lực hướng tâm: F_ht = mω²r = mv²/r (tăng theo ω², r và m). Khi dây đứt không còn lực hướng tâm, vật bay đi thẳng theo phương tiếp tuyến với quỹ đạo tại điểm đứt (quán tính).",
 P:[["r","Bán kính quỹ đạo r (m)",.3,1,.6,.05],["w","Tốc độ góc ω (rad/s)",1,12,5,.5],["m","Khối lượng vật m (kg)",.05,.5,.2,.05]],
 btn:[["Cắt dây",(S,P)=>{if(S.cut)return;S.cut=true;S.vx=-Math.sin(S.a)*P.w*P.r;S.vy=Math.cos(S.a)*P.w*P.r;S.px=P.r*Math.cos(S.a);S.py=P.r*Math.sin(S.a);run=true;$("chay").textContent="⏸ Tạm dừng"}]],
 init(S){S.a=0;S.cut=false},
 step(S,P,dt){if(!S.cut)S.a+=P.w*dt;else{S.px+=S.vx*dt;S.py+=S.vy*dt;if(Math.abs(S.px)>1.8||Math.abs(S.py)>.9)S.fin=true}},
 draw(S,P){const cx=360,cy=180,s=140,x=S.cut?cx+S.px*s:cx+P.r*s*Math.cos(S.a),y=S.cut?cy+S.py*s:cy+P.r*s*Math.sin(S.a);c.setLineDash([3,5]);c.beginPath();c.arc(cx,cy,P.r*s,0,7);c.strokeStyle=col("--v");c.stroke();c.setLineDash([]);O(cx,cy,4,col("--c"));
  if(!S.cut){L(cx,cy,x,y,2);const T0=P.m*P.w*P.w*P.r,q=Math.min(90,T0*8);A(x,y,x+(cx-x)/(P.r*s)*q,y+(cy-y)/(P.r*s)*q,col("--r"));T("lực căng = lực hướng tâm",x+10,y-12,12,col("--r"))}else{A(x,y,x+S.vx*10,y+S.vy*10,col("--gr"));T("bay theo tiếp tuyến",x+10,y-12,12,col("--gr"))}O(x,y,10+P.m*20,col("--m"))},
 info(S,P){return `Lực căng dây = F_ht = mω²r = ${F(P.m*P.w*P.w*P.r,2)} N;  tốc độ dài v = ωr = ${F(P.w*P.r,2)} m/s`}});

SIMS.push({id:"k15",ten:"Thí nghiệm Joule",ch:"IV",
 vd:"Vật nặng rơi xuống làm quay cánh khuấy trong bình cách nhiệt chứa nước. Thả nhiều lần và quan sát nhiệt kế. Công của trọng lực (mgh) và nhiệt lượng nước nhận được (mcΔt) liên hệ thế nào?",
 kl:"Cơ năng của vật nặng giảm đi (công A = n·mgh) chuyển hoá thành nhiệt làm nước nóng lên: Q = m_nước·c·Δt. Hai giá trị gần bằng nhau (sai lệch do sai số đo, cách nhiệt chưa hoàn hảo), thể hiện sự bảo toàn năng lượng; 1 cal ≈ 4,19 J.",
 P:[["m","Khối lượng vật nặng (kg)",1,20,10,1],["M","Khối lượng nước (kg)",.2,1,.5,.05]],
 init(S){S.y=0;S.n=0;S.dT=0},
 step(S,P,dt){S.y+=dt/1.2;if(S.y>=1){S.y=0;S.n++;S.dT+=P.m*g*2/(P.M*4186);if(S.n>=20)S.fin=true}},
 draw(S,P){R(60,20,6,300,col("--c"));const y=40+S.y*200;L(130,30,130,y,1.5);R(110,y,40,30,col("--m"));T(`${P.m} kg`,112,y+20,12,"#fff");L(130,30,300,30,1.5);R(300,150,150,170,"rgba(74,163,232,.4)",col("--c"));L(375,60,375,230,3);
  for(let i=0;i<3;i++)L(375,200+i*8,375+(i%2?30:-30)*Math.cos(S.n*3+S.y*10),210+i*8,3,col("--o"));R(500,60,24,260,col("--n"),col("--c"));const h=Math.min(240,S.dT/10*240);R(502,318-h,20,h,col("--r"));T(`${F(20+N(S.dT),2)} °C`,470,52,13)},
 info(S,P){const A_=S.n*P.m*g*2,Q=P.M*4186*N(S.dT);return `Số lần thả: ${S.n} (mỗi lần rơi 2 m)\nCông cơ học A = n·mgh = ${F(A_,0)} J;   nhiệt lượng Q = m·c·Δt = ${F(Q,0)} J  (c = 4186 J/kg·K)\nΔt = ${F(S.dT,3)} K`}});

SIMS.push({id:"k16",ten:"Chuyển hoá động năng – thế năng",ch:"IV",
 vd:"Con lắc đơn dao động. Quan sát biểu đồ cột động năng, thế năng và cơ năng theo thời gian thực. Cơ năng có đổi không? Thử thêm ma sát (lực cản) để xem điều gì xảy ra.",
 kl:"Khi con lắc đi xuống, thế năng giảm và động năng tăng; ở vị trí thấp nhất động năng cực đại; lên cao thì ngược lại. Tổng W = Wđ + Wt (cơ năng) không đổi khi bỏ qua ma sát. Có lực cản, cơ năng giảm dần vì chuyển hoá thành nhiệt.",
 P:[["L","Chiều dài dây (m)",.5,2,1,.1],["a0","Góc lệch ban đầu (độ)",5,80,40,1],["k","Lực cản (hệ số)",0,.5,0,.02]],
 init(S,P){S.th=P.a0*D;S.om=0;S.W0=g*P.L*(1-Math.cos(S.th))},
 step(S,P,dt){const al=-g/P.L*Math.sin(S.th)-P.k*S.om;S.om+=al*dt;S.th+=S.om*dt},
 draw(S,P){const px=200,py=40,s=120,x=px+P.L*s*Math.sin(S.th),y=py+P.L*s*Math.cos(S.th);L(px-40,py,px+40,py,4);L(px,py,x,y,2);O(x,y,12,col("--m"));
  const wd=.5*Math.pow(P.L*S.om,2),wt=g*P.L*(1-Math.cos(S.th)),mx=Math.max(S.W0,wd+wt,.01),bars=[["Wđ",wd,col("--r")],["Wt",wt,col("--gr")],["W",wd+wt,col("--m")]];
  bars.forEach((b,i)=>{const h=Math.min(260,260*b[1]/mx),x0=430+i*90;R(x0,320-h,60,h,b[2]);T(b[0],x0+16,338,14);T(F(b[1],2)+" J",x0+4,314-h,12)})},
 info(S,P){const wd=.5*Math.pow(P.L*S.om,2),wt=g*P.L*(1-Math.cos(S.th));return `(vật nặng 1 kg)  Wđ = ${F(wd,3)} J;  Wt = ${F(wt,3)} J;  W = ${F(wd+wt,3)} J  (ban đầu ${F(S.W0,3)} J)`}});
SIMS.push({id:"k17",ten:"Truyền chuyển động và con lắc Newton",ch:"V",
 vd:"Năm quả cầu kim loại treo sát nhau. Nâng một số quả ở một đầu rồi thả. Điều gì xảy ra ở đầu bên kia? Thử nâng 1, 2, 3, 4 quả.",
 kl:"Nâng n quả và thả, đúng n quả ở đầu kia bật lên với cùng độ cao, các quả ở giữa gần như đứng yên. Đó là va chạm đàn hồi xuyên tâm liên tiếp: động lượng và động năng đều được bảo toàn, nên xung lượng được truyền hoàn hảo qua dãy bi (số quả bật lên bằng số quả thả).",
 P:[["n","Số quả được nâng",1,4,1,1]],
 init(S){S.ph=0},
 step(S,P,dt){S.ph+=2.2*dt},
 draw(S,P){const th=-35*D*Math.cos(S.ph),px=360,py=30,l=200;L(150,py,570,py,4);for(let i=0;i<5;i++){const mv=th<0?i<P.n:i>=5-P.n,a=mv?th:0,x0=px+(i-2)*38,x=x0+l*Math.sin(a),y=py+l*Math.cos(a);L(x0,py,x,y,1);O(x,y,19,mv?col("--r"):col("--m"))}},
 info(S,P){const th=-35*Math.cos(S.ph);return `Số quả đang chuyển động: ${P.n} (${th<0?"đầu trái":"đầu phải"});  góc lệch ${F(Math.abs(th),0)}°\nSố quả bật lên ở đầu kia = số quả thả = ${P.n}`}});

SIMS.push({id:"k18",ten:"Chuyển động tròn đều và gia tốc hướng tâm",ch:"VI",
 vd:"Một vật chuyển động tròn đều. Xác định chu kì T, tần số f, tốc độ góc ω, tốc độ dài v, và quan sát vectơ gia tốc. Vectơ vận tốc và vectơ gia tốc luôn hướng thế nào?",
 kl:"T là thời gian đi một vòng, f = 1/T, ω = 2π/T, v = ωr. Độ lớn vận tốc không đổi nhưng hướng luôn đổi (tiếp tuyến) nên có gia tốc: gia tốc hướng tâm a_ht = v²/r = ω²r, luôn hướng vào tâm, vuông góc với vận tốc.",
 P:[["r","Bán kính r (m)",.2,2,1,.1],["T","Chu kì T (s)",.5,6,3,.1]],
 init(S){S.a=0},
 step(S,P,dt){S.a+=2*Math.PI/P.T*dt},
 draw(S,P){const cx=260,cy=180,s=80,w=2*Math.PI/P.T,v=w*P.r,x=cx+P.r*s*Math.cos(S.a),y=cy+P.r*s*Math.sin(S.a);O(cx,cy,P.r*s,null);O(cx,cy,3,col("--c"));L(cx,cy,x,y,1,col("--v"));
  A(x,y,x-Math.sin(S.a)*Math.min(70,v*8),y+Math.cos(S.a)*Math.min(70,v*8),col("--gr"));const q=Math.min(80,w*w*P.r*4);A(x,y,x-Math.cos(S.a)*q,y-Math.sin(S.a)*q,col("--r"));O(x,y,9,col("--m"));T("v (tiếp tuyến)",x+12,y+18,12,col("--gr"));T("a_ht (vào tâm)",x+12,y-10,12,col("--r"))},
 info(S,P){const w=2*Math.PI/P.T;return `T = ${F(P.T,2)} s;  f = ${F(1/P.T,3)} Hz;  ω = ${F(w,3)} rad/s\nv = ωr = ${F(w*P.r,3)} m/s;  a_ht = ω²r = ${F(w*w*P.r,3)} m/s²`}});

SIMS.push({id:"k19",ten:"Hiện tượng chuyển động li tâm",ch:"VI",
 vd:"Đặt vật trên bàn quay và tăng dần tốc độ góc. Đến khi nào vật trượt ra ngoài? Thay đổi vị trí đặt vật và hệ số ma sát nghỉ rồi tìm ngưỡng ω.",
 kl:"Khi bàn quay, lực ma sát nghỉ đóng vai trò lực hướng tâm: F_ms = mω²r. Lực này có giá trị tối đa μ_n·mg nên vật trượt khi ω² r > μ_n g, tức ω > √(μ_n g/r). Vật đặt càng xa tâm hoặc ma sát càng nhỏ thì càng dễ văng; vật bay đi theo phương tiếp tuyến chứ không phải 'bị đẩy ra' bởi một lực li tâm thật.",
 P:[["r","Khoảng cách tới tâm r (m)",.1,.5,.3,.01],["mu","Hệ số ma sát nghỉ μ",.1,.8,.4,.05]],
 init(S,P){S.w=0;S.a=0;S.slip=false;S.wth=null;S.px=P.r;S.py=0},
 step(S,P,dt){S.w+=.5*dt;S.a+=S.w*dt;if(!S.slip){S.px=P.r*Math.cos(S.a);S.py=P.r*Math.sin(S.a);if(S.w*S.w*P.r>P.mu*g){S.slip=true;S.wth=S.w;S.vx=-Math.sin(S.a)*S.w*P.r;S.vy=Math.cos(S.a)*S.w*P.r}}else{S.px+=S.vx*dt;S.py+=S.vy*dt;if(Math.hypot(S.px,S.py)>1.1)S.fin=true}},
 draw(S,P){const cx=360,cy=180,s=250;O(cx,cy,.6*s,"rgba(232,148,58,.25)");for(let k=0;k<8;k++){const a=S.a+k*Math.PI/4;L(cx,cy,cx+.6*s*Math.cos(a),cy+.6*s*Math.sin(a),.5,col("--v"))}O(cx,cy,3,col("--c"));
  O(cx+S.px*s,cy+S.py*s,9,S.slip?col("--r"):col("--m"));if(!S.slip)A(cx+S.px*s,cy+S.py*s,cx+S.px*s*.6,cy+S.py*s*.6,col("--r"));else T("trượt, bay theo tiếp tuyến",cx+S.px*s+12,cy+S.py*s,12,col("--r"))},
 info(S,P){return `ω hiện tại = ${F(S.w,2)} rad/s`+(S.slip?`\nVật bắt đầu trượt tại ω ≈ ${F(S.wth,2)} rad/s;  công thức √(μg/r) = ${F(Math.sqrt(P.mu*g/P.r),2)} rad/s`:`\nMa sát nghỉ cần để giữ vật: m·ω²r = ${F(S.w*S.w*P.r,2)} (đơn vị m·N/kg) so với tối đa μg = ${F(P.mu*g,2)}`)}});

SIMS.push({id:"k20",ten:"Khảo sát Định luật Hooke",ch:"VII",
 vd:"Treo lò xo thẳng đứng và thêm dần từng quả cân 50 g. Đo độ dãn Δl, vẽ đồ thị lực đàn hồi theo độ dãn và tính độ cứng k. Chọn hai lò xo khác nhau và thử vượt quá giới hạn đàn hồi.",
 kl:"Trong giới hạn đàn hồi, lực đàn hồi tỉ lệ thuận với độ dãn: F = kΔl; đồ thị F–Δl là đường thẳng qua gốc, hệ số góc là độ cứng k = ΔF/Δl. Lò xo cứng hơn (k lớn) dãn ít hơn với cùng lực. Vượt giới hạn đàn hồi, đồ thị cong lên và lò xo không về lại chiều dài ban đầu.",
 P:[["sp","Lò xo (0 = A, 1 = B)",0,1,0,1]],
 btn:[["+ 1 quả cân (50 g)",(S,P)=>{if(S.n<8){S.n++;const k=P.sp?80:40,F_=S.n*.49;S.rd[S.n]=N(F_<=3.5?F_/k:F_/k*1.5)}}],["− 1 quả cân",(S)=>{if(S.n>0)S.n--}]],
 init(S){S.n=0;S.rd={0:0}},
 draw(S,P){const k=P.sp?80:40,F_=S.n*.49,dl=S.rd[S.n]||0,x=120;L(60,30,180,30,5);let y=30;const len=100+dl*800;for(let i=0;i<12;i++){const y2=30+len*(i+1)/12;L(x+(i%2?-14:14),y+ (i?0:0),x+(i%2?14:-14),y2,2,col("--m"));y=y2}
  L(x,y,x,y+10,2);for(let i=0;i<S.n;i++)R(x-16,y+10+i*14,32,13,col("--o"),col("--c"));T(`Δl = ${F(dl*100,1)} cm`,170,60+len/2,13);
  const pts=[];for(let i=1;i<=S.n;i++)pts.push([S.rd[i]*100,i*.49]);const kk=pts.length?pts.reduce((a,p)=>a+p[1]*p[0]/100,0)/pts.reduce((a,p)=>a+Math.pow(p[0]/100,2),0):0;GR(300,40,390,290,pts,"Δl (cm)","F (N)",kk/100);if(S.n>=7)T("gần giới hạn đàn hồi",330,350,12,col("--r"))},
 info(S,P){const rows=[];let a=0,b=0;for(let i=1;i<=S.n;i++){rows.push([i*50,F(i*.49,2),F(S.rd[i]*100,1)]);if(i<=7){a+=i*.49*S.rd[i];b+=S.rd[i]*S.rd[i]}}return (b?`Độ cứng ước lượng từ số liệu: k ≈ ${F(a/b,1)} N/m`:"Thêm quả cân để bắt đầu đo.")+tab(["m (g)","F (N)","Δl (cm)"],rows)}});

SIMS.push({id:"k21",ten:"Sự tồn tại áp suất chất lỏng",ch:"VII",static:true,
 vd:"Bình trụ chứa nước có các lỗ thủng ở thành bình. Ấn pít-tông ở phía trên: nước phun ra theo hướng nào? Tăng lực ấn và quan sát các mũi tên áp lực.",
 kl:"Chất lỏng gây áp suất lên mọi điểm của thành bình và đáy bình, theo phương vuông góc với thành. Ấn pít-tông làm tăng áp suất và áp suất này được truyền nguyên vẹn tới mọi điểm của chất lỏng (nguyên lí Pascal): nước phun mạnh hơn, và ở lỗ sâu hơn (áp suất lớn hơn) nước phun xa hơn.",
 P:[["F","Lực ấn pít-tông (N)",0,100,30,5]],
 draw(S,P){const x0=300,x1=420,y0=60+Math.min(P.F,100)*.1,yb=300;R(x0,y0,x1-x0,yb-y0,"rgba(74,163,232,.35)");L(x0,60,x0,yb,4);L(x1,60,x1,yb,4);L(x0,yb,x1,yb,4);R(x0+2,y0-10,x1-x0-4,10,col("--o"),col("--c"));A(360,y0-60,360,y0-12,col("--r"));T(`F = ${F(P.F,0)} N`,372,y0-36,13,col("--r"));ground();
  [110,170,230].forEach(h=>{const y=h+60,d=(y-y0)/200,p=P.F/.01+1000*g*Math.max(d,0),v=Math.sqrt(2*p/1000);[-1,1].forEach(sd=>{const xs=sd<0?x0:x1;O(xs,y,3,col("--c"));A(xs,y,xs+sd*Math.min(50,p/400),y,col("--r"));c.beginPath();c.moveTo(xs,y);for(let t=0;t<1;t+=.02){const yy=y+.5*g*t*t*200;if(yy>GND)break;c.lineTo(xs+sd*v*t*100,yy)}c.strokeStyle=col("--w");c.lineWidth=2;c.stroke()})})},
 info(S,P){return [110,170,230].map((h,i)=>`Lỗ ${i+1} (sâu ${F((h+60-(60+Math.min(P.F,100)*.1))/200,2)} m): p = F/S + ρgh ≈ ${F((P.F/.01+1000*g*Math.max((h+60-(60+Math.min(P.F,100)*.1))/200,0))/1000,1)} kPa`).join("\n")}});

SIMS.push({id:"k22",ten:"Áp suất thuỷ tĩnh theo độ sâu (p = ρ·g·h)",ch:"VII",
 vd:"Một ống thuỷ tinh có đĩa nhựa đậy đáy, nhúng vào chất lỏng ở độ sâu h. Rót dần nước vào ống: đĩa rời ra khi mực nước trong ống đạt bao nhiêu? Thay độ sâu và chất lỏng rồi so sánh.",
 kl:"Chất lỏng ở độ sâu h gây áp suất p = ρgh lên đĩa từ phía dưới đẩy đĩa ép vào miệng ống. Đĩa rời ra khi áp suất do cột nước trong ống (ρ_nước·g·H) bằng áp suất của chất lỏng ngoài (ρ·g·h). Với nước: H ≈ h; với chất lỏng đặc hơn, H lớn hơn h. Áp suất tăng tỉ lệ thuận với độ sâu.",
 P:[["h","Độ sâu của đĩa h (cm)",5,60,30,1],["ld","Chất lỏng (0 = nước, 1 = nước muối, 2 = dầu)",0,2,0,1]],
 btn:[["Rót nước vào ống",(S)=>{S.pour=true;run=true;$("chay").textContent="⏸ Tạm dừng"}]],
 init(S){S.H=0;S.pour=false;S.fell=false;S.Hf=null},
 step(S,P,dt){if(!S.pour||S.fell)return;S.H+=6*dt;const rho=[1000,1200,800][P.ld];if(S.H*1000>=rho*P.h){S.fell=true;S.Hf=S.H;S.fin=true}},
 draw(S,P){const rho=[1000,1200,800][P.ld],s=5,top=30;R(350,100,300,GND-100,["rgba(74,163,232,.3)","rgba(120,200,160,.35)","rgba(232,200,80,.35)"][P.ld]);L(350,100,350,GND,3);L(650,100,650,GND,3);L(350,GND,650,GND,3);
  const yb=100+P.h*s;R(488,top,4,yb-top,col("--c"));R(512,top,4,yb-top,col("--c"));if(S.H>0)R(492,yb-S.H*s,20,S.H*s,col("--w"));if(!S.fell)R(486,yb,32,5,col("--o"),col("--c"));else{R(486,GND-8,32,5,col("--o"),col("--c"));R(492,yb-S.H*s,20,S.H*s+5,col("--w"))}
  A(502,yb+30,502,yb+8,col("--r"));T(`p = ρgh = ${F(rho*g*P.h/100/1000,2)} kPa`,170,yb+4,13);L(350,100,330,100,1);T("mặt thoáng",270,104,12);L(335,100,335,yb,1,col("--r"));T(`h = ${P.h} cm`,280,(100+yb)/2,12,col("--r"))},
 info(S,P){const rho=[1000,1200,800][P.ld];return `Mực nước trong ống: H = ${F(S.H,1)} cm`+(S.fell?`\nĐĩa rời ra khi H ≈ ${F(S.Hf,1)} cm;  so với h = ${P.h} cm và tỉ lệ ρ_chất lỏng/ρ_nước = ${F(rho/1000,2)}`:"")}});

SIMS.push({id:"k23",ten:"Thùng gỗ Pascal",ch:"VII",
 vd:"Một thùng gỗ kín chứa đầy nước, cắm vào nắp một ống nhỏ cao 10 m. Chỉ cần đổ một lượng nước rất ít vào ống: điều gì xảy ra với thùng? Quan sát áp suất tại đáy ống theo chiều cao cột nước.",
 kl:"Áp suất chất lỏng chỉ phụ thuộc độ sâu (chiều cao cột nước), không phụ thuộc lượng nước hay hình dạng bình: p = ρgH. Ống rất cao dù chứa ít nước vẫn tạo áp suất lớn lên nắp và thành thùng (F = p·S), vượt giới hạn chịu đựng làm thùng vỡ — Pascal gọi là 'nghịch lí thuỷ tĩnh'.",
 P:[["A","Diện tích nắp thùng (cm²)",200,1000,500,50]],
 btn:[["Đổ nước vào ống cao",(S)=>{S.pour=true;run=true;$("chay").textContent="⏸ Tạm dừng"}]],
 init(S){S.H=0;S.pour=false;S.burst=false;S.bt=0},
 step(S,P,dt){if(S.burst){S.bt+=dt;if(S.bt>2)S.fin=true;return}if(!S.pour)return;S.H=Math.min(10,S.H+.8*dt);if(1000*g*S.H>=9e4){S.burst=true}},
 draw(S,P){const s=20,by=GND-110,sp=S.burst?Math.min(30,S.bt*60):0;R(158,by-210,6,210,col("--n"),col("--c"));R(159,by-S.H*s,4,S.H*s,col("--w"));for(let m=0;m<=10;m+=2){L(150,by-m*s,158,by-m*s,1);T(`${m} m`,118,by-m*s+4,11)}
  R(100-sp,by,140+sp*0,110,"rgba(74,163,232,.5)",col("--c"));if(S.burst){R(160+sp,by,80,110,"rgba(74,163,232,.5)",col("--c"));for(let i=0;i<14;i++){const a=i*.45;L(160+sp/2,by+55,160+sp/2+Math.cos(a)*sp*2.5,by+55+Math.sin(a)*sp*2.5,2,col("--w"))}T("thùng vỡ!",260,by+50,18,col("--r"))}
  const p=1000*g*S.H;R(440,60,40,260,col("--n"),col("--c"));R(442,318-258*Math.min(1,p/9e4),36,258*Math.min(1,p/9e4),p>=8e4?col("--r"):col("--m"));T("áp suất",436,52,12);T("giới hạn",486,66,12,col("--r"))},
 info(S,P){const p=1000*g*S.H;return `Cột nước trong ống: H = ${F(S.H,2)} m  (lượng nước chỉ cỡ vài chục mL)\nÁp suất tại đáy: p = ρgH = ${F(p/1000,1)} kPa;  lực lên nắp F = p·S = ${F(p*P.A*1e-4,0)} N`}});
