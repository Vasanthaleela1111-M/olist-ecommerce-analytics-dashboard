const fs = require('fs');
const path = require('path');

const htmlPath = path.join(__dirname, '..', 'app', 'index.html');
const jsPath = path.join(__dirname, '..', 'app', 'js', 'app.js');

const htmlContent = fs.readFileSync(htmlPath, 'utf8');
const jsContent = fs.readFileSync(jsPath, 'utf8');

console.log("=== VERIFYING DRILL-DOWN MODAL DOM & LOGIC INTEGRITY ===");

const requiredIDs = [
  'modalDrillDown',
  'drillDownTitle',
  'drillDownSub',
  'btnApplyDrillDownFilter',
  'btnCloseDrillDownModal',
  'drillDownOrders',
  'drillDownRevenue',
  'drillDownReview',
  'drillDownLate',
  'drillDownComplaintText',
  'tbodyDrillDownOrders'
];

let missingIDs = [];
requiredIDs.forEach(id => {
  if (!htmlContent.includes(`id="${id}"`)) {
    missingIDs.push(id);
  }
});

if (missingIDs.length === 0) {
  console.log("[PASS] All 11 required Drill-Down Modal HTML element IDs exist in index.html");
} else {
  console.error("[FAIL] Missing HTML element IDs:", missingIDs);
}

const requiredJSFunctions = [
  'openDrillDownModal',
  'activeDrillDownFilter',
  'data-drill-type="state"',
  'data-drill-type="route"',
  'data-drill-type="category"',
  'data-drill-type="seller_state"'
];

let missingJS = [];
requiredJSFunctions.forEach(fn => {
  if (!jsContent.includes(fn)) {
    missingJS.push(fn);
  }
});

if (missingJS.length === 0) {
  console.log("[PASS] All required JS functions and table data-drill attributes exist in app.js");
} else {
  console.error("[FAIL] Missing JS patterns:", missingJS);
}

console.log("=== DOM & SCRIPT INTEGRITY VERIFICATION COMPLETE ===");
