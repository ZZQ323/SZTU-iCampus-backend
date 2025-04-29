router.post('/register', async (req, res, next) => {
    //测试邮件
    let mailId = 'xxxxxx'                //收件人的邮箱账号
    let VerificationCode = '8888'        //四位验证码，随机码下面有封装，直接调用即可
    //  let VerificationCode = getVerificationCode()        //生成随机码
    //  console.log('发送的验证码为：'+ VerificationCode)   //查看随机码
    sendMails(mailId, VerificationCode).then(res => {
        // console.log(res, '返回的数据');
        if (res.response == '250 OK: queued as.') {             //如果发送成功执行的操作
            console.log('发送成功了，收件人是：' + res.accepted)    //是个数组
        } else {    //发送失败执行的操作
            console.log('发送失败了，错误为：' + res.rejected)      //也是个数组
        }
    })
    return
});