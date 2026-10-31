const {feature}=require('topojson-client');const fs=require('fs');
const c=require('world-atlas/countries-50m.json'), l=require('world-atlas/land-50m.json');
const cs=feature(c,c.objects.countries).features.filter(f=>['Canada','Germany','India'].includes(f.properties.name));
fs.writeFileSync('geo.json',JSON.stringify({land:feature(l,l.objects.land),countries:cs}));
console.log(cs.map(f=>f.properties.name));
