# Wingz Ride Information API

Django REST API for managing ride information with advanced filtering, distance-based sorting, and performance optimizations.

## Features

- **Admin-only authentication** using custom role-based permissions
- **Full CRUD operations** for Rides, Users, and RideEvents
- **Advanced filtering** by status and rider email
- **Distance-based sorting** using Haversine formula calculated in database
- **Performance optimized** with select_related and prefetch_related (2-3 queries total)
- **Smart pagination** with customizable page size
- **24-hour event filtering** for large RideEvent tables

## Prerequisites

- Python 3.8+
- PostgreSQL 12+
- pip

## Installation

### 1. Clone Repository

```bash
git clone <repository-url>
cd wingz-ride-information-api
```

### 2. Create Virtual Environment

```bash
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
```

### 3. Install Dependencies

```bash
pip install -r requirements.txt
```

### 4. Configure Environment Variables

Create a `.env` file in the project root:

```env
SECRET_KEY=your-secret-key-here
DEBUG=True

# PostgreSQL Database Configuration
DATABASE_NAME=wingz_ride_db
DATABASE_USER=postgres
DATABASE_PASSWORD=your-password
DATABASE_HOST=localhost
DATABASE_PORT=5433
```

### 5. Create Database

```bash
# Using psql
psql -U postgres
CREATE DATABASE wingz_ride_db;
\q

# Or just create the db manually using pgadmin for example
```

### 6. Run Migrations

```bash
python manage.py migrate
```

### 7. Seed Test Data

```bash
python manage.py seed_data
```

This creates:
- 2 admin users (credentials: `admin`/`admin123`)
- 4 drivers (John Smith, Jane Doe, Mike Johnson, Lisa Brown)
- 6 riders
- 10 rides with various statuses for API testing
- 51 completed trips across 4 months (Jan-Apr 2024) with pickup/dropoff events for bonus SQL query
- Multiple ride events with timestamps

**Test Credentials:**
- Admin: `admin` / `admin123`
- Driver: `john_driver` / `driver123`
- Rider: `alice_rider` / `rider123`

### 8. Run Development Server

```bash
python manage.py runserver
```

API available at: `http://localhost:8000/api/`

## API Endpoints

### Authentication

All endpoints require admin role authentication. Use HTTP Basic Auth:

```bash
curl -u admin:admin123 http://localhost:8000/api/rides/
```

### Rides

- `GET /api/rides/` - List rides (with filters, sorting, pagination)
- `POST /api/rides/` - Create ride
- `GET /api/rides/{id}/` - Get ride details
- `PUT /api/rides/{id}/` - Update ride
- `PATCH /api/rides/{id}/` - Partial update
- `DELETE /api/rides/{id}/` - Delete ride

### Users

- `GET /api/users/` - List users
- `POST /api/users/` - Create user
- `GET /api/users/{id}/` - Get user details
- `PUT /api/users/{id}/` - Update user
- `DELETE /api/users/{id}/` - Delete user

### Ride Events

- `GET /api/ride-events/` - List ride events
- `POST /api/ride-events/` - Create ride event
- `GET /api/ride-events/{id}/` - Get event details
- `PUT /api/ride-events/{id}/` - Update event
- `DELETE /api/ride-events/{id}/` - Delete event

## Query Parameters

### Filtering

```bash
# Filter by ride status
/api/rides/?status=completed

# Filter by rider email
/api/rides/?rider_email=alice@example.com

# Filter ride events by ride ID
/api/ride-events/?id_ride=1
```

### Sorting

```bash
# Sort by pickup time (descending)
/api/rides/?ordering=-pickup_time

# Sort by distance to pickup location
/api/rides/?ordering=distance&latitude=37.7749&longitude=-122.4194
```

### Pagination

```bash
# Navigate pages (default: 10 items per page)
/api/rides/?page=2

# Custom page size (max: 100)
/api/rides/?page=1&page_size=20
```

### Combined Example

```bash
/api/rides/?status=completed&ordering=-pickup_time&page=2&page_size=15
```

## Performance Notes

- **Query Optimization**: Ride list API uses only 2-3 database queries regardless of result size
  - Query 1: Rides with related users (JOIN via `select_related`)
  - Query 2: Today's events only (filtered `prefetch_related`)
  - Query 3: Pagination count
  
- **24-Hour Events**: The `todays_ride_events` field returns only events from last 24 hours to optimize for large RideEvent tables

- **Distance Calculation**: Haversine formula computed in database using PostgreSQL functions for scalability

- **Database Indexes**: Composite indexes on frequently queried fields (`status`, `pickup_time`, `created_at`)

## Design Decisions

### 1. Modular Structure
Separated models, serializers, and views into individual files within dedicated folders for better maintainability.

### 2. TimestampedModel Base Class
Abstract base class provides DRY approach for `created_at`/`updated_at` fields across models.

### 3. Nullable Driver
`id_driver` is nullable to support ride lifecycle (requested → driver assigned → completed). Using `SET_NULL` on delete preserves ride history.

### 4. Separate Read/Write Serializers
- Read serializers include nested relationships for rich responses
- Write serializers use ForeignKey IDs for simpler input and password hashing

### 5. Custom Pagination Class
Allows clients to specify page size while enforcing maximum limit to prevent resource exhaustion.

### 6. Error Handling
- Validates GPS coordinates (latitude: -90 to 90, longitude: -180 to 180)
- Requires coordinates when using distance sorting

## Bonus: SQL Query for Trips > 1 Hour

Report showing count of trips longer than 1 hour, grouped by month and driver:

```sql
WITH ride_events_ordered AS (
    SELECT 
        id_ride,
        description,
        created_at,
        ROW_NUMBER() OVER (
            PARTITION BY id_ride, description 
            ORDER BY created_at
        ) as rn
    FROM ride_event
    WHERE description IN ('Status changed to pickup', 'Status changed to dropoff')
),
trip_durations AS (
    SELECT 
        r.id_driver,
        CONCAT(u.first_name, ' ', LEFT(u.last_name, 1)) as driver_name,
        TO_CHAR(pickup_event.created_at, 'YYYY-MM') as month,
        EXTRACT(EPOCH FROM (dropoff_event.created_at - pickup_event.created_at))/3600 as duration_hours
    FROM ride r
    INNER JOIN "user" u ON r.id_driver = u.id_user
    INNER JOIN ride_events_ordered pickup_event 
        ON r.id_ride = pickup_event.id_ride 
        AND pickup_event.description = 'Status changed to pickup' 
        AND pickup_event.rn = 1
    INNER JOIN ride_events_ordered dropoff_event 
        ON r.id_ride = dropoff_event.id_ride 
        AND dropoff_event.description = 'Status changed to dropoff' 
        AND dropoff_event.rn = 1
)
SELECT 
    month as "Month",
    driver_name as "Driver",
    COUNT(*) as "Count of Trips > 1 hr"
FROM trip_durations
WHERE duration_hours > 1
GROUP BY month, driver_name
ORDER BY month, driver_name;
```

### Query Explanation

1. **CTE 1 (ride_events_ordered)**: Uses `ROW_NUMBER()` to handle potential duplicate events, ensuring we get the first pickup and dropoff event for each ride
2. **CTE 2 (trip_durations)**: Uses `INNER JOIN` to match rides with both pickup and dropoff events, then calculates trip duration in hours using `EXTRACT(EPOCH FROM ...)`
3. **Final SELECT**: Filters trips > 1 hour, groups by month and driver name, returns sorted results

**Key Features:**
- Uses INNER JOIN to ensure rides have both pickup AND dropoff events
- Calculates duration by finding time difference between events
- Formats month as YYYY-MM for clean grouping
- Handles edge cases with ROW_NUMBER() partitioning

### Expected Output (from seed data)

After running `python manage.py seed_data`, the query will return:

```
    Month    |   Driver    | Count of Trips > 1 hr
-------------|-------------|----------------------
   2024-01   | Jane D      |           5
   2024-01   | John S      |           4
   2024-01   | Mike J      |           2
   2024-02   | Jane D      |           5
   2024-02   | John S      |           7
   2024-03   | Jane D      |           2
   2024-03   | John S      |           2
   2024-03   | Mike J      |          11
   2024-04   | Jane D      |           7
   2024-04   | Mike J      |           3
```

**Note**: The seed data creates 51 completed trips across 4 months (Jan-Apr 2024) with proper "Status changed to pickup" and "Status changed to dropoff" events to demonstrate the query functionality.

## Project Structure

```
wingz-ride-information-api/
├── config/                 # Django settings
├── rides/                  # Main app
│   ├── models/             # User, Ride, RideEvent models
│   ├── serializers/        # DRF serializers (read/write variants)
│   ├── views/              # ViewSets for API endpoints
│   ├── management/         # Custom commands (seed_data)
│   ├── filters.py          # Django-filter configurations
│   ├── permissions.py      # Custom permission classes
│   └── pagination.py       # Custom pagination class
├── requirements.txt        # Python dependencies
└── .env                    # Environment variables (not in repo)
```

## Technologies Used

- **Django 4.2.29** - Web framework
- **Django REST Framework 3.17.0** - API toolkit
- **PostgreSQL** - Database
- **django-filter 25.1** - Filtering support
- **psycopg2-binary** - PostgreSQL adapter
