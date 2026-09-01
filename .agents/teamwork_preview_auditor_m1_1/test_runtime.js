
const path = require('path');
const assert = require('assert');
const engine = require(path.join(__dirname, '../../dist/engine.js'));

console.log('  Testing engine.js exports...');
assert(typeof engine.translateText === 'function', 'translateText must be a function');
assert(typeof engine.matchDynamicPatterns === 'function', 'matchDynamicPatterns must be a function');
assert(typeof engine.isBypassedElement === 'function', 'isBypassedElement must be a function');
assert(typeof engine.walk === 'function', 'walk must be a function');
assert(typeof engine.dictionary === 'object', 'dictionary must be an object');
assert(Object.keys(engine.dictionary).length >= 400, 'dictionary keys >= 400');

console.log('  [PASS] All exports present and valid.');

// Test 1: Static dictionary translation
assert.strictEqual(engine.translateText('New Conversation'), '新建对话');
assert.strictEqual(engine.translateText('Files Changed'), '已修改文件');
assert.strictEqual(engine.translateText('Subagents'), '子智能体');

// Test 2: Dynamic timers
assert.strictEqual(engine.translateText('Thinking for 1.2s'), '思考中 (1.2秒)');
assert.strictEqual(engine.translateText('Thinking for 250ms'), '思考中 (250毫秒)');
assert.strictEqual(engine.translateText('Thought for 0.8s'), '思考中 (0.8秒)');
assert.strictEqual(engine.translateText('Working for 3.4s'), '处理中 (3.4秒)');
assert.strictEqual(engine.translateText('Working for 500ms'), '处理中 (500毫秒)');
assert.strictEqual(engine.translateText('Completed in 4.5s'), '已完成 (耗时 4.5秒)');
assert.strictEqual(engine.translateText('Finished in 100ms'), '已完成 (耗时 100毫秒)');
assert.strictEqual(engine.translateText('Done in 12s'), '已完成 (耗时 12秒)');

// Test 3: Relative timestamps
assert.strictEqual(engine.translateText('10d'), '10天前');
assert.strictEqual(engine.translateText('5m'), '5分钟前');
assert.strictEqual(engine.translateText('1mo'), '1个月前');
assert.strictEqual(engine.translateText('2h'), '2小时前');
assert.strictEqual(engine.translateText('30s'), '30秒前');
assert.strictEqual(engine.translateText('1y'), '1年前');
assert.strictEqual(engine.translateText('5 minutes ago'), '5分钟前');
assert.strictEqual(engine.translateText('2 days ago'), '2天前');
assert.strictEqual(engine.translateText('1 month ago'), '1个月前');
assert.strictEqual(engine.translateText('just now'), '刚刚');
assert.strictEqual(engine.translateText('a few seconds ago'), '几秒前');

// Test 4: Dynamic counters
assert.strictEqual(engine.translateText('Subagents 3'), '子智能体 3');
assert.strictEqual(engine.translateText('Files Changed 5'), '已修改文件 5');
assert.strictEqual(engine.translateText('3 files changed'), '3 个文件已修改');
assert.strictEqual(engine.translateText('1 file changed'), '1 个文件已修改');
assert.strictEqual(engine.translateText('2 subagents'), '2 个子智能体');
assert.strictEqual(engine.translateText('3 agents running'), '3 个智能体运行中');

// Test 5: Date prefixes
assert.strictEqual(engine.translateText('Today at 10:00 AM'), '今天 at 10:00 AM');
assert.strictEqual(engine.translateText('Yesterday 3:30 PM'), '昨天 3:30 PM');

// Test 6: Non-breaking space
assert.strictEqual(engine.translateText('New\u00a0Conversation'), '新建对话');

console.log('  [PASS] Node.js translation engine runtime tests passed cleanly.');
