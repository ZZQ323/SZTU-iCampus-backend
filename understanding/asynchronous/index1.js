console.log('① 脚本开始');

const p = new Promise((resolve) => {
    console.log('② Promise 执行器');
    resolve('OK');
});

p.then((msg) => {
    console.log('⑤ .then 回调 ->', msg);
});

console.log('③ 创建 Promise 之后');

setTimeout(() => {
    console.log('⑥ setTimeout 回调（宏任务）');
}, 0);

console.log('④ 脚本结束');
