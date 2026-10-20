// Test runner: imports all suites (they self-register), then reports.
import './tests_gameplay.mjs';
import './tests_boss.mjs';
import './tests_meta.mjs';
import './tests_campaign.mjs';
import { tests } from './harness.mjs';


let failed = 0;
for (const t of tests) {
  try {
    await t.fn();
    console.log(`PASS  ${t.name}`);
  } catch (e) {
    failed++;
    console.error(`FAIL  ${t.name}\n      ${e.message}`);
  }
}
console.log(failed === 0 ? `\nALL ${tests.length} TESTS PASSED` : `\n${failed}/${tests.length} FAILED`);
process.exit(failed === 0 ? 0 : 1);
