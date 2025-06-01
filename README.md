# Prompt-Microservice


이 프로젝트는 한국어 특화 Gemma2 모델을 활용해 Big5 성향을 유도하도록 정의된 프롬프트를 기반으로 사용자와의 실시간 대화를 Kafka를 통해 전송하는 Prompt 마이크로서비스입니다.

- LangChain + Ollama 기반 LLM 응답 생성
- Kafka 메시지 기반 비동기 성향 분석
- 3단계 체인 구조: 주감지 체인 / 감시 체인 / 보조 체인
- 성향 수집이 부족할 경우 보완 질문 또는 직접 설문 질문 수행

---

## 시스템 구조

```mermaid
graph TD
    U[사용자 입력 (chat_input)] -->|Kafka| C[ChatConsumer (주감지 체인)]
    C -->|LLM 응답 생성| O[chat_output]
    C -->|응답 기록| R[RAG 시스템 (성향 분석)]
    R -->|Kafka big5_scores| M[MonitorService (감시 체인)]
    M -->|누락 성향 확인| B[AuxiliaryPromptService (보조 체인)]
    B -->|보완/직접 질문| C
    M -->|5성향 수집 시| DONE[chat_done]