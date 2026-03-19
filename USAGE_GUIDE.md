# E-Voting Application - Usage Guide

## Overview
This guide explains how to use the E-Voting application as different user types (Voter, Admin, Super Admin) and how to interact with the API.

---

## 🌐 Application URLs

| Component | URL | Purpose |
|-----------|-----|---------|
| **Frontend** | `http://localhost:3000` | Voter & Admin web interface |
| **Backend API** | `http://localhost:8000/api/` | REST API endpoints |
| **Django Admin** | `http://localhost:8000/admin/` | Django admin panel |

---

## 👥 User Roles & Access Levels

### 1. **Voter**
- Self-register on the platform
- View personal profile
- Cast votes in active elections
- View election results
- Access voting history

### 2. **Admin**
- Manage voters (verify, deactivate)
- Create and manage elections, candidates, positions
- View audit logs
- Generate statistics and reports
- Cannot manage other admins

### 3. **Super Admin**
- All admin capabilities
- Manage other admin accounts (create, deactivate)
- Full system access
- Audit trail review

---

## 🔐 Authentication

### Admin Login
1. Navigate to `http://localhost:3000/login`
2. Enter credentials:
   - **Username:** `admin`
   - **Password:** `admin123`
3. Click **Login**
4. Redirected to admin dashboard

### Voter Login
1. Navigate to `http://localhost:3000/login`
2. Toggle to **Voter Login**
3. Enter credentials:
   - **Voter Card Number:** (provided during registration)
   - **Password:** (voter's password)
4. Click **Login**
5. Redirected to voter dashboard

### API Token Authentication
All API requests require a JWT Bearer token:

```bash
# Get access token
curl -X POST http://localhost:8000/api/accounts/login/admin/ \
  -H "Content-Type: application/json" \
  -d '{"username": "admin", "password": "admin123"}'

# Response
{
  "access": "eyJ0eXAiOiJKV1QiLCJhbGc...",
  "refresh": "eyJ0eXAiOiJKV1QiLCJhbGc..."
}

# Use token in subsequent requests
curl -H "Authorization: Bearer eyJ0eXAiOiJKV1QiLCJhbGc..." \
  http://localhost:8000/api/elections/candidates/
```

---

## 📱 Frontend Usage

### For Voters

#### 1. **Registration**
- Click **"Register as Voter"** on login page
- Fill in required information:
  - Full Name
  - National ID
  - Voter Card Number
  - Email
  - Phone Number
  - Assigned Voting Station
  - Create Password
- Submit form
- Account pending admin verification

#### 2. **Access Dashboard**
- Login with voter credentials
- View personal information
- See assigned voting station

#### 3. **Cast Vote**
1. Navigate to **"Polls"** or **"Vote"** section
2. View active elections
3. Click **"Vote Now"** on desired election
4. Select candidate(s) per position
5. Review selections
6. **Confirm Vote**
7. Receive confirmation message

#### 4. **View Results**
- Navigate to **"Results"** section
- Select specific election or poll
- View vote counts per candidate
- See live statistics

#### 5. **View History**
- Navigate to **"My Votes"** or **"History"**
- See all previous voting activities
- View timestamps and details

#### 6. **Update Profile**
- Click **"Profile"** in navigation
- Update allowed fields:
  - Email
  - Phone Number
  - Password
- Save changes

---

### For Admins

#### 1. **Dashboard Overview**
Access admin panel at: `http://localhost:3000/admin`

**Key Sections:**
- **Dashboard** - Overall statistics (total voters, elections, votes)
- **Voters** - Manage voter accounts
- **Elections** - Create and manage elections
- **Candidates** - Add candidates
- **Positions** - Define voting positions
- **Stations** - Manage voting stations
- **Admins** - Manage admin accounts
- **Audit** - View activity logs
- **Results** - View voting results
- **Statistics** - Detailed analytics

#### 2. **Manage Voters**

**Verify Voters:**
1. Navigate to **Voters** → **Pending Verification**
2. Review voter information
3. Click **"Verify"** to approve
4. Or click **"Reject"** to deny

**Bulk Verify:**
1. Go to **Voters** → **Pending**
2. Click **"Verify All"**
3. Confirms all pending voters at once

**Deactivate Voter:**
1. Navigate to **Voters** → **Search** voter
2. Click voter profile
3. Click **"Deactivate"**
4. Confirm action

**Search Voters:**
- By Name: `?name=John`
- By Card Number: `?card=12345`
- By National ID: `?national_id=987654`
- By Station: `?station_id=1`

#### 3. **Create Election**

1. Navigate to **Elections** → **Polls**
2. Click **"Create New Poll"**
3. Fill in details:
   - **Poll Name** (e.g., "Presidential Election 2026")
   - **Description**
   - **Start Date/Time**
   - **End Date/Time**
   - **Select Positions** to include
4. Click **"Create"**
5. Add candidates to positions

#### 4. **Add Candidates**

1. Navigate to **Elections** → **Candidates**
2. Click **"Add Candidate"**
3. Enter details:
   - **Name**
   - **Position** (select from dropdown)
   - **Bio/Description**
   - **Image** (optional)
   - **Party** (optional)
4. Click **"Save"**

#### 5. **Create Positions**

1. Navigate to **Elections** → **Positions**
2. Click **"Create Position"**
3. Enter:
   - **Position Name** (e.g., "President", "Governor")
   - **Number of Candidates Allowed**
   - **Description**
4. Click **"Create"**

#### 6. **Manage Voting Stations**

1. Navigate to **Elections** → **Stations**
2. Click **"Create Station"**
3. Enter:
   - **Station Name**
   - **Location**
   - **Capacity**
   - **Address**
4. Click **"Save"**

#### 7. **View Audit Log**

1. Navigate to **Audit Log**
2. View all system activities:
   - User actions
   - Vote records
   - Administrative changes
   - Timestamps and user info
3. Filter by date or action type
4. Export audit trail if needed

#### 8. **Generate Statistics**

1. Navigate to **Statistics**
2. View metrics:
   - Total registered voters
   - Verified vs. pending
   - Votes cast per election
   - Voter turnout percentage
   - Candidate vote distribution
3. Download reports (CSV/PDF)

---

## 🔌 API Usage

### Authentication Endpoints

```bash
# Admin Login
POST /api/accounts/login/admin/
Body: {"username": "admin", "password": "admin123"}

# Voter Login
POST /api/accounts/login/voter/
Body: {"voter_card_number": "12345", "password": "password"}

# Refresh Token
POST /api/accounts/token/refresh/
Body: {"refresh": "refresh_token"}
```

### Account Endpoints

```bash
# Voter Registration
POST /api/accounts/register/
Body: {
  "full_name": "John Doe",
  "national_id": "987654",
  "voter_card_number": "12345",
  "email": "john@example.com",
  "phone_number": "+1234567890",
  "voting_station": 1,
  "password": "password123"
}

# Get Voter Profile
GET /api/accounts/profile/
Header: Authorization: Bearer <token>

# Change Password
POST /api/accounts/change-password/
Body: {"old_password": "old", "new_password": "new"}

# List All Voters (Admin)
GET /api/accounts/voters/?name=John
Header: Authorization: Bearer <admin_token>

# Verify Voter (Admin)
POST /api/accounts/voters/{id}/verify/
Header: Authorization: Bearer <admin_token>

# List Admins (Admin)
GET /api/accounts/admins/
Header: Authorization: Bearer <admin_token>
```

### Election Endpoints

```bash
# List Candidates
GET /api/elections/candidates/
Header: Authorization: Bearer <token>

# Create Candidate (Admin)
POST /api/elections/candidates/
Body: {
  "name": "John Smith",
  "position": 1,
  "bio": "Candidate bio...",
  "image": "url_to_image"
}

# List Positions
GET /api/elections/positions/

# List Voting Stations
GET /api/elections/stations/

# List/Create Polls
GET /api/elections/polls/
POST /api/elections/polls/
Body: {
  "name": "Election 2026",
  "description": "...",
  "start_date": "2026-03-20T08:00:00Z",
  "end_date": "2026-03-20T17:00:00Z",
  "positions": [1, 2, 3]
}
```

### Voting Endpoints

```bash
# Cast Vote
POST /api/voting/votes/
Header: Authorization: Bearer <voter_token>
Body: {
  "poll": 1,
  "candidates": [1, 2, 3]
}

# View Results
GET /api/voting/results/?poll_id=1

# Get Statistics
GET /api/voting/statistics/?poll_id=1

# Voter's Vote History
GET /api/voting/votes/my-votes/
Header: Authorization: Bearer <voter_token>
```

### Audit Endpoints

```bash
# View Audit Log
GET /api/audit/logs/
Header: Authorization: Bearer <admin_token>

# Filter by action
GET /api/audit/logs/?action=VOTE_CAST
```

---

## 📊 Common Workflows

### Workflow 1: Setup & Run Election

```
1. Super Admin creates voting stations
2. Super Admin creates positions
3. Super Admin creates candidates
4. Super Admin creates poll (election)
5. Voters self-register
6. Admin verifies voter accounts
7. Poll starts (voters can vote)
8. Poll ends (no more votes accepted)
9. Admin views results
10. Admin generates audit report
```

### Workflow 2: Voter Voting Process

```
1. Voter registers on platform
2. Wait for admin verification
3. Login to voter dashboard
4. Navigate to active polls
5. Select candidates for each position
6. Review selected choices
7. Confirm and cast vote
8. Receive confirmation message
9. Vote recorded in audit trail
```

### Workflow 3: Admin Election Management

```
1. Create voting stations
2. Add election positions
3. Register candidate candidates
4. Create poll with positions
5. Monitor voter registration
6. Verify pending voters
7. Monitor voting activity (real-time stats)
8. Close poll after end time
9. Review results
10. Export audit logs for compliance
```

---

## 🔍 Troubleshooting

### Issue: Cannot login
- **Voter:** Verify account has been approved by admin
- **Admin:** Check credentials are correct (default: admin/admin123)
- **Both:** Clear browser cache and cookies

### Issue: Cannot cast vote
- **Check:** Poll must be in "open" status
- **Check:** You haven't already voted in this poll
- **Check:** All required positions have selections

### Issue: Results not showing
- **Check:** Poll must be closed or results published
- **Check:** At least one vote must be cast
- **Try:** Refresh browser (F5)

### Issue: API returns 401 Unauthorized
- **Check:** Token included in Authorization header
- **Check:** Token hasn't expired (refresh if needed)
- **Check:** Use correct token for user type

### Issue: Port 8000 or 3000 already in use
```bash
# Kill process on port 8000
netstat -ano | findstr :8000
taskkill /PID <PID> /F

# OR run on different port
python manage.py runserver 8001
```

---

## 📋 Quick Reference

**Default Credentials:**
```
Username: admin
Password: admin123
```

**Database:** SQLite (db.sqlite3)

**API Documentation:** Available via OpenAPI/Swagger at backend

**Support:** See SETUP_DOCUMENTATION.md for setup issues

---

## 🎯 Best Practices

1. **Always verify voters** before elections start
2. **Back up database** regularly
3. **Review audit logs** after each election
4. **Test with test voters** before live election
5. **Use strong passwords** for admin accounts
6. **Monitor voting in real-time** during elections
7. **Export results** after poll closes for records
8. **Change default admin password** in production

---

**Last Updated:** March 19, 2026  
**Version:** 1.0  
**Status:** ✅ Complete
