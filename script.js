// 학생 버튼들을 선택하고 클릭 시 login.html로 이동
document.querySelectorAll('.studentButton').forEach(button => {
    button.addEventListener('click', function() {
        window.location.href = 'login.html'; // 버튼 클릭 시 로그인 페이지로 이동
    });
});

// 로그인 페이지에서 로그인 폼 제출 시 이벤트 처리
// 로그인 검증에 대해서는 따로 공부해야할듯;; fastapi jwt인증설정 - 로그인 엔드포인트 - html 수정까지
document.getElementById('loginForm')?.addEventListener('submit', function(event) {
    event.preventDefault(); // 폼 제출 기본 동작
    // 로그인 로직 추가 할 것 (사용자 이름과 비밀번호 검증) 로그인 검증은 서버와의 통신을 통해 이루어져야 함
    // 로그인 성공 시 게시판 페이지로 이동 (현재는 바로 이동)
    window.location.href = 'board.html';
});

// 게시판 페이지에서 폼 표시 여부 토글
function toggleForm() {
    const tableSelect = document.getElementById('tableSelect');
    const formContainer = document.getElementById('formContainer');
    if (tableSelect.value) {
        formContainer.style.display = 'block'; // 선택된 값이 있으면 폼 표시
    } else {
        formContainer.style.display = 'none'; // 선택된 값이 없으면 폼 숨김
    }
}

// 드롭다운 메뉴의 선택지가 변경될 때 input 칸을 초기화하는 함수임
function resetInputFields() {
    document.querySelectorAll('#messageForm input').forEach(input => input.value = ''); // 모든 입력 필드를 초기화함
}

// 드롭다운 메뉴의 onchange 이벤트 리스너 추가
document.getElementById("tableSelect").addEventListener("change", resetInputFields);

document.addEventListener("DOMContentLoaded", () => {
    const form = document.getElementById("messageForm");

    // 폼 제출 이벤트 리스너 추가
    form.addEventListener("submit", event => {
        event.preventDefault(); // 폼 제출 시 페이지 리로드를 막음
        submitForm(); // 폼 데이터를 제출하는 함수 호출
    });

    // 페이지 로드 시 각 DB의 데이터를 가져와 테이블에 표시
    fetchData('personal'); // 개인 DB 가져오기
    fetchData('team2'); // 2팀 DB 가져오기
    fetchData('team3'); // 3팀 DB 가져오기
});

// 서버에서 데이터를 가져와 테이블에 표시하는 함수
async function fetchData(tableType) {
    let url;

    // DB 유형에 따라 URL을 설정
    if (tableType === 'personal') {
        url = 'http://127.0.0.1:8000/api/getFirstMessages'; 
    } else if (tableType === 'team2') {
        url = 'http://127.0.0.1:8000/api/getTeam2Messages'; 
    } else if (tableType === 'team3') {
        url = 'http://127.0.0.1:8000/api/getTeam3Messages'; 
    }

    try {
        // 서버에 GET 요청을 보내 데이터를 가져옴
        const response = await fetch(url);
        if (response.ok) {
            const data = await response.json();
            // 가져온 데이터를 테이블에 추가
            data.forEach(message => addRowToTable(message, tableType));
        } else {
            console.error("Failed to fetch data:", response.statusText);
        }
    } catch (error) {
        console.error("Error:", error);
    }
}

// 폼 데이터를 서버에 제출하는 함수
async function submitForm() {
    // 폼 데이터 수집
    const tableSelect = document.getElementById("tableSelect").value.trim();
    const messageId = document.getElementById("messageId").value.trim();
    const purposeIdx = document.getElementById("purposeIdx").value.trim();
    const message = document.getElementById("message").value.trim();
    const mean = parseFloat(document.getElementById("mean").value.trim());
    const meanAddPhrase = parseFloat(document.getElementById("meanAddPhrase").value.trim());
    const meanAddMor = parseFloat(document.getElementById("meanAddMor").value.trim());
    const meanAddAll = parseFloat(document.getElementById("meanAddAll").value.trim());
    const runningTime = document.getElementById("runningTime").value.trim();
    const yesValue = parseFloat(document.getElementById("yesValue").value.trim());
    const noValue = parseFloat(document.getElementById("noValue").value.trim());
    const confirmStatus = parseInt(document.getElementById("confirmStatus").value.trim());

    // 폼 데이터를 객체로 저장
    const formData = {
        messageId,
        purposeIdx,
        message,
        mean,
        meanAddPhrase,
        meanAddMor,
        meanAddAll,
        runningTime,
        yesValue,
        noValue,
        confirmStatus
    };

    try {
        // 서버에 POST 요청을 보내 데이터를 저장
        const response = await fetch('http://127.0.0.1:8000/api/saveFirstMessage', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json'
            },
            body: JSON.stringify(formData)
        });

        if (response.ok) {
            const result = await response.json();
            alert("등록 성공: " + JSON.stringify(result));
            // 등록된 데이터를 테이블에 추가
            addRowToTable(result.data, tableSelect);
        } else {
            const error = await response.json();
            console.error("등록 실패:", error);
            alert("등록 실패: " + JSON.stringify(error.detail || error));
        }
    } catch (error) {
        console.error("Error:", error);
        alert("오류 발생: " + error.message); // 오류알리기
    }
}

// 날짜 문자열을 원하는 형식으로 변환하는 함수
function formatDateString(dateString) {
    const date = new Date(dateString);
    const year = date.getFullYear();
    const month = ('0' + (date.getMonth() + 1)).slice(-2);
    const day = ('0' + date.getDate()).slice(-2);
    const hours = ('0' + date.getHours()).slice(-2);
    const minutes = ('0' + date.getMinutes()).slice(-2);
    const seconds = ('0' + date.getSeconds()).slice(-2);

    // 원하는 형식: 년-월-일 / 시:분:초
    return `${year}-${month}-${day} / ${hours}:${minutes}:${seconds}`;
}

// 데이터를 테이블에 추가하는 함수
function addRowToTable(data, tableType) {
    let table;
    // DB 유형에 따라 테이블을 선택
    if (tableType === 'personal') {
        table = document.getElementById('messageTable').getElementsByTagName('tbody')[0];
    } else if (tableType === 'team2') {
        table = document.getElementById('team2Table').getElementsByTagName('tbody')[0];
    } else if (tableType === 'team3') {
        table = document.getElementById('team3Table').getElementsByTagName('tbody')[0];
    }

    // 새로운 행을 추가
    const newRow = table.insertRow();
    newRow.classList.add('newRow'); // 새 행에 클래스 추가

    newRow.insertCell(0).textContent = data.messageId;
    if (tableType === 'personal') {
        newRow.insertCell(1).textContent = data.purposeIdx;
        newRow.insertCell(2).textContent = data.message;
        newRow.insertCell(3).textContent = data.mean;
        newRow.insertCell(4).textContent = data.meanAddPhrase;
        newRow.insertCell(5).textContent = data.meanAddMor;
        newRow.insertCell(6).textContent = data.meanAddAll;
        newRow.insertCell(7).textContent = data.runningTime;
        newRow.insertCell(8).textContent = formatDateString(data.createdDate);
        newRow.insertCell(9).textContent = formatDateString(data.sendDate) || '';

        // '보내기' 버튼 추가
        const receiveCell = newRow.insertCell(10);
        const sendButton = document.createElement('button');
        sendButton.textContent = '보내기';
        sendButton.addEventListener('click', () => sendDate(data.messageId, newRow));
        receiveCell.appendChild(sendButton);

        newRow.insertCell(11).textContent = data.yesValue;
        newRow.insertCell(12).textContent = data.noValue;
        newRow.insertCell(13).textContent = data.confirmStatus === 1 ? 'yes' : 'no';

       // 삭제 버튼 추가
       const deleteButton = document.createElement('button');
       deleteButton.textContent = '삭제';
       deleteButton.classList.add('deleteButton'); // 삭제 버튼에 클래스 추가
       deleteButton.addEventListener('click', () => deleteRow(data.messageId, newRow));
       newRow.insertCell(14).appendChild(deleteButton);

       // 추가된 행에 answermessages 열을 위한 빈 행 추가 (for 문 쓰고싶은데 for문 사용하면 먹통됨;;)
       const answerRow = table.insertRow();
       answerRow.insertCell(0).textContent = 'answermessages';
       answerRow.insertCell(1).textContent = '는';
       answerRow.insertCell(2).textContent = '이곳에';
       answerRow.insertCell(3).textContent = '들';
       answerRow.insertCell(4).textContent = '어';
       answerRow.insertCell(5).textContent = '갑';
       answerRow.insertCell(6).textContent = '니';
       answerRow.insertCell(7).textContent = '다';
       answerRow.insertCell(8).textContent = ' ';
       answerRow.insertCell(9).textContent = ' ';
       answerRow.insertCell(10).textContent = ' ';
   } else {
       newRow.insertCell(1).textContent = data.message;
   }
}

// '보내기' 버튼 클릭 시 호출되는 함수
async function sendDate(messageId, rowElement) {
    try {
        const response = await fetch(`http://127.0.0.1:8000/api/sendDate/${messageId}`, {
            method: 'POST'
        });

        if (response.ok) {
            const result = await response.json();
            rowElement.cells[9].textContent = formatDateString(result.sendDate); // sendDate 열 업데이트
        } else {
            const error = await response.json();
            console.error("sendDate 실패:", error);
            alert("sendDate 실패: " + JSON.stringify(error.detail || error));
        }
    } catch (error) {
        console.error("Error:", error);
        alert("오류 발생: " + error.message);
    }
}

// 행을 삭제하는 함수
async function deleteRow(messageId, rowElement) {
    try {
        const response = await fetch(`http://127.0.0.1:8000/api/deleteMessage/${messageId}`, {
            method: 'DELETE'
        });

        if (response.ok) {
            rowElement.remove(); // 행을 테이블에서 삭제
        } else {
            const error = await response.json();
            console.error("삭제 실패:", error);
            alert("삭제 실패: " + JSON.stringify(error.detail || error));
        }
    } catch (error) {
        console.error("Error:", error);
        alert("오류 발생: " + error.message);
    }
}

// 새로고침 버튼 클릭 시 페이지를 새로고침
document.getElementById('refreshBtn').addEventListener('click', function() {
    location.reload();
});
