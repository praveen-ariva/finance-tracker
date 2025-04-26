# RESTful Finance Tracker

A comprehensive RESTful API for personal finance tracking, built with Python and Flask.

## Features

- 🔐 **User Authentication**: Secure registration and JWT-based login
- 💰 **Transaction Management**: Track income and expenses with categories
- 📊 **Budget Planning**: Set and monitor spending limits by category
- 📈 **Financial Reports**: Get spending summaries and budget compliance stats
- 🔄 **RESTful Architecture**: Well-designed API following REST principles
- 📚 **API Documentation**: Swagger UI for interactive API testing

## Tech Stack

- **Backend**: Python 3.10+, Flask
- **Database**: SQLAlchemy ORM with SQLite (dev) / PostgreSQL (prod)
- **Authentication**: Flask-JWT-Extended for token-based auth
- **Documentation**: Swagger/OpenAPI
- **Testing**: Pytest for unit and integration tests
- **Deployment**: Docker ready

## Installation

### Prerequisites

- Python 3.10+
- pip

### Setup Steps

1. **Clone the repository**

```bash
git clone https://github.com/yourusername/finance-tracker.git
cd finance-tracker
```

2. **Create and activate a virtual environment**

```bash
python -m venv venv

# On Windows
venv\Scripts\activate

# On macOS/Linux
source venv/bin/activate
```

3. **Install dependencies**

```bash
pip install -r requirements.txt
```

4. **Set up environment variables**

Create a `.env` file in the project root:

```
FLASK_APP=run.py
FLASK_ENV=development
DATABASE_URL=sqlite:///finance_tracker.db
JWT_SECRET_KEY=your-secret-key-change-this-in-production
```

5. **Initialize the database**

```bash
flask db init
flask db migrate -m "Initial migration"
flask db upgrade
```

6. **Run the application**

```bash
flask run
```

The API will be available at `http://127.0.0.1:5000/api`.

## API Documentation

Once the server is running, access the Swagger UI documentation at:

```
http://127.0.0.1:5000/api/docs
```

## API Endpoints

### Authentication

- `POST /api/auth/register` - Register a new user
- `POST /api/auth/login` - Login and get access token
- `POST /api/auth/refresh` - Refresh access token
- `GET /api/auth/profile` - Get current user profile

### Categories

- `GET /api/categories` - List all categories
- `GET /api/categories/{id}` - Get a specific category
- `POST /api/categories` - Create a new category
- `PUT /api/categories/{id}` - Update a category
- `DELETE /api/categories/{id}` - Delete a category

### Transactions

- `GET /api/transactions` - List all transactions
- `GET /api/transactions/{id}` - Get a specific transaction
- `POST /api/transactions` - Create a new transaction
- `PUT /api/transactions/{id}` - Update a transaction
- `DELETE /api/transactions/{id}` - Delete a transaction
- `GET /api/transactions/summary` - Get transaction summary

### Budgets

- `GET /api/budgets` - List all budgets
- `GET /api/budgets/{id}` - Get a specific budget
- `POST /api/budgets` - Create a new budget
- `PUT /api/budgets/{id}` - Update a budget
- `DELETE /api/budgets/{id}` - Delete a budget

### User Management

- `GET /api/users/me` - Get current user profile
- `PUT /api/users/me` - Update current user profile
- `POST /api/users/me/change-password` - Change password

## Testing

Run the tests with pytest:

```bash
pytest
```

## Docker Support

To build and run with Docker:

```bash
docker build -t finance-tracker .
docker run -p 5000:5000 finance-tracker
```

## Project Structure

```
finance-tracker/
│
├── app/
│   ├── __init__.py           # App initialization
│   ├── config.py             # Configuration
│   ├── api/                  # API endpoints
│   │   ├── __init__.py
│   │   ├── auth.py
│   │   ├── users.py
│   │   ├── transactions.py
│   │   ├── categories.py
│   │   └── budgets.py
│   │
│   ├── models/               # Database models
│   │   ├── __init__.py
│   │   ├── user.py
│   │   ├── transaction.py
│   │   ├── category.py
│   │   └── budget.py
│   │
│   ├── utils/                # Utilities
│   │   ├── __init__.py
│   │   └── helpers.py
│   │
│   └── static/               # Static files
│       └── swagger.json      # API documentation
│
├── tests/                    # Test suite
├── instance/                 # Instance-specific data
├── .env                      # Environment variables
├── .gitignore
├── README.md
├── requirements.txt
├── run.py                    # Application entry point
└── Dockerfile                # Docker configuration
```

## Development Workflow

1. Create categories for your expenses and income
2. Add transactions, associating them with categories
3. Set up budgets for different spending categories
4. Monitor your spending with the summary endpoints

## Future Enhancements

- Data visualization endpoints
- Currency conversion
- Financial goal setting
- Recurring transactions
- Export to CSV/PDF
- Email notifications for budget alerts

## Contributing

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/amazing-feature`)
3. Commit your changes (`git commit -m 'Add some amazing feature'`)
4. Push to the branch (`git push origin feature/amazing-feature`)
5. Open a Pull Request

## License

This project is licensed under the MIT License - see the LICENSE file for details.
