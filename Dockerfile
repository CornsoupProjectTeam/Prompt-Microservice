# 베이스 이미지 선택
FROM python:3.10-slim

# 작업 디렉토리 설정
WORKDIR /app

# 의존성 파일 복사 및 패키지 설치
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# 프로젝트 전체 소스 복사
COPY . .

# 컨테이너 시작 시 실행할 명령어 (메인 엔트리포인트)
CMD ["python", "app/main.py"]
