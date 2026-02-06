# System Design Diagrams

## 1. Data Flow Diagram (DFD)

### Level 0 (Context Diagram)
```mermaid
graph TD
    User[Normal User] -->|Submit Report, Login| System[Garbage Management System]
    Auth[Authority User] -->|Manage Locations, View Reports, Login| System
    Camera[CCTV Camera] -->|Stream Video, Detect Events| System
    System -->|Dashboard, Status| User
    System -->|Analytics, Evidence, Alerts| Auth
```

### Level 1 DFD
```mermaid
graph TD
    User[Normal User] -->|1. Credentials| AuthProc[Authentication Process]
    Auth[Authority User] -->|1. Credentials| AuthProc
    
    User -->|2. Report Details| ReportProc[Reporting Process]
    
    Auth -->|3. Location Data| LocProc[Location Management]
    
    Camera[CCTV Camera] -->|4. Video Feed| DetectProc[Event Detection Process]
    
    AuthProc -->|User Session| UserStore[(User DB)]
    AuthProc -->|Auth Session| AuthStore[(Authority DB)]
    
    ReportProc -->|Report Data| ReportStore[(Garbage Report DB)]
    ReportProc -->|Evidence Files| FileStore[(File Storage)]
    
    LocProc -->|Location Info| LocStore[(Location DB)]
    
    DetectProc -->|Event Data| EventStore[(Dumping Event DB)]
    DetectProc -->|Video/Plate Images| FileStore
    
    Auth -->|5. View Analytics| AnalyticsProc[Analytics Process]
    ReportStore --> AnalyticsProc
    EventStore --> AnalyticsProc
    LocStore --> AnalyticsProc
```

## 2. UML Class Diagram
```mermaid
classDiagram
    class Normal_user {
        +int id
        +String fullname
        +String username
        +String email
        +String phone
        +Image profile
        +String password
        +register()
        +login()
        +submit_report()
    }

    class Authority_user {
        +int id
        +String first_name
        +String last_name
        +String auth_id
        +String email
        +String phone
        +Image profile_image
        +String password
        +login()
        +manage_locations()
        +view_reports()
    }

    class LegalDumpingLocation {
        +int id
        +String name
        +String location_type
        +float latitude
        +float longitude
        +boolean is_active
        +datetime created_at
        +soft_delete()
    }

    class Camera {
        +int id
        +String camera_id
        +String location
    }

    class DumpingEvent {
        +int id
        +String event_id
        +datetime timestamp
        +String actor
        +File dumping_video
        +String illegal_location
    }

    class NumberPlate {
        +int id
        +Image image
        +datetime timestamp
        +String plate_text
    }

    class GarbageReport {
        +int id
        +String location
        +String description
        +String severity
        +datetime created_at
    }

    class GarbageEvidence {
        +int id
        +File file
        +datetime uploaded_at
    }

    Normal_user "1" -- "*" GarbageReport : submits
    Authority_user "1" -- "*" LegalDumpingLocation : adds
    GarbageReport "1" -- "*" GarbageEvidence : has
    Camera "1" -- "*" DumpingEvent : captures
    DumpingEvent "1" -- "*" NumberPlate : has
    Authority_user ..> DumpingEvent : monitors
    Authority_user ..> GarbageReport : reviews
```

## 3. UML Use Case Diagram
```mermaid
graph LR
    User((Normal User))
    Auth((Authority User))
    Cam((CCTV System))

    subgraph System ["Garbage Management System"]
        direction TB
        UC1(Register)
        UC2(Login)
        UC3(View Dashboard)
        UC4(Submit Garbage Report)
        UC5(Upload Evidence)
        UC6(Chat with Bot)
        UC7(Manage Dumping Locations)
        UC8(View Analytics)
        UC9(View CCTV Events)
        UC10(Review Reports)
        UC11(Process Video Feed)
        UC12(Detect Dumping)
    end

    User --> UC1
    User --> UC2
    User --> UC3
    User --> UC4
    UC4 -.-> UC5
    User --> UC6

    Auth --> UC2
    Auth --> UC3
    Auth --> UC7
    Auth --> UC8
    Auth --> UC9
    Auth --> UC10

    Cam --> UC11
    UC11 -.-> UC12
```

## 4. UML State Chart Diagram (Report Lifecycle)
```mermaid
stateDiagram-v2
    [*] --> Draft : User starts report
    Draft --> Submitted : User submits report
    Submitted --> Reviewed : Authority views report
    Reviewed --> [*]
    
    state Submitted {
        [*] --> Stored
        Stored --> EvidenceUploaded : Files processing
        EvidenceUploaded --> [*]
    }
```

## 5. UML State Chart Diagram (Dumping Event)
```mermaid
stateDiagram-v2
    [*] --> Monitoring : Camera Active
    Monitoring --> EventDetected : Motion/Object Detection
    EventDetected --> Recording : Video Capture Start
    Recording --> Processing : Video Capture End
    Processing --> PlateDetection : Analyze Frames
    PlateDetection --> Saved : Data Persisted
    Saved --> [*]
```
