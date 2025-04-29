let getVerificationCode = (codeLength = 4) => { 
    //传入需要的字符串长度，不传默认为4
    // 准备一个用来抽取码的字符串，或者字典
    // let verification_code_str = "abcdefghijklmnopqrstuvwxyz0123456789ABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789";  //数字和字母
    let verification_code_str = "0123456789";     //纯数字
    // 获取某个范围的随机整数，封装的函数，在上面抽取字典的时候进行了调用
    function getRandom(min, max) {                 //意思是获取min-max数字之间的某个随机数，直接调用即可
        return Math.round(Math.random() * (max - min) + min);
    }
    let newStr = '';                    //创建一个空字符串，用来拼接四位随机码
    for (var i = 0; i < codeLength; i++) {       //for循环四次，则拼接四次随机码
        newStr += verification_code_str[getRandom(0, verification_code_str.length - 1)];   //从字典中随机选一个下标，并拼接到空字符串中
    }
    return newStr
}


//调用
let mycode = getVerificationCode()  //可以不传值，默认为4位随机码
console.log('生成的随机码为：' + mycode)