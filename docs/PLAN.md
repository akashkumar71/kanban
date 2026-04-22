# Detailed Project Plan

## Part 1: Plan

### Description
Enrich this PLAN.md document with detailed substeps, checklists, tests, and success criteria for each part (2-10). Create an AGENTS.md file in the frontend/ directory describing the existing code. Ensure the user reviews and approves the enriched plan before proceeding.

### Substeps
1. Review existing frontend code structure and components.
2. Document the frontend code in frontend/AGENTS.md, including component purposes, file structure, and current functionality.
3. Break down each subsequent part (2-10) into detailed, actionable substeps.
4. Add checklists with markdown checkboxes for tracking progress.
5. Define appropriate tests (unit, integration, manual) and success criteria for each part.
6. Present the enriched plan to the user for approval.

### Checklist
- [x] Create frontend/AGENTS.md describing existing code
- [ ] Enrich PLAN.md with detailed substeps, checklists, tests, and success criteria for all parts
- [ ] User reviews and approves the enriched plan

### Tests
- Manual review: Verify frontend/AGENTS.md accurately describes the code
- Manual review: Ensure PLAN.md is comprehensive and follows the structure

### Success Criteria
- frontend/AGENTS.md exists and provides clear documentation of the existing frontend code
- PLAN.md is enriched with details for all parts, including substeps, checklists, tests, and success criteria
- User explicitly approves the plan via confirmation

## Part 2: Scaffolding

### Description
Set up the Docker infrastructure, initialize the FastAPI backend in backend/, and create start/stop scripts in scripts/. The setup should serve example static HTML at / and include a test API endpoint to confirm functionality.

### Substeps
1. Create a Dockerfile that packages the entire application, using uv for Python dependencies.
2. Initialize backend/ with a basic FastAPI application that serves static HTML at / and exposes a simple API endpoint (e.g., GET /api/test returning JSON).
3. Install FastAPI and uvicorn in the backend using uv.
4. Create start and stop scripts in scripts/ for Mac (bash), PC (PowerShell/batch), and Linux (bash), handling Docker container lifecycle.
5. Test the setup locally: Build and run the Docker container, verify HTML is served at /, and API endpoint responds correctly.

### Checklist
- [ ] Dockerfile created with proper configuration
- [ ] FastAPI backend initialized in backend/ with static HTML serving and test API
- [ ] Python dependencies installed via uv
- [ ] Start/stop scripts created for Mac, PC, Linux
- [ ] Local Docker test: Container builds and runs successfully
- [ ] HTML served at / in browser
- [ ] API endpoint (/api/test) returns expected JSON

### Tests
- Unit test: FastAPI app starts without errors
- Integration test: API endpoint responds with correct JSON
- Manual test: Access / in browser to see HTML
- Manual test: Run start script, verify container is running; run stop script, verify container stops

### Success Criteria
- Docker container builds and runs without errors
- Visiting / displays the example static HTML
- API call to /api/test returns valid JSON response
- Start/stop scripts work on the local OS (Windows in this case)

## Part 3: Add in Frontend

### Description
Update the setup to build and serve the NextJS frontend statically, displaying the demo Kanban board at /. Ensure comprehensive unit and integration tests pass.

### Substeps
1. Configure the backend to serve the built NextJS static files at / instead of example HTML.
2. Update Dockerfile to include NextJS build process.
3. Build the NextJS app statically during Docker build.
4. Ensure the Kanban board demo is accessible at /.
5. Run and verify all existing unit tests (Vitest) and integration tests (Playwright) pass in the containerized environment.

### Checklist
- [x] Backend updated to serve NextJS static build
- [x] Dockerfile updated for NextJS build
- [x] NextJS app builds successfully in Docker
- [x] Kanban board demo displays at /
- [x] All unit tests (Vitest) pass
- [x] All integration tests (Playwright) pass

### Tests
- Unit tests: Run Vitest on Kanban components and logic
- Integration tests: Run Playwright E2E tests for Kanban functionality
- Manual test: Access / in browser, verify Kanban board renders and is interactive

### Success Criteria
- Docker container serves the NextJS-built Kanban demo at /
- All tests pass without failures
- Kanban board is fully functional (drag-drop, editing, etc.) as in the demo

## Part 4: Add in a Fake User Sign In Experience

### Description
Implement a fake sign-in page at / that requires dummy credentials ("user", "password") to access the Kanban board. Include logout functionality. Add comprehensive tests.

### Substeps
1. Create a sign-in page/component in NextJS that prompts for username/password.
2. Implement client-side validation for dummy credentials.
3. Upon successful "login", redirect to Kanban board; store session state (e.g., in localStorage).
4. Add logout button/functionality to return to sign-in.
5. Update tests to cover sign-in flow, logout, and access control.

### Checklist
- [x] Sign-in page created with form for username/password
- [x] Validation implemented for "user"/"password"
- [x] Successful login redirects to Kanban
- [x] Session state managed (e.g., localStorage)
- [x] Logout functionality added
- [x] Unit tests for sign-in logic
- [x] Integration tests for full sign-in/logout flow

### Tests
- Unit tests: Validate credential checking logic
- Integration tests: Playwright tests for sign-in form submission, redirect, logout, and access denial without login
- Manual test: Attempt access without login (should redirect to sign-in), login with correct/incorrect credentials, logout

### Success Criteria
- / requires sign-in; invalid credentials denied
- Valid login ("user", "password") grants access to Kanban
- Logout returns to sign-in page
- All new and existing tests pass

## Part 5: Database Modeling

### Description
Design and document a database schema for the Kanban data (boards, columns, cards) using SQLite. Save as JSON and document in docs/. Get user sign-off.

### Substeps
1. Analyze Kanban data structure from frontend code (boards, columns, cards).
2. Design SQLite schema with tables for users, boards, columns, cards.
3. Create a JSON representation of the schema.
4. Document the approach in docs/DATABASE.md, including migration strategy.
5. Present to user for approval.

### Checklist
- [x] Schema designed for users, boards, columns, cards
- [x] JSON schema file created
- [x] docs/DATABASE.md created with documentation
- [x] User reviews and approves schema

### Tests
- Manual review: Validate schema covers all Kanban entities and relationships

### Success Criteria
- JSON schema accurately represents Kanban data model
- Documentation in docs/ is clear and complete
- User explicitly approves the database design

## Part 6: Backend

### Description
Add API routes to the FastAPI backend for reading and modifying Kanban data for a user. Implement SQLite database creation and operations. Thorough backend unit tests.

### Substeps
1. Set up SQLite database connection in FastAPI.
2. Create database tables based on approved schema.
3. Implement API routes: GET /api/kanban (get board), POST /api/kanban (update board), etc.
4. Add user authentication context (hardcoded for MVP).
5. Write comprehensive unit tests for API routes and database operations.

### Checklist
- [x] SQLite setup in FastAPI
- [x] Database tables created on startup
- [x] API routes implemented for Kanban CRUD
- [x] User context handled
- [x] Unit tests written and passing for all routes
- [x] Unit tests for database operations

### Tests
- Unit tests: Test each API route with mock data
- Unit tests: Test database create/read/update operations
- Integration test: Full API flow with database

### Success Criteria
- API routes return correct data for valid requests
- Database persists changes correctly
- All unit tests pass
- Database created automatically if not exists

## Part 7: Frontend + Backend

### Description
Integrate the frontend to use the backend API for persistent Kanban data. Ensure thorough testing of the full stack.

### Substeps
1. Update frontend to fetch Kanban data from API on load.
2. Implement API calls for updating board (moves, edits).
3. Handle API responses and update UI state.
4. Add error handling for API failures.
5. Run comprehensive tests: unit, integration, E2E.

### Checklist
- [x] Frontend fetches data from /api/kanban
- [x] API calls for updates implemented
- [x] UI updates on API responses
- [x] Error handling added
- [x] Unit tests for API integration
- [x] Integration tests for full flow
- [x] E2E tests with Playwright

### Tests
- Unit tests: Mock API calls in components
- Integration tests: Frontend-backend interaction
- E2E tests: Full user flows (load board, move cards, persist changes)

### Success Criteria
- Kanban board loads data from backend
- Changes persist via API
- UI refreshes correctly after updates
- All tests pass
- No data loss on refresh

## Part 8: AI Connectivity

### Description
Enable backend AI calls via OpenRouter. Test with a simple query.

### Substeps
1. Install OpenRouter SDK or use requests for API calls.
2. Configure OPENROUTER_API_KEY from .env.
3. Implement a test endpoint that calls AI with "2+2" and returns response.
4. Test connectivity and response parsing.

### Checklist
- [x] OpenRouter integration added
- [x] API key configured
- [x] Test endpoint created (/api/ai-test)
- [x] "2+2" test succeeds

### Tests
- Unit test: AI call function
- Manual test: Call /api/ai-test, verify response

### Success Criteria
- AI API call works and returns expected response for simple query
- No authentication or rate limit errors

## Part 9: AI Chat Backend

### Description
Extend AI integration to handle Kanban context and user questions with structured outputs for responses and optional board updates.

### Substeps
1. Update AI call to include Kanban JSON, user question, conversation history.
2. Configure structured outputs: response text + optional Kanban update.
3. Parse AI response and apply updates to database if present.
4. Add API endpoint for chat (/api/chat).
5. Thorough tests for parsing and updates.

### Checklist
- [x] AI prompt includes Kanban data
- [x] Structured outputs configured
- [x] Response parsing implemented
- [x] Database updates from AI
- [x] /api/chat endpoint
- [x] Unit tests for parsing
- [x] Integration tests for full chat flow

### Tests
- Unit tests: Parse structured outputs
- Integration tests: Chat API with mock AI
- Manual test: Simulate chat, verify board updates

### Success Criteria
- AI responds to questions with context
- Optional board updates applied correctly
- All tests pass

## Part 10: AI Chat UI

### Description
Add a sidebar widget for AI chat in the UI. Allow AI to update Kanban and auto-refresh UI.

### Substeps
1. Create sidebar component for chat input/output.
2. Integrate with /api/chat endpoint.
3. Display conversation history.
4. On AI board update, refresh Kanban UI.
5. Style with color scheme; ensure responsive.

### Checklist
- [x] Sidebar chat component created
- [x] Chat API integration
- [x] Conversation history displayed
- [x] UI auto-refreshes on board updates
- [x] Styling applied
- [x] Unit tests for component
- [x] E2E tests for chat flow

### Tests
- Unit tests: Chat component logic
- E2E tests: Full chat interaction, board updates
- Manual test: Chat with AI, observe UI changes

### Success Criteria
- Sidebar chat functional
- AI responses displayed
- Board updates trigger UI refresh
- All tests pass
- UI is beautiful and matches design