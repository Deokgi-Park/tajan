// 관리자 토큰 발급
$.ajax({
    type: "POST",
    url: "/login",
    data: {'number' : '0-0', 'password' : "tarzanjjang"},
    success: function (response) {
        if (response['result'] == 'success') {
            alert('좋아요 완료!')
            if(response['access_token']) {
                createCookie(response['access_token'])
        } else {
            alert('좋아요 실패ㅠㅠ')
        }
    }
    }
});


$.ajax({
    type: "POST",
    url: "/login",
    data: {'number' : '0-0', 'password' : "tarzanjjang"},
    success: function (response) {
        if (response.result == 'success') {
            alert('좋아요 완료!')
        } else {
            alert('좋아요 실패ㅠㅠ')
        }
    }
});

// 토큰으로 로그인 수행
$.ajax({
    url: "/listAuth", // 요청을 보낼 엔드포인트 URL
    type: "POST", // 요청 메서드 (GET, POST, PUT, DELETE 등)
    headers: {
        "Authorization": "Bearer " + getCookie("access_token")// JWT 토큰을 Authorization 헤더에 포함
    },
    success: function(response) {
        debugger;
        // 요청이 성공인 경우 이동
        if(response.result == 'admin')
            window.location.href = '/loginManager';
        else if(response.result == 'success')
            window.location.href = '/loginUser';
        else
            alert('로그인에 실패했습니다. 아이디와 비밀번호를 확인해주세요.')
    },
    error: function(xhr, status, error) {
        // 요청이 실패한 경우 또는 오류가 발생한 경우
        alert('인증 오류 및 서버 장애가 확인 됩니다. 관리자에게 문의하세요')
        console.error("요청 실패 또는 오류 발생:", status, error);
    }
});


// 토큰으로 로그인 수행
$.ajax({
    url: "/logout", // 요청을 보낼 엔드포인트 URL
    type: "POST", // 요청 메서드 (GET, POST, PUT, DELETE 등)
    headers: {
        "Authorization": "Bearer " + document.cookie // JWT 토큰을 Authorization 헤더에 포함
    },
    success: function(response) {
        debugger
        alert(response.message);
        window.location.href = '/';
        document.cookie = 'removed';
    },
    error: function(xhr, status, error) {
        // 요청이 실패한 경우 또는 오류가 발생한 경우
        alert('인증 토큰 분실 및 서버 장애가 확인 됩니다. 관리자에게 문의하세요')
        console.error("요청 실패 또는 오류 발생:", status, error);
    }
});