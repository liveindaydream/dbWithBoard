from fastapi import FastAPI, HTTPException, Body, Request
from databases import Database
from pydantic import BaseModel, Field
from typing import List, Optional
from datetime import datetime, timedelta, timezone
from decimal import Decimal
from contextlib import asynccontextmanager
from fastapi.responses import JSONResponse
from fastapi.middleware.cors import CORSMiddleware

# 데이터베이스 URL 설정
databaseDb1Url = "mysql://admin:Seigakushakorea0308(!@57.180.41.44/boardDB1_hgj7"
databaseDb1 = Database(databaseDb1Url)

databaseDb2Url = "mysql://admin:Seigakushakorea0308(!@57.180.41.44/boardDB2_hgj7"
databaseDb2 = Database(databaseDb2Url)

databaseDb3Url = "mysql://admin:Seigakushakorea0308(!@57.180.41.44/boardDB3_hgj7"
databaseDb3 = Database(databaseDb3Url)

# 한국 시간 반환 함수
def getKoreaTime():
    return datetime.utcnow().replace(tzinfo=timezone.utc).astimezone(timezone(timedelta(hours=9)))

# 애플리케이션이 시작될 때 데이터베이스에 연결하는 함수
async def start():
    print("서버 시작 중...")
    await databaseDb1.connect()  
    await databaseDb2.connect()  
    await databaseDb3.connect()  

# 애플리케이션이 종료될 때 데이터베이스 연결을 종료하는 함수
async def shutdown():
    print("서버 종료 중...")
    await databaseDb1.disconnect()  
    await databaseDb2.disconnect()  
    await databaseDb3.disconnect()  

# FastAPI 애플리케이션의 수명 주기를 관리하는 함수
@asynccontextmanager
async def lifespan(app: FastAPI):
    await start()
    yield
    await shutdown()

# FastAPI 애플리케이션을 생성하고 lifespan 함수를 적용함
app = FastAPI(lifespan=lifespan)

# CORS 설정 추가
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Pydantic 모델 정의
class FirstMessageCreate(BaseModel):
    messageId: str
    purposeIdx: str
    message: str
    mean: Decimal
    meanAddPhrase: Decimal
    meanAddMor: Decimal
    meanAddAll: Decimal
    runningTime: str
    createdDate: Optional[datetime] = Field(default_factory=datetime.utcnow)
    sendDate: Optional[datetime] = None
    yesValue: Decimal
    noValue: Decimal
    confirmStatus: int

class AnswerMessageCreate(BaseModel):
    answerId: str
    messageId: str
    answer: str
    mean: Decimal
    meanAddPhrase: Decimal
    meanAddMor: Decimal
    meanAddAll: Decimal
    sendDate: datetime
    receiveDate: Optional[datetime] = None
    yesOrNo: int

# 여러 데이터베이스에 동일한 쿼리를 실행하는 함수
async def executeQueryOnAllDatabases(query: str, values: dict):
    try:
        await databaseDb1.execute(query, values=values)
        await databaseDb2.execute(query, values=values)
        await databaseDb3.execute(query, values=values)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

# firstmessage를 저장하는 API 엔드포인트 (개인db)
@app.post("/api/saveFirstMessage")
async def saveFirstMessage(message: FirstMessageCreate = Body(...)):
    message.createdDate = getKoreaTime()
    query = """
    INSERT INTO firstmessages (messageId, purposeIdx, message, mean, meanAddPhrase, meanAddMor, meanAddAll, runningTime, createdDate, sendDate, yesValue, noValue, confirmStatus)
    VALUES (:messageId, :purposeIdx, :message, :mean, :meanAddPhrase, :meanAddMor, :meanAddAll, :runningTime, :createdDate, :sendDate, :yesValue, :noValue, :confirmStatus)
    """
    values = message.dict()
    try:
        await executeQueryOnAllDatabases(query, values)
        return {"status": "success", "data": message.dict()}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

# answermessage를 저장하는 API 엔드포인트 (개인db)
@app.post("/api/saveAnswerMessage")
async def saveAnswerMessage(message: AnswerMessageCreate = Body(...)):
    query = """
    INSERT INTO answermessages (answerId, messageId, answer, mean, meanAddPhrase, meanAddMor, meanAddAll, sendDate, receiveDate, yesOrNo)
    VALUES (:answerId, :messageId, :answer, :mean, :meanAddPhrase, :meanAddMor, :meanAddAll, :sendDate, :receiveDate, :yesOrNo)
    """
    values = message.dict()
    try:
        await executeQueryOnAllDatabases(query, values)
        return {"status": "success", "data": message.dict()}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

# firstmessages 테이블의 모든 메시지를 조회하는 API 엔드포인트 (개인db)
@app.get("/api/db1FirstMessages")
async def getFirstMessages():
    try:
        query = "SELECT * FROM firstmessages"
        messages = await databaseDb1.fetch_all(query=query)
        if not messages:
            raise HTTPException(status_code=404, detail="No messages found")
        return messages
    except HTTPException as e:
        raise e
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

# answermessages 테이블의 모든 메시지를 조회하는 API 엔드포인트 (개인db)
@app.get("/api/db1AnswerMessages")
async def getAnswerMessages():
    try:
        query = "SELECT * FROM answermessages"
        messages = await databaseDb1.fetch_all(query=query)
        if not messages:
            raise HTTPException(status_code=404, detail="No messages found")
        return messages
    except HTTPException as e:
        raise e
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

# 2팀 DB의 firstmessages 테이블을 조회하는 API 엔드포인트
@app.get("/api/team2FirstMessages")
async def getTeam2FirstMessages():
    try:
        query = "SELECT * FROM firstmessages"
        messages = await databaseDb2.fetch_all(query=query)
        if not messages:
            raise HTTPException(status_code=404, detail="No team 2 messages found")
        return messages
    except HTTPException as e:
        raise e
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

# 2팀 DB의 answermessages 테이블을 조회하는 API 엔드포인트
@app.get("/api/team2AnswerMessages")
async def getTeam2AnswerMessages():
    try:
        query = "SELECT * FROM answermessages"
        messages = await databaseDb2.fetch_all(query=query)
        if not messages:
            raise HTTPException(status_code=404, detail="No team 2 messages found")
        return messages
    except HTTPException as e:
        raise e
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

# 3팀 DB의 firstmessages 테이블을 조회하는 API 엔드포인트
@app.get("/api/team3FirstMessages")
async def getTeam3FirstMessages():
    try:
        query = "SELECT * FROM firstmessages"
        messages = await databaseDb3.fetch_all(query=query)
        if not messages:
            raise HTTPException(status_code=404, detail="No team 3 messages found")
        return messages
    except HTTPException as e:
        raise e
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

# 3팀 DB의 answermessages 테이블을 조회하는 API 엔드포인트
@app.get("/api/team3AnswerMessages")
async def getTeam3AnswerMessages():
    try:
        query = "SELECT * FROM answermessages"
        messages = await databaseDb3.fetch_all(query=query)
        if not messages:
            raise HTTPException(status_code=404, detail="No team 3 messages found")
        return messages
    except HTTPException as e:
        raise e
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

# 현재 한국 시간을 반환하고 특정 메시지의 sendDate를 업데이트하는 API 엔드포인트
@app.post("/api/sendDate/{messageId}")
async def sendDate(messageId: str):
    timestamp = getKoreaTime().isoformat()
    try:
        query = "UPDATE firstmessages SET sendDate = :sendDate WHERE messageId = :messageId"
        values = {"sendDate": timestamp, "messageId": messageId}
        
        await executeQueryOnAllDatabases(query, values)
        
        return {"sendDate": timestamp}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

# 에러 처리 핸들러: HTTPException 발생 시 호출됨
@app.exception_handler(HTTPException)
async def httpExceptionHandler(request: Request, exc: HTTPException):
    return JSONResponse(
        status_code=exc.status_code,
        content={"message": exc.detail},
    )

# 에러 처리 핸들러: 일반적인 예외 발생 시 호출됨
@app.exception_handler(Exception)
async def globalExceptionHandler(request: Request, exc: Exception):
    return JSONResponse(
        status_code=500,
        content={"message": "Internal Server Error"},
    )

# 전체 데이터를 가져오는 엔드포인트
# 전부 전체데이터로 퉁치지 않고 만든 이유 : first, answer 메세지를 각각 조회할 일이 있을 수 있어서.
@app.get("/api/getFirstMessages")
async def getFirstMessages():
    query = "SELECT * FROM firstmessages"
    try:
        messages = await databaseDb1.fetch_all(query=query)
        return messages
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/api/getTeam2Messages")
async def getTeam2Messages():
    query = "SELECT * FROM firstmessages"
    try:
        messages = await databaseDb2.fetch_all(query=query)
        return messages
    except Exception as e:
        print(f"Error fetching team2messages: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/api/getTeam3Messages")
async def getTeam3Messages():
    query = "SELECT * FROM firstmessages"
    try:
        messages = await databaseDb3.fetch_all(query=query)
        return messages
    except Exception as e:
        print(f"Error fetching team3messages: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

# 데이터를 삭제하는 엔드포인트
# 이거 왜만듬? 매번 workbench나 movaxterm 들어가서 삭제하는거 번거로워서. 테스트만 100번 넘어가니 힘들더라.
@app.delete("/api/deleteMessage/{messageId}")
async def deleteMessage(messageId: str):
    query = "DELETE FROM firstmessages WHERE messageId = :messageId"
    values = {"messageId": messageId}
    try:
        await executeQueryOnAllDatabases(query, values)
        return {"status": "success", "message": "Message deleted"}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
