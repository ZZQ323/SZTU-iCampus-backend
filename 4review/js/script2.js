// Demo1

// var num1 = 1; // num1为全局变量，num2为window的一个属性
// num2 = 2;

// console.log(window);

// delete num1;  //无法删除
// // delete num2;  //删除，但是前后的输出都看不见num2了，不知为何；
// // __VUE_DEVTOOLS_GLOBAL_HOOK__: 
// // ​loadedGsCtx: true
// // ​model: function model()
// // ​num1: 1
// // ​num4: 2
// // num5: 3

// console.log(window);

// function model() {
//     var num3 = 1; // 本地变量
//     num4 = 2;     // window的属性
//     // 匿名函数
//     (function () {
//         var num = 1; // 本地变量
//         num3 = 2; // 继承作用域（闭包）
//         num5 = 3; // window的属性
//     }())
// }
// model();



// Demo2

// var x = 0; // x 是全局变量，并且赋值为 0
// console.log(typeof z); // // “undefined”，因为 z 还不存在
// function a() {
//     var y = 2; // y 被声明成函数 a 作用域的变量，并且赋值为 2
//     console.log(x, y); // 0 2
//     function b() {
//         x = 3; // 全局变量 x 被赋值为 3
//         y = 4; // 已存在的外部函数的 y 变量被赋值为 4
//         z = 5; // 创建新的全局变量 z，并且赋值为 5
//         // （在严格模式下抛出 ReferenceError）
//     }
//     b(); // 调用 b 时创建了全局变量 z
//     console.log(x, y, z); // 3 4 5
// }

// a(); // 也调用了 b。
// console.log(x, z); // 3 5
// console.log(typeof y); // “undefined”，因为 y 是 a 函数的局部变量


// Demo3

try {
    var a = "a";
    throw 1;
} catch (e) {
    console.log(a); // a
    console.log(e); // undefined
    // 只有当 catch 绑定的是一个简单标识符，而不是解构模式时才可以
    // 这种情况下，声明会被提升到 catch 块外部，但在 catch 块内的任何赋值都不会在外部可见
    var e = 2; // 有效
    console.log(e); // 2
}
console.log(a); // a
console.log(e); // undefined

// Demo4

// "use strict";

// var x = 0;
// function f() {
//   var x = y = 1; // ReferenceError: y is not defined
// }
// f();

// console.log(x, y);
