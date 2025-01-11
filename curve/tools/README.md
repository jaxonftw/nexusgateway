## Setup Instructions(User): curve CLI

This guide will walk you through the steps to set up the curve cli on your local machine

### Step 1: Create a Python virtual environment

In the tools directory, create a Python virtual environment by running:

```bash
python -m venv venv
```

### Step 2: Activate the virtual environment
* On Linux/MacOS:

```bash
source venv/bin/activate
```

### Step 3: Run the build script
```bash
pip install curve==0.1.8
```

## Uninstall Instructions: curve CLI
```bash
pip uninstall curve
```

## Setup Instructions (Dev): curve CLI

This guide will walk you through the steps to set up the curve cli on your local machine when you want to develop the Curvegw CLI

### Step 1: Create a Python virtual environment

In the tools directory, create a Python virtual environment by running:

```bash
python -m venv venv
```

### Step 2: Activate the virtual environment
* On Linux/MacOS:

```bash
source venv/bin/activate
```

### Step 3: Run the build script
```bash
poetry install
```

### Step 4: build Curve
```bash
curve build
```

### Step 5: download models
This will help download models so server can load faster. This should be done once.

```bash
curve download-models
```

### Logs
`curve` command can also view logs from gateway and server. Use following command to view logs,

```bash
curve logs --follow
```

## Uninstall Instructions: curve CLI
```bash
pip uninstall curve
