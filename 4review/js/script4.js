// let retId = setTimeout(() => {
//     console.log("异步任务")
// }, 2000);

// // 9007199254740991
// for(let i=0;i<=21474836470;++i);

// console.log("主线程");
// // 1：大概 8s ，才在这里轮到了异步任务
// for(let i=0;i<=2147483647;++i);
// console.log("主线程");
// for(let i=0;i<=2147483647;++i);
// console.log("主线程");
// for(let i=0;i<=2147483647;++i);
// console.log("主线程");
// for(let i=0;i<=2147483647;++i);
// console.log("主线程");
// for(let i=0;i<=2147483647;++i);
// console.log("主线程");

const isb = new Int32Array(new SharedArrayBuffer(4));
function sleep(ms) {
    Atomics.wait(isb, 0, 0, ms);
}

let id = setTimeout(() => {
    console.log("计时结束");
    console.log("This是" + this);
}, 2000);

sleep(4000);
console.log("主线程结束");

