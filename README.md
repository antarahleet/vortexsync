# VortexSync Lead Migration Tool

VortexSync is a full-stack web application designed to automate the migration of real estate leads from the Vortex platform to the Boldtrail CRM. It provides a simple web interface for agents to trigger migrations for specific lead folders or for daily expired listings.

## Features

- **Simple Web Interface**: A clean UI built with Next.js and Tailwind CSS.
- **Folder-Based Migration**: Select any folder from your Vortex account and migrate all its leads with a single click.
- **Expireds Migration**: A dedicated button to migrate all of the latest "Daily Expireds" leads.
- **Automated Data Transformation**: Automatically converts the downloaded Vortex CSV into a format compatible with Boldtrail's bulk importer.
- **Dynamic Note Generation**: Creates a detailed, bulleted list of all available lead data in the Boldtrail agent notes for a comprehensive record.
- **Secure**: All credentials are kept safe in a local `.env` file and are never committed to the repository.

## Setup and Installation

Follow these steps to get VortexSync running on your local machine.

### 1. Clone the Repository
```bash
git clone <your-repository-url>
cd VortexSync
```

### 2. Backend Setup
First, set up the Python environment for the backend server.

```bash
# Create a virtual environment
python -m venv .venv

# Activate the virtual environment
# On Windows:
.venv\\Scripts\\activate
# On macOS/Linux:
# source .venv/bin/activate

# Install the required Python packages
pip install -r requirements.txt

# Install the required Playwright browser drivers
playwright install chromium
```

### 3. Frontend Setup
Next, set up the Node.js environment for the frontend interface.

```bash
# Navigate to the frontend directory
cd frontend

# Install the required Node packages
npm install
```

### 4. Configuration
Before running the application, you need to provide your credentials.

1.  Make a copy of the `.env.example` file and rename it to `.env`.
2.  Open the `.env` file and replace the placeholder values with your actual Vortex and Boldtrail login credentials.

## Running the Application

VortexSync requires two terminal windows to run simultaneously: one for the backend and one for the frontend.

**In your first terminal (for the backend):**
```bash
# Make sure you are in the project's root directory (VortexSync)
# and your virtual environment is activated.

python -m flask --app backend.app run --port 5000
```

**In your second terminal (for the frontend):**
```bash
# Navigate to the frontend directory
cd frontend

# Start the Next.js development server
npm run dev
```

Once both servers are running, you can access the application by opening your web browser to **`http://localhost:3000`**. 