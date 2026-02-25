# Architecture Documentation

## 🏗️ Clean Architecture Layers

```
┌─────────────────────────────────────────────────────────────┐
│                    Presentation Layer                        │
│  ┌────────────────────────────────────────────────────────┐ │
│  │  FastAPI Controllers (chat_controller.py)              │ │
│  │  - JWT Authentication                                  │ │
│  │  - Request/Response DTOs                               │ │
│  │  - HTTP Endpoints                                      │ │
│  └────────────────────────────────────────────────────────┘ │
└─────────────────────────────────────────────────────────────┘
                            ▼
┌─────────────────────────────────────────────────────────────┐
│                    Application Layer                         │
│  ┌────────────────────────────────────────────────────────┐ │
│  │  Use Cases (chat_usecase.py)                           │ │
│  │  - Business Logic Orchestration                        │ │
│  │  - Domain Entity Mapping                               │ │
│  └────────────────────────────────────────────────────────┘ │
└─────────────────────────────────────────────────────────────┘
                            ▼
┌─────────────────────────────────────────────────────────────┐
│                    LangGraph Agent Layer                     │
│  ┌────────────────────────────────────────────────────────┐ │
│  │  ChatAgent (agent_graph.py)                            │ │
│  │  - Workflow Orchestration                              │ │
│  │  - State Management                                    │ │
│  │  - Node Execution                                      │ │
│  └────────────────────────────────────────────────────────┘ │
└─────────────────────────────────────────────────────────────┘
                            ▼
┌─────────────────────────────────────────────────────────────┐
│                      Domain Layer                            │
│  ┌────────────────────────────────────────────────────────┐ │
│  │  Entities (entities.py)                                │ │
│  │  - ChatMessage, ShortMemory, LongMemory                │ │
│  │  - VectorSearchResult, ChatRequest, ChatResponse       │ │
│  └────────────────────────────────────────────────────────┘ │
│  ┌────────────────────────────────────────────────────────┐ │
│  │  Repository Interfaces (repositories.py)               │ │
│  │  - IShortMemoryRepository                              │ │
│  │  - ILongMemoryRepository                               │ │
│  │  - IVectorDBRepository                                 │ │
│  │  - ILLMService                                         │ │
│  └────────────────────────────────────────────────────────┘ │
└─────────────────────────────────────────────────────────────┘
                            ▼
┌─────────────────────────────────────────────────────────────┐
│                  Infrastructure Layer                        │
│  ┌──────────────┐  ┌──────────────┐  ┌──────────────┐      │
│  │  DynamoDB    │  │   Qdrant     │  │   Gemini     │      │
│  │  Short Mem   │  │  Long Mem    │  │     LLM      │      │
│  └──────────────┘  └──────────────┘  └──────────────┘      │
│  ┌──────────────┐                                           │
│  │   Qdrant     │                                           │
│  │  Vector DB   │                                           │
│  └──────────────┘                                           │
└─────────────────────────────────────────────────────────────┘
```

## 🔄 LangGraph Workflow Detail

```
User Request
     │
     ▼
┌─────────────────────────────────────────────────────────────┐
│                    LANGGRAPH WORKFLOW                        │
│                                                              │
│  ┌────────────────────────────────────────────────────────┐ │
│  │  Node 1: fetch_short_memory                            │ │
│  │  ┌──────────────────────────────────────────────────┐  │ │
│  │  │  - Query DynamoDB for recent chat history        │  │ │
│  │  │  - Get last 5 messages                            │  │ │
│  │  │  - Convert to ChatMessage entities                │  │ │
│  │  └──────────────────────────────────────────────────┘  │ │
│  └────────────────────────────────────────────────────────┘ │
│                            │                                 │
│                            ▼                                 │
│  ┌────────────────────────────────────────────────────────┐ │
│  │  Node 2: fetch_long_memory                             │ │
│  │  ┌──────────────────────────────────────────────────┐  │ │
│  │  │  - Create embedding from user message             │  │ │
│  │  │  - Search Qdrant with semantic similarity         │  │ │
│  │  │  - Filter by user_id and session_id               │  │ │
│  │  │  - Return top 3 relevant memories                 │  │ │
│  │  └──────────────────────────────────────────────────┘  │ │
│  └────────────────────────────────────────────────────────┘ │
│                            │                                 │
│                            ▼                                 │
│  ┌────────────────────────────────────────────────────────┐ │
│  │  Node 3: search_vector_db                              │ │
│  │  ┌──────────────────────────────────────────────────┐  │ │
│  │  │  - Create embedding from user message             │  │ │
│  │  │  - Search knowledge base (NFL Wiki)               │  │ │
│  │  │  - Return top 3 relevant documents                │  │ │
│  │  │  - Extract sources (URLs)                         │  │ │
│  │  └──────────────────────────────────────────────────┘  │ │
│  └────────────────────────────────────────────────────────┘ │
│                            │                                 │
│                            ▼                                 │
│  ┌────────────────────────────────────────────────────────┐ │
│  │  Node 4: build_context                                 │ │
│  │  ┌──────────────────────────────────────────────────┐  │ │
│  │  │  - Combine short memory context                   │  │ │
│  │  │  - Add long memory context                        │  │ │
│  │  │  - Add vector DB context                          │  │ │
│  │  │  - Build final prompt with all context            │  │ │
│  │  └──────────────────────────────────────────────────┘  │ │
│  └────────────────────────────────────────────────────────┘ │
│                            │                                 │
│                            ▼                                 │
│  ┌────────────────────────────────────────────────────────┐ │
│  │  Node 5: generate_response                             │ │
│  │  ┌──────────────────────────────────────────────────┐  │ │
│  │  │  - Send prompt to Gemini LLM                      │  │ │
│  │  │  - Get AI response                                │  │ │
│  │  └──────────────────────────────────────────────────┘  │ │
│  └────────────────────────────────────────────────────────┘ │
│                            │                                 │
│                            ▼                                 │
│  ┌────────────────────────────────────────────────────────┐ │
│  │  Node 6: save_memories                                 │ │
│  │  ┌──────────────────────────────────────────────────┐  │ │
│  │  │  - Save to DynamoDB (short memory)                │  │ │
│  │  │  - Save to Qdrant (long memory)                   │  │ │
│  │  │  - Create embeddings for long memory              │  │ │
│  │  └──────────────────────────────────────────────────┘  │ │
│  └────────────────────────────────────────────────────────┘ │
│                            │                                 │
└────────────────────────────┼─────────────────────────────────┘
                             ▼
                      Response to User
```

## 📊 Data Flow

```
┌──────────────┐
│   Frontend   │
│  (React)     │
└──────┬───────┘
       │ HTTP POST /api/chat/
       │ Header: X-User-Authorization: Bearer JWT
       │ Body: { session_id, message }
       ▼
┌──────────────────────────────────────────────────────────┐
│  FastAPI Controller                                      │
│  1. Extract JWT from header                              │
│  2. Decode JWT → get user_id                             │
│  3. Create ChatRequest entity                            │
│  4. Call ChatUseCase                                     │
└──────┬───────────────────────────────────────────────────┘
       │
       ▼
┌──────────────────────────────────────────────────────────┐
│  ChatUseCase                                             │
│  1. Receive ChatRequest                                  │
│  2. Call ChatAgent.chat()                                │
│  3. Convert result to ChatResponse                       │
└──────┬───────────────────────────────────────────────────┘
       │
       ▼
┌──────────────────────────────────────────────────────────┐
│  ChatAgent (LangGraph)                                   │
│  1. Initialize AgentState                                │
│  2. Execute workflow graph                               │
│  3. Return final state                                   │
└──────┬───────────────────────────────────────────────────┘
       │
       ├─────────────────────────────────────────────────┐
       │                                                  │
       ▼                                                  ▼
┌──────────────────┐                          ┌──────────────────┐
│  DynamoDB        │                          │  Qdrant          │
│  (Short Memory)  │                          │  (Long Memory)   │
│                  │                          │  (Vector DB)     │
│  - Get history   │                          │  - Search memory │
│  - Save new msg  │                          │  - Search KB     │
└──────────────────┘                          │  - Save memory   │
                                               └──────────────────┘
       │
       ▼
┌──────────────────┐
│  Gemini LLM      │
│  - Generate      │
│    response      │
└──────────────────┘
       │
       ▼
┌──────────────────────────────────────────────────────────┐
│  Response                                                │
│  {                                                       │
│    message: "AI response",                              │
│    sources: ["url1", "url2"],                           │
│    used_short_memory: true,                             │
│    used_long_memory: true,                              │
│    used_vector_db: true                                 │
│  }                                                       │
└──────────────────────────────────────────────────────────┘
```

## 🔐 Authentication Flow

```
┌──────────────┐
│   Frontend   │
└──────┬───────┘
       │ Login
       ▼
┌──────────────┐
│  Auth Server │ (Your existing auth system)
└──────┬───────┘
       │ Generate JWT
       │ Payload: { sub: "user_id", exp: ... }
       ▼
┌──────────────┐
│   Frontend   │ Store JWT in localStorage
└──────┬───────┘
       │ Chat Request
       │ Header: X-User-Authorization: Bearer JWT_TOKEN
       ▼
┌──────────────────────────────────────────────────────────┐
│  FastAPI Middleware (jwt_auth.py)                        │
│  1. Extract header: X-User-Authorization                 │
│  2. Parse: Bearer JWT_TOKEN                              │
│  3. Decode JWT with SECRET_KEY                           │
│  4. Extract user_id from payload["sub"]                  │
│  5. Inject user_id into request                          │
└──────┬───────────────────────────────────────────────────┘
       │
       ▼
┌──────────────┐
│  Controller  │ Use user_id for chat
└──────────────┘
```

## 🎯 Key Design Principles

### 1. Dependency Inversion
- Domain layer không phụ thuộc vào Infrastructure
- Sử dụng interfaces (repositories) để abstract implementation
- Infrastructure implements domain interfaces

### 2. Single Responsibility
- Mỗi class có một trách nhiệm duy nhất
- Repository chỉ lo data access
- Use case chỉ lo business logic
- Controller chỉ lo HTTP handling

### 3. Open/Closed Principle
- Dễ dàng thêm repository mới (e.g., PostgreSQL thay vì DynamoDB)
- Dễ dàng thêm LLM mới (e.g., OpenAI thay vì Gemini)
- Không cần sửa code hiện tại

### 4. Testability
- Mỗi layer có thể test độc lập
- Mock repositories dễ dàng
- Test use case không cần database thật

## 🚀 Scalability

### Horizontal Scaling
- FastAPI app có thể chạy nhiều instance
- Load balancer phân phối request
- Stateless design (JWT auth)

### Caching Strategy
- Short memory: DynamoDB với TTL
- Long memory: Qdrant với index
- Vector DB: Pre-computed embeddings

### Performance Optimization
- Async/await trong FastAPI
- Parallel execution trong LangGraph (có thể)
- Connection pooling cho DynamoDB và Qdrant

## 📈 Monitoring & Observability

### Logging Points
- Each LangGraph node logs execution
- Repository operations log success/failure
- LLM calls log latency

### Metrics to Track
- Request latency
- Memory hit rate (short/long/vector)
- LLM token usage
- Error rate per component

### Health Checks
- `/health` endpoint checks all services
- DynamoDB connection
- Qdrant connection
- Gemini API availability
