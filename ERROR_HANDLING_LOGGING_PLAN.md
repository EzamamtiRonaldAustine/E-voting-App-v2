# Error Handling & Logging Implementation Plan
**E-Voting Backend Enhancement**  
**Date:** March 19, 2026

---

## 📊 File Inventory Summary

### Total Files to Enhance: **12 Files**

#### Services Layer (4 files)
```
1. evoting-app-backend/accounts/services.py
2. evoting-app-backend/elections/services.py
3. evoting-app-backend/voting/services.py
4. evoting-app-backend/audit/services.py
```

#### Views Layer (4 files)
```
1. evoting-app-backend/accounts/views.py
2. evoting-app-backend/elections/views.py
3. evoting-app-backend/voting/views.py
4. evoting-app-backend/audit/views.py
```

#### Serializers Layer (4 files)
```
1. evoting-app-backend/accounts/serializers.py
2. evoting-app-backend/elections/serializers.py
3. evoting-app-backend/voting/serializers.py
4. evoting-app-backend/audit/serializers.py
```

---

## 🔍 Current State Analysis

### Services Layer - Current State
✅ **What's Good:**
- Basic try-catch for specific exceptions (User.DoesNotExist)
- Audit logging is implemented
- Service classes are properly structured

❌ **What's Missing:**
- Centralized exception handling
- Structured logging with log levels
- Error context capture
- Exception chaining
- Resource cleanup patterns
- Validation error handling before DB operations
- Transaction rollback logging

### Views Layer - Current State
✅ **What's Good:**
- Basic REST framework integration
- Permission classes implemented
- Serializer validation used

❌ **What's Missing:**
- Comprehensive exception handling
- Request/response logging
- Error context with request details
- Proper HTTP status code mapping
- Request correlation IDs
- Logging of failed validations
- Performance monitoring

### Serializers Layer - Current State
✅ **What's Good:**
- Good validation logic present
- Custom validation methods implemented
- Clear validation error messages

❌ **What's Missing:**
- Validation failure logging
- Context-rich error information
- Structured error response format
- Validation error tracking
- Performance metrics

---

## 🏗️ Implementation Architecture

### Layer 1: Custom Exceptions (New)
Create: `evoting-app-backend/core/exceptions.py`

**Exception Hierarchy:**
```
EVotingException (Base)
├── AuthenticationException
│   ├── InvalidCredentialsException
│   ├── AccountDeactivatedException
│   └── AccountNotVerifiedException
├── ValidationException
│   ├── DuplicateRecordException
│   └── InvalidStateException
├── AuthorizationException
│   └── InsufficientPermissionsException
├── ResourceException
│   ├── ResourceNotFoundException
│   └── ResourceConflictException
├── BusinessRuleException
│   ├── VoterAlreadyVotedException
│   ├── PollNotOpenException
│   └── InvalidElectionStateException
└── DatabaseException
    ├── DatabaseUnavailableException
    └── TransactionFailedException
```

### Layer 2: Logging Configuration (New)
Create: `evoting-app-backend/core/logging_config.py`

**Features:**
- Centralized logger setup
- Structured logging format (JSON-compatible)
- Log rotation by size and time
- Separate logs by component
- Sensitive data masking
- Request correlation ID generation

**Log Files:**
```
logs/
├── debug.log          (All events, DEBUG level)
├── info.log           (General info, INFO level)
├── errors.log         (Errors only, ERROR level)
├── audit.log          (Audit trail, INFO level)
├── security.log       (Security events, WARNING level)
└── performance.log    (Performance metrics, INFO level)
```

### Layer 3: Decorators & Utilities (New)
Create: `evoting-app-backend/core/decorators.py`
Create: `evoting-app-backend/core/error_handlers.py`

**Decorators:**
- `@log_method_execution` - Logs entry, exit, and execution time
- `@handle_exceptions` - Wraps exceptions with proper logging
- `@log_database_operation` - Tracks DB operations
- `@rate_limit_check` - Log rate limiting attempts
- `@validate_permissions` - Log permission checks

### Layer 4: Error Response Formatter (New)
Create: `evoting-app-backend/core/response_formatter.py`

**Standardized Error Response:**
```json
{
  "success": false,
  "error": {
    "code": "INVALID_CREDENTIALS",
    "message": "Username or password is incorrect",
    "details": {
      "field": "username",
      "reason": "not_found"
    },
    "correlation_id": "abc123def456",
    "timestamp": "2026-03-19T10:30:45Z"
  }
}
```

### Layer 5: Middleware (New)
Create: `evoting-app-backend/core/middleware.py`

**Features:**
- Request logging (method, path, user, IP)
- Response logging (status, duration)
- Error tracking
- Correlation ID generation and tracking
- Performance metrics
- Security event tracking

---

## 📋 Implementation Phases

### Phase 1: Foundation Setup (Days 1-2)
**Objective:** Create core infrastructure

1. **Create Core Module Structure**
   - Create `evoting-app-backend/core/` directory
   - Create `__init__.py` files

2. **Implement Custom Exceptions**
   - Define exception hierarchy
   - Add proper docstrings
   - Include error codes (constants)

3. **Implement Logging Configuration**
   - Configure Python logging
   - Setup log formatters
   - Define log rotation policy
   - Create logger factories

4. **Create Decorators & Utilities**
   - Implement execution logging decorator
   - Implement exception handling decorator
   - Create error handler utilities

5. **Create Response Formatter**
   - Standardized error response format
   - Success response wrapper
   - Error code mapping

6. **Create Middleware**
   - Request/response logging
   - Correlation ID generation
   - Performance tracking

**Deliverable:** Foundation infrastructure ready

---

### Phase 2: Services Layer Enhancement (Days 3-4)
**Objective:** Add error handling & logging to services

**Tasks per Service File (repeat for all 4):**

1. **Import Infrastructure**
   - Import custom exceptions
   - Import logger
   - Import decorators

2. **Add Method-Level Logging**
   - Log method entry with parameters
   - Log business logic steps
   - Log method exit with results
   - Log execution time

3. **Implement Exception Handling**
   - Replace generic try-catch with custom exceptions
   - Add proper error context
   - Chain exceptions properly
   - Log stack traces for debugging

4. **Add Input Validation**
   - Validate parameters before processing
   - Log validation failures
   - Raise appropriate exceptions

5. **Add Database Error Handling**
   - Handle IntegrityError
   - Handle OperationalError
   - Log database issues

6. **Add Business Logic Validation**
   - Validate business rules before operations
   - Throw BusinessRuleException on violations
   - Log rule violations

**Example Patterns:**
```python
# Before (Old)
def verify_voter(self, voter_id):
    user = User.objects.get(pk=voter_id)
    user.is_verified = True
    user.save()

# After (New)
def verify_voter(self, voter_id: int, verified_by: User) -> User:
    """Verify a voter account with full error handling and logging."""
    logger = self._get_logger()
    
    try:
        logger.debug(f"Verifying voter: {voter_id} by {verified_by.username}")
        
        # Validate input
        if not isinstance(voter_id, int) or voter_id <= 0:
            logger.warning(f"Invalid voter_id type: {type(voter_id)}")
            raise ValidationException("Invalid voter ID")
        
        # Check existence
        try:
            user = User.objects.get(pk=voter_id)
        except User.DoesNotExist:
            logger.warning(f"Voter not found: {voter_id}")
            raise ResourceNotFoundException(f"Voter {voter_id} not found")
        
        # Business rule check
        if user.is_verified:
            logger.info(f"Voter already verified: {voter_id}")
            raise InvalidStateException("Voter is already verified")
        
        # Update
        user.is_verified = True
        user.save(update_fields=["is_verified"])
        
        logger.info(f"Voter {voter_id} verified successfully")
        self._audit.log("VERIFY_VOTER", verified_by.username, 
                       f"Verified voter: {user.get_full_name()}")
        
        return user
        
    except EVotingException:
        raise  # Re-raise custom exceptions
    except Exception as exc:
        logger.error(f"Unexpected error verifying voter {voter_id}: {exc}", 
                    exc_info=True)
        raise SystemException("Failed to verify voter") from exc
```

---

### Phase 3: Views Layer Enhancement (Days 5-6)
**Objective:** Add error handling & logging to views

**Tasks per View File (repeat for all 4):**

1. **Add Request Logging**
   - Log incoming request details
   - Log user/authentication info
   - Log request parameters

2. **Implement Exception Handling**
   - Catch custom exceptions
   - Map to proper HTTP status codes
   - Return standardized error responses

3. **Add Response Logging**
   - Log outgoing response status
   - Log response time
   - Log response size (for large responses)

4. **Implement Global Error Handler**
   - Create exception handler method
   - Map custom exceptions to HTTP status codes
   - Create error response from exception

5. **Add Permission Logging**
   - Log permission checks
   - Log authorization failures
   - Log access attempts

6. **Add Serializer Error Handling**
   - Log validation errors
   - Format validation error responses
   - Track common validation failures

**Example Pattern:**
```python
# Before (Old)
class AdminLoginView(APIView):
    def post(self, request):
        serializer = AdminLoginSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        service = AuthenticationService()
        user, error = service.authenticate_admin(
            serializer.validated_data["username"],
            serializer.validated_data["password"],
        )
        if error:
            return Response({"detail": error}, status=status.HTTP_401_UNAUTHORIZED)
        # ... rest of logic

# After (New)
class AdminLoginView(APIView):
    permission_classes = [AllowAny]
    serializer_class = AdminLoginSerializer
    
    def post(self, request):
        """Handle admin login with comprehensive error handling and logging."""
        correlation_id = request.headers.get('X-Correlation-ID')
        logger = self._get_logger()
        logger.info(f"[{correlation_id}] Admin login attempt: {request.data.get('username')}")
        
        try:
            # Validate serializer
            serializer = self.serializer_class(data=request.data)
            if not serializer.is_valid():
                logger.warning(f"[{correlation_id}] Validation failed: {serializer.errors}")
                return Response({
                    "success": False,
                    "error": {"code": "VALIDATION_ERROR", "details": serializer.errors}
                }, status=status.HTTP_400_BAD_REQUEST)
            
            # Authenticate
            service = AuthenticationService()
            user = service.authenticate_admin(
                serializer.validated_data["username"],
                serializer.validated_data["password"],
            )
            
            # Generate tokens
            refresh = RefreshToken.for_user(user)
            logger.info(f"[{correlation_id}] Admin login successful: {user.username}")
            
            return Response({
                "success": True,
                "data": {
                    "access": str(refresh.access_token),
                    "refresh": str(refresh),
                    "user": UserResponseSerializer(user).data
                }
            }, status=status.HTTP_200_OK)
            
        except InvalidCredentialsException as exc:
            logger.warning(f"[{correlation_id}] Invalid credentials: {exc}")
            return Response({
                "success": False,
                "error": {"code": "INVALID_CREDENTIALS", "message": str(exc)}
            }, status=status.HTTP_401_UNAUTHORIZED)
            
        except AccountDeactivatedException as exc:
            logger.warning(f"[{correlation_id}] Account deactivated: {exc}")
            return Response({
                "success": False,
                "error": {"code": "ACCOUNT_DEACTIVATED", "message": str(exc)}
            }, status=status.HTTP_403_FORBIDDEN)
            
        except Exception as exc:
            logger.error(f"[{correlation_id}] Unexpected error: {exc}", exc_info=True)
            return Response({
                "success": False,
                "error": {"code": "INTERNAL_SERVER_ERROR", "message": "An error occurred"}
            }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
```

---

### Phase 4: Serializers Layer Enhancement (Days 7)
**Objective:** Add validation logging and error context

**Tasks per Serializer File (repeat for all 4):**

1. **Add Custom Validators**
   - Create class-based validators
   - Add logging to validators
   - Track validation failures

2. **Add Field Validators**
   - Add logging to field validators
   - Track field-specific validation failures
   - Create detailed error messages

3. **Add Validation Error Tracking**
   - Log each validation failure
   - Include context in logs
   - Track patterns

4. **Add Documentation**
   - Add docstrings to validators
   - Document error codes
   - Include examples

**Example Pattern:**
```python
# Before (Old)
def validate_national_id(self, value):
    if VoterProfile.objects.filter(national_id=value).exists():
        raise serializers.ValidationError("A voter with this National ID already exists.")
    return value

# After (New)
def validate_national_id(self, value: str) -> str:
    """
    Validate national ID is not already registered.
    
    Args:
        value: The national ID to validate
        
    Returns:
        The validated national ID
        
    Raises:
        serializers.ValidationError: If national ID already exists
    """
    logger = self._get_logger()
    
    try:
        if not value or len(value) < 5:
            logger.debug(f"Invalid national ID format: {value}")
            raise serializers.ValidationError(
                {
                    "code": "INVALID_FORMAT",
                    "message": "National ID must be at least 5 characters"
                }
            )
        
        if VoterProfile.objects.filter(national_id=value).exists():
            logger.warning(f"Duplicate national ID registration attempt: {value}")
            raise serializers.ValidationError(
                {
                    "code": "DUPLICATE_RECORD",
                    "message": "A voter with this National ID already exists"
                }
            )
        
        logger.debug(f"National ID validation passed: {value[:5]}***")
        return value
        
    except serializers.ValidationError:
        raise
    except Exception as exc:
        logger.error(f"Unexpected error validating national ID: {exc}", exc_info=True)
        raise serializers.ValidationError(
            {
                "code": "VALIDATION_ERROR",
                "message": "Failed to validate National ID"
            }
        )
```

---

### Phase 5: Integration & Testing (Days 8-9)
**Objective:** Test, document, and optimize

1. **Integration Testing**
   - Test error flows end-to-end
   - Verify logging is working
   - Check log outputs

2. **Performance Testing**
   - Monitor logging performance impact
   - Optimize slow operations
   - Check log file sizes

3. **Security Testing**
   - Verify sensitive data is masked
   - Check for information leaks in logs
   - Test error message disclosure

4. **Documentation**
   - Create error code reference
   - Create troubleshooting guide
   - Document logging setup

5. **Code Review & Optimization**
   - Review all changes
   - Optimize repeated patterns
   - Final refinements

---

## 🎯 SOLID Principles Application

### Single Responsibility Principle
- Each exception class handles one error type
- Each logger handles one concern (audit, errors, performance)
- Each decorator has one purpose (logging, error handling, etc.)

### Open/Closed Principle
- Custom exception hierarchy is open for extension
- New exceptions can be added without modifying existing code
- Decorators can be composed for new functionality

### Liskov Substitution Principle
- All custom exceptions inherit from EVotingException
- Can be caught and handled uniformly
- Specific exception types can be caught individually

### Interface Segregation Principle
- Services define specific interfaces
- Loggers segmented by concern
- Error handlers separated by error type

### Dependency Inversion Principle
- Services depend on abstract logger interface
- Views depend on abstract service interface
- Database dependencies injected, not hardcoded

---

## 🔒 Security Considerations

1. **Sensitive Data Masking**
   - Mask email addresses in logs
   - Mask voter card numbers (except last 4)
   - Mask passwords (never log)
   - Mask personal identification numbers

2. **Error Message Disclosure**
   - Don't expose internal system details
   - Generic error messages to users
   - Detailed errors in server logs only
   - Stack traces only in debug mode

3. **Log File Security**
   - Restrict log file permissions (600)
   - Regular log rotation
   - Archive old logs
   - Encrypt sensitive logs

---

## 📊 Logging Levels & Usage

```
DEBUG   - Detailed diagnostic information (parameters, values)
INFO    - General informational messages (successful operations)
WARNING - Warning messages (unusual but non-critical)
ERROR   - Error messages (failures, exceptions)
CRITICAL- Critical messages (system shutdown, security issues)
```

---

## 🔢 Magic Numbers to Use as Constants

```python
# validation.py - CONSTANTS
MIN_PASSWORD_LENGTH = 6
MAX_USERNAME_LENGTH = 150
MIN_AGE = 18
MAX_NAME_LENGTH = 200
VOTER_CARD_LENGTH = 12
MAX_PHONE_LENGTH = 20

# logging.py - CONSTANTS
LOG_ROTATION_BYTES = 10 * 1024 * 1024  # 10MB
MAX_LOG_FILES = 5
LOG_FORMAT = '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
REQUEST_TIMEOUT_SECONDS = 30

# database.py - CONSTANTS
DEFAULT_DB_CONNECTION_TIMEOUT = 5
MAX_QUERY_TIME_SECONDS = 10
BATCH_SIZE = 100
```

---

## 📈 Performance Monitoring

Include in logs:
- Method execution time
- Database query time
- API response time
- Cache hit/miss rates
- Memory usage for large operations

---

## 🚀 Implementation Order

1. **Day 1-2:** Create core infrastructure
2. **Day 3-4:** Services layer
3. **Day 5-6:** Views layer
4. **Day 7:** Serializers layer
5. **Day 8-9:** Testing & optimization

**Total Duration:** 9 days

---

## ✅ Success Criteria

- [ ] All exceptions properly logged
- [ ] All database operations logged
- [ ] All API requests/responses logged
- [ ] All validation failures logged
- [ ] Error codes documented
- [ ] Sensitive data masked
- [ ] Log files created successfully
- [ ] No sensitive data in logs
- [ ] Performance impact < 5%
- [ ] All tests passing
- [ ] Code review completed

---

## 📚 Files to Create/Modify

### New Files to Create
```
evoting-app-backend/core/__init__.py
evoting-app-backend/core/exceptions.py          (450 lines)
evoting-app-backend/core/logging_config.py      (300 lines)
evoting-app-backend/core/decorators.py          (250 lines)
evoting-app-backend/core/error_handlers.py      (200 lines)
evoting-app-backend/core/response_formatter.py  (150 lines)
evoting-app-backend/core/middleware.py          (200 lines)
evoting-app-backend/core/constants.py           (100 lines)
```

### Existing Files to Modify
```
services.py files (4) - Average 200 lines added per file
views.py files (4) - Average 150 lines added per file
serializers.py files (4) - Average 100 lines added per file
settings.py - Add logging configuration
urls.py - Add middleware
```

---

**Status:** Plan ready for approval  
**Next Step:** Review with PowerPoint requirements, then proceed with Phase 1
