# 🛠️ Android Development Skills & Protocols

## 📌 Project Context
*   **Environment**: Native Android (Kotlin).
*   **Build System**: Gradle Kotlin DSL (`.kts`) with Version Catalogs (`libs.versions.toml`).
*   **UI Paradigm**: Jetpack Compose (Material3).
*   **Annotation Processing**: KSP (Kotlin Symbol Processing).
*   **Database**: Local SQLite/Room (detected via `kls_database.db`).

---

## 1. 🏗️ Modern Architecture (MVVM + Clean)
Follow the **Unidirectional Data Flow (UDF)** pattern.

### Layer Separation
1.  **UI Layer (Presentation)**
    *   **Components**: Composable functions (`@Composable`).
    *   **State Holder**: `ViewModel` extending `androidx.lifecycle.ViewModel`.
    *   **Observation**: Use `collectAsStateWithLifecycle()` to observe `StateFlow` from the ViewModel.
2.  **Domain Layer (Optional but Recommended)**
    *   **UseCases**: Single-responsibility classes (e.g., `GetUserDataUseCase`) that contain business logic.
3.  **Data Layer**
    *   **Repository**: The single source of truth. It mediates between Local Data (Room) and Remote Data (Retrofit).
    *   **Data Sources**: DAOs (Room) or API Services (Retrofit).

### File Directory Standard
Although your tree shows `src/main/java`, modern Kotlin best practice prefers:
`src/main/kotlin/com/yourpackage/`
├── `ui/` (Screens, ViewModels, Theme)
├── `data/` (Repository impl, API, Database)
├── `domain/` (Models, Repository interfaces, UseCases)
└── `di/` (Hilt Modules)

---

## 2. 🎨 Modern UI: Jetpack Compose
Avoid XML Layouts. All UI should be written in Kotlin.

### Essential Patterns
*   **State Hoisting**: Pass values *down* to Composables, pass events (lambdas) *up* to the parent/ViewModel.
*   **Material Design 3**: Use `androidx.compose.material3`.
    *   *Usage*: Use `Scaffold` for basic screen structure (TopBar, FAB, Content).
*   **Previews**: Use `@Preview(showBackground = true)` to visualize components without running the app.

### Type-Safe Navigation (Latest Protocol)
*Deprecated*: XML Navigation Graphs.
*Current*: **Navigation Compose** with Type Safety (Kotlin Serialization).

**Code Example:**
```kotlin
@Serializable object HomeScreen
@Serializable data class DetailScreen(val id: Int)

// In NavHost
composable<DetailScreen> { backStackEntry ->
    val args = backStackEntry.toRoute<DetailScreen>()
    DetailScreen(id = args.id)
}