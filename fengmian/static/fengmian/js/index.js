$(function () {
    const TABLEHEAD = ['下载地址','商品id','点赞数','评论数','发布日期'];
    let $qnumber = $('#qid'),
        $origin_url = $('#origin_url'),
        $qsubmit = $('#qsubmit'),
        $addUserSubmit = $('#add'),
        $addAll = $('#addAll'),
        $del = $('#del'),
        $submit = $('#submit');
    

        
    function register() {
        // 提交前检查格式
        let $qq = $.trim($qnumber.val());
        if (!tools.isNumber($qq) && !tools.spaceCheck($qq)) return false;
        $.ajax({
            type: 'get',
            url: '/pdd-video/',
            data: { qid: $qq },
            dataType: 'json',
            contentType: 'application/json',
            success: function (data) {
                if (data.code === -1) {
                    $('span.tips-none').addClass('color-red').text(data.msg+'请联系管理员!');
                }else if (data.code === -2) {
                    $('span.tips-none').addClass('color-red').text('当前仅允许登录两个设备!!'+'请联系管理员!');
                }else if (data.code === 1) {
                    $('span.color-red').text(data.msg + '   跳转中...');
                    setTimeout(()=>{ window.location.reload(); },3000)
                    
                }
            },
            error: function (data) {

            },
        })
    };
    function getUrl() {
        let $urlStr = $.trim($origin_url.val());
        let $tips = $('div.form>span.tips');
        let $result = $('div.result>table');
        let $tdHtml = '<tbody><tr>';
        let $thHtml = '<thead class="thead-light"><tr class="">';
        if (!tools.spaceCheck($urlStr)) {
            $tips.addClass('color-red').val('请检查连接!!!');
        } else {
            $.ajax({
                type: 'get',
                url: '/pdd-video/',
                data: { 'ou': $urlStr },
                dataType: 'json',
                contentType: 'application/json',
                success: function (data) {
                    $result.siblings('span.tips').removeClass('d-none');
                    if (data.code === 0){
                        let result = data.data
                        for (key in result) {
                            if (key === 'url') {
                                $tdHtml += '<td class="col-2 p-1"><a target="_blank" href="' + result[key] + '">下载</a></td>'
                            }else{
                                $tdHtml += '<td class="col-2 p-1">' + result[key] + '</td>'
                            }
                        }
                        for (i in TABLEHEAD) {
                            $thHtml += '<th scope="col" class="p-0 font-weight-normal">' + TABLEHEAD[i] + '</th>';
                        }
                        $thHtml += '</tr></thead>';
                        $tdHtml += '</tr></tbody>';
                        $result.html($thHtml + $tdHtml);
                        $result.siblings('span.tips').text('解析成功!!!')

                    }else if (data.code === -1) {
                        $result.siblings('span.tips').removeClass('d-none').text('链接错误!!!')
                    }else if (data.code === -2) {
                        $result.siblings('span.tips').removeClass('d-none').text('当天下载次数用完，请隔天再来或联系管理!!!')
                    }else {$result.siblings('span.tips').removeClass('d-none').text('未知错误!!!')}
                }
            })
        }
    };
    // user manage
    var userManage = {
        addUser: function() {
            let $uid = $('#addUid'),
                $tips = $uid.siblings('span.add-tips');
            let $uidValue = $uid.val()
            tools.userManageAjax($uid,$tips,{'uid':$uidValue})
        },
        addAllUser: function() {
            let $allUser= $('#addList'),
                $tips = $allUser.siblings('span.add-tips');
            let $allUserValue = $allUser.val();
            tools.userManageAjax($allUser,$tips,{'list':$allUserValue});
        },
        delUser: function() {
            let $deluid = $('#deluid'),
                $tips = $deluid.siblings('span.add-tips');
            let $deluidValue = $deluid.val();
            tools.userManageAjax($deluid,$tips,{'delnum':$deluidValue})
        },
   
    }
    var tools = {
        // 检查是否是数字及是否含有空格
        isNumber: function (str) {
            let reg = /^[1-9]{8,12}$/;
            let $tips = $qnumber.siblings('span')
            if (!reg.test(str)) {
                $tips.addClass('color-red').text('输入有误，请检查空格或者号码!!!');
                $qnumber.val('');
                return false
            } else {
                $tips.removeClass('color-red');
                return true
            }
        },
        // 空格及空值检测
        spaceCheck: function (str) {
            return str != '' && (str.indexOf('') != -1 ? true : false)
        },
        userManageAjax: function(valdom,tipdom,params){
            if (!tools.spaceCheck(valdom.val())) {
                tipdom.text('请检查!!!');
                valdom.val('');
            } else {
                $.ajax({
                    type: 'get',
                    url: '/userchange/',
                    data: params,
                    dataType: 'json',
                    contentType: 'application/json',
                    success: function (data) {
                        tipdom.text(data.msg)
                        valdom.val('')
                    }
                })
            }
        },
    }

    // $qnumber.change(() => { tools.isNumber() });
    // user mange
    $addUserSubmit.click(() => { userManage.addUser() });
    $addAll.click(()=>{ userManage.addAllUser() })
    $del.click(()=>{ userManage.delUser() })
    // end
    $submit.click(() => { getUrl() });
    $qsubmit.click(()=>{ register() });


})