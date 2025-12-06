# backend/services/prompt_templates.py

def get_diagram_prompt(diagram_type: str, repo_context: str) -> str:
    """Get prompt template that GUARANTEES comprehensive, detailed diagrams"""
    
    base_rules = """
=================================================================
CRITICAL RULES - YOU MUST FOLLOW THESE EXACTLY
=================================================================

1. **COMPREHENSIVE COVERAGE (MANDATORY):**
   - Include MINIMUM 20-30 components (files/modules)
   - Show ALL major folders as subgraphs
   - Include ALL services, routes, pages, components found
   - Don't skip files - include everything important
   - Use actual filenames from the repository data provided

2. **SYNTAX RULES (STRICT):**
   - Node IDs: ONLY letters, numbers, underscores (NO SPACES)
   - Arrows: ONLY --> or -.-> or ==>
   - Labels: Use square brackets [Label Text]
   - NO markdown code blocks (no ``` backticks)
   - Start directly with diagram type

3. **ORGANIZATION (REQUIRED):**
   - Use subgraphs for EVERY major folder
   - Group related files together
   - Show clear hierarchy
   - Include external dependencies

4. **QUALITY STANDARDS:**
   - Minimum 20 nodes for small repos (< 20 files)
   - Minimum 30 nodes for medium repos (20-50 files)
   - Minimum 40+ nodes for large repos (50+ files)
   - Show all important relationships/connections
   - Include configuration files, utilities, helpers

5. **FORBIDDEN:**
   - Generic names like "Service", "Component", "Module"
   - Placeholder nodes
   - Incomplete diagrams
   - Skipping folders or major files
   - Using made-up filenames

=================================================================
REPOSITORY DATA PROVIDED BELOW - USE IT ALL
=================================================================

""" + repo_context + """

=================================================================
"""
    
    specific_instructions = {
        "sequence": """
CREATE A DETAILED SEQUENCE DIAGRAM

REQUIREMENTS:
✓ Show COMPLETE user flow from start to finish
✓ Include at least 15-25 steps
✓ Show ALL components involved (frontend, backend, database, external APIs)
✓ Include error handling paths
✓ Show authentication/authorization steps
✓ Include data validation
✓ Show response handling

STRUCTURE - Follow this EXACT pattern:

sequenceDiagram
    participant User as 👤 User
    participant Frontend as [Actual Frontend File]
    participant Router as [Actual Route File]
    participant Service1 as [Actual Service 1]
    participant Service2 as [Actual Service 2]
    participant Database as 💾 Database
    participant ExternalAPI as 🌐 External API
    
    Note over User,Frontend: User Interaction Phase
    User->>Frontend: Initial Action
    Frontend->>Frontend: Validate Input
    Frontend->>Router: POST /api/endpoint {data}
    
    Note over Router,Service1: Processing Phase
    Router->>Router: Authenticate Request
    Router->>Service1: process_request(data)
    Service1->>Service2: transform_data(data)
    Service2->>Database: SELECT * FROM table
    Database-->>Service2: Return rows
    Service2->>ExternalAPI: GET /external/data
    ExternalAPI-->>Service2: API Response
    
    Note over Service2,Router: Response Phase
    Service2-->>Service1: Processed Data
    Service1-->>Router: Result
    Router-->>Frontend: JSON Response
    Frontend-->>User: Display Result
    
    Note over User,Database: Error Handling
    Router->>Router: Validate Token
    alt Invalid Token
        Router-->>Frontend: 401 Unauthorized
        Frontend-->>User: Show Login
    end

CRITICAL: Replace ALL bracketed items with ACTUAL filenames from repo!
Include: auth flow, data processing, database operations, API calls, error handling

NOW CREATE YOUR COMPREHENSIVE DIAGRAM WITH 20-30+ STEPS:
""",
        
        "component": """
CREATE A COMPREHENSIVE ARCHITECTURE/COMPONENT DIAGRAM

REQUIREMENTS:
✓ Include ALL major files (minimum 25-40 components)
✓ Show complete folder structure with subgraphs
✓ Include frontend, backend, database, external services
✓ Show ALL connections between components
✓ Include configuration files, utilities, helpers
✓ Show data flow with labeled arrows

MANDATORY STRUCTURE:

flowchart TB
    %% Define ALL components first
    
    subgraph Frontend ["🎨 Frontend (Streamlit/React/Vue)"]
        subgraph Pages ["pages/"]
            page1["[actual_page_1.py]"]
            page2["[actual_page_2.py]"]
            page3["[actual_page_3.py]"]
            %% ADD ALL PAGE FILES
        end
        
        subgraph Components ["components/"]
            comp1["[actual_component_1.py]"]
            comp2["[actual_component_2.py]"]
            comp3["[actual_component_3.py]"]
            %% ADD ALL COMPONENT FILES
        end
        
        subgraph FrontendUtils ["utils/"]
            futil1["[actual_util_1.py]"]
            futil2["[actual_util_2.py]"]
            %% ADD ALL UTILITY FILES
        end
    end
    
    subgraph Backend ["⚙️ Backend (FastAPI/Flask/Django)"]
        subgraph Routes ["routes/"]
            route1["[actual_route_1.py]"]
            route2["[actual_route_2.py]"]
            route3["[actual_route_3.py]"]
            %% ADD ALL ROUTE FILES
        end
        
        subgraph Services ["services/"]
            service1["[actual_service_1.py]"]
            service2["[actual_service_2.py]"]
            service3["[actual_service_3.py]"]
            %% ADD ALL SERVICE FILES
        end
        
        subgraph Models ["models/"]
            model1["[actual_model_1.py]"]
            model2["[actual_model_2.py]"]
            %% ADD ALL MODEL FILES
        end
        
        subgraph BackendUtils ["utils/"]
            butil1["[actual_util_1.py]"]
            butil2["[actual_util_2.py]"]
            %% ADD ALL UTILITY FILES
        end
        
        config["config.py / .env"]
        main["main.py / app.py"]
    end
    
    subgraph Database ["💾 Database Layer"]
        db1[("PostgreSQL / MongoDB")]
        db2[("Redis Cache")]
        db3[("File Storage")]
    end
    
    subgraph External ["🌐 External Services"]
        api1["GitHub API"]
        api2["OpenAI API"]
        api3["Other APIs"]
    end
    
    %% Frontend Connections (SHOW ALL)
    page1 --> comp1
    page1 --> comp2
    page2 --> comp1
    page2 --> comp3
    page3 --> comp2
    comp1 --> futil1
    comp2 --> futil2
    
    %% Frontend to Backend (SHOW ALL)
    page1 --> route1
    page2 --> route2
    page3 --> route3
    comp1 --> route1
    
    %% Backend Internal (SHOW ALL)
    route1 --> service1
    route2 --> service2
    route3 --> service1
    route3 --> service3
    service1 --> model1
    service2 --> model2
    service1 --> butil1
    service2 --> butil2
    main --> route1
    main --> route2
    main --> route3
    config --> service1
    config --> service2
    
    %% Database Connections (SHOW ALL)
    service1 --> db1
    service2 --> db1
    service1 --> db2
    model1 --> db1
    model2 --> db1
    
    %% External API Connections (SHOW ALL)
    service1 --> api1
    service2 --> api2
    service3 --> api3

CRITICAL RULES:
1. Replace ALL [actual_*] with REAL filenames from the repo
2. Include EVERY major file - don't skip any
3. Show EVERY important connection
4. If repo has 30 files, show 30+ nodes
5. Add comments showing where to add more

NOW CREATE YOUR COMPREHENSIVE DIAGRAM WITH 30-50+ COMPONENTS:
""",
        
        "database": """
CREATE A COMPLETE DATABASE/ER DIAGRAM

REQUIREMENTS:
✓ Include ALL tables/collections found in models
✓ Show ALL relationships (1:1, 1:N, M:N)
✓ Include ALL fields with types
✓ Show indexes, primary keys, foreign keys
✓ Include junction tables

STRUCTURE - Follow this pattern:

erDiagram
    %% Define ALL entities
    
    USER ||--o{ ORDER : places
    USER ||--o{ PROFILE : has
    USER ||--o{ SESSION : creates
    USER }|--|| ROLE : has
    
    ORDER ||--|{ ORDER_ITEM : contains
    ORDER ||--o{ PAYMENT : has
    ORDER }o--|| SHIPPING : requires
    
    PRODUCT ||--o{ ORDER_ITEM : includes
    PRODUCT }o--|| CATEGORY : belongs_to
    PRODUCT ||--o{ REVIEW : has
    PRODUCT ||--o{ INVENTORY : tracks
    
    %% Define complete schemas
    USER {
        uuid id PK "Primary Key"
        string email UK "Unique"
        string username UK "Unique"
        string password_hash
        string first_name
        string last_name
        string phone
        datetime created_at
        datetime updated_at
        datetime last_login
        boolean is_active
        boolean is_verified
        uuid role_id FK
    }
    
    PROFILE {
        uuid id PK
        uuid user_id FK
        text bio
        string avatar_url
        json preferences
        json settings
        datetime created_at
        datetime updated_at
    }
    
    ORDER {
        uuid id PK
        uuid user_id FK
        decimal total_amount
        string currency
        string status
        string payment_status
        datetime order_date
        datetime shipped_date
        datetime delivered_date
        text notes
    }
    
    %% ADD ALL OTHER TABLES WITH COMPLETE FIELDS

CRITICAL: 
- Include MINIMUM 8-12 entities
- Show ALL fields (aim for 8-15 fields per entity)
- Include ALL relationships
- Add field descriptions
- Show cardinality correctly

NOW CREATE YOUR COMPLETE DATABASE DIAGRAM:
""",
        
        "flowchart": """
CREATE A DETAILED PROCESS FLOWCHART

REQUIREMENTS:
✓ Show COMPLETE process from start to end
✓ Include ALL decision points
✓ Show ALL error handling paths
✓ Include validation steps
✓ Show parallel processes if any
✓ Include minimum 20-30 steps

STRUCTURE:

flowchart TD
    Start([🚀 Start Process])
    
    %% Input Phase
    Input[/📥 Receive Input/]
    ValidateInput{✅ Validate Input?}
    
    %% Authentication Phase
    CheckAuth{🔐 Authenticated?}
    Login[🔑 Login User]
    VerifyToken{✅ Valid Token?}
    
    %% Processing Phase
    FetchData[📊 Fetch Data]
    ProcessData[⚙️ Process Data]
    TransformData[🔄 Transform Data]
    ValidateData{✅ Valid Data?}
    
    %% Business Logic Phase
    CheckPermissions{🔒 Has Permissions?}
    ApplyBusinessRules[📋 Apply Rules]
    CalculateResults[🧮 Calculate]
    
    %% Database Phase
    CheckCache{💾 In Cache?}
    ReadCache[📖 Read Cache]
    QueryDB[(🗄️ Query Database)]
    UpdateCache[💾 Update Cache]
    
    %% External API Phase
    NeedExternalData{🌐 Need External?}
    CallExternalAPI[🌍 Call API]
    ProcessResponse[📥 Process Response]
    
    %% Output Phase
    PrepareResponse[📦 Prepare Response]
    SendResponse[📤 Send Response]
    LogSuccess[📝 Log Success]
    Success([✅ Success])
    
    %% Error Handling
    InvalidInput[❌ Invalid Input]
    AuthError[🚫 Auth Failed]
    PermissionError[⛔ No Permission]
    DataError[❌ Data Error]
    APIError[🔴 API Error]
    LogError[📝 Log Error]
    ErrorResponse[⚠️ Error Response]
    End([🏁 End])
    
    %% Flow Connections (SHOW ALL PATHS)
    Start-->Input
    Input-->ValidateInput
    ValidateInput-->|Valid|CheckAuth
    ValidateInput-->|Invalid|InvalidInput
    InvalidInput-->ErrorResponse
    
    CheckAuth-->|Yes|VerifyToken
    CheckAuth-->|No|Login
    Login-->VerifyToken
    VerifyToken-->|Valid|CheckPermissions
    VerifyToken-->|Invalid|AuthError
    AuthError-->ErrorResponse
    
    CheckPermissions-->|Granted|CheckCache
    CheckPermissions-->|Denied|PermissionError
    PermissionError-->ErrorResponse
    
    CheckCache-->|Hit|ReadCache
    CheckCache-->|Miss|QueryDB
    ReadCache-->ProcessData
    QueryDB-->UpdateCache
    UpdateCache-->ProcessData
    
    ProcessData-->TransformData
    TransformData-->ValidateData
    ValidateData-->|Valid|ApplyBusinessRules
    ValidateData-->|Invalid|DataError
    DataError-->ErrorResponse
    
    ApplyBusinessRules-->CalculateResults
    CalculateResults-->NeedExternalData
    NeedExternalData-->|Yes|CallExternalAPI
    NeedExternalData-->|No|PrepareResponse
    
    CallExternalAPI-->ProcessResponse
    ProcessResponse-->PrepareResponse
    
    PrepareResponse-->SendResponse
    SendResponse-->LogSuccess
    LogSuccess-->Success
    Success-->End
    
    ErrorResponse-->LogError
    LogError-->End

CRITICAL: Adapt this pattern to your actual repository's process
Include ALL steps, decisions, and error paths

NOW CREATE YOUR DETAILED FLOWCHART WITH 25-40+ STEPS:
""",
        
        "class": """
CREATE A COMPREHENSIVE CLASS DIAGRAM

REQUIREMENTS:
✓ Include ALL classes found in code
✓ Show ALL methods and properties
✓ Include inheritance relationships
✓ Show composition/aggregation
✓ Include interfaces/abstract classes
✓ Minimum 10-15 classes

STRUCTURE:

classDiagram
    %% Inheritance and Interfaces
    <<interface>> IRepository
    <<abstract>> BaseModel
    <<interface>> IService
    
    IRepository <|.. UserRepository
    IRepository <|.. ProductRepository
    BaseModel <|-- User
    BaseModel <|-- Product
    IService <|.. UserService
    
    %% Main Classes
    class BaseModel {
        <<abstract>>
        +UUID id
        +DateTime created_at
        +DateTime updated_at
        +save()
        +delete()
        +to_dict()
        #validate()
    }
    
    class User {
        +String email
        +String username
        +String password_hash
        +String first_name
        +String last_name
        +Boolean is_active
        +Boolean is_verified
        +List~Order~ orders
        +Profile profile
        +Role role
        +__init__(email, username)
        +verify_password(password)
        +hash_password(password)
        +generate_token()
        +verify_token(token)
        +get_full_name()
        +activate()
        +deactivate()
        +to_public_dict()
    }
    
    class Profile {
        +UUID user_id
        +String bio
        +String avatar_url
        +JSON preferences
        +JSON settings
        +User user
        +__init__(user_id)
        +update_avatar(url)
        +update_bio(bio)
        +get_preferences()
        +set_preference(key, value)
    }
    
    class Order {
        +UUID user_id
        +Decimal total_amount
        +String status
        +DateTime order_date
        +List~OrderItem~ items
        +User user
        +Payment payment
        +__init__(user_id)
        +add_item(product, quantity)
        +remove_item(item_id)
        +calculate_total()
        +submit()
        +cancel()
        +get_status()
    }
    
    class Product {
        +String name
        +Decimal price
        +String description
        +Integer stock
        +UUID category_id
        +Category category
        +List~Review~ reviews
        +__init__(name, price)
        +update_stock(quantity)
        +get_average_rating()
        +is_in_stock()
        +apply_discount(percentage)
    }
    
    class UserRepository {
        -Database db
        +find_by_id(id)
        +find_by_email(email)
        +find_all()
        +create(user_data)
        +update(id, data)
        +delete(id)
        +search(query)
    }
    
    class UserService {
        -UserRepository repo
        -EmailService email_service
        +register(user_data)
        +login(email, password)
        +logout(user_id)
        +update_profile(user_id, data)
        +delete_account(user_id)
        +send_verification(user)
    }
    
    %% Relationships
    User "1" --> "1" Profile : has
    User "1" --> "*" Order : places
    User "*" --> "1" Role : has
    Order "1" --> "*" OrderItem : contains
    Product "1" --> "*" OrderItem : included_in
    Product "*" --> "1" Category : belongs_to
    Product "1" --> "*" Review : has
    UserService --> UserRepository : uses
    UserService --> EmailService : uses
    
    %% ADD MORE CLASSES AND RELATIONSHIPS

CRITICAL:
- Include ALL classes found in models/
- Show ALL methods (public +, private -, protected #)
- Include ALL properties with types
- Show ALL relationships with cardinality
- Add 15-20+ classes for comprehensive view

NOW CREATE YOUR COMPLETE CLASS DIAGRAM:
"""
    }
    
    instruction = specific_instructions.get(diagram_type, specific_instructions["component"])
    
    return base_rules + "\n\n" + instruction


def get_custom_diagram_prompt(user_request: str, repo_context: str) -> str:
    """Get prompt for custom diagrams with comprehensive requirements"""
    
    return f"""
=================================================================
CRITICAL: CREATE A COMPREHENSIVE, DETAILED DIAGRAM
=================================================================

Repository Data:
{repo_context}

User Request: {user_request}

MANDATORY REQUIREMENTS:
1. Include MINIMUM 20-30 components/nodes
2. Use ONLY real filenames from repository
3. Show ALL major relationships
4. Organize with subgraphs by folder
5. Include configuration, utilities, external services
6. No generic/placeholder names

SYNTAX RULES (STRICT):
- Node IDs: only letters, numbers, underscores (NO SPACES)
- Arrows: only --> or -.-> or ==>
- Labels: use square brackets [Label]
- NO markdown code blocks
- Start directly with diagram type

CHOOSE APPROPRIATE TYPE:
- sequenceDiagram: for flows/interactions (15-25 steps minimum)
- flowchart TB: for architecture (25-40 components minimum)
- classDiagram: for classes (12-20 classes minimum)
- erDiagram: for database (8-12 entities minimum)

QUALITY CHECKLIST:
☐ Used 20+ real filenames from repo
☐ Showed all major folders as subgraphs
☐ Included all services, routes, models
☐ Showed external dependencies
☐ Added configuration files
☐ Included error handling/edge cases
☐ Showed all important connections

NOW CREATE A COMPREHENSIVE, PRODUCTION-QUALITY DIAGRAM:
"""