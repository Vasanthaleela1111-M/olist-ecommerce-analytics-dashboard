const fs = require('fs');
const path = require('path');
const { JSDOM } = require('jsdom');

const htmlPath = path.join(__dirname, '../app/index.html');
const htmlContent = fs.readFileSync(htmlPath, 'utf8');

const dom = new JSDOM(htmlContent, { runScripts: "dangerously" });
const { document } = dom.window;

// 1. Verify DOM hierarchy of #view-geography
const viewGeo = document.getElementById('view-geography');
console.log("Checking #view-geography presence:", !!viewGeo);

if (viewGeo) {
  const parentId = viewGeo.parentElement ? viewGeo.parentElement.className : 'null';
  console.log("Parent element class of #view-geography:", parentId);
  
  const isNestedInDelivery = viewGeo.closest('#view-delivery') !== null;
  console.log("Is #view-geography nested inside #view-delivery?:", isNestedInDelivery);
  
  const chartCanvas = viewGeo.querySelector('#chartGeoScope');
  console.log("Canvas #chartGeoScope present in #view-geography:", !!chartCanvas);
  
  const tbody = viewGeo.querySelector('#tbodyGeoHotspots');
  console.log("Table body #tbodyGeoHotspots present in #view-geography:", !!tbody);
}

// 2. Load data.js and test app logic
const dataPath = path.join(__dirname, '../app/js/data.js');
const dataContent = fs.readFileSync(dataPath, 'utf8');
eval(dataContent); // Populates window.OLIST_DATA

console.log("\nTesting OLIST_DATA integration:");
console.log("q3_hotspots array size:", dom.window.OLIST_DATA.q3_hotspots ? dom.window.OLIST_DATA.q3_hotspots.length : 'MISSING');
