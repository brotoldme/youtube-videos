import fs from 'fs';
import {geoPath,geoMercator} from 'd3-geo';
import {feature,mesh} from 'topojson-client';
import iso from 'i18n-iso-countries';
import {countries as CL} from 'countries-list';
const topo=JSON.parse(fs.readFileSync('node_modules/world-atlas/countries-50m.json'));
const fc=feature(topo,topo.objects.countries);
const W=1920,H=1080;
const proj=geoMercator().scale(W/(2*Math.PI)*1.0).translate([W/2,H*0.62]).precision(0.05);
const P=geoPath(proj).digits(2);
const PAL={AF:['#f2d16b','#f6e08f','#e7c25a'],AS:['#e89a7e','#f2b39b','#dc8a6d'],EU:['#d9a7c7','#e8c1d8','#c895b6'],NA:['#f6b26b','#f9c98d','#efa25a'],SA:['#b7c27a','#cfd59a','#a4b268'],OC:['#f7b6a0','#fbcab8','#f0a58c'],RU:['#e2a8a0','#e2a8a0','#e2a8a0'],CREAM:['#f8f1de','#f8f1de','#f8f1de'],ME:['#f2d16b','#f6e08f','#e7c25a']};
const ME=new Set(['SA','YE','OM','AE','QA','KW','BH','JO','IL','PS','LB']);
const byName={'Antarctica':'CREAM','Greenland':'CREAM','Kosovo':'EU'};
const cont={AF:'AF',AN:'CREAM',AS:'AS',EU:'EU',NA:'NA',OC:'OC',SA:'SA'};
function cls(f){const a2=f.id!==undefined?iso.numericToAlpha2(String(f.id).padStart(3,'0')):undefined;
 if(byName[f.properties.name])return byName[f.properties.name];if(a2==='RU')return 'RU';if(a2&&ME.has(a2))return 'ME';if(a2&&CL[a2])return cont[CL[a2].continent];return 'EU';}
const countries=[];let iran=null;
fc.features.forEach((f,i)=>{const d=P(f);if(!d)return;const g=cls(f);const col=PAL[g][i%3];
 if(f.properties.name==='Iran'){iran=d;}
 countries.push({d,col,iran:f.properties.name==='Iran'});});
const iranF=fc.features.find(x=>x.properties.name==='Iran');
const [[x0,y0],[x1,y1]]=P.bounds(iranF);
const tehran=proj([51.389,35.689]);
const borders=P(mesh(topo,topo.objects.countries,(a,b)=>a!==b));
fs.writeFileSync('data.json',JSON.stringify({countries,borders,bounds:[x0,y0,x1,y1],tehran}));
console.error('ok',x0,y0,x1,y1,tehran);
