const fs = require('fs');
const path = require('path');

const dataPath = path.join(__dirname, '../app/js/data.js');
const dataContent = fs.readFileSync(dataPath, 'utf8');

const window = {};
eval(dataContent);

const data = window.OLIST_DATA;
const delivered = data.orders_spine.filter(r => r.stat === 'delivered');
const totalDelivered = delivered.length;
const baselineLateCount = delivered.filter(r => r.late === 1).length;
const baselineLateRate = (baselineLateCount / totalDelivered) * 100;

function runSimulation(bufferDays, dispatchSLA) {
  let simLateCount = 0;
  let simLowAvoidedCount = 0;
  let simSavedGmv = 0;

  delivered.forEach(r => {
    let isSimLate = r.late === 1;
    if (isSimLate) {
      const origDelay = r.dd != null ? r.dd : (r.late === 1 ? 4.0 : 0);
      const dispatchDays = r.cd != null ? r.cd : (r.slow === 1 ? 6.0 : 2.0);
      const savedDispatchDays = Math.max(0, dispatchDays - dispatchSLA);
      const netDelay = origDelay - bufferDays - savedDispatchDays;

      if (netDelay <= 0) {
        isSimLate = false;
        if (r.low === 1) simLowAvoidedCount++;
        simSavedGmv += (r.rev || 0);
      }
    }
    if (isSimLate) simLateCount++;
  });

  const simLateRate = (simLateCount / totalDelivered) * 100;
  return {
    simLateRate: simLateRate.toFixed(2) + '%',
    simLateCount,
    simLowAvoidedCount,
    simSavedGmv: 'R$ ' + (simSavedGmv / 1000).toFixed(1) + 'K'
  };
}

console.log("=== TESTING SIMULATOR CALCULATIONS ===");
console.log(`Total Delivered Orders: ${totalDelivered.toLocaleString()}`);
console.log(`Baseline Late Orders: ${baselineLateCount.toLocaleString()} (${baselineLateRate.toFixed(2)}%)\n`);

console.log("--- Testing Buffer Days Slider (with Dispatch SLA fixed at 10 days) ---");
[0, 1, 2, 3, 4, 5, 7].forEach(buf => {
  const res = runSimulation(buf, 10);
  console.log(`Buffer +${buf}d | SLA 10d => Late Rate: ${res.simLateRate} | Avoided Low: ${res.simLowAvoidedCount} | Saved GMV: ${res.simSavedGmv}`);
});

console.log("\n--- Testing Dispatch SLA Slider (with Buffer Days fixed at +0 days) ---");
[10, 7, 5, 4, 3, 2, 1].forEach(sla => {
  const res = runSimulation(0, sla);
  console.log(`Buffer +0d | SLA ${sla}d  => Late Rate: ${res.simLateRate} | Avoided Low: ${res.simLowAvoidedCount} | Saved GMV: ${res.simSavedGmv}`);
});

console.log("\n--- Testing Combined Policy (Buffer Days + Dispatch SLA) ---");
[
  { buf: 0, sla: 10 },
  { buf: 1, sla: 5 },
  { buf: 2, sla: 3 },
  { buf: 3, sla: 2 },
  { buf: 4, sla: 1 }
].forEach(({ buf, sla }) => {
  const res = runSimulation(buf, sla);
  console.log(`Buffer +${buf}d & SLA ${sla}d => Late Rate: ${res.simLateRate} | Avoided Low: ${res.simLowAvoidedCount} | Saved GMV: ${res.simSavedGmv}`);
});
