# Salty Gmailer

[![Python application](https://github.com/ryanlong1004/salty_gmailer/actions/workflows/python-app.yml/badge.svg?branch=main)](https://github.com/ryanlong1004/salty_gmailer/actions/workflows/python-app.yml)

Salty Gmailer is a FastAPI-based project designed to interact with Gmail using a salty approach. This project aims to provide a unique and efficient way to manage your Gmail account.

## Features

- Send and receive emails
- Organize emails with labels
- Search emails with advanced filters
- Manage contacts
- Schedule emails

## Installation

To install Salty Gmailer, follow these steps:

1. Clone the repository:
   ```bash
   git clone https://github.com/yourusername/salty_gmailer.git
   ```
2. Navigate to the project directory:
   ```bash
   cd salty_gmailer
   ```
3. Create a virtual environment:
   ```bash
   python -m venv venv
   ```
4. Activate the virtual environment:
   - On Windows:
     ```bash
     venv\Scripts\activate
     ```
   - On macOS/Linux:
     ```bash
     source venv/bin/activate
     ```
5. Install the required dependencies:
   ```bash
   pip install -r requirements.txt
   ```

## Usage

To start using Salty Gmailer, run the following command:

```bash
uvicorn app:app --host 0.0.0.0 --port 5010
```

## Dev

```bash
fastapi dev
```

## Docker

To build and run the application using Docker, follow these steps:

1. Build the Docker image:
   ```bash
   ./build.sh
   ```
2. Run the Docker container:
   ```bash
   ./run.sh
   ```

## API Endpoints

- `POST /folders`: Retrieves a list of folders.
- `POST /mark_as_read`: Marks emails as read.
- `POST /search`: Searches for emails.
- `POST /delete`: Deletes emails.
- `POST /unread_count_by_sender`: Retrieves the count of unread emails from each sender.

## Contributing

We welcome contributions! Please read our contributing guidelines for more information.

## License

This project is licensed under the MIT License. See the LICENSE file for details.

## Contact

For any questions or feedback, please open an issue on GitHub or contact us at support@saltygmailer.com.
