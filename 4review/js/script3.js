function cl(){
    if(!new.target){
        throw console.error("必须使用 new 调用");
    }
    const tmp = Object.create(Object.prototype);
    Object.defineProperties(tmp,{
        valueOf:{
            // 数值运算、Number() 转换、== 比较	
            value:function(){
                console.log("调用 valueOf 函数啦");
                return 1;
            },
            // enumerable:true,
            // configurable:true
        },
        toString:{
            // 显式调用或字符串上下文
            value:function(){
                return "这是字符串函数";
            },
            // enumerable:true,
                // 没有的时候 {}
                // 有的时候 {} 
            // configurable:true
        }
    });
    return tmp;
}

// const a = cl();
/*
    必须使用 new 调用

    d:\Project\SZTU-iCampus\4review\js\script3.js:3
            throw console.error("必须使用 new 调用");
            ^
    undefined
    (Use `node --trace-uncaught ...` to show where the exception was thrown)
*/

const a = new cl();
// console.log(Object.getOwnPropertyDescriptors(a));
console.log(a);     // {}
console.log(a+1);   // 2

