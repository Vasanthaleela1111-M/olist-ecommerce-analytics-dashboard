/**
 * Automated JS Engine Regression & Reconciliation Test Suite
 * Tests all 10 canonical filter combinations against ground truth analytical values.
 */

const fs = require('fs');
const path = require('path');

// Setup minimal global DOM environment
class MockElement {
  constructor(id, tag = 'div') {
    this.id = id;
    this.tagName = tag.toUpperCase();
    this.children = [];
    this.classList = {
      add: (cls) => this.classes.add(cls),
      remove: (cls) => this.classes.delete(cls),
      contains: (cls) => this.classes.has(cls)
    };
    this.classes = new Set();
    this.dataset = {};
    this.value = 'ALL';
    this.innerHTML = '';
    this.textContent = '';
    this.listeners = {};
  }
  addEventListener(event, fn) {
    if (!this.listeners[event]) this.listeners[event] = [];
    this.listeners[event].push(fn);
  }
  dispatchEvent(event) {
    if (this.listeners[event]) {
      this.listeners[event].forEach(fn => fn({ target: this }));
    }
  }
  appendChild(child) {
    this.children.push(child);
  }
  getContext() {
    return {
      clearRect: () => {},
      fillRect: () => {},
      measureText: () => ({ width: 10 }),
    };
  }
}

function isNumeric(n) { return !isNaN(parseFloat(n)) && isFinite(n); }
function formatCurrency(val, decimals = 2) {
  if (!isNumeric(val)) return '-';
  if (val === 0) return 'R$ 0.00';
  if (val >= 1000000) {
    return 'R$ ' + (val / 1000000).toFixed(2) + 'M';
  } else if (val >= 10000) {
    return 'R$ ' + (val / 1000).toFixed(2) + 'K';
  } else {
    return 'R$ ' + val.toLocaleString(undefined, { minimumFractionDigits: decimals, maximumFractionDigits: decimals });
  }
}

const elements = {};
function getOrCreateElement(id, tag = 'div') {
  if (!elements[id]) {
    elements[id] = new MockElement(id, tag);
  }
  return elements[id];
}

const elIds = [
  'filterState', 'filterCategory', 'filterStatus', 'filterSeller',
  'btnResetFilters', 'btnMethodology', 'modalMethodology', 'btnCloseModal',
  'kpiOrdersNum', 'kpiOrdersSub', 'kpiRevenueNum', 'kpiRevenueSub',
  'kpiReviewNum', 'kpiReviewSub', 'kpiLowRateNum', 'kpiLowRateSub',
  'kpiLateNum', 'kpiLateSub',
  'chartOverviewMonthly', 'chartOverviewScoreDist', 'chartDeliveryBuckets',
  'tbodyDeliveryState', 'chartGeoScope', 'tbodyGeoHotspots',
  'chartCatScatter', 'tbodyCategoryAnalysis', 'chartSellerDispatch',
  'tbodySellerDist', 'chartPaymentShares', 'chartPaymentInstallments',
  'tbodyRootCauseFull', 'tbodyRootCauseEvidence'
];

elIds.forEach(id => getOrCreateElement(id, id.startsWith('tbody') ? 'tbody' : (id.startsWith('select') || id.startsWith('filter') ? 'select' : 'div')));

const tabIds = ['overview', 'delivery', 'geography', 'categories', 'sellers', 'payments', 'rootcause', 'recommendations'];
const mockTabs = tabIds.map(t => {
  const el = new MockElement(`tab-${t}`, 'button');
  el.dataset.tab = t;
  el.classList.add('nav-tab');
  return el;
});

const mockViews = tabIds.map(t => {
  const el = new MockElement(`view-${t}`, 'div');
  el.classList.add('tab-view');
  return el;
});

global.window = {
  OLIST_DATA: null
};

global.document = {
  addEventListener: (event, fn) => {
    if (event === 'DOMContentLoaded') global.domContentLoadedFn = fn;
  },
  getElementById: (id) => getOrCreateElement(id),
  querySelectorAll: (selector) => {
    if (selector === '.nav-tab') return mockTabs;
    if (selector === '.tab-view') return mockViews;
    return [];
  },
  createElement: (tag) => new MockElement('', tag)
};

// Mock Chart.js constructor
global.Chart = class Chart {
  constructor(ctx, config) {
    this.ctx = ctx;
    this.config = config;
  }
  destroy() {}
};

// Load data.js
require('../app/js/data.js');

// Execute app.js
const appJsCode = fs.readFileSync(path.join(__dirname, '../app/js/app.js'), 'utf8');
eval(appJsCode);

// Trigger DOMContentLoaded
global.domContentLoadedFn();

console.log("=== EXECUTING CANONICAL METRIC RECONCILIATION TEST SUITE ===");

let errorCount = 0;

function setFilters({ st = 'ALL', cat = 'ALL', stat = 'ALL', seller = 'ALL' }) {
  getOrCreateElement('filterState').value = st;
  getOrCreateElement('filterCategory').value = cat;
  getOrCreateElement('filterStatus').value = stat;
  getOrCreateElement('filterSeller').value = seller;
  getOrCreateElement('filterState').dispatchEvent('change');
}

function verifyKPIs(testName, expected) {
  try {
    const ordersText = getOrCreateElement('kpiOrdersNum').textContent;
    const revText = getOrCreateElement('kpiRevenueNum').textContent;
    const reviewText = getOrCreateElement('kpiReviewNum').textContent;
    const lowRateText = getOrCreateElement('kpiLowRateNum').textContent;
    const lateRateText = getOrCreateElement('kpiLateNum').textContent;
    const lowSubText = getOrCreateElement('kpiLowRateSub').textContent;
    const lateSubText = getOrCreateElement('kpiLateSub').textContent;

    console.log(`\n--- Test: ${testName} ---`);
    console.log(`  Orders: ${ordersText} (Expected: ${expected.orders})`);
    console.log(`  Revenue: ${revText} (Expected: ${expected.rev})`);
    console.log(`  Avg Review: ${reviewText} (Expected: ${expected.score})`);
    console.log(`  Low Rating: ${lowRateText} | Sub: "${lowSubText}" (Expected count: ${expected.lowCount})`);
    console.log(`  Late Delivery: ${lateRateText} | Sub: "${lateSubText}" (Expected count: ${expected.lateCount})`);

    if (ordersText !== expected.orders) throw new Error(`Orders mismatch: ${ordersText} vs expected ${expected.orders}`);
    if (revText !== expected.rev) throw new Error(`Revenue mismatch: ${revText} vs expected ${expected.rev}`);
    if (reviewText !== expected.score) throw new Error(`Review score mismatch: ${reviewText} vs expected ${expected.score}`);
    if (expected.lowCount != null && !lowSubText.includes(expected.lowCount)) throw new Error(`Low rating count subtitle mismatch: "${lowSubText}" does not contain ${expected.lowCount}`);
    if (expected.lateCount != null && !lateSubText.includes(expected.lateCount)) throw new Error(`Late count subtitle mismatch: "${lateSubText}" does not contain ${expected.lateCount}`);

    console.log(`[PASS] ${testName}`);
  } catch (err) {
    errorCount++;
    console.error(`[FAIL] ${testName}:`, err.message);
  }
}

// 1. All States + All Categories
setFilters({});
verifyKPIs("1. All States + All Categories", {
  orders: "99,441",
  rev: "R$ 15.84M",
  score: "4.07 / 5.0",
  lowCount: "15,010",
  lateCount: "7,826"
});

// 2. AC + All Categories
setFilters({ st: 'AC' });
verifyKPIs("2. AC + All Categories", {
  orders: "81",
  rev: "R$ 19.67K",
  score: "4.05 / 5.0",
  lowCount: "13",
  lateCount: "3"
});

// 3. AC + baby
setFilters({ st: 'AC', cat: 'baby' });
verifyKPIs("3. AC + baby", {
  orders: "3",
  rev: "R$ 871.97",
  score: "5.00 / 5.0",
  lowCount: "0",
  lateCount: "0"
});

// 4. AC + health_beauty
setFilters({ st: 'AC', cat: 'health_beauty' });
verifyKPIs("4. AC + health_beauty", {
  orders: "6",
  rev: "R$ 1,655.00",
  score: "4.17 / 5.0",
  lowCount: "1",
  lateCount: "0"
});

// 5. SP + All Categories
setFilters({ st: 'SP' });
verifyKPIs("5. SP + All Categories", {
  orders: "41,746",
  rev: "R$ 5.92M",
  score: "4.16 / 5.0",
  lowCount: "5,420",
  lateCount: "2,387"
});

// 6. SP + baby
setFilters({ st: 'SP', cat: 'baby' });
verifyKPIs("6. SP + baby", {
  orders: "1,167",
  rev: "R$ 177.56K",
  score: "4.15 / 5.0",
  lowCount: "149",
  lateCount: "73"
});

// 7. All States + baby
setFilters({ cat: 'baby' });
verifyKPIs("7. All States + baby", {
  orders: "2,840",
  rev: "R$ 479.80K",
  score: "4.04 / 5.0",
  lowCount: "455",
  lateCount: "256"
});

// 8. SP + baby + Late
setFilters({ st: 'SP', cat: 'baby', stat: 'late' });
verifyKPIs("8. SP + baby + Late Delivered", {
  orders: "73",
  rev: "R$ 11.53K",
  score: "2.41 / 5.0",
  lowCount: "42",
  lateCount: "73"
});

// 9. SP + health_beauty + Top 10% Seller
setFilters({ st: 'SP', cat: 'health_beauty', seller: 'top10' });
verifyKPIs("9. SP + health_beauty + Top 10% Seller", {
  orders: "2,109",
  rev: "R$ 347.00K",
  score: "4.26 / 5.0",
  lowCount: "232",
  lateCount: "153"
});

// 10. Deliberately Empty Combination
setFilters({ st: 'AC', cat: 'non_existent_category' });
verifyKPIs("10. Deliberately Empty (AC + non_existent_cat)", {
  orders: "0",
  rev: "R$ 0.00",
  score: "- / 5.0",
  lowCount: "0",
  lateCount: "0"
});

console.log("\n==================================================");
console.log(`TOTAL UNCAUGHT RECONCILIATION ERRORS: ${errorCount}`);
console.log("==================================================");

if (errorCount > 0) {
  process.exit(1);
} else {
  console.log("ALL 10 RECONCILIATION TEST CASES PASSED WITH 100% ACCURACY!");
}
