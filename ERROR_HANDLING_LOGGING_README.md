# Error Handling & Logging Overview

This README summarizes the changes made to the e-voting app for structured error handling and logging, what you should see in the UI, and how to quickly test the main flows.

---

## 1. What Changed (High Level)

- **Centralized exceptions**
  - New domain-specific exception hierarchy under [evoting-app-backend/core/exceptions.py](evoting-app-backend/core/exceptions.py).
  - Services raise clear exceptions like `InvalidCredentialsException`, `ResourceNotFoundException`, `BusinessRuleException`, `PollNotOpenException`, instead of returning ad-hoc error strings.

- **Standardized API responses**
  - Successful responses in views now generally follow:
    - `{"success": true, "data": { ... useful payload ... }}`
  - Errors are wrapped consistently using helper functions in [evoting-app-backend/core/response_formatter.py](evoting-app-backend/core/response_formatter.py), e.g.:
    - `{"success": false, "error": {"code": "SOME_CODE", "message": "Human readable message"}}`
  - Existing frontend remains compatible because the frontend API layer unwraps `data` when `success === true`.

- **Request correlation and logging**
  - New middleware in [evoting-app-backend/evoting/settings.py](evoting-app-backend/evoting/settings.py) wires in `core.middleware.RequestLoggingMiddleware`.
  - Each request gets a **correlation ID** that appears in logs and can be used to trace a request end-to-end.

- **Structured application logging**
  - Logging configuration added in `LOGGING` section of [evoting-app-backend/evoting/settings.py](evoting-app-backend/evoting/settings.py).
  - Multiple rotating log files (exact filenames depend on the config), for example:
    - General debug information
    - Errors and stack traces
    - Audit/security/performance focused logs
  - Service classes in accounts, elections, voting, and audit apps now log key events and validation failures.

- **Serializer-level validation logging**
  - Key serializers (voter registration, candidate creation, poll creation, vote casting) log notable validation failures (duplicate IDs, underage voters/candidates, invalid references, inconsistent vote payloads).

---

## 2. What You Should See in the UI

When using the web interface (Next.js frontend in evoting-app-frontend):

- **On success**
  - Flows like admin login, voter login, registration, poll creation, and casting votes should behave as before:
    - You will be logged in and redirected appropriately.
    - New voters receive a voter card number.
    - Admin actions (create/deactivate/verify) and poll lifecycle actions work normally.

- **On validation or business errors**
  - When you intentionally cause an error (wrong password, underage registration, invalid poll transition, etc.):
    - You should see clear, human-readable error messages in the UI.
    - For field-level errors (e.g., `national_id` duplicate), messages still appear near the relevant fields.
    - For process errors (e.g., poll not open, station not assigned), a general error message should be shown.

- **On more serious/internal errors**
  - If an unexpected error happens on the server:
    - The UI will typically show a generic error message (for security), while details are recorded in the backend logs.
    - You might see a toast or inline message such as “Something went wrong. Please try again later.”

The goal is **predictable, structured errors for machines and clear messages for humans**, without breaking the existing UI.

---

## 3. How to Test Using the Interface (UI)

Below are quick manual test scenarios you can run through the existing UI to exercise the new error handling and logging.

### 3.1 Preparation

1. **Backend**
   - In a terminal at `evoting-app-backend` with your virtualenv activated:
     - Install dependencies (once): `pip install -r requirements.txt`
     - Apply migrations: `python manage.py migrate`
     - Run server: `python manage.py runserver`

2. **Frontend**
   - In another terminal at `evoting-app-frontend`:
     - Install dependencies (once): `npm install`
     - Run dev server: `npm run dev`

3. Open the frontend URL shown in the terminal (usually `http://localhost:3000`).

### 3.2 Accounts: Login and Registration

- **Admin login**
  - Use a valid seeded admin user.
    - Expect: Successful login, tokens stored in localStorage, redirect to admin dashboard.
  - Try a wrong password.
    - Expect: UI shows an “invalid credentials” style message. Logs contain an `InvalidCredentialsException` entry.
  - Try logging in with a deactivated admin.
    - Expect: UI shows a message that the account is deactivated or access is denied.

- **Voter registration**
  - Register a valid new voter.
    - Expect: Success message, display of a voter card number.
  - Register with the **same national ID** again.
    - Expect: Field-level error near national ID, corresponding to a duplicate record.
    - Logs should contain a warning/info entry about duplicate national ID.
  - Register with an **underage date of birth**.
    - Expect: Error indicating the voter is underage.
  - Register with an **invalid station ID**.
    - Expect: Error indicating the station is invalid.

- **Voter login**
  - Log in as a newly registered (and verified) voter.
    - Expect: Normal login success.
  - Attempt login before verification (if your flow allows this scenario).
    - Expect: Error indicating account not yet verified.

### 3.3 Elections: Poll Lifecycle and Business Rules

- **Poll creation**
  - Create a poll with valid positions and stations.
    - Expect: Poll appears in the list, no errors.
  - Create a poll with an invalid position or station ID.
    - Expect: UI shows a validation error; backend logs record the invalid reference.

- **Poll status transitions**
  - From the admin interface, open a poll and toggle its status.
    - Valid transition (e.g., DRAFT → OPEN after proper setup): success message.
    - Invalid scenario, e.g.:
      - Try to modify a poll already in OPEN state.
      - Try to open a poll without assigned candidates.
    - Expect: Clear error messages in UI indicating why the action is not allowed; logs record a business rule exception.

### 3.4 Voting: Casting a Vote

- As a voter, navigate to the voting area.

- **Valid vote**
  - Select an open poll, choose a candidate, and cast a vote.
    - Expect: Confirmation message and a vote reference.
    - Logs: A successful voting event is logged with poll, voter, and station context (no sensitive personal data beyond what is already stored).

- **Invalid vote scenarios**
  - Try to vote in a **closed or not-yet-open** poll.
    - Expect: UI error about the poll not being open.
  - Try to cast a vote for a **position or candidate not assigned** to that poll.
    - Expect: error explaining the inconsistency.
  - If multiple voting per voter per poll is prevented by business rules, attempt to vote again in the same poll.
    - Expect: clear “already voted” style error.

### 3.5 Audit and Logs

- After performing the above actions, from the admin interface check the **audit log** view.
  - Expect: New entries for logins, registrations, management actions, and voting where audit logging is configured.

- On the backend, open the log directory configured in [evoting-app-backend/evoting/settings.py](evoting-app-backend/evoting/settings.py).
  - Confirm that:
    - Requests and responses (at least summary info) are logged with correlation IDs.
    - Exceptions and stack traces appear in an error-oriented log file.
    - Audit and security events appear in their dedicated logs if configured.

---

## 4. Explanation of the Error Handling & Logging Design

- **Layered responsibility**
  - **Serializers**: Validate input data and raise `ValidationError` with field-specific feedback; log notable invalid conditions (duplicates, under/over-age issues, invalid IDs).
  - **Services**: Contain business logic. They:
    - Perform lookups and state checks.
    - Raise domain exceptions (`ResourceNotFoundException`, `BusinessRuleException`, `PollNotOpenException`, etc.) when a rule is violated.
    - Log key events (e.g., authentication attempts, poll state changes, vote casting) with structured context using helpers from `core.logging_config`.
  - **Views**: Translate domain exceptions into HTTP responses using `success_response` and `error_response_from_exception` from [evoting-app-backend/core/response_formatter.py](evoting-app-backend/core/response_formatter.py).

- **Consistent response format**
  - For success, the frontend usually gets:
    - `success: true` plus a `data` object containing whatever the UI needs.
  - For errors, the frontend gets:
    - `success: false`
    - `error.code`: a short, machine-friendly identifier.
    - `error.message`: a human-readable message suitable for display.
  - The frontend’s shared API helper unwraps `data` on success so existing components can remain mostly unchanged.

- **Traceability and observability**
  - Middleware adds a correlation ID to each request, which is logged alongside service and view logs.
  - This makes it possible to trace a single user action from the HTTP request, through services, to the database and back.
  - Domain-specific exceptions and structured logs make it easier to:
    - Debug issues in production.
    - Understand why a particular action was rejected.
    - Analyze voting and management activity through audit logs.

In summary, the changes aim to make the system **more robust, diagnosable, and user-friendly** without disrupting existing UI flows. You now have predictable error shapes for clients, detailed logs for operators, and clearly separated responsibilities across serializers, services, and views.
