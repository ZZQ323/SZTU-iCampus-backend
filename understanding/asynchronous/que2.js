console.log(Promise);
new Promise(resolve => {
    console.log(1);
    resolve(3); // 标记状态为fullfilled
    // 相当于直接在 promise 这一步进入 then
    Promise.resolve().then(
        ()=> console.log(4) // 下一步执行
    )
}).then(num => {
    // 下一步执行
    console.log(num)
});
console.log(2);

// 1
// 2
// 4
// 3