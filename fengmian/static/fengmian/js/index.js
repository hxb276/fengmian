$(function() {
    let $qnumber = $('#qid'),
        $qsubmit = $('#qsubmit');

    $qsubmit.click(function() {
        // 提交前检查格式
        if (!isNumber()) return false;
        let $qq = $qnumber.val();
        $.ajax({
            type:'get',
            url:'/pdd-video/',
            data:{qid:$qq},
            dataType:'json',
            contentType:'application/json',
            success:function(data){
                if (data.code != -1) {
                    
                    $('span.uname').text(data.msg)
                }
        },
        })
    });
    // 检查是否是数字及是否含有空格
    function isNumber() {
        let reg = /^[1-9]{8,12}$/;
        let $qq = $qnumber.val();
        let $tips = $qnumber.siblings('span')
        if (!tools.spaceCheck($qq) || !reg.test($qq)) {
            $tips.addClass('color-red').text('输入有误，请检查空格或者号码!!!');
            $qnumber.val('')
            return false
        }else {
            $tips.removeClass('color-red');
            return true
        }

    };
    var tools = {
        // 空格及空值检测
        spaceCheck: function(str) {
          return str != '' && str.indexOf(' ') != -1 ? false : true
            },
        }

    $qnumber.change(()=>{isNumber()})


})